import { useState } from "react";
import { apiPost } from "../api";

export default function ResendVerification({ defaultEmail = "" }) {
  const [email, setEmail] = useState(defaultEmail);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function send(e) {
    e.preventDefault();
    setMsg("");
    setBusy(true);
    try {
      await apiPost("/auth/resend-verification/", { email });
      setMsg(
        "Si un compte existe avec cette adresse et n'est pas confirmé, un nouveau lien vient d'être envoyé (vérifie aussi les spams)."
      );
    } catch (err) {
      setMsg(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={send} className="space-y-2 text-left">
      <label className="text-xs font-semibold text-muted" htmlFor="resend-email">
        Renvoyer le lien de confirmation
      </label>
      <div className="flex gap-2">
        <input
          id="resend-email"
          className="input"
          type="email"
          placeholder="Ton adresse email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          required
        />
        <button className="btn-ghost shrink-0" disabled={busy}>
          {busy ? "Envoi…" : "Renvoyer"}
        </button>
      </div>
      {msg && <p className="text-xs text-muted">{msg}</p>}
    </form>
  );
}