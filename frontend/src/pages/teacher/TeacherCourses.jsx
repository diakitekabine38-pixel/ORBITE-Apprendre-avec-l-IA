import { useEffect, useMemo, useState } from "react";
import { api, apiPost } from "../../api";
import { useAuth } from "../../auth";
import {
  Badge,
  Button,
  EmptyState,
  LoadingState,
  Table,
  TableCell,
  TableHead,
  TableHeadCell,
  TableRow,
} from "../../components/ui";
import { PlusCircle, Send, Eye } from "lucide-react";
import { COURSE_STATUS, COURSE_LEVELS } from "../../navigation";

export default function TeacherCourses() {
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

  async function submitCourse(course) {
    setBusySlug(course.slug);
    setError("");
    try {
      const res = await apiPost(`/courses/courses/${course.slug}/submit/`);
      setCourses((prev) => prev.map((c) => (c.slug === course.slug ? { ...c, status: res.status } : c)));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusySlug(null);
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold">Mes formations</h1>
          <p className="mt-1 text-sm text-muted">
            Soumets un brouillon pour le faire entrer dans le circuit de validation.
          </p>
        </div>
        <Button to="/teacher/cours/nouveau" icon={PlusCircle}>
          Nouvelle formation
        </Button>
      </div>

      {error && <p className="text-sm text-error">{error}</p>}

      {mine.length === 0 ? (
        <EmptyState
          icon={PlusCircle}
          title="Aucune formation pour l'instant"
          description="Lance-toi : crée une formation, puis soumets-la à la validation."
          action={<Button to="/teacher/cours/nouveau">Créer une formation</Button>}
        />
      ) : (
        <Table>
          <TableHead>
            <TableRow>
              <TableHeadCell>Titre</TableHeadCell>
              <TableHeadCell>Catégorie</TableHeadCell>
              <TableHeadCell>Niveau</TableHeadCell>
              <TableHeadCell>Statut</TableHeadCell>
              <TableHeadCell>Apprenants</TableHeadCell>
              <TableHeadCell className="text-right">Actions</TableHeadCell>
            </TableRow>
          </TableHead>
          <tbody>
            {mine.map((course) => {
              const meta = COURSE_STATUS[course.status] || COURSE_STATUS.draft;
              return (
                <TableRow key={course.id}>
                  <TableCell className="max-w-xs">
                    <p className="font-medium">{course.title}</p>
                    <p className="truncate text-xs text-muted">{course.short_description}</p>
                  </TableCell>
                  <TableCell className="text-muted">{course.category?.name || "—"}</TableCell>
                  <TableCell className="text-muted">
                    {COURSE_LEVELS[course.level] || course.level || "—"}
                  </TableCell>
                  <TableCell>
                    <Badge variant={meta.variant} dot>
                      {meta.label}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted">{course.student_count || 0}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button to={`/formations/${course.slug}`} variant="secondary" size="sm" icon={Eye}>
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
                  </TableCell>
                </TableRow>
              );
            })}
          </tbody>
        </Table>
      )}
    </div>
  );
}