# 🇨🇲 Réseau Académique Camerounais — Plateforme E-Learning

Plateforme e-learning adaptée au contexte camerounais : faible bande passante, accès mobile,
bilinguisme FR/EN, modération communautaire, mode hors ligne.

---

## 🗂️ Architecture

```
cameroun_elearning/
├── backend/                    # Django 4.2 + DRF + PostgreSQL
│   ├── apps/
│   │   ├── users/              # Auth JWT, profils, rôles
│   │   ├── courses/            # Cours, modules, progression, notes
│   │   ├── social/             # Follow, fil d'actualité, likes
│   │   ├── moderation/         # Signalements, file de modération
│   │   └── reputation/         # Points, badges, classement
│   ├── config/                 # settings.py, urls.py, wsgi.py
│   ├── media/                  # Uploads (vidéos, PDFs, avatars)
│   ├── init_db.py              # Initialisation BDD + données démo
│   └── requirements.txt
└── frontend/                   # HTML + Bootstrap 5 + Vanilla JS
    ├── index.html              # Catalogue
    ├── login.html              # Connexion
    ├── register.html           # Inscription
    ├── profile.html            # Profil public / personnel
    ├── course_detail.html      # Détail cours + lecteur vidéo
    ├── create_course.html      # Création de cours (formateurs)
    ├── dashboard_moderator.html # Tableau de bord modération
    ├── offline.html            # Page hors ligne (Service Worker)
    ├── css/style.css           # Design mobile-first
    ├── js/
    │   ├── api.js              # Client JWT, fetch, toasts
    │   ├── offline-sync.js     # Queue offline, progression locale
    │   └── i18n.js             # Traductions FR/EN
    └── sw.js                   # Service Worker (cache offline)
```

---

## ⚡ Démarrage rapide

### 1. Prérequis

- Python 3.10+
- PostgreSQL 14+
- Node.js (optionnel, uniquement pour outils de dev)

### 2. Environnement virtuel et dépendances

```bash
cd cameroun_elearning/backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Variables d'environnement

```bash
cp .env.example .env
# Éditez .env avec vos paramètres de base de données
```

Contenu minimal du `.env` :
```
SECRET_KEY=votre-cle-secrete-aleatoire-longue
DEBUG=True
DB_NAME=cameroun_elearning
DB_USER=postgres
DB_PASSWORD=votre_mdp
DB_HOST=localhost
DB_PORT=5432
```

### 4. Base de données PostgreSQL

```sql
-- Dans psql ou pgAdmin :
CREATE DATABASE cameroun_elearning;
CREATE USER postgres WITH PASSWORD 'votre_mdp';
GRANT ALL PRIVILEGES ON DATABASE cameroun_elearning TO postgres;
```

### 5. Migrations Django

```bash
python manage.py makemigrations users
python manage.py makemigrations courses
python manage.py makemigrations social
python manage.py makemigrations moderation
python manage.py makemigrations reputation
python manage.py migrate
```

### 6. Initialisation — données de démo

```bash
python init_db.py
```

Ce script crée automatiquement :
- 👤 **Admin** : `admin@elearning.cm` / `admin123`
- 🛡️ **Modérateur** : `moderateur@elearning.cm` / `mod123456`
- 🎓 **Formateur** : `formateur@elearning.cm` / `form123456`
- 📚 **Étudiant** : `etudiant@elearning.cm` / `etud123456`
- 10 catégories camerounaises (Agriculture, NTIC, Santé…)
- 8 badges (dont 3 badges spéciaux 🇨🇲)
- 3 cours de démonstration approuvés

### 7. Lancer le serveur

```bash
python manage.py runserver
```

Ouvrez ensuite **`frontend/index.html`** dans votre navigateur,
ou naviguez vers `http://127.0.0.1:8000/`.

---

## 🌐 API REST — Endpoints

Tous les endpoints sont préfixés par `/api/v1/`.
Toutes les réponses JSON incluent `success` et `message`.

### Authentification

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/auth/register/` | Créer un compte |
| POST | `/auth/login/` | Connexion (retourne JWT) |
| POST | `/auth/refresh/` | Rafraîchir le token |
| POST | `/auth/logout/` | Blacklister le refresh token |
| POST | `/auth/verify/` | Vérifier l'email par code |
| POST | `/auth/change-password/` | Changer le mot de passe |

### Utilisateurs

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET/PATCH | `/users/me/` | Profil personnel |
| GET | `/users/{id}/` | Profil public |
| POST | `/users/{id}/follow/` | Suivre un utilisateur |
| DELETE | `/users/{id}/unfollow/` | Ne plus suivre |
| GET | `/users/{id}/followers/` | Liste des abonnés |
| GET | `/users/{id}/following/` | Liste des abonnements |

### Cours

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/courses/` | Catalogue (filtres, recherche, pagination) |
| POST | `/courses/create/` | Créer un cours (formateur) |
| GET | `/courses/my/` | Mes cours créés |
| GET | `/courses/enrolled/` | Cours auxquels je suis inscrit |
| GET | `/courses/categories/` | Liste des catégories |
| GET | `/courses/{id}/` | Détail d'un cours |
| PATCH | `/courses/{id}/` | Modifier un cours |
| DELETE | `/courses/{id}/` | Supprimer un cours |
| POST | `/courses/{id}/enroll/` | S'inscrire à un cours |
| GET/POST | `/courses/{id}/rate/` | Voir/Ajouter une note (≥80% progression) |
| GET/POST | `/courses/{course_id}/modules/` | Modules d'un cours |
| GET/PATCH | `/courses/modules/{id}/` | Détail/modif d'un module |
| POST | `/courses/modules/{id}/progress/` | Mettre à jour la progression |

**Paramètres de filtre (GET /courses/)** :
- `search` — recherche textuelle
- `category` — ID de catégorie
- `level` — `beginner`, `intermediate`, `expert`
- `language` — `fr`, `en`, `both`
- `low_bandwidth` — `true` (< 50 Mo)
- `ordering` — `-created_at`, `-average_rating`, `-enrollment_count`

### Social

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/social/feed/` | Fil d'actualité personnel |
| POST | `/social/feed/{id}/like/` | Liker/unliker une publication |

### Modération

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/moderation/queue/` | File de modération (modérateurs+) |
| POST | `/moderation/courses/{id}/report/` | Signaler un cours |
| POST | `/moderation/courses/{id}/review/` | Soumettre un avis de modération |

### Réputation

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/reputation/badges/` | Liste de tous les badges |
| GET | `/reputation/leaderboard/` | Classement (top 50) |
| GET | `/reputation/my-history/` | Mon historique de points |

---

## 🏆 Système de réputation

| Action | Points |
|--------|--------|
| Cours approuvé par un modérateur | +10 pts |
| Like reçu sur une publication | +1 pt |
| Signalement validé par un modérateur | +2 pts |

**Seuil modérateur** : 100 points de réputation

### Badges camerounais spéciaux

| Badge | Icône | Condition |
|-------|-------|-----------|
| Champion de la Data | 📡 | Tous les cours publiés font < 50 Mo |
| Prof Hors Ligne | 📴 | A des modules téléchargeables |
| Mentor Bilangue | 🇨🇲 | A publié des cours bilingues (FR+EN) |
| Signaleur Vigilant | 🔍 | A signalé du contenu invalide avec succès |

---

## 📡 Mode hors ligne

### Fonctionnement

1. **Service Worker** (`sw.js`) cache tous les assets statiques à l'installation.
2. **Progression vidéo** → sauvegardée dans `localStorage` toutes les 5 secondes.
3. **File d'attente** (`OfflineQueue`) → les requêtes POST échouées sont rejouées à la reconnexion.
4. **Modules téléchargés** → mis en cache via Cache API (vidéo + PDF).
5. **Synchronisation automatique** → à la reconnexion (`window.addEventListener('online', ...)`).

### Télécharger un module

1. S'inscrire au cours
2. Ouvrir un module
3. Cliquer sur ⬇️ **Télécharger hors ligne**
4. Le module est disponible même sans connexion

---

## 🌐 Bilinguisme (FR/EN)

- Toggle dans la navbar → change la langue de l'interface instantanément
- La langue est sauvegardée dans `localStorage`
- Le profil utilisateur contient `preferred_language` (fr/en)
- Les catégories et badges ont `name_fr` + `name_en`
- Les réponses API incluent `message` dans la langue du profil utilisateur

---

## 🔒 Sécurité

- JWT stocké dans `localStorage` avec expiration courte (2h) + refresh (7j)
- Blacklist des refresh tokens à la déconnexion
- Validation des types MIME pour les uploads (vidéo MP4, PDF)
- Limite taille : vidéo 300 Mo, PDF 20 Mo
- Protection XSS : `escHtml()` systématique dans les templates JS
- CORS configuré via `ALLOWED_HOSTS` et `CORS_ALLOWED_ORIGINS`
- En production : `SECURE_SSL_REDIRECT`, cookies sécurisés

---

## 🗃️ Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `SECRET_KEY` | — | Clé secrète Django (obligatoire) |
| `DEBUG` | `True` | Mode debug |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hôtes autorisés |
| `DB_NAME` | `cameroun_elearning` | Nom de la BDD |
| `DB_USER` | `postgres` | Utilisateur PostgreSQL |
| `DB_PASSWORD` | `postgres` | Mot de passe PostgreSQL |
| `DB_HOST` | `localhost` | Hôte PostgreSQL |
| `DB_PORT` | `5432` | Port PostgreSQL |
| `EMAIL_BACKEND` | Console | Backend email |
| `EMAIL_HOST_USER` | — | Adresse email d'envoi |
| `EMAIL_HOST_PASSWORD` | — | Mot de passe email |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:8000` | Origines CORS autorisées |

---

## 🛠️ Commandes utiles

```bash
# Créer les migrations après modification d'un modèle
python manage.py makemigrations <app_name>
python manage.py migrate

# Créer un superadmin manuellement
python manage.py createsuperuser

# Vider le cache de tokens blacklistés (tâche périodique)
python manage.py flushexpiredtokens

# Collecter les fichiers statiques (production)
python manage.py collectstatic --noinput

# Shell Django
python manage.py shell
```

---

## 📱 Design Mobile

- Bootstrap 5 — mobile-first
- Cartes cours : 2 colonnes sur mobile, 4 sur desktop
- Formulaires courts (champs optionnels minimisés)
- Composants tactiles (zones de tap larges ≥ 44px)
- Images en `lazy loading` pour économiser la data
- Mode économie de données : masque images et vidéos

---

## 🐛 Dépannage

**Erreur `psycopg2` à l'installation** :
```bash
pip install psycopg2-binary
```

**`ModuleNotFoundError: No module named 'decouple'`** :
```bash
pip install python-decouple
```

**Le frontend ne charge pas le CSS** :
- Ouvrez via `http://127.0.0.1:8000/` (pas en double-cliquant sur le fichier HTML)
- Ou servez avec `python -m http.server 3000` depuis le dossier `frontend/`

**Erreur JWT 401** :
- Vérifiez que `SIMPLE_JWT.ACCESS_TOKEN_LIFETIME` est correct dans `settings.py`
- Effacez `localStorage` du navigateur et reconnectez-vous
