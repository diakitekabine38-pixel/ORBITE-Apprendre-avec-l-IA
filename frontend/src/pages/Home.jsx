import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import CourseCard from "../components/CourseCard";

const AGENTS_PREVIEW = [
  { code: "kodex", name: "KODEX", sub: "Développement", emoji: "💻" },
  { code: "kora", name: "KORA", sub: "Langues & expression", emoji: "🗣️" },
  { code: "nova", name: "NOVA", sub: "Sciences & logique", emoji: "🧪" },
  { code: "pixel", name: "PIXEL", sub: "Design & créativité", emoji: "🎨" },
  { code: "lumen", name: "LUMEN", sub: "Entrepreneuriat", emoji: "🚀" },
  { code: "aura", name: "AURA", sub: "Formation professionnelle", emoji: "✨" },
];

export default function Home() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api("/courses/courses/")
      .then((data) => setCourses(data.results || []))
      .catch(() => setCourses([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <section className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(139,92,246,.16),transparent_55%),radial-gradient(ellipse_at_bottom_right,rgba(124,58,237,.10),transparent_50%)]" />
        <div className="relative mx-auto max-w-6xl px-4 pt-20 pb-16 text-center">
          <span className="badge mb-6">Piloté par l'IA · 6 coachs dédiés</span>
          <h1 className="mx-auto max-w-3xl text-4xl leading-tight font-bold tracking-tight sm:text-6xl">
            Apprends plus vite,
            <span className="bg-gradient-to-r from-brand-soft to-glow bg-clip-text text-transparent">
              {" "}avec un coach IA
            </span>
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-lg text-muted">
            ORBITE combine formations structurées, tuteur IA personnel et certification
            vérifiable. Ton apprentissage est adapté à ton niveau, à ton rythme, à tes objectifs.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link to="/catalogue" className="btn-primary text-base">Explorer les formations</Link>
            <Link to="/inscription" className="btn-ghost text-base">Inscription gratuite</Link>
          </div>

          <div className="mx-auto mt-14 grid max-w-4xl grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-6">
            {AGENTS_PREVIEW.map((agent) => (
              <div key={agent.code} className="glass flex flex-col items-center gap-1 p-4 text-center">
                <span className="text-3xl">{agent.emoji}</span>
                <span className="font-display text-sm font-semibold">{agent.name}</span>
                <span className="text-xs text-muted">{agent.sub}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 pt-10 pb-20">
        <div className="mb-6 flex items-end justify-between">
          <div>
            <h2 className="text-2xl font-bold">Formations à la une</h2>
            <p className="text-muted">Sélectionnées et certifiantes sur ORBITE.</p>
          </div>
          <Link to="/catalogue" className="link">Voir tout →</Link>
        </div>
        {loading ? (
          <p className="text-muted">Chargement…</p>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {courses.slice(0, 6).map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        )}
      </section>

      <section className="border-t border-line">
        <div className="mx-auto grid max-w-6xl gap-6 px-4 py-14 md:grid-cols-3">
          {[
            { title: "Coaching adaptatif", body: "KODEX, NOVA et les autres s'appuient sur ta progression pour te guider exactement là où tu en as besoin." },
            { title: "Certification vérifiable", body: "Chaque formation terminée génère un certificat ORBITE dont l'authenticité se vérifie en un lien public." },
            { title: "Méthode ORBITE", body: "Expliquer, reformuler, exemplifier, questionner, exercer, corriger : un cycle d'apprentissage complet." },
          ].map((f) => (
            <div key={f.title} className="glass p-6">
              <h3 className="mb-2 text-lg font-semibold text-brand-soft">{f.title}</h3>
              <p className="text-sm text-muted">{f.body}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}