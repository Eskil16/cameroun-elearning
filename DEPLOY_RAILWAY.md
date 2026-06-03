# 🚂 Déploiement Railway — Guide Pas-à-Pas

## Réseau Académique Camerounais · Hébergement 100% Gratuit

---

## ⏱️ Temps estimé : 10 minutes

---

## ÉTAPE 1 — Installer Git (si pas déjà fait)

Télécharge Git : https://git-scm.com/download/win  
Installe avec les options par défaut, puis ouvre **Git Bash**.

---

## ÉTAPE 2 — Créer un compte GitHub (gratuit)

1. Va sur https://github.com
2. Clique **"Sign up"**
3. Crée ton compte (email + mot de passe)

---

## ÉTAPE 3 — Pousser le projet sur GitHub

Ouvre **Git Bash** dans le dossier `cameroun_elearning/` :

```bash
# Initialise Git
git init
git add .
git commit -m "Initial commit — Réseau Académique Camerounais"

# Crée un repo GitHub (remplace TON_USERNAME par ton nom GitHub)
# Va sur github.com → New Repository → Nom: "cameroun-elearning" → Create
# Puis :
git remote add origin https://github.com/TON_USERNAME/cameroun-elearning.git
git branch -M main
git push -u origin main
```

✅ Ton code est maintenant sur GitHub.

---

## ÉTAPE 4 — Créer le compte Railway

1. Va sur **https://railway.app**
2. Clique **"Start a New Project"**
3. Clique **"Login with GitHub"** → Autorise Railway
4. $5 de crédit offert automatiquement (≈ 1-2 mois gratuit)

---

## ÉTAPE 5 — Créer le projet sur Railway

### 5.1 Nouveau projet
1. Clique **"New Project"**
2. Choisit **"Deploy from GitHub repo"**
3. Sélectionne **"cameroun-elearning"**
4. ⚠️ Clique **"Add variables"** → on va configurer ça maintenant

### 5.2 Ajouter PostgreSQL
1. Dans ton projet Railway, clique **"+ New"**
2. Choisit **"Database"** → **"PostgreSQL"**
3. Railway crée la BDD et injecte `DATABASE_URL` automatiquement ✅

### 5.3 Configurer le dossier racine
1. Clique sur ton service (le code Django)
2. Va dans **Settings** → **Root Directory**
3. Tape : `backend`
4. Clique **"Save"**

---

## ÉTAPE 6 — Variables d'environnement

Dans Railway → ton service → onglet **"Variables"** → clique **"Raw Editor"** et colle :

```
SECRET_KEY=remplace-par-une-cle-aleatoire-longue-minimum-50-caracteres
DEBUG=False
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@elearning.cm
```

> **Générer une SECRET_KEY :** ouvre Python sur ton PC et tape :
> ```python
> import secrets; print(secrets.token_urlsafe(50))
> ```
> Copie le résultat dans la variable SECRET_KEY.

⚠️ **NE PAS** ajouter DATABASE_URL manuellement — Railway le gère tout seul.

---

## ÉTAPE 7 — Déployer !

1. Clique **"Deploy"** dans Railway
2. Regarde les logs en temps réel (onglet **"Deploy Logs"**)
3. Tu verras :
   ```
   🔧 Installation des dépendances...
   📊 Application des migrations...
   📁 Collecte des fichiers statiques...
   🌱 Initialisation des données...
   ✅ Build terminé avec succès !
   ```
4. Après ~3-5 minutes → **"Success"** ✅

---

## ÉTAPE 8 — Récupérer ton URL publique

1. Dans Railway → ton service → onglet **"Settings"**
2. Section **"Networking"** → clique **"Generate Domain"**
3. Tu obtiens une URL comme : `cameroun-elearning-production.up.railway.app`

Ouvre cette URL dans ton navigateur 🎉

---

## ✅ Comptes de démonstration

| Rôle | Email | Mot de passe |
|------|-------|-------------|
| Admin | admin@elearning.cm | admin123 |
| Modérateur | moderateur@elearning.cm | mod123456 |
| Formateur | formateur@elearning.cm | form123456 |
| Étudiant | etudiant@elearning.cm | etud123456 |

> ⚠️ Changie les mots de passe après la première connexion !

---

## 🔄 Mettre à jour l'application

À chaque modification du code :

```bash
git add .
git commit -m "Description de la modification"
git push origin main
```

Railway redéploie **automatiquement** en quelques minutes.

---

## 🛠️ Dépannage

### "Application Error" ou "502 Bad Gateway"
→ Vérifie les logs : Railway → Deploy Logs
→ La cause la plus fréquente : `SECRET_KEY` non définie

### "relation does not exist" (erreur BDD)
→ Va dans Railway → ton service → onglet "Settings" → "Deploy" → "Redeploy"
→ Les migrations se relancent automatiquement

### L'URL `/api/v1/` retourne 404
→ Vérifie que **Root Directory** = `backend` dans les settings du service

### Voir les logs en direct
Railway → ton service → onglet **"Logs"**

---

## 💡 Conseils

- **Garde ton crédit Railway** : le projet consomme environ $2-3/mois
  → Avec $5 offerts, tu as ~2 mois gratuits
  → Après, Railway coûte **~$5/mois** (très raisonnable)

- **Alternative si crédit épuisé** : utilise Render.com avec le même code,
  le déploiement est similaire.

---

*Réseau Académique Camerounais · KENFACK TATANG ALDO CHRISTIAN (ICTU20233734) · KISSO ESKIL HADAR (ICTU20233963)*
