# Architecture du Projet

## 📂 Architecture des dossiers

```bash
📦 projet-final-nsi
├── 📂 frontend/              # Nuxt 4
│   ├── 📂 app/
│   │   ├── 📂 components/    # Composants Vue
│   │   │   └── 📂 ui/        # Composants réutilisables (boutons, inputs, etc.)
│   │   ├── 📂 pages/         # Pages principales (index.vue, login.vue)
│   │   └── 📂 stores/        # Stores Pinia (auth.ts, posts.ts)
│   ├── 📂 server/            # Pour contacter l'API
│   ├── 📄 .env               # Configuration Nuxt
│   └── 📄 nuxt.config.ts     # Configuration Nuxt
│
├── 📂 backend/               # FastAPI (ARCHITECTURE VARIABLE)
│   ├── 📂 api/               # Endpoints API
│   │   ├── 📄 auth.py        # Routes d'authentification
│   │   ├── 📄 posts.py       # Routes pour les posts
│   │   └── 📄 users.py       # Routes pour les utilisateurs
│   ├── 📂 models/            # Modèles SQLModel
│   │   ├── 📄 user.py        # Modèle utilisateur
│   │   └── 📄 post.py        # Modèle post
│   ├── 📂 schemas/           # Schémas Pydantic
│   ├── 📂 core/              # Configuration de base
│   │   ├── 📄 config.py      # Configuration de l'application
│   │   └── 📄 security.py    # Gestion de la sécurité (JWT, etc.)
│   ├── 📄 main.py            # Point d'entrée FastAPI
│   ├── 📄 requirements.txt   # Dépendances Python
│   └── 📄 .env               # Les variables d'environnements
│
├── 📂 desktop/               # Tauri (Rust)
│   ├── 📂 src-tauri/         # Code source Rust
│   └── 📄 tauri.conf.json    # Configuration Tauri
│
│
├── 📂 docs/                  # Documentation
│   ├── 📄 CONTRIBUTING.md    # Guide de contribution
│   └── 📄 ARCHITECTURE.md    # Vous êtes ici <==
├── 📄 .gitignore             # Fichiers ignorés par Git
├── 📄 README.md              # Fichier général

```

---

## Diagramme du projet

```mermaid
graph TD;
    Nuxt4["Nuxt 4 (Frontend)"] -->|Packaging| Tauri["Tauri (Desktop App)"];
    Nuxt4 -->|Call| Serveur["Serveur"];
    Serveur -->|Host| PostgreSQL["PostgreSQL<br>(Backend)"];
    Serveur -->|Stock| User["Dossier utilisateurs<br>(Le drive)"];
    Serveur -->|Appel API| FastAPI["FastAPI <br>(Backend)"]

    style Nuxt4 fill:#90EE90,stroke:#333
    style FastAPI fill:#87CEFA,stroke:#333
    style Tauri fill:#FFB6C1,stroke:#333
    style PostgreSQL fill:#F0E68C,stroke:#333
    style Serveur fill:#4287f5
```
