import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";

export default function VerifyCertificate() {
  const { certificateId } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api(`/certificates/verify/${certificateId}/`, { auth: false })
      .then(setData)
      .catch((e) => setError(e.message || "Certificat introuvable."))
      .finally(() => setLoading(false));
  }, [certificateId]);

  return (
    <div className="mx-auto max-w-2xl px-4 py-14">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Vérification de certificat</h1>
          <p className="mt-1 text-muted">Authenticité ORBITE · contrôle public en temps réel.</p>
        </div>
        <Link to="/" className="btn-ghost text-sm">Accueil</Link>
      </div>

      {loading ? (
        <div className="glass p-10 text-center text-muted">Vérification en cours…</div>
      ) : error ? (
        <div className="glass border-rose-300 p-8 text-center">
          <p className="text-4xl">❌</p>
          <h2 className="mt-3 text-xl font-bold text-rose-600">Certificat invalide</h2>
          <p className="mt-2 text-sm text-muted">{error}</p>
        </div>
      ) : (
        <div className="glass border-emerald-500/40 p-8">
          <div className="flex items-center justify-between">
            <p className="text-5xl">🎓</p>
            <span className="badge !border-emerald-600/40 !text-emerald-700">✓ valide</span>
          </div>
          <p className="mt-5 font-display text-xl font-bold">Certificat authentique ORBITE</p>
          <div className="mt-6 space-y-3 border-t border-line pt-5 text-sm">
            <p className="flex justify-between gap-4">
              <span className="text-muted">Titulaire</span>
              <span className="font-semibold">{data.user_name}</span>
            </p>
            <p className="flex justify-between gap-4">
              <span className="text-muted">Formation</span>
              <span className="font-semibold">{data.course_title}</span>
            </p>
            <p className="flex justify-between gap-4">
              <span className="text-muted">Décerné le</span>
              <span className="font-semibold">{new Date(data.issued_at).toLocaleDateString("fr-FR")}</span>
            </p>
            <p className="flex flex-col gap-1 border-t border-line pt-3">
              <span className="text-muted">Identifiant</span>
              <span className="font-mono text-xs text-glow break-all">{data.certificate_id}</span>
            </p>
          </div>
          <div className="mt-6 rounded-xl bg-ivory-soft p-4 text-center text-sm">
            <span className="font-display font-semibold">ORBITE</span> — Apprendre avec l'IA ·
            Certificat vérifié via <code className="rounded bg-paper px-1.5 py-0.5 font-mono text-xs">/certificates/verify</code>
          </div>
        </div>
      )}
    </div>
  );
}