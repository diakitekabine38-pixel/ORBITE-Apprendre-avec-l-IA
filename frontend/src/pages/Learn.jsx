import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, apiPost } from "../api";

export default function Learn() {
  const { slug } = useParams();
  const [course, setCourse] = useState(null);
  const [progress, setProgress] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [current, setCurrent] = useState(null);
  const [lesson, setLesson] = useState(null);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api(`/courses/courses/${slug}/`).then(setCourse).catch(() => setCourse(null));
    api("/learning/progress/")
      .then((d) => setProgress(d.results || []))
      .catch(() => {});
    api(`/assessments/quizzes/?course=${slug}`)
      .then((d) => setQuizzes(d.results || []))
      .catch(() => {});
  }, [slug]);

  const completed = useMemo(() => new Set(progress.map((p) => p.lesson)), [progress]);
  const quizByLesson = useMemo(() => Object.fromEntries(quizzes.map((q) => [q.lesson, q])), [quizzes]);
  const lessonEx = useMemo(() => (lesson ? quizByLesson[lesson.id] || null : null), [lesson, quizByLesson]);

  const openLesson = useCallback(async (lessonId) => {
    setResult(null);
    setError("");
    setLesson(null);
    const detail = await api(`/courses/lessons/${lessonId}/`).catch(() => null);
    setLesson(detail && !detail.locked ? detail : { id: lessonId, locked: true });
  }, []);

  const markComplete = useCallback(async () => {
    setBusy(true);
    try {
      const res = await apiPost("/learning/progress/complete/", {
        course_slug: slug,
        lesson_id: lesson.id,
      });
      setResult({ type: "complete", progress: res.progress });
      setProgress((prev) => [...prev, { lesson: lesson.id }]);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [slug, lesson]);

  const submitQuiz = useCallback(
    async (answers) => {
      setBusy(true);
      setError("");
      try {
        const res = await apiPost("/assessments/attempts/submit/", {
          quiz: lessonEx.id,
          answers,
        });
        setResult({ type: "quiz", score: res.score, passed: res.passed });
      } catch (e) {
        setError(e.message);
      } finally {
        setBusy(false);
      }
    },
    [lessonEx]
  );

  if (!course) {
    return <div className="mx-auto max-w-4xl px-4 py-16 text-muted">Chargement…</div>;
  }

  const lessons = (course.modules || []).map((m) => m.lessons).flat();

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <nav className="mb-6 text-sm text-muted">
        <Link to="/dashboard" className="link">Mon espace</Link>
        <span className="mx-1">/</span>
        <Link to={`/formations/${course.slug}`} className="link">{course.title}</Link>
      </nav>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
        <main className="glass min-h-[60vh] p-6">
          {!lesson ? (
            <div className="grid h-full place-items-center text-center text-muted">
              <div>
                <p className="text-5xl">🎬</p>
                <p className="mt-3">Choisis une leçon dans le programme pour commencer.</p>
              </div>
            </div>
          ) : lesson.locked ? (
            <div className="grid h-full place-items-center text-center">
              <div>
                <p className="text-4xl">🔒</p>
                <p className="mt-3 font-semibold">Cette leçon est réservée aux inscrits.</p>
                <Link to={`/formations/${course.slug}`} className="btn-primary mt-4">
                  Voir la page de la formation
                </Link>
              </div>
            </div>
          ) : (
            <div>
              <h1 className="text-2xl font-bold">{lesson.title}</h1>
              <p className="mt-2 text-sm text-muted">{lesson.summary}</p>

              {lesson.video?.hls_url ? (
                <video controls className="mt-5 aspect-video w-full rounded-xl bg-black" src={lesson.video.hls_url} />
              ) : (
                <div className="mt-5 aspect-video w-full rounded-xl bg-gradient-to-br from-brand/30 via-panel-2 to-glow/20" />
              )}

              <div className="mt-5 space-y-4 text-muted">
                {lesson.content && typeof lesson.content === "string" ? (
                  lesson.content.split("\n").filter(Boolean).map((p, i) => <p key={i}>{p}</p>)
                ) : null}
              </div>

              {lesson.resources?.length > 0 && (
                <div className="mt-5 rounded-xl border border-line bg-white/5 p-4">
                  <p className="mb-2 text-sm font-semibold text-white">Ressources</p>
                  {lesson.resources.map((r) => (
                    <p key={r.id} className="text-sm">{r.title} — <a className="link" href={r.url} target="_blank" rel="noreferrer">{r.url}</a></p>
                  ))}
                </div>
              )}

              <div className="mt-6 flex items-center gap-3">
                <button
                  className="btn-primary"
                  disabled={busy || completed.has(lesson.id)}
                  onClick={markComplete}
                >
                  {completed.has(lesson.id) ? "✓ Leçon terminée" : busy ? "Validation…" : "Marquer comme terminée"}
                </button>
              </div>

              {lessonEx && (
                <QuizBlock quiz={lessonEx} busy={busy} onSubmit={submitQuiz} />
              )}

              {result?.type === "complete" && (
                <p className="mt-3 text-sm text-emerald-400">Progression : {Math.round(result.progress)}% 🎉</p>
              )}
              {result?.type === "quiz" && (
                <p className={`mt-3 text-sm ${result.passed ? "text-emerald-400" : "text-rose-400"}`}>
                  Quiz : {result.score}% — {result.passed ? "réussi !" : "essaye encore."}
                </p>
              )}
              {error && <p className="mt-3 text-sm text-rose-400">{error}</p>}
            </div>
          )}
        </main>

        <aside>
          {course.modules.map((module) => (
            <div key={module.id} className="glass mb-4 p-4">
              <p className="mb-2 text-sm font-semibold text-brand-soft">
                Module {module.order} — {module.title}
              </p>
              <ul className="space-y-1">
                {module.lessons.map((lesson) => (
                  <li key={lesson.id}>
                    <button
                      onClick={() => openLesson(lesson.id)}
                      className={`flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-sm transition hover:bg-white/5 ${
                        current === lesson.id ? "bg-white/10 text-white" : completed.has(lesson.id) ? "text-emerald-300" : "text-muted"
                      }`}
                    >
                      <span className={completed.has(lesson.id) ? "" : "text-xs"}>
                        {completed.has(lesson.id) ? "✓" : "•"}
                      </span>
                      <span className="truncate">{lesson.title}</span>
                    </button>
                    {quizByLesson[lesson.id] && (
                      <p className="ml-6 text-xs text-glow">🎯 quiz disponible</p>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </aside>
      </div>
    </div>
  );
}

function QuizBlock({ quiz, busy, onSubmit }) {
  const [answers, setAnswers] = useState({});

  function choose(qId, option) {
    setAnswers((prev) => {
      const current = prev[qId];
      if (Array.isArray(current)) {
        return { ...prev, [qId]: current.includes(option) ? current.filter((o) => o !== option) : [...current, option] };
      }
      return { ...prev, [qId]: option };
    });
  }

  return (
    <div className="mt-6 rounded-xl border border-brand/30 bg-white/5 p-5">
      <h2 className="font-bold">{quiz.title}</h2>
      <p className="mt-1 text-xs text-muted">
        Score minimal : {quiz.pass_score}% · Note sur {quiz.questions.reduce((s, q) => s + q.points, 0)}
      </p>
      <div className="mt-4 space-y-4">
        {quiz.questions.map((q) => (
          <div key={q.id}>
            <p className="mb-2 text-sm font-medium">{q.text}</p>
            <div className="flex flex-wrap gap-2">
              {(q.options || []).map((opt) => {
                const active = answers[q.id] === opt || (Array.isArray(answers[q.id]) && answers[q.id].includes(opt));
                return (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => choose(q.id, opt)}
                    className={`rounded-lg border px-3 py-2 text-sm transition ${
                      active ? "border-brand bg-brand/20 text-white" : "border-line bg-panel-2 text-muted hover:text-white"
                    }`}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
      <button
        className="btn-primary mt-5"
        disabled={busy || Object.keys(answers).length !== quiz.questions.length}
        onClick={() =>
          onSubmit(quiz.questions.map((q) => ({ question_id: q.id, answer: answers[q.id] })))
        }
      >
        {busy ? "Correction…" : "Valider mes réponses"}
      </button>
    </div>
  );
}