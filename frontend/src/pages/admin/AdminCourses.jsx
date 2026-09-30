import { useEffect, useState } from "react";
import { api, apiPost } from "../../api";
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
import { BookOpenCheck, Eye, SearchCheck, Send, Star, ArrowRightCircle } from "lucide-react";
import { COURSE_STATUS } from "../../navigation";

const TABS = ["all", "submitted", "in_review", "approved", "published"];

const ACTION_BY_STATUS = {
  submitted: {
    flag: "can_start_review",
    action: "start_review",
    label: "Mettre en révision",
    icon: ArrowRightCircle,
    variant: "secondary",
  },
  in_review: {
    flag: "can_approve",
    action: "approve",
    label: "Approuver",
    icon: SearchCheck,
    variant: "secondary",
  },
  approved: {
    flag: "can_publish",
    action: "publish",
    label: "Publier",
    icon: Star,
    variant: "primary",
  },
  published: {
    flag: "can_unpublish",
    action: "unpublish",
    label: "Dépublier",
    icon: Send,
    variant: "ghost",
  },
};

export default function AdminCourses() {
  const [courses, setCourses] = useState(null);
  const [tab, setTab] = useState("all");
  const [error, setError] = useState("");
  const [busySlug, setBusySlug] = useState(null);

  async function load() {
    const d = await api("/courses/courses/").catch((e) => {
      setError(e.message);
      return null;
    });
    setCourses(d?.results || []);
  }

  useEffect(() => {
    load();
  }, []);

  if (error) return <p className="text-error">{error}</p>;
  if (!courses) return <LoadingState label="Chargement du flux de validation…" />;

  const filtered = tab === "all" ? courses : courses.filter((c) => c.status === tab);

  async function run(status, course) {
    const config = ACTION_BY_STATUS[status];
    setBusySlug(course.slug);
    setError("");
    try {
      await apiPost(`/courses/courses/${course.slug}/${config.action}/`);
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusySlug(null);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-3xl font-bold">Flux de validation</h1>
        <p className="mt-1 text-sm text-muted">
          Fais avancer chaque formation : révision → approbation → publication.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-full px-4 py-1.5 text-sm transition ${
              tab === t
                ? "bg-orbital-600 font-medium text-white"
                : "border border-line bg-paper text-ink-soft hover:text-ink-deep"
            }`}
          >
            {t === "all" ? "Toutes" : COURSE_STATUS[t]?.label || t}
          </button>
        ))}
      </div>

      {error && <p className="text-sm text-error">{error}</p>}

      {filtered.length === 0 ? (
        <EmptyState
          icon={BookOpenCheck}
          title="Aucune formation ici"
          description={
            tab === "all"
              ? "Les formations créées par les enseignants apparaîtront ici."
              : "Aucune formation dans ce statut pour le moment."
          }
        />
      ) : (
        <Table>
          <TableHead>
            <TableRow>
              <TableHeadCell>Titre</TableHeadCell>
              <TableHeadCell>Formateur</TableHeadCell>
              <TableHeadCell>Catégorie</TableHeadCell>
              <TableHeadCell>Statut</TableHeadCell>
              <TableHeadCell>Apprenants</TableHeadCell>
              <TableHeadCell className="text-right">Actions</TableHeadCell>
            </TableRow>
          </TableHead>
          <tbody>
            {filtered.map((course) => {
              const meta = COURSE_STATUS[course.status] || COURSE_STATUS.draft;
              const config = ACTION_BY_STATUS[course.status];
              return (
                <TableRow key={course.id}>
                  <TableCell className="max-w-xs">
                    <p className="font-medium">{course.title}</p>
                    <p className="truncate text-xs text-muted">{course.short_description}</p>
                  </TableCell>
                  <TableCell className="text-muted">{course.instructor_name || "—"}</TableCell>
                  <TableCell className="text-muted">{course.category?.name || "—"}</TableCell>
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
                      {config && course[config.flag] && (
                        <Button
                          size="sm"
                          variant={config.variant}
                          icon={config.icon}
                          loading={busySlug === course.slug}
                          onClick={() => run(course.status, course)}
                        >
                          {config.label}
                        </Button>
                      )}
                      {course.status === "draft" && (
                        <span className="self-center text-xs text-muted">brouillon de l'enseignant</span>
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