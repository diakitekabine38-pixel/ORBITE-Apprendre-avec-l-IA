import { useEffect, useState } from "react";
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
            <a
              className="link mt-4 inline-block text-sm"
              href={`${import.meta.env.VITE_API_BASE || "/api/v1"}/certificates/verify/${c.certificate_id}/`}
              target="_blank"
              rel="noreferrer"
            >
              Vérifier publiquement →
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}