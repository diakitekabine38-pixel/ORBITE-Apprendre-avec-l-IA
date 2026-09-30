import { useEffect, useMemo, useState } from "react";
import { api, apiPost } from "../../api";
import { useAuth } from "../../auth";
import { Badge, Button, Card, EmptyState, LoadingState } from "../../components/ui";
import { CheckCircle2, Clock3, LayoutDashboard, PlusCircle, Send } from "lucide-react";
import { COURSE_STATUS } from "../../navigation";

export default function TeacherDashboard() {
  const { user } = useAuth();
  const [courses, setCourses] = useState(null);
  const [error, setError] = useState("");
  const [busySlug, setBusySlug] = useState(null);

  useEffect(() => {
    api("/courses/courses/")
      .then((d) => setCourses(d.results || []))
      .catch((e) => setError(e.message));
  }, []);

  const mine = useMemo(
    () => (courses || []).filter((c) => c.instructor === user?.id),
    [courses, user],
  );

  if (error) return <p className="text-error">{error}</p>;
  if (!courses) return <LoadingState label="Chargement de tes formations…" />;

  const published = mine.filter((c) => c.status === "published").length;
  const inProgress = mine.filter((c) => ["draft", "submitted", "in_review"].includes(c.status)).length;
  const learners = mine.reduce((sum, c) => sum + (c.student_count || 0), 0);

  async function submitCourse(course) {
    setBusySlug(course.slug);
    setError("");
    try {
      const res = await apiPost(`/courses/courses/${course.slug}/submit/`);
      setCourses((prev) =>
        prev.map((c) => (c.slug === course.slug ? { ...c, status: res.status } : c)),
      );
    } catch (e) {
      setError(e.message);
    } finally {
      setBusySlug(null);
    }
  }

  const stats = [
    { icon: LayoutDashboard, label: "Formations", value: mine.length },
    { icon: CheckCircle2, label: "Publiées", value: published, tone: "text-success" },
    { icon: Clock3, label: "En cours de validation", value: inProgress, tone: "text-warning" },
    { icon: Send, label: "Apprenants", value: learners, tone: "text-orbital-600" },
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold">
            Bonjour, {user?.first_name || user?.username}
          </h1>
          <p className="mt-1 text-sm text-muted">Espace enseignant — gère et publie tes formations.</p>
        </div>
        <Button to="/teacher/cours/nouveau" icon={PlusCircle}>
          Créer une formation
        </Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((s) => (
          <Card key={s.label} padding={false} className="p-5">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-orbital-100 text-orbital-600">
                <s.icon className="h-4 w-4" />
              </span>
              <div>
                <p className="font-display text-2xl font-bold leading-none">{s.value}</p>
                <p className="mt-1 text-xs text-muted">{s.label}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {error && <p className="text-sm text-error">{error}</p>}

      <section>
        <h2 className="mb-4 text-xl font-bold">Tes formations</h2>
        {mine.length === 0 ? (
          <EmptyState
            icon={PlusCircle}
            title="Aucune formation pour l'instant"
            description="Crée ta première formation : elle sera soumise à validation avant publication."
            action={<Button to="/teacher/cours/nouveau">Créer une formation</Button>}
          />
        ) : (
          <div className="space-y-3">
            {mine.map((course) => {
              const meta = COURSE_STATUS[course.status] || COURSE_STATUS.draft;
              return (
                <Card key={course.id} variant="interactive" padding={false} className="p-5">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-semibold">{course.title}</p>
                        <Badge variant={meta.variant} dot>
                          {meta.label}
                        </Badge>
                      </div>
                      <p className="mt-1 truncate text-sm text-muted">{course.short_description}</p>
                      <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted">
                        <span>{course.category?.name || "Sans catégorie"}</span>
                        <span>{course.student_count || 0} apprenants</span>
                        {course.price > 0 ? (
                          <span>{course.price} FCFA</span>
                        ) : (
                          <span className="text-success">Gratuit</span>
                        )}
                      </div>
                    </div>
                    <div className="flex shrink-0 flex-wrap items-center gap-2">
                      <Button to={`/formations/${course.slug}`} variant="secondary" size="sm">
                        Voir
                      </Button>
                      {course.can_submit && (
                        <Button
                          size="sm"
                          icon={Send}
                          loading={busySlug === course.slug}
                          onClick={() => submitCourse(course)}
                        >
                          Soumettre
                        </Button>
                      )}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}