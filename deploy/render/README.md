# Déploiement ORBITE : Render (gratuit, sans carte) + base Supabase

Après le calvaire Oracle, voici l'alternative simple, gratuite et sans carte
bancaire : **hôte = Render** (web service Python/free, git deploys, HTTPS) et
**base = Supabase** (Postgres gratuit et persistant). Le frontend React buildé
est servi par WhiteNoise depuis le même service : **une seule URL**.

> Limites connues du plan free Render : le service s'endort après 15 min sans
> trafic et met ~1 min à redémarrer. Fichiers locaux (media uploads) non
> persistés entre deux déploiements — tout le reste (comptes, certificats,
> sessions) vit **dans Postgres** donc ne se perd jamais.

| Fichier                | Rôle                                            |
| ---------------------- | ----------------------------------------------- |
| `build.sh`             | Build (deps Python + frontend + collectstatic)  |
| `start.sh`             | Migrations + gunicorn                          |
| `render.yaml`          | Blueprint Render (optionnel)                    |

---

## 1. Créer la base Postgres (Supabase, ~5 min)

1. Compte sur https://supabase.com (gratuit, **pas de carte**).
2. **New project** → nom (`orbite`), région proche, mot de passe base.
   (Note-le dans un gestionnaire de mots de passe.)
3. Une fois créé : **Connect → Database strings → Direct connection** :
   - `Host` = `db.<ref>.supabase.co`
   - `Port` = `5432`
   - `User` = `postgres`
   - `Password` = celui du projet
   - `Database` = `postgres`

---

## 2. Créer le service sur Render (~10 min)

1. Compte sur https://render.com avec ton compte GitHub (gratuit, **pas de carte**).
2.  Dashboard **New → Web Service** :
   - Connecter le repo `ORBITE-Apprendre-avec-l-IA`.
   - Niveau "Blueprint" : Render détecte `deploy/render/render.yaml` → accepter.
   - OU manuel : sélectionner la branche, garder `Runtime = Python 3`, régler
     **Root Directory = `backend`**, puis `Build Command = bash ../deploy/render/build.sh`
     et `Start Command = bash ../deploy/render/start.sh`.
3. Plan **Free**, région `Frankfurt` (ou `Virginia` selon tes utilisateurs).
4. Si manuel : remplir les variables d'environnement suivantes (le blueprint les
   pose déjà, on ne remplit que les valeurs secrètes) :

   | Variable                  | Valeur                                                 |
   | ------------------------- | ------------------------------------------------------ |
   | `ORBITE_ALLOWED_HOSTS`    | `monapp.onrender.com`                                  |
   | `ORBITE_SITE_URL`         | `https://monapp.onrender.com`                          |
   | `ORBITE_CORS_ORIGINS`     | `https://monapp.onrender.com`                          |
   | `ORBITE_SECRET_KEY`       | (longue chaîne aléatoire, ex. générée par Render)      |
   | `ORBITE_JWT_SIGNING_KEY`  | (idem, différente)                                     |
   | `ORBITE_DB_SSLMODE`       | `require`                                              |
   | `ORBITE_DB_NAME`          | `postgres`                                             |
   | `ORBITE_DB_USER`          | `postgres`                                             |
   | `ORBITE_DB_PASSWORD`      | le mot de passe Supabase                               |
   | `ORBITE_DB_HOST`          | `db.<ref>.supabase.co`                                 |
   | `ORBITE_DB_PORT`          | `5432`                                                 |
   | `ORBITE_LLM_PROVIDER`     | `openai`                                               |
   | `ORBITE_LLM_MODEL`        | `openai/gpt-oss-120b`                                  |
   | `ORBITE_LLM_API_KEY`      | ta clé Groq                                            |
   | `ORBITE_TAVILY_API_KEY`   | (optionnel)                                            |
   | `ORBITE_STRIPE_*`         | (optionnel, sans rien : paiement manuel)               |

5. **Create Web Service** puis attends le premier build (~5-10 min).
6. Rends le service éveillé si besoin : oringine l'URL → le free tier connaît des
   cold starts après 15 min d'inactivité.

---

## 3. Créer l'administrateur (une seule fois)

Pendant le déploiement, on a besoin d'exécuter une commande dans l'environnement
Render : soit **Logs → Push to Shell**, soit utiliser **SQL de Supabase** pour
créer l'admin (plus propre, aucun accès serveur nécessaire) :

```sql
-- Dans Supabase -> SQL Editor (ferme la clé : hashé ci-dessous par exemple)
INSERT INTO users_user ...;
```
Plus simple pour démarrer : passer par l'endpoint d'inscription de l'app
(`/api/v1/auth/register/`) depuis la page d'inscription du site en ligne ; puis
promouvoir le compte en admin via SQL :
```sql
UPDATE users_user SET is_staff = true, is_superuser = true
WHERE username = 'ton_compte_inscrit';
```

---

## 4. Vérifier

1. `https://monapp.onrender.com/api/health/` → `{"status":"ok","service":"ORBITE API"}`
2. Accueil : le frontend React s'affiche.
3. Inscription + login : le compte est écrit dans **Postgres/ Supabase** → il
   survit à tout redéploiement.

---

## 5. Évoluer / déployer

- **Déploiement auto** : chaque push sur `main` redéploie automatiquement Render.
- **Migrations** : elles tournent au démarrage (`start.sh` → `manage.py migrate`).
- Pour un vrai domaine : onglet **Settings** du service → Custom Domain → HTTPS
  incluse.
- Sauvegardes : Supabase fournit des exports (Dashboard → Database → Backups /
  meilleur : `pg_dump` via l'URL de connexion).

---

## Dépannage

| Symptôme                     | Action                                                        |
| ---------------------------- | -------------------------------------------------------------- |
| `502` au premier accès        | Cold start free (~1 min), relancer l'URL                        |
| `DisallowedHost`              | `ORBITE_ALLOWED_HOSTS` doit contenir ton `*.onrender.com`       |
| `connection refused...5432`   | Host/Port/PASSWORD Supabase mal copiés, ou `ORBITE_DB_SSLMODE`  |
| `SSL error`                   | mettre `ORBITE_DB_SSLMODE=require`                              |
| Page sans styles              | logs du build → `collectstatic` + redéploiement (push vierge)   |
| L'IA répond « mock »          | `ORBITE_LLM_API_KEY` absente                                   |
| Certificats/avatars perdus    | normal : media éphémère sur free (données sont en base)         |