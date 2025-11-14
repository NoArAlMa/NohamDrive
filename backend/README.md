# Documentation Backend pour Débutants

---

## Introduction

Ce document explique comment utiliser les outils principaux du backend : **FastAPI**, **SQLModel**, **Alembic**, et **Ruff**. L'objectif est de vous guider pour prendre en main ces outils efficacement.

---

## FastAPI

### Description

FastAPI est un framework web moderne pour construire des APIs avec Python. Il est rapide, facile à utiliser, et supporte la programmation asynchrone.

### Utilisation de Base

- Le fichier principal (`main.py`) contient l'instance de l'application FastAPI.
- Les endpoints sont définis avec des décorateurs comme `@app.get()` ou `@app.post()`.
- La documentation interactive est disponible à l'adresse `/docs` une fois le serveur lancé.

---

## SQLModel

### Description

SQLModel combine SQLAlchemy et Pydantic pour définir des modèles de base de données en utilisant des classes Python. Cela simplifie l'interaction avec la base de données tout en gardant de la puissance (Arthut ; ) .

### Utilisation de Base

- Définissez vos modèles dans des fichiers dédiés (ex: `models.py`).
- Utilisez `SQLModel` pour créer des tables et des relations.
- Les modèles sont utilisés pour interagir avec la base de données via des sessions SQLAlchemy.

---

## Alembic

### Description

Alembic est un outil de migration pour SQLAlchemy. Il permet de gérer les changements dans le schéma de la base de données.

### Commandes Importantes

| Commande                                       | Description                                                       |
| ---------------------------------------------- | ----------------------------------------------------------------- |
| `alembic init migrations`                      | Initialise Alembic dans votre projet.                             |
| `alembic revision --autogenerate -m "message"` | Génère une nouvelle migration basée sur les changements détectés. |
| `alembic upgrade head`                         | Applique toutes les migrations en attente.                        |
| `alembic downgrade -1`                         | Annule la dernière migration appliquée.                           |

### Configuration

- Modifiez `.env` pour configurer la connexion à votre base de données.

---

## Ruff

### Description

Ruff est un linter Python rapide qui aide à maintenir un code propre et cohérent.

### Commandes Importantes

| Commande             | Description                                                |
| -------------------- | ---------------------------------------------------------- |
| `ruff check .`       | Vérifie les erreurs de style et de syntaxe dans le projet. |
| `ruff check --fix .` | Corrige automatiquement les erreurs détectées.             |

---

## Pour Commencer

### Lancer le Serveur FastAPI

```bash
uvicorn main\:app --reload
```
