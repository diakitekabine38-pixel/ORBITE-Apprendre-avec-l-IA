import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, apiPost, apiPatch } from "../api";
import { useAuth } from "../auth";

const EXPERTISE = ["beginner", "intermediate", "advanced"];

const EMPTY = {
  name: "",
  code: "",
  specialty: "",
  personality: "",
  system_prompt: "",
  teaching_rules: [] ,
  expertise: "intermediate",
  color: "#7C3AED",
  model: "",
  is_active: true,
};

export default function AdminAgents() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [agents, setAgents] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [teachingText, setTeachingText] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const isAdmin = useMemo(() => ["admin", "super_admin"].includes(user?.role), [user]);

  useEffect(() => {
    if (!isAdmin) {
      navigate("/dashboard", { replace: true });
      return;
    }
    api("/ai/admin/agents/")
      .then((d) => setAgents(d.results || []))
      .catch(() => {});
  }, [isAdmin, navigate]);

  function startEdit(agent) {
    setEditingId(agent.id);
    setError("");
    setNotice("");
    setForm({
      name: agent.name,
      code: agent.code,
      specialty: agent.specialty,
      personality: agent.personality || "",
      system_prompt: agent.system_prompt || "",
      teaching_rules: agent.teaching_rules || [],
      expertise: agent.expertise || "intermediate",
      color: agent.color || "#7C3AED",
      model: agent.model || "",
      is_active: agent.is_active,
    });
    setTeachingText((agent.teaching_rules || []).join("\n"));
  }

  function reset() {
    setEditingId(null);
    setForm(EMPTY);
    setTeachingText("");
    setError("");
    setNotice("");
  }

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  async function save(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setNotice("");
    const payload = {
      ...form,
      code: form.code.trim().toLowerCase().replace(/[^a-z0-9-]/g, "-"),
      teaching_rules: teachingText
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean),
    };
    try {
      if (editingId) {
        const updated = await apiPatch(`/ai/admin/agents/${editingId}/`, payload);
        setAgents((prev) => prev.map((a) => (a.id === editingId ? updated : a)));
        setNotice("Profil mis à jour — le rôle est actif immédiatement dans les conversations.");
      } else {
        const created = await apiPost("/ai/admin/agents/", payload);
        setAgents((prev) => [...prev, created]);
        setNotice("Nouvel agent créé — il apparaît dans le chat et le panneau Learn.");
      }
      reset();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function remove(agent) {
    if (!window.confirm(`Supprimer définitivement ${agent.name} ?`)) return;
    try {
      await api(`/ai/admin/agents/${agent.id}/`, { method: "DELETE" });
      setAgents((prev) => prev.filter((a) => a.id !== agent.id));
      if (editingId === agent.id) reset();
    } catch (err) {
      setError(err.message);
    }
  }

  async function toggleActive(agent) {
    try {
      const updated = await apiPatch(`/ai/admin/agents/${agent.id}/`, {
        is_active: !agent.is_active,
      });
      setAgents((prev) => prev.map((a) => (a.id === agent.id ? updated : a)));
    } catch (err) {
      setError(err.message);
    }
  }

  if (!isAdmin) return null;

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Personnalisation des agents IA</h1>
          <p className="mt-1 text-muted">
            Chaque agent joue un rôle : « system_prompt » définit la personnalité, « teaching_rules »
            les règles de tutorat. Les changements sont appliqués dès le prochain message.
          </p>
        </div>
        <Link to="/chat" className="btn-ghost text-sm">Tester dans le chat →</Link>
      </div>

      <div className="mt-8 grid gap-8 lg:grid-cols-[minmax(0,1fr)_420px]">
        <div>
          <h2 className="text-lg font-bold">Coachs ({agents.length})</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {agents.map((agent) => (
              <div key={agent.id} className={`glass p-4 ${agent.is_active ? "" : "opacity-60"}`}>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <span
                      className="grid h-10 w-10 place-items-center rounded-xl font-display text-sm font-bold text-white"
                      style={{ background: agent.color }}
                    >
                      {agent.name?.[0] || "?"}
                    </span>
                    <div>
                      <p className="font-semibold">{agent.name}</p>
                      <p className="text-xs text-muted">{agent.specialty}</p>
                    </div>
                  </div>
                  <span className={`badge ${agent.is_active ? "!border-emerald-600/40 !text-emerald-700" : ""}`}>
                    {agent.is_active ? "actif" : "masqué"}
                  </span>
                </div>
                <p className="mt-3 text-xs text-muted line-clamp-2">{agent.personality}</p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <button className="btn-ghost !px-3 !py-1 text-xs" onClick={() => startEdit(agent)}>
                    Modifier le rôle
                  </button>
                  <button className="btn-ghost !px-3 !py-1 text-xs" onClick={() => toggleActive(agent)}>
                    {agent.is_active ? "Masquer" : "Activer"}
                  </button>
                  <button className="btn-ghost !px-3 !py-1 text-xs !text-rose-600" onClick={() => remove(agent)}>
                    Supprimer
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={save} className="glass space-y-4 p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold">{editingId ? `Modifier ${form.name}` : "Nouvel agent"}</h2>
            {editingId && (
              <button type="button" className="btn-ghost !px-3 !py-1 text-xs" onClick={reset}>
                Annuler
              </button>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <input className="input" placeholder="Nom (ex. MATHIS)" value={form.name} onChange={set("name")} required />
            <input className="input" placeholder="Code (ex. mathis)" value={form.code} onChange={set("code")} required />
          </div>
          <input className="input" placeholder="Spécialité (ex. Mathématiques)" value={form.specialty} onChange={set("specialty")} required />

          <div className="grid grid-cols-2 gap-3">
            <select className="input" value={form.expertise} onChange={set("expertise")}>
              {EXPERTISE.map((level) => (
                <option key={level} value={level}>Niveau : {level}</option>
              ))}
            </select>
            <input className="input" type="color" value={form.color} onChange={set("color")} title="Couleur de l'avatar" />
          </div>
          <input className="input" placeholder="Modèle IA (vide = modèle global ORBITE)" value={form.model} onChange={set("model")} />

          <textarea
            className="input resize-none"
            rows={2}
            placeholder="Personnalité (visible des apprenants)"
            value={form.personality}
            onChange={set("personality")}
          />
          <textarea
            className="input resize-none"
            rows={3}
            placeholder="Règles de tutorat — une par ligne (ex. Expliquer simplement, Poser une question)"
            value={teachingText}
            onChange={(e) => setTeachingText(e.target.value)}
          />
          <textarea
            className="input resize-none font-mono text-xs"
            rows={6}
            placeholder="Prompt système : le cerveau du rôle…"
            value={form.system_prompt}
            onChange={set("system_prompt")}
          />

          <label className="flex items-center gap-2 text-sm text-muted">
            <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
            Agent visible et utilisable
          </label>

          {error && <p className="text-sm text-rose-600">{error}</p>}
          {notice && <p className="text-sm text-emerald-600">{notice}</p>}

          <button className="btn-primary w-full" disabled={busy}>
            {busy ? "Enregistrement…" : editingId ? "Enregistrer le rôle" : "Créer l'agent"}
          </button>
        </form>
      </div>
    </div>
  );
}