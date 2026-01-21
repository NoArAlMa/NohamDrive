# Documentation Backend : Configuration et Développement

Ce guide est conçu pour vous aider à configurer et développer le backend du projet en utilisant **FastAPI**, **Ruff** et **MinIO**. Suivez ces instructions pour installer, configurer et lancer le serveur localement.

---

## Table des Matières

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Lancement du serveur](#lancement-du-serveur)
4. [Bonnes pratiques](#bonnes-pratiques)

---

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les outils suivants sur votre machine :

- **Python 3.12 ou supérieur** ([Téléchargement](https://www.python.org/downloads/))
- **PostgreSQL** ([Téléchargement](https://www.postgresql.org/download/))
- **Docker** (pour MinIO, optionnel mais recommandé) ([Téléchargement](https://www.docker.com/get-started))
- **Git** ([Téléchargement](https://git-scm.com/downloads))

---

## Installation

### 1. Créer un environnement virtuel

- Créez un environnement virtuel pour isoler les dépendances du projet :

  ```bash
  python -m venv .venv
  ```

- Ensuite, il faut installer les dépendances du projet, pour cela il faut s'assurer que le .venv est activé ! Pour l'activer tapez :

  ```bash
  ./.venv/Scrips/activate
  ```

  Pour vérifier qu'on utilise bien le **.venv**, regarder votre terminal, si un **(venv)** apparaît devant le champs de saisie, c'est bon !

- Finalement on installe toutes les dépendances du projet avec la commande :

  ```bash
  pip install -r requirements.txt
  ```

### 2. Configuration de l'environnement

Si vous venez de copier le projet, vous avez certainement un `.env.example` à la racine du dossier `backend/`, celui-ci contient différentes variables obligatoire pour le bon fonctionnement de l'API

- Créer un fichier .env
  Copiez le contenu ci-dessous dans un fichier `.env` à la racine du projet backend :

#### Configuration de la base de données

DB_USER=michel
DB_PASSWORD=root
DB_NAME=lala
DB_HOST=localhost

#### Configuration JWT

SECRET_KEY=ta_cle_secrete_ici
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAY=30

#### Configuration MinIO

MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=False

#### Configuration du serveur

DEBUG=True
CORS_ORIGINS=["*"]
PORT=8000

> > Notes : Vous pouvez générer facilement une clée secrète en tapant la commande suivante dans le terminal :
>
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(32))"
> ```

- Explications des variables d'environnement

#### Base de données

DB_USER : Nom d'utilisateur pour la base de données PostgreSQL.
DB_PASSWORD : Mot de passe pour la base de données.
DB_NAME : Nom de la base de données.
DB_HOST : Adresse du serveur PostgreSQL .

#### JWT

SECRET_KEY : Clé secrète pour la génération des tokens JWT.
ALGORITHM : Algorithme utilisé pour la signature des tokens (par défaut : HS256).
ACCESS_TOKEN_EXPIRE_DAY : Durée de validité des tokens (en jours).

#### MinIO

MINIO_ENDPOINT : Adresse du serveur MinIO.
MINIO_ACCESS_KEY et MINIO_SECRET_KEY : Identifiants pour accéder à MinIO.
MINIO_SECURE : Définissez sur True si vous utilisez HTTPS.

#### Serveur

DEBUG : Active le mode debug (ne pas utiliser en production).
CORS_ORIGINS : Liste des origines autorisées pour les requêtes CORS.
PORT : Port sur lequel le serveur FastAPI écoute.

---

## Lancement du serveur

### 1. Démarrer le serveur FastAPI

Lancez le serveur avec la commande suivante :

```bash
uvicorn main:app --reload
```

> --reload : Active le rechargement automatique du serveur lors des modifications du code. 2. Accéder à la documentation interactive

> Notes : Assurez vous d'avoir bien mis toutes vos variables d'environnements, le serveur ne se lancera pas tant que ce sera le cas

Une fois le serveur démarré, accédez à la documentation interactive de FastAPI à l'adresse suivante :
http://localhost:8000/docs

### 2. Utilisation de MinIO

- Lancer MinIO avec Docker
  Si vous utilisez Docker, lancez MinIO avec la commande suivante :

docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"

- Accéder à la console MinIO
  Accédez à la console MinIO à l'adresse suivante :

  http://localhost:9001
  Utilisez les identifiants définis dans votre fichier `.env` (MINIO_ACCESS_KEY et MINIO_SECRET_KEY).

---

## Bonnes pratiques

### 1. Utilisation de Ruff

Ruff est un linter rapide pour Python. Pour vérifier la qualité de votre code :

```bash
ruff check .
```

Pour corriger automatiquement les problèmes :

```bash
ruff check --fix .
```
