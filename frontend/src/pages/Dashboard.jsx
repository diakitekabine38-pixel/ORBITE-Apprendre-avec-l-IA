import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, apiPost } from "../api";
import { useAuth } from "../auth";

export default function Dashboard() {
  const { user, refresh } = useAuth();
  const [data, setData] = useState(null);
  const [recs, setRecs] = useState([]);

  useEffect(() => {
    api("/learning/enrollments/dashboard/")
      .then(setData)
      .catch(() => setData({ enrollments: [], streak_days: 0, xp: 0, level: 1, goals: [] }));
  }, []);

  async function refreshRecs() {
    const r = await apiPost("/ai/recommendations/refresh/").catch(() => []);
    setRecs(r || []);
  }

  useEffect(() => {
    if (data) refreshRecs();
  }, [data]);

  const enrollments = data?.enrollments || [];

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">
            Bonjour, {user?.first_name || user?.username} 👋
          </h1>
          <p className="mt-1 text-muted">Voici ta vue centrale d'apprentissage.</p>
        </div>
        <div className="flex gap-3">
          <div className="glass px-5 py-3 text-center">
            <p className="font-display text-2xl font-bold text-brand-soft">{data?.xp ?? user?.xp ?? 0}</p>
            <p className="text-xs text-muted">XP · Nv.{data?.level ?? 1}</p>
          </div>
          <div className="glass px-5 py-3 text-center">
            <p className="font-display text-2xl font-bold text-glow">{data?.streak_days ?? 0}</p>
            <p className="text-xs text-muted">jours actifs</p>
          </div>
          <div className="glass px-5 py-3 text-center">
            <p className="font-display text-2xl font-bold">{enrollments.length}</p>
            <p className="text-xs text-muted">formations</p>
          </div>
        </div>
      </div>

      {data?.goals?.length > 0 && (
        <div className="glass mt-8 p-4">
          <p className="text-sm text-muted">Objectifs actifs : {data.goals.join(" · ")}</p>
        </div>
      )}

      <h2 className="mt-10 mb-4 text-xl font-bold">Mes formations</h2>
      {enrollments.length === 0 ? (
        <div className="glass p-10 text-center">
          <p className="text-muted">Tu n'es pas encore inscrit à une formation.</p>
          <Link to="/catalogue" className="btn-primary mt-4">Découvrir le catalogue</Link>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {enrollments.map((enr) => (
            <div key={enr.id} className="glass p-5">
              <div className="flex items-start justify-between gap-2">
                <h3 className="font-semibold leading-snug">{enr.course.title}</h3>
                {enr.completed ? (
                  <span className="badge !border-emerald-600/40 !text-emerald-700">Terminée</span>
                ) : (
                  <span className="badge">En cours</span>
                )}
              </div>
              <div className="mt-4 h-2 overflow-hidden rounded-full bg-ink/10">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-brand to-glow transition-all"
                  style={{ width: `${Math.min(100, Math.round(enr.progress || 0))}%` }}
                />
              </div>
              <p className="mt-2 text-sm text-muted">{Math.round(enr.progress || 0)}% terminée</p>
              <div className="mt-4 flex gap-2">
                <Link to={`/apprentissage/${enr.course.slug}`} className="btn-primary w-full !py-2 text-xs">
                  {enr.completed ? "Revoir" : "Continuer"}
                </Link>
                {enr.certificate && (
                  <Link to="/certificats" className="btn-ghost !py-2 text-xs" title="Voir le certificat">🎓</Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <h2 className="mt-10 mb-4 text-xl font-bold">Recommandations du moteur adaptatif</h2>
      {recs.length === 0 ? (
        <p className="text-muted">Commence une formation pour recevoir des recommandations.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {recs.map((r) => (
            <div key={r.id} className="glass p-5">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-sm text-brand-soft">{r.reason}</span>
                <span className="text-xs text-muted">score {Math.round(r.score * 100)}</span>
              </div>
              <p className="text-sm text-muted">{r.rationale}</p>
              <Link to={`/formations/${r.course.slug}`} className="link mt-2 inline-block text-sm">
                Voir la formation →
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}