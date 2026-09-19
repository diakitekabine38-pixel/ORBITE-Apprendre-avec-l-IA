import { useEffect, useMemo, useState } from "react";
import { api } from "../api";
import CourseCard from "../components/CourseCard";

export default function Catalog() {
  const [data, setData] = useState({ results: [], count: 0 });
  const [categories, setCategories] = useState([]);
  const [category, setCategory] = useState("");
  const [level, setLevel] = useState("");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api("/courses/categories/")
      .then((r) => setCategories(r.results || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (level) params.set("level", level);
    if (query) params.set("search", query);
    api(`/courses/courses/?${params}`)
      .then(setData)
      .catch(() => setData({ results: [], count: 0 }))
      .finally(() => setLoading(false));
  }, [category, level, query]);

  const [courses, count] = useMemo(() => [data.results || [], data.count || 0], [data]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="text-3xl font-bold">Catalogue</h1>
      <p className="mt-1 text-muted">{count} formation(s) disponible(s) sur ORBITE.</p>

      <div className="mt-6 flex flex-wrap gap-3">
        <input
          className="input max-w-xs"
          placeholder="Rechercher une formation…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select className="input max-w-[12rem]" value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">Toutes catégories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.slug}>{c.name}</option>
          ))}
        </select>
        <select className="input max-w-[12rem]" value={level} onChange={(e) => setLevel(e.target.value)}>
          <option value="">Tous niveaux</option>
          <option value="beginner">Débutant</option>
          <option value="intermediate">Intermédiaire</option>
          <option value="advanced">Avancé</option>
        </select>
      </div>

      {loading ? (
        <p className="mt-10 text-muted">Chargement…</p>
      ) : courses.length === 0 ? (
        <p className="mt-10 text-muted">Aucune formation trouvée.</p>
      ) : (
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {courses.map((course) => (
            <CourseCard key={course.id} course={course} />
          ))}
        </div>
      )}
    </div>
  );
}