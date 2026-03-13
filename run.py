#!/usr/bin/env python3
"""
🚀 Lanceur du Moteur de Recherche N8N Workflows
Démarre le système de recherche avancé avec des performances optimisées.
"""
import sys
import os
import argparse


def print_banner():
        """Affiche la bannière de l'application."""
        print("🚀 n8n-workflows Moteur de Recherche Avancé")
        print("=" * 50)


def check_requirements() -> bool:
        """Vérifie que les dépendances requises sont installées."""
        missing_deps = []
        try:
                    import sqlite3
except ImportError:
        missing_deps.append("sqlite3")
    try:
                import uvicorn
except ImportError:
            missing_deps.append("uvicorn")
        try:
                    import fastapi
except ImportError:
            missing_deps.append("fastapi")
        if missing_deps:
                    print(f"❌ Dépendances manquantes : {', '.join(missing_deps)}")
                    print("💡 Installez-les avec : pip install -r requirements.txt")
                    return False
                print("✅ Dépendances vérifiées")
    return True


def setup_directories():
        """Crée les répertoires nécessaires."""
        directories = ["database", "static", "workflows"]
        for directory in directories:
                    os.makedirs(directory, exist_ok=True)
                print("✅ Répertoires vérifiés")


def setup_database(force_reindex: bool = False, skip_index: bool = False) -> str:
        """Configure et initialise la base de données."""
    from workflow_db import WorkflowDatabase

    db_path = "database/workflows.db"
    print(f"🔄 Configuration de la base de données : {db_path}")
    db = WorkflowDatabase(db_path)

    # Ignorer l'indexation en mode CI ou si explicitement demandé
    if skip_index:
                print("⏭️ Indexation des workflows ignorée (mode CI)")
                stats = db.get_stats()
                print(f"✅ Base de données prête : {stats['total']} workflows")
                return db_path

    # Vérifier si la base de données contient des données ou forcer la réindexation
    stats = db.get_stats()
    if stats["total"] == 0 or force_reindex:
                print("📚 Indexation des workflows...")
                index_stats = db.index_all_workflows(force_reindex=True)
                print(f"✅ {index_stats['processed']} workflows indexés")

    # Afficher les statistiques finales
    final_stats = db.get_stats()
    print(f"📊 La base de données contient {final_stats['total']} workflows")
    return db_path


def start_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
        """Démarre le serveur FastAPI."""
    print(f"🌐 Démarrage du serveur sur http://{host}:{port}")
    print(f"📊 Documentation API : http://{host}:{port}/docs")
    print(f"🔍 Recherche de workflows : http://{host}:{port}/api/workflows")
    print()
    print("Appuyez sur Ctrl+C pour arrêter le serveur")
    print("-" * 50)

    # Configurer le chemin de la base de données
    os.environ["WORKFLOW_DB_PATH"] = "database/workflows.db"

    # Démarrer uvicorn avec une meilleure configuration
    import uvicorn

    uvicorn.run(
                "api_server:app",
                host=host,
                port=port,
                reload=reload,
                log_level="info",
                access_log=False,  # Réduire le bruit dans les logs
    )


def main():
        """Point d'entrée principal avec arguments en ligne de commande."""
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
                description="Moteur de Recherche N8N Workflows",
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog="""
                Exemples :
                  python run.py                  # Démarrage avec les paramètres par défaut
                    python run.py --port 3000      # Démarrage sur le port 3000
                      python run.py --host 0.0.0.0   # Accepter les connexions externes
                        python run.py --reindex        # Forcer la réindexation de la base de données
                          python run.py --dev            # Mode développement avec rechargement auto
                                  """,
    )
    parser.add_argument(
                "--host",
                default="127.0.0.1",
                help="Hôte sur lequel se connecter (par défaut : 127.0.0.1)",
    )
    parser.add_argument(
                "--port",
                type=int,
                default=8000,
                help="Port sur lequel se connecter (par défaut : 8000)",
    )
    parser.add_argument(
                "--reindex",
                action="store_true",
                help="Forcer la réindexation de la base de données",
    )
    parser.add_argument(
                "--dev",
                action="store_true",
                help="Mode développement avec rechargement automatique",
    )
    parser.add_argument(
                "--skip-index",
                action="store_true",
                help="Ignorer l'indexation des workflows (utile pour CI/tests)",
    )
    args = parser.parse_args()

    # Vérifier également la variable d'environnement pour le mode CI
    ci_mode = os.environ.get("CI", "").lower() in ("true", "1", "yes")
    skip_index = args.skip_index or ci_mode

    print_banner()

    # Vérifier les dépendances
    if not check_requirements():
                sys.exit(1)

    # Configurer les répertoires
    setup_directories()

    # Configurer la base de données
    try:
                setup_database(force_reindex=args.reindex, skip_index=skip_index)
except Exception as e:
            print(f"❌ Erreur de configuration de la base de données : {e}")
            sys.exit(1)

    # Démarrer le serveur
        try:
                    start_server(host=args.host, port=args.port, reload=args.dev)
except KeyboardInterrupt:
            print("\n👋 Serveur arrêté !")
except Exception as e:
            print(f"❌ Erreur du serveur : {e}")
            sys.exit(1)


if __name__ == "__main__":
        main()
