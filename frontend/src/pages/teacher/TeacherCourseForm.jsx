import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, apiPost } from "../../api";
import { Button, Card, Input, Select, Textarea } from "../../components/ui";
import { COURSE_LEVELS } from "../../navigation";

const EMPTY = {
  title: "",
  category: "",
  level: "beginner",
  price: "0",
  duration_hours: "10",
  is_free: true,
  short_description: "",
  description: "",
  objectivesText: "",
};

export default function TeacherCourseForm() {
  const navigate = useNavigate();
  const [form, setForm] = useState(EMPTY);
  const [categories, setCategories] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/courses/categories/")
      .then((d) => {
        const list = d.results || [];
        setCategories(list);
        if (list.length && !form.category) setForm((f) => ({ ...f, category: list[0].id }));
      })
      .catch(() => {});
  }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  async function create(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const payload = {
        title: form.title.trim(),
        category: form.category || null,
        level: form.level,
        price: form.is_free ? 0 : Number(form.price) || 0,
        duration_hours: Number(form.duration_hours) || 0,
        is_free: form.is_free,
        short_description: form.short_description.trim(),
        description: form.description.trim(),
        objectives: form.objectivesText
          .split("\n")
          .map((line) => line.trim())
          .filter(Boolean),
      };
      await apiPost("/courses/courses/", payload);
      navigate("/teacher/cours");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="font-display text-3xl font-bold">Nouvelle formation</h1>
        <p className="mt-1 text-sm text-muted">
          Elle est créée en brouillon, puis soumise à la validation avant publication.
        </p>
      </div>

      <Card>
        <form onSubmit={create} className="space-y-5">
          <Input
            label="Titre de la formation"
            placeholder="Ex. Les bases des réseaux neuronaux"
            value={form.title}
            onChange={set("title")}
            required
          />

          <div className="grid gap-4 sm:grid-cols-2">
            <Select label="Catégorie" value={form.category} onChange={set("category")}>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </Select>
            <Select label="Niveau" value={form.level} onChange={set("level")}>
              {Object.entries(COURSE_LEVELS).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </Select>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Input
              label="Durée estimée (heures)"
              type="number"
              min="0"
              value={form.duration_hours}
              onChange={set("duration_hours")}
            />
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-ink-soft">Prix</label>
              <div className="flex gap-3">
                <Input
                  type="number"
                  min="0"
                  value={form.price}
                  onChange={set("price")}
                  disabled={form.is_free}
                  className="flex-1"
                  hint="En FCFA"
                />
              </div>
              <label className="flex items-center gap-2 pt-1 text-sm text-ink-soft">
                <input
                  type="checkbox"
                  checked={form.is_free}
                  onChange={(e) => setForm({ ...form, is_free: e.target.checked })}
                />
                Formation gratuite
              </label>
            </div>
          </div>

          <Input
            label="Description courte"
            placeholder="Une phrase d'accroche (max 255 caractères)"
            value={form.short_description}
            onChange={set("short_description")}
            hint={`${form.short_description.length}/255`}
          />

          <Textarea
            label="Description détaillée"
            placeholder="Le contenu, la pédagogie, ce que l'apprenant va découvrir…"
            rows={5}
            value={form.description}
            onChange={set("description")}
          />

          <Textarea
            label="Objectifs pédagogiques"
            placeholder={"Un objectif par ligne, ex.\nComprendre la rétropropagation\nImplémenter un perceptron en Python"}
            rows={4}
            value={form.objectivesText}
            onChange={set("objectivesText")}
          />

          {error && <p className="text-sm text-error">{error}</p>}

          <div className="flex justify-end gap-3">
            <Button to="/teacher/cours" variant="secondary">
              Annuler
            </Button>
            <Button type="submit" loading={busy}>
              {busy ? "Création…" : "Créer la formation"}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}