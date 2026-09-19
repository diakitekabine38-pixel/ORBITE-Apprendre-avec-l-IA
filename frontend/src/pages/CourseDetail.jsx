import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, apiPost, money } from "../api";
import { useAuth } from "../auth";

const LEVELS = { beginner: "Débutant", intermediate: "Intermédiaire", advanced: "Avancé" };

export default function CourseDetail() {
  const { slug } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [course, setCourse] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    api(`/courses/courses/${slug}/`)
      .then(setCourse)
      .catch(() => setCourse(null));
  }, [slug]);

  const enroll = useCallback(async () => {
    setBusy(true);
    setError("");
    try {
      await apiPost("/learning/enrollments/enroll/", { slug });
      navigate(`/apprentissage/${slug}`);
    } catch (e) {
      if (e.status === 402) setNotice("pay");
      else setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [slug, navigate]);

  const addToCart = useCallback(async () => {
    setBusy(true);
    setError("");
    try {
      await apiPost("/cart/add/", { course_id: course.id });
      navigate("/panier");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [course, navigate]);

  async function review() {
    setError("");
    try {
      await apiPost("/courses/reviews/", { course: course.id, rating: 5, comment: "Excellent !" });
      setNotice("review");
    } catch (e) {
      setError(e.message);
    }
  }

  if (!course) {
    return <div className="mx-auto max-w-4xl px-4 py-16 text-muted">Chargement de la formation…</div>;
  }

  const canEnrollNow = course.is_free || course.price === 0;

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <nav className="mb-6 text-sm text-muted">
        <Link to="/catalogue" className="link">Catalogue</Link> <span className="mx-1">/</span>
        <span className="text-white">{course.title}</span>
      </nav>

      <div className="grid gap-8 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="relative aspect-video overflow-hidden rounded-2xl bg-gradient-to-br from-brand/30 via-panel-2 to-glow/20">
            {course.thumbnail ? (
              <img src={course.thumbnail} alt={course.title} className="h-full w-full object-cover" />
            ) : (
              <div className="absolute inset-0 grid place-items-center text-6xl opacity-30">◍</div>
            )}
          </div>

          <div className="glass p-6">
            <div className="mb-3 flex flex-wrap gap-2">
              <span className="badge">{course.category?.name}</span>
              <span className="badge">{LEVELS[course.level] || course.level}</span>
              {course.certification_enabled && <span className="badge">🎓 Certifiant</span>}
            </div>
            <h1 className="text-3xl font-bold">{course.title}</h1>
            <p className="mt-3 text-muted">{course.description || course.short_description}</p>

            {course.objectives?.length > 0 && (
              <>
                <h2 className="mt-6 mb-2 font-display font-semibold">Objectifs de la formation</h2>
                <ul className="list-disc space-y-1 pl-5 text-sm text-muted">
                  {course.objectives.map((o, i) => <li key={i}>{o}</li>)}
                </ul>
              </>
            )}
          </div>

          <div className="glass p-6">
            <h2 className="mb-4 text-lg font-bold">Programme</h2>
            {(course.modules || []).map((module) => (
              <div key={module.id} className="border-b border-line py-3 last:border-0">
                <p className="font-medium">Module {module.order} — {module.title}</p>
                <ul className="mt-2 space-y-1 text-sm text-muted">
                  {module.lessons.map((lesson) => (
                    <li key={lesson.id} className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-glow" />
                      {lesson.title}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          {course.ai_mentor && (
            <div className="glass border-brand/30 p-6">
              <h2 className="text-lg font-bold">
                Coach IA : {course.ai_mentor_name || "ton mentor"}
              </h2>
              {course.ai_mentor.description && <p className="mt-2 text-sm text-muted">{course.ai_mentor.description}</p>}
              <Link to="/chat" className="btn-primary mt-4">Discuter avec ton coach</Link>
            </div>
          )}
        </div>

        <aside className="space-y-4 lg:sticky lg:top-24 lg:self-start">
          <div className="glass p-6 text-center">
            {course.is_free ? (
              <p className="font-display text-3xl font-bold text-emerald-400">Gratuit</p>
            ) : (
              <>
                <p className="font-display text-3xl font-bold">{money(course.price)}</p>
                <p className="text-xs text-muted">Paiement mobile (Orange Money, etc.)</p>
              </>
            )}

            {user ? (
              notice === "pay" ? (
                <p className="mt-4 text-sm text-glow">
                  Cette formation est payante. Ajoute-la au panier pour finaliser le paiement.
                </p>
              ) : canEnrollNow ? (
                <button className="btn-primary mt-4 w-full" disabled={busy} onClick={enroll}>
                  {busy ? "Inscription…" : "S'inscrire gratuitement"}
                </button>
              ) : (
                <button className="btn-primary mt-4 w-full" disabled={busy} onClick={addToCart}>
                  {busy ? "Ajout…" : "Ajouter au panier"}
                </button>
              )
            ) : (
              <Link to="/login" className="btn-primary mt-4 w-full">Se connecter pour s'inscrire</Link>
            )}

            {!user && (
              <Link to="/inscription" className="link mt-4 inline-block text-sm">Créer un compte</Link>
            )}

            {notice === "review" && <p className="mt-4 text-sm text-emerald-400">Merci pour votre avis.</p>}
            {error && <p className="mt-4 text-sm text-rose-400">{error}</p>}
          </div>

          <div className="glass p-6 text-sm text-muted">
            <p className="flex justify-between"><span>Formateur</span><span className="text-white">{course.instructor_name || "—"}</span></p>
            <p className="mt-2 flex justify-between"><span>Niveau</span><span className="text-white">{LEVELS[course.level] || course.level}</span></p>
            <p className="mt-2 flex justify-between"><span>Durée</span><span className="text-white">{course.duration_hours || "—"} h</span></p>
            <p className="mt-2 flex justify-between"><span>Note</span><span className="text-white">⭐ {course.rating ? course.rating.toFixed(1) : "—"} ({course.review_count ?? 0})</span></p>
          </div>

          <button className="btn-ghost w-full" onClick={review}>Laisser un avis ★★★★★</button>
        </aside>
      </div>
    </div>
  );
}