import { useState } from "react";
import { Link } from "react-router-dom";

export default function OrbitalCanvas({ orbiteData }) {
  const [selectedSkill, setSelectedSkill] = useState(null);

  if (!orbiteData) return null;

  const { learner, orbital_rings = [], recommendation } = orbiteData;

  const size = 700;
  const center = size / 2;

  const allPlottedSkills = [];

  orbital_rings.forEach((ring) => {
    const skills = ring.skills || [];
    const count = skills.length;
    if (count === 0) return;
    const angleStep = (2 * Math.PI) / count;
    const phaseShift = (ring.tier * Math.PI) / 4;
    skills.forEach((skill, index) => {
      const angle = index * angleStep + phaseShift;
      allPlottedSkills.push({
        ...skill,
        ringTier: ring.tier,
        ringName: ring.name,
        x: center + ring.radius * Math.cos(angle),
        y: center + ring.radius * Math.sin(angle),
      });
    });
  });

  const ringFills = { 1: "bg-cyan-500/15", 2: "bg-brand/15", 3: "bg-rose-500/15" };

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="glass space-y-1 p-4 shadow-sm">
          <span className="flex items-center gap-1.5 text-[11px] font-medium tracking-wider text-muted uppercase">🎯 Gravité orbitale</span>
          <p className="font-display text-xl font-bold">{learner.gravitational_index}%</p>
          <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full border border-line bg-paper-soft">
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${learner.gravitational_index}%`,
                background: "linear-gradient(to right,#22D3EE,#7C5CFF,#4C1D95)",
              }}
            />
          </div>
        </div>
        <div className="glass space-y-1 p-4 shadow-sm">
          <span className="flex items-center gap-1.5 text-[11px] font-medium tracking-wider text-muted uppercase">⚡ Expérience totale</span>
          <p className="font-display text-xl font-bold">
            {learner.xp} <span className="text-xs font-normal text-amber-500">XP</span>
          </p>
          <span className="text-[10px] text-muted">Niveau {learner.level} atteint</span>
        </div>
        <div className="glass space-y-1 p-4 shadow-sm">
          <span className="flex items-center gap-1.5 text-[11px] font-medium tracking-wider text-muted uppercase">🔥 Série active</span>
          <p className="font-display text-xl font-bold">
            {learner.streak_days} <span className="text-xs font-normal text-muted">jours</span>
          </p>
          <span className="text-[10px] font-medium text-emerald-500">Régularité optimale</span>
        </div>
        <div className="glass space-y-1 p-4 shadow-sm">
          <span className="flex items-center gap-1.5 text-[11px] font-medium tracking-wider text-muted uppercase">🧠 Compétences</span>
          <p className="font-display text-xl font-bold">{learner.active_skills_count}</p>
          <span className="text-[10px] text-muted">En rotation orbitale</span>
        </div>
      </div>

      <div className="grid grid-cols-1 items-start gap-8 lg:grid-cols-3">
        <div className="relative flex flex-col items-center justify-center overflow-hidden rounded-3xl border border-line bg-paper p-4 shadow-sm sm:p-8 lg:col-span-2">
          <div className="pointer-events-none absolute h-[500px] w-[500px] rounded-full bg-brand/10 blur-[100px]" />
          <div className="pointer-events-none absolute h-[300px] w-[300px] rounded-full bg-cyan-500/10 blur-[80px]" />

          <div className="relative aspect-square w-full max-w-[620px]">
            <svg viewBox={`0 0 ${size} ${size}`} className="h-full w-full select-none">
              <defs>
                <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="6" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
                <filter id="coreGlow" x="-50%" y="-50%" width="200%" height="200%">
                  <feGaussianBlur stdDeviation="15" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
                <radialGradient id="centerGradient" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#7C3AED" stopOpacity="0.7" />
                  <stop offset="60%" stopColor="#2563EB" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="transparent" stopOpacity="0" />
                </radialGradient>
              </defs>

              {orbital_rings.map((ring) => (
                <g key={ring.tier}>
                  <circle
                    cx={center}
                    cy={center}
                    r={ring.radius}
                    fill="none"
                    stroke={ring.tier === 1 ? "#2563EB" : ring.tier === 2 ? "#7C3AED" : "#EC4899"}
                    strokeWidth="1.2"
                    strokeDasharray="4 6"
                    opacity="0.35"
                  />
                  <text
                    x={center}
                    y={center - ring.radius + 14}
                    fill="var(--color-muted)"
                    fontSize="9"
                    fontFamily="monospace"
                    textAnchor="middle"
                    letterSpacing="1"
                    opacity="0.8"
                  >
                    ORBITE {ring.tier} · {ring.name.toUpperCase()}
                  </text>
                </g>
              ))}

              {selectedSkill && (
                <line
                  x1={center}
                  y1={center}
                  x2={selectedSkill.x}
                  y2={selectedSkill.y}
                  stroke={selectedSkill.color || "#7C3AED"}
                  strokeWidth="1.5"
                  strokeDasharray="3 3"
                  opacity="0.8"
                />
              )}

              <circle cx={center} cy={center} r="65" fill="url(#centerGradient)" filter="url(#coreGlow)" />
              <circle cx={center} cy={center} r="40" fill="var(--color-paper)" stroke="#7C3AED" strokeWidth="2.5" />
              <circle
                cx={center}
                cy={center}
                r="45"
                fill="none"
                stroke="#2563EB"
                strokeWidth="1"
                opacity="0.4"
                className="animate-ping [animation-duration:3s]"
              />
              <text
                x={center}
                y={center - 6}
                fill="var(--color-ink-deep)"
                fontSize="12"
                fontWeight="bold"
                textAnchor="middle"
              >
                {(learner.full_name || "ORBITE").split(" ")[0]}
              </text>
              <text
                x={center}
                y={center + 12}
                fill="#7C3AED"
                fontSize="10"
                fontWeight="bold"
                textAnchor="middle"
              >
                NIV. {learner.level}
              </text>

              {allPlottedSkills.map((skill) => {
                const isSelected = selectedSkill?.id === skill.id;
                const planetRadius = Math.max(14, Math.min(22, 12 + (skill.mastery_score / 100) * 10));
                return (
                  <g
                    key={skill.id}
                    onClick={() => setSelectedSkill(skill)}
                    className="cursor-pointer transition-transform duration-200 active:scale-95"
                    style={{ transformOrigin: `${skill.x}px ${skill.y}px` }}
                  >
                    <circle cx={skill.x} cy={skill.y} r={Math.max(28, planetRadius + 10)} fill="transparent" />
                    {isSelected && (
                      <circle
                        cx={skill.x}
                        cy={skill.y}
                        r={planetRadius + 10}
                        fill="none"
                        stroke={skill.color || "#7C3AED"}
                        strokeWidth="2"
                        filter="url(#glow)"
                        opacity="0.8"
                      />
                    )}
                    <circle
                      cx={skill.x}
                      cy={skill.y}
                      r={planetRadius}
                      fill="var(--color-paper)"
                      stroke={skill.color || "#7C3AED"}
                      strokeWidth={isSelected ? "3" : "2"}
                      filter="url(#glow)"
                    />
                    <text
                      x={skill.x}
                      y={skill.y + 4}
                      fill="var(--color-ink-deep)"
                      fontSize="10"
                      fontWeight="bold"
                      textAnchor="middle"
                    >
                      {skill.mastery_score}%
                    </text>
                    <text
                      x={skill.x}
                      y={skill.y + planetRadius + 14}
                      fill="var(--color-ink-deep)"
                      fontSize="9"
                      fontWeight={isSelected ? "bold" : "normal"}
                      textAnchor="middle"
                      className="pointer-events-none"
                    >
                      {skill.name.length > 18 ? `${skill.name.slice(0, 16)}...` : skill.name}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          <p className="flex items-center gap-1.5 pt-2 text-[11px] text-center text-muted">
            <span className="text-brand">ℹ️</span>
            Cliquez sur un astre pour examiner votre niveau de maîtrise et planifier votre prochaine accélération.
          </p>
        </div>

        <div className="space-y-6">
          {selectedSkill ? (
            <div className="glass space-y-5 border-brand/30 p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <span
                  className="rounded-full px-3 py-1 text-xs font-bold tracking-wider uppercase"
                  style={{ backgroundColor: `${selectedSkill.color}20`, color: selectedSkill.color }}
                >
                  {selectedSkill.ringName}
                </span>
                <span className="rounded-full border border-cyan-500/30 bg-cyan-500/15 px-2.5 py-0.5 text-[10px] font-semibold text-cyan-600">
                  Niveau {selectedSkill.level} / 5
                </span>
              </div>

              <div>
                <h3 className="font-display text-lg font-semibold">{selectedSkill.name}</h3>
                <p className="mt-1 text-xs leading-relaxed text-muted">
                  {selectedSkill.description || "Compétence active dans votre parcours d'apprentissage."}
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-muted">Maîtrise opérationnelle</span>
                  <span className="font-bold">{selectedSkill.mastery_score}%</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full border border-line bg-paper-soft">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{ width: `${selectedSkill.mastery_score}%`, backgroundColor: selectedSkill.color || "#7C3AED" }}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between rounded-2xl border border-line bg-paper-soft p-3 text-xs">
                <span className="text-muted">Points d'expérience cumulés</span>
                <span className="font-bold text-amber-500">+{selectedSkill.xp} XP</span>
              </div>

              <Link to={selectedSkill.mastery_score > 0 ? `/apprentissage/${selectedSkill.slug}` : `/formations/${selectedSkill.slug}`} className="btn-primary w-full text-xs">
                {selectedSkill.mastery_score > 0 ? "Reprendre la formation" : "Renforcer cette compétence"} ➜
              </Link>
            </div>
          ) : (
            <div className="glass space-y-4 p-6 text-center shadow-sm">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-brand/15 text-brand">
                <span className="text-2xl">✨</span>
              </div>
              <div>
                <h4 className="font-display text-sm font-semibold">Sélectionnez un astre orbital</h4>
                <p className="mt-1 text-xs leading-relaxed text-muted">
                  Consultez la trajectoire de chaque compétence, son ancrage gravitationnel et vos prochains objectifs.
                </p>
              </div>
            </div>
          )}

          {recommendation && (
            <div className="glass space-y-4 border-cyan-500/30 p-6 shadow-sm">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-cyan-500/15 text-cyan-600">
                  <span className="text-sm">📈</span>
                </div>
                <div>
                  <span className="rounded-full border border-cyan-500/30 bg-cyan-500/15 px-2.5 py-0.5 text-[10px] font-semibold text-cyan-600">
                    Recommandation Socratique
                  </span>
                  <h4 className="mt-0.5 font-display text-xs font-bold">{recommendation.title}</h4>
                </div>
              </div>

              <p className="text-xs leading-relaxed text-muted">{recommendation.reason}</p>

              <Link to="/catalogue" className="btn-ghost w-full text-xs">
                {recommendation.action_label} ›
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}