import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import OrbitalCanvas from "../components/OrbitalCanvas";

const RING_STYLES = {
  1: { badge: "border-cyan-500/30 bg-cyan-500/15 text-cyan-600", ring: "🔵" },
  2: { badge: "border-brand/30 bg-brand/15 text-brand", ring: "🟣" },
  3: { badge: "border-rose-500/30 bg-rose-500/15 text-rose-500", ring: "🔴" },
};

export default function Orbite() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const orbite = await api("/learning/orbite/");
      setData(orbite);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleRefresh = () => {
    setRefreshing(true);
    load();
  };

  if (loading) {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center space-y-4">
        <div className="h-12 w-12 animate-spin rounded-full border-2 border-brand border-t-transparent" />
        <p className="text-xs text-muted">Calcul de votre trajectoire orbitale en cours…</p>
      </div>
    );
  }

  const rings = data?.orbital_rings || [];

  return (
    <div className="mx-auto max-w-7xl space-y-10 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="badge !border-cyan-500/30 !bg-cyan-500/15 !text-cyan-600">🧭 Cartographie des Compétences</span>
            <span className="hidden text-xs text-muted sm:block">Moteur d'apprentissage adaptatif</span>
          </div>
          <h1 className="font-display text-3xl font-semibold sm:text-5xl">
            Mon{" "}
            <em className="bg-gradient-to-r from-brand-soft via-brand to-glow bg-clip-text font-semibold text-transparent not-italic">
              Orbite Personnelle
            </em>
          </h1>
          <p className="max-w-2xl text-xs leading-relaxed text-muted sm:text-sm">
            Visualisez vos compétences en rotation autour de votre profil. Chaque cours complété et quiz validé
            accélère votre gravité orbitale et débloque de nouveaux cercles de maîtrise.
          </p>
        </div>
        <button onClick={handleRefresh} disabled={refreshing} className="btn-ghost shrink-0 !px-4 text-xs">
          <span className={refreshing ? "inline-block animate-spin" : ""}>🔄</span> Recalculer mon Orbite
        </button>
      </div>

      <OrbitalCanvas orbiteData={data} />

      <div className="space-y-6 border-t border-line pt-6">
        <div>
          <h2 className="font-display text-xl font-semibold">Répartition par Anneaux d'Acquisition</h2>
          <p className="mt-0.5 text-xs text-muted">Détail des compétences acquises et en cours d'assimilation.</p>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {rings.map((ring) => (
            <div key={ring.tier} className="glass flex flex-col justify-between gap-4 p-5 shadow-sm">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className={`rounded-full px-3 py-1 text-xs font-bold tracking-wider uppercase ${RING_STYLES[ring.tier]?.badge}`}>
                    {RING_STYLES[ring.tier]?.ring} Orbite {ring.tier}
                  </span>
                  <span className="text-[11px] text-muted">
                    {ring.skills.length} compétence{ring.skills.length > 1 ? "s" : ""}
                  </span>
                </div>
                <div>
                  <h3 className="font-display text-base font-semibold">{ring.name}</h3>
                  <p className="mt-0.5 text-xs text-muted">{ring.subtitle}</p>
                </div>

                <div className="space-y-2 pt-2">
                  {ring.skills.length === 0 ? (
                    <p className="rounded-2xl border border-dashed border-line p-3 text-center text-xs text-muted">
                      Aucune compétence sur cet anneau pour le moment.
                    </p>
                  ) : (
                    ring.skills.map((skill) => (
                      <Link
                        key={skill.id}
                        to={`/formations/${skill.slug}`}
                        className="block space-y-1.5 rounded-2xl border border-line bg-paper-soft p-2.5 transition hover:border-brand/40"
                      >
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-medium">{skill.name}</span>
                          <span className="font-bold" style={{ color: skill.color || "#7C5CFF" }}>
                            {skill.mastery_score}%
                          </span>
                        </div>
                        <div className="h-1.5 w-full overflow-hidden rounded-full border border-line bg-paper">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{ width: `${skill.mastery_score}%`, backgroundColor: skill.color || "#7C5CFF" }}
                          />
                        </div>
                      </Link>
                    ))
                  )}
                </div>
              </div>

              <Link to="/catalogue" className="btn-ghost w-full text-xs">
                Explorer les formations liées ➜
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}