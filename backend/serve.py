"""Point d'entrée production locale — ORBITE.

Lance Django (site buildé + API + statiques) derrière Waitress,
serveur WSGI compatible Windows. Usage :

    python serve.py            # production locale, port 8000

TODO: sur un VPS Linux, remplacer par gunicorn/web.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from waitress import serve  # noqa: E402
from config.wsgi import application  # noqa: E402

HOST = os.environ.get("ORBITE_SERVE_HOST", "127.0.0.1")
PORT = int(os.environ.get("ORBITE_SERVE_PORT", "8000"))
THREADS = int(os.environ.get("ORBITE_SERVE_THREADS", "8"))

# Cap on Windows console write issues when launched detached.
if os.environ.get("ORBITE_SERVE_LOGFILE"):
    logfile = Path(os.environ["ORBITE_SERVE_LOGFILE"])
    logfile.parent.mkdir(parents=True, exist_ok=True)
    stream = logfile.open("a", encoding="utf-8")
    sys.stdout = stream
    sys.stderr = stream

if __name__ == "__main__":
    print(f"ORBITE prêt sur http://{HOST}:{PORT} (waitress, {THREADS} threads)")
    serve(application, host=HOST, port=PORT, threads=THREADS)