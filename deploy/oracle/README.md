# Déploiement ORBITE sur Oracle Cloud Always Free

Mettre ORBITE en production **sans payer** : un VPS Ubuntu 24.04 toujours allumé
(Ampere A1), persistant (base de données, fichiers, certificats), avec nginx +
gunicorn. Environ **30 minutes** au total, une seule commande de provisioning.

Le dossier contient :

| Fichier                  | Rôle                                                           |
| ------------------------ | -------------------------------------------------------------- |
| `setup_oracle.sh`        | Provisionnement complet, idempotent (à relancer pour mettre à jour) |
| `update_oracle.sh`       | Mise à jour rapide (git pull + build + migrate + restart)      |
| `env.example`            | Variables d'environnement documentées                          |

---

## 1. Pré-requis (côté Windows)

La clé SSH a déjà été générée sur ta machine :

- Privée : `C:\Users\Perso\.ssh\orbite_oci`
- Publique : `C:\Users\Perso\.ssh\orbite_oci.pub`

Tu utiliseras cette **clé publique** pour créer la VM ci-dessous.

---

## 2. Créer le compte Oracle Cloud

1. Va sur https://signup.cloud.oracle.com
2. Renseigne email + mot de passe, puis les étapes de vérification
   (téléphone, carte bancaire **uniquement pour vérifier l'identité** — rien n'est débité
   tant que tu restes sur Always Free).
3. Termine l'onboarding (pays, type de compte **Personnel/Individuel**).

---

## 3. Ouvrir les ports (obligatoire)

1. Cloud → **Networking → Virtual Cloud Networks → (ton VCN)** → `Default Security List`.
2. Ajouter les **Ingress Rules** (Source `0.0.0.0/0`) :
   - `TCP 22` (SSH) — normalement déjà présente
   - `TCP 80` (HTTP)
   - `TCP 443` (HTTPS)

> Sans ces règles, le site répondra depuis la VM mais restera bloqué de l'extérieur.

---

## 4. Créer la machine (instance)

1. **Compute → Instances → Create instance.**
2. Nom : `orbite-dev` (par exemple).
3. **Image : Ubuntu 24.04** (Canonical) — pas Oracle Linux, pas Cloud Native Image.
4. **Shape : Ampere** → `VM.Standard.A1.Flex`, sélectionne `4 OCPU` / `24 GB RAM`
   (c'est le quota Always Free complet ; tu peux réduire à 2/12).
   → clic **Change shape** si le défaut est AMD.
5. **SSH keys** : coche *Paste public keys* et colle le contenu de
   `C:\Users\Perso\.ssh\orbite_oci.pub`.
6. **Boot volume** : garde les défauts (BALANCED, 50 Go — libre).
7. **Create instance**, attends que le statut passe à **Running**.
8. Note l'**IP publique** affichée (`130.61.x.x`).

> Conseil : `pin` l'instance dans le dashboard pour la retrouver vite.

---

## 5. Étape facultative : un vrai domaine (HTTPS)

Sans domaine, le site répond en **HTTP sur l'IP** — suffisant pour tester.
Pour du HTTPS (gratuit via Let's Encrypt), le plus simple est **DuckDNS** :

1. Crée un compte sur https://www.duckdns.org avec ton compte GitHub/Google.
2. Ajoute un sous-domaine, ex. `orbite-kweb.duckdns.org`.
3. Note ton **token** (utilisé plus bas).

---

## 6. Lancer le provisioning

Depuis **Windows** (PowerShell) :

```powershell
ssh -i C:\Users\Perso\.ssh\orbite_oci ubuntu@<IP_PUBLIQUE>
```

Puis sur le serveur :

```bash
cd ~
git clone https://github.com/diakitekabine38-pixel/ORBITE-Apprendre-avec-l-IA.git
cd ORBITE-Apprendre-avec-l-IA

# ---- Sans domaine (HTTP sur IP) ----
sudo ORBITE_LLM_API_KEY='ta_cle_groq' bash deploy/oracle/setup_oracle.sh

# ---- Avec domaine + HTTPS (ex. DuckDNS) ----
sudo ORBITE_LLM_API_KEY='ta_cle_groq' \
     ORBITE_DOMAIN='orbite-kweb.duckdns.org' \
     ORBITE_EMAIL='ton@email.com' \
     bash deploy/oracle/setup_oracle.sh
```

Ajoute au besoin `ORBITE_STRIPE_SECRET_KEY=...`, `ORBITE_TAVILY_API_KEY=...`.

Le script installe tout (nginx, PostgreSQL, Python, Node), construit le frontend,
migre la base et démarre le service. **Termine par un health-check.**

> La clé et le mot de passe de la base sont générés et stockés dans
> `/opt/orbite/app/backend/.env` (mode 600). Ne jamais committer ce fichier.

---

## 7. Vérifications post-install

```bash
# Statut du service + logs
systemctl status orbite --no-pager
journalctl -u orbite -n 50

# Test local
curl -s http://127.0.0.1:8000/api/health/
# -> {"status":"ok","service":"ORBITE API"}

# Test public (depuis ton PC)
Invoke-WebRequest -Uri "http://<IP_PUBLIQUE>/api/health/" -UseBasicParsing
```

Ouvre ensuite l'URL du site (IP ou domaine) dans le navigateur : tu dois voir
l'app REACT DE sécurité.

---

## 8. Créer l'administrateur et une apprenante de test

```bash
sudo -u orbite /opt/orbite/venv/bin/python /opt/orbite/app/backend/manage.py createsuperuser
# Puis, pour l'apprenant :
sudo -u orbite /opt/orbite/venv/bin/python /opt/orbite/app/backend/manage.py shell \
  -c "from apps.users.models import User; User.objects.create_user('apprenant_pa','a@orbite.example','Apprenant123!')"
```

---

## 9. Faire évoluer le site

1. Côté Windows : modifie le code, fais les migrations, **pushe sur GitHub**.
2. Sur le serveur :
   ```bash
   sudo bash /opt/orbite/app/deploy/oracle/update_oracle.sh
   ```
   (git pull + dépendances + build frontend + migrations + redémarrage)

---

## 10. Sauvegardes (régulières)

```bash
sudo -u postgres pg_dump orbite | gzip > /var/backups/orbite_$(date +%F).sql.gz
```
Récupère ce fichier sur ton PC :
```powershell
scp -i C:\Users\Perso\.ssh\orbite_oci ubuntu@<IP_PUBLIQUE>:/var/backups/orbite_2026-10-02.sql.gz .
```

---

## Dépannage

| Symptôme                  | Action                                                        |
| ------------------------- | ------------------------------------------------------------- |
| Site inaccessible en public | Ports 80/443 absents de la Security List (étape 3)            |
| `502 Bad Gateway`          | gunicorn Down : `journalctl -u orbite -n 50`                  |
| `DisallowedHost`           | `ORBITE_ALLOWED_HOSTS` ne contient pas l'URL → `.env`         |
| Page sans CSS              | `collectstatic` → relancer `update_oracle.sh`                 |
| L'IA répond « mock »       | `ORBITE_LLM_API_KEY` absente du `.env`                        |
| Lenteur au chat            | temps LLM > 180 s → augmenter `--timeout` de gunicorn         |