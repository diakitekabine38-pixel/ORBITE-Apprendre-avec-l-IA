import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import ResendVerification from "../components/ResendVerification";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    password2: "",
  });
  const [done, setDone] = useState(false);
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
      setDone(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (done) {
    return (
      <div className="mx-auto grid min-h-[70vh] max-w-6xl place-items-center px-4">
        <div className="glass w-full max-w-md space-y-4 p-8 text-center">
          <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-brand/15 text-3xl text-brand-soft">📬</div>
          <h1 className="text-2xl font-bold">Compte créé !</h1>
          <p className="text-sm text-muted">
            On vient de t'envoyer un lien de confirmation sur <strong>{form.email}</strong>.
            Clique dessus pour valider ton adresse email.
          </p>
          <div className="rounded-xl border border-amber-300/40 bg-amber-300/10 p-3 text-left text-xs text-muted">
            <p className="font-semibold text-amber-700">Tu ne reçois rien ?</p>
            <p className="mt-1 mb-3">
              Vérifie d'abord ton dossier <strong>Spam / courriers indésirables</strong> —
              les emails de confirmation s'y retrouvent parfois.
            </p>
            <ResendVerification defaultEmail={form.email} />
          </div>
          <p className="text-sm text-muted">
            Tu pourras te connecter dès que ton adresse sera confirmée.
          </p>
          <button className="btn-primary w-full" onClick={() => navigate("/login")}>
            Aller à la connexion
          </button>
        </div>
      </div>
    );
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