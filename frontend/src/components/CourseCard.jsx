import { Link } from "react-router-dom";
import { money } from "../api";

const LEVELS = {
  beginner: "Débutant",
  intermediate: "Intermédiaire",
  advanced: "Avancé",
};

export default function CourseCard({ course }) {
  return (
    <Link
      to={`/formations/${course.slug}`}
      className="glass group overflow-hidden transition hover:border-brand/40 hover:bg-panel-2"
    >
      <div className="relative aspect-video overflow-hidden bg-gradient-to-br from-brand/30 via-panel-2 to-glow/20">
        {course.thumbnail ? (
          <img src={course.thumbnail} alt={course.title} className="h-full w-full object-cover" loading="lazy" />
        ) : (
          <div className="absolute inset-0 grid place-items-center text-4xl opacity-40">◍</div>
        )}
        {course.is_free ? (
          <span className="absolute top-3 left-3 rounded-full bg-emerald-400/90 px-2.5 py-1 text-xs font-bold text-emerald-950">
            Gratuit
          </span>
        ) : (
          <span className="absolute top-3 left-3 rounded-full bg-glow/90 px-2.5 py-1 text-xs font-bold text-ink">
            {money(course.price)}
          </span>
        )}
      </div>
      <div className="space-y-2 p-4">
        <div className="flex items-center gap-2">
          <span className="badge">{course.category?.name}</span>
          <span className="badge">{LEVELS[course.level] || course.level}</span>
        </div>
        <h3 className="font-semibold leading-snug group-hover:text-brand-soft">{course.title}</h3>
        {course.short_description && (
          <p className="line-clamp-2 text-sm text-muted">{course.short_description}</p>
        )}
        <div className="flex items-center justify-between pt-1 text-xs text-muted">
          <span>⭐ {course.rating ? course.rating.toFixed(1) : "—"} · {course.student_count ?? 0} apprenants</span>
          <span>{course.duration_hours ? `${course.duration_hours} h` : ""}</span>
        </div>
      </div>
    </Link>
  );
}