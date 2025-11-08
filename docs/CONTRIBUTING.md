# Contribuer à Projet Final NSI

⚠️ **ATTENTION CE PROJET N'ACCEPTE AUCUN CONTRIBUTEURS EXTERNES !** ⚠️
Pour que tout se passe bien, voici les règles du jeu.

---

## 1. Branches

- **Nommage** : `type/description-courte` (ex: `feature/auth-login`, `fix/post-likes`).
  - Types autorisés : `feature`, `fix`, `docs`, `refactor`.
- **Base** : Toujours brancher depuis `dev`.
- **Mise à jour** : `git pull origin dev` avant de commencer.

---

## 2. Pull Requests (PR)

### Conditions pour merger

- [ ] La PR est liée à une **issue** (ex: "Closes #12").
- [ ] Un **reviewer** a approuvé (mentionne @Karssou).

### Titre de la PR

- Format : `[TYPE] Description courte` (ex: `[FEAT] Ajout du bouton Like`).
- Types : `FEAT`, `FIX`, `DOCS`, `REFACTOR`.

### Description de la PR

- **Contexte** : Pourquoi ce changement ?
- **Modifications** : Liste des fichiers modifiés entre gros guillemets
- **Captures** : Si UI, ajoutez un screenshot (optionnel) (utilisez [Markdown](https://guides.github.com/features/mastering-markdown/)).
- **Checklist** :
  - [ ] J’ai testé mon code localement.
  - [ ] J’ai suivi les conventions du projet.

---

## 3. Conventions de code

### Général

- **Commits** : Messages clairs en anglais (ex: "Add login form validation").
- **Langue** : Commentaires en **français** (pour l’équipe de loups ahouuuu), mais noms de variables/fonctions en **anglais**.

### Frontend (Nuxt)

- Composants **réutilisables** → dans `/components/ui/`.

### Backend (FastAPI)

- **Endpoints** : Toujours typer les retours (ex: `def get_user() -> UserSchema`).
- **Sécurité** : Ne jamais commiter de secrets (utilisez `.env`).

---

## 4. Setup local

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

### Backend

```bash
python venv venv ./venv #un truc dans le genre quoi
./Scripts/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**\*N'oubliez pas d'utilisez **Postman** pour tester NOTRE api\***

Et surtout n'oubliez pas qu'a chaque erreur je vous défonce !!
Et si vous avez des questions à ne pas hésitez surtout = D
