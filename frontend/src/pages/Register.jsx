import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function Register() {
  const { register, login } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    password2: "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    if (form.password !== form.password2) {
      setError("Les deux mots de passe ne correspondent pas.");
      setBusy(false);
      return;
    }
    try {
      await register(form);
      await login(form.username, form.password);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto grid min-h-[70vh] max-w-6xl place-items-center px-4">
      <form onSubmit={submit} className="glass w-full max-w-md space-y-4 p-8">
        <div>
          <h1 className="text-2xl font-bold">Créer un compte</h1>
          <p className="mt-1 text-sm text-muted">Rejoins la communauté ORBITE, gratuitement.</p>
        </div>
        <input className="input" placeholder="Nom d'utilisateur (username)" value={form.username} onChange={set("username")} autoComplete="username" required />
        <input className="input" type="email" placeholder="Email" value={form.email} onChange={set("email")} autoComplete="email" required />
        <div className="grid grid-cols-2 gap-3">
          <input className="input" placeholder="Prénom" value={form.first_name} onChange={set("first_name")} required />
          <input className="input" placeholder="Nom" value={form.last_name} onChange={set("last_name")} required />
        </div>
        <input className="input" type="password" placeholder="Mot de passe" value={form.password} onChange={set("password")} autoComplete="new-password" required />
        <input className="input" type="password" placeholder="Confirmer le mot de passe" value={form.password2} onChange={set("password2")} autoComplete="new-password" required />
        {error && <p className="text-sm text-rose-600">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Création…" : "Créer mon compte"}</button>
        <p className="text-center text-sm text-muted">
          Déjà inscrit ? <Link to="/login" className="link">Connexion</Link>
        </p>
      </form>
    </div>
  );
}