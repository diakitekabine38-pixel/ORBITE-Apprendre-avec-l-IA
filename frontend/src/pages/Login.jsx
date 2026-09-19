import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/dashboard";

  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(form.username, form.password);
      navigate(from, { replace: true });
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
          <h1 className="text-2xl font-bold">Connexion</h1>
          <p className="mt-1 text-sm text-muted">
            Demo : <code className="rounded bg-white/5 px-1.5 py-0.5">apprenant</code> /{" "}
            <code className="rounded bg-white/5 px-1.5 py-0.5">Apprenant123!</code>
          </p>
        </div>
        <input
          className="input"
          placeholder="Nom d'utilisateur"
          value={form.username}
          onChange={(e) => setForm({ ...form, username: e.target.value })}
          autoComplete="username"
          required
        />
        <input
          className="input"
          type="password"
          placeholder="Mot de passe"
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
          autoComplete="current-password"
          required
        />
        {error && <p className="text-sm text-rose-400">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Connexion…" : "Se connecter"}</button>
        <p className="text-center text-sm text-muted">
          Pas encore de compte ? <Link to="/inscription" className="link">Inscription</Link>
        </p>
      </form>
    </div>
  );
}