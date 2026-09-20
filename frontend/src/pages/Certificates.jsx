import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function Certificates() {
  const [certs, setCerts] = useState([]);

  useEffect(() => {
    api("/certificates/")
      .then((d) => setCerts(d.results || []))
      .catch(() => {});
  }, []);

  if (certs.length === 0) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-16 text-center">
        <p className="text-5xl">🎓</p>
        <h1 className="mt-4 text-2xl font-bold">Tes certificats</h1>
        <p className="mt-2 text-muted">Termine une formation à 100% pour décrocher un certificat ORBITE vérifiable.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="text-3xl font-bold">Tes certificats</h1>
      <p className="mt-1 text-muted">Chaque certificat dispose d'un identifiant vérifiable publiquement.</p>

      <div className="mt-8 grid gap-5 md:grid-cols-2">
        {certs.map((c) => (
          <div key={c.id} className="glass border-brand/30 p-6">
            <div className="flex items-start justify-between">
              <span className="text-4xl">🎓</span>
              <span className="badge">vérifiable</span>
            </div>
            <h2 className="mt-4 font-display text-lg font-bold">{c.course_title || c.certificate_id}</h2>
            <p className="mt-1 text-sm text-muted">Décerné le {new Date(c.issued_at).toLocaleDateString("fr-FR")}</p>
            <p className="mt-4 font-mono text-xs text-glow">{c.certificate_id}</p>
            <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
              <Link to={`/verification/${c.certificate_id}`} className="link">
                Vérifier publiquement →
              </Link>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <a
                className="btn-ghost inline-flex !px-3 !py-1 text-xs"
                href={`${window.location.origin}/verification/${c.certificate_id}`}
                target="_blank"
                rel="noreferrer"
              >
                Lien de partage ↗
              </a>
              <button
                className="btn-ghost inline-flex !px-3 !py-1 text-xs"
                onClick={() =>
                  navigator.clipboard
                    ?.writeText(`${window.location.origin}/verification/${c.certificate_id}`)
                    .then(() => alert("Lien copié !"))
                }
              >
                Copier le lien
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}