# Déploiement ORBITE : alwaysdata Free (jamais endormi, 0 €, sans carte)

L'offre qui ne dort jamais : gratuite à vie, sans carte bancaire, disque
persistant (SQLite fonctionne, fichiers conservés), HTTPS automatique et
sauvegardes quotidiennes (3 jours glissants).

| Fichier   | Rôle                                            |
| --------- | ----------------------------------------------- |
| `setup.sh`| Préparation idempotente (clone→venv→migrate) et mise à jour |

Limites honnêtes du plan **Free** : **256 Mo RAM**, 1/4 CPU, usage **personnel /
non commercial**, sites sur le sous-domaine `moncompte.alwaysdata.net`.
Sans carte bancaire enregistrée, alwaysdata met un « mode restreint »
(traitement HTTP un peu plus lent, envoi d'emails SMTP plafonné) — **rien de
bloquant** pour ORBITE.

---

## 1. Créer le compte (~2 min)

1. Inscription sur https://www.alwaysdata.com (email + mot de passe, **aucune
   carte**, offre **Free**, défauts)
2. Choisis le **nom de compte**, ex. `orbite-kweb` → ton URL sera
   `https://orbite-kweb.alwaysdata.net`. Note cette URL.

## 2. Préparer l'accès SSH

1. Panneau → **Profil → Keys SSH** → colle ta clé publique
   (`C:\Users\Perso\.ssh\orbite_oci.pub`).
2. Depuis Windows :
   ```powershell
   ssh -i C:\Users\Perso\.ssh\orbite_oci orbite-kweb@ssh-orbite-kweb.alwaysdata.net
   ```
   (Si pas de clé : panneau → **Remote access → Web terminal**.)

## 3. Lancer la préparation (une seule commande)

```bash
# Depuis le shell SSH :
export ORBITE_LLM_API_KEY='ta_cle_groq'          # obligatoire pour l'IA
export ORBITE_SITE_URL='https://orbite-kweb.alwaysdata.net'
curl -fsSL -o ~/setup.sh https://raw.githubusercontent.com/diakitekabine38-pixel/ORBITE-Apprendre-avec-l-IA/main/deploy/alwaysdata/setup.sh
bash ~/setup.sh
```

Le script : clone le dépôt, crée le venv, installe les dépendances, écrit le
`.env`, fait les **migrations** et le **collectstatic**. (Le frontend React est
déjà buildé dans le dépôt → aucun build Node sur le serveur.)

## 4. Créer le site (panneau alwaysdata)

1. Onglet **Web → Sites → Add a site**.
2. **Type** : `Python (WSGI)`.
3. **Address** : `orbite-kweb.alwaysdata.net`.
4. **Application path** : `/home/orbite-kweb/orbite/backend/config/wsgi.py`
5. **Working directory** : `/home/orbite-kweb/orbite/backend`
6. **Python virtualenv** : `/home/orbite-kweb/orbite/venv`
7. **Python version** : celle du venv (3.12).
8. **Status : On** → Save.

HTTPS : panneau → **SSL certificates** → *Let's Encrypt* sur ton sous-domaine
(ou activer « Let's Encrypt automatique » au niveau « Sites → settings »).

## 5. Vérifier

```powershell
Invoke-WebRequest -Uri "https://orbite-kweb.alwaysdata.net/api/health/"
# -> {"status":"ok","service":"ORBITE API"}
```
Puis ouvre l'URL dans le navigateur : le frontend s'affiche, l'inscription
écrit dans **SQLite** → les comptes survivent aux mises à jour.

## 6. Créer l'administrateur

```bash
# Dans le shell SSH :
/home/orbite-kweb/orbite/venv/bin/python /home/orbite-kweb/orbite/backend/manage.py createsuperuser
```

## 7. Mettre à jour

```bash
# Re-lancer le script : git pull + deps + migrations + statiques.
bash ~/setup.sh
```
(puis toujours relancer via SSH ; l'URL ne change pas).

## 8. Sauvegardes

alwaysdata sauvegarde le compte automatiquement (3 jours glissants sur Free).
Export manuel ponctuel :
```powershell
scp -i C:\Users\Perso\.ssh\orbite_oci orbite-kweb@ssh-orbite-kweb.alwaysdata.net:orbite/backend/orbite.sqlite3 .
```

---

## Dépannage

| Symptôme                      | Action                                                        |
| ----------------------------- | ------------------------------------------------------------- |
| `DisallowedHost`              | `ORBITE_ALLOWED_HOSTS` dans `~/orbite/backend/.env`           |
| 500 au premier accès           | `ssh` → `bash ~/setup.sh` (migrations) puis recharge le site  |
| L'IA répond « mock »           | `ORBITE_LLM_API_KEY` absente du `.env`                        |
| HTTPS absent                   | activer Let's Encrypt dans **SSL certificates**               |
| Site instable / RAM saturée    | passer à l'offre Small (5 €/mois) quand tu passes en production |
| Emails non envoyés             | mode restreint (pas de carte) : SMTP plafonné — pas critique   |

---

## Comparaison rapide des 3 cibles préparées

| Cible        | Sommeil | Carte requise | Disque persist. | Données | Complexité |
| ------------ | ------- | ------------- | --------------- | ------- | ---------- |
| **alwaysdata Free** | **Non**    | Non           | Oui             | SQLite  | Faible |
| Render Free (dossier `deploy/render`) | Oui (15 min) | Non | Non (Postgres via Supabase) | Supabase | Moyenne |
| PythonAnywhere Free | Non | Non | Oui | SQLite | Faible |