import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { apiGet } from "../api";
import { useAuth } from "../auth";
import ResendVerification from "../components/ResendVerification";

export default function VerifyEmail() {
  const { token } = useParams();
  const { user, enterSession } = useAuth();
  const navigate = useNavigate();
  const [state, setState] = useState("loading"); // loading | ok | error

  useEffect(() => {
    let alive = true;
    apiGet(`/auth/verify-email/${token}/`)
      .then(async (data) => {
        if (data.access && data.refresh) {
          const me = await enterSession(data);
          if (alive) navigate(["admin", "super_admin"].includes(me?.role) ? "/admin/agents" : "/dashboard", { replace: true });
          return;
        }
        if (alive) setState("ok");
      })
      .catch(() => alive && setState("error"));
    return () => {
      alive = false;
    };
  }, [token]);

  return (
    <div className="mx-auto grid min-h-[70vh] max-w-6xl place-items-center px-4">
      <div className="glass w-full max-w-md space-y-4 p-8 text-center">
        {state === "loading" && (
          <>
            <div className="mx-auto h-16 w-16 animate-spin rounded-full border-4 border-brand/20 border-t-brand" />
            <p className="text-muted">Vérification en cours…</p>
          </>
        )}
        {state === "ok" && (
          <>
            <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-emerald-500/15 text-3xl">✅</div>
            <h1 className="text-2xl font-bold">Email vérifié !</h1>
            <p className="text-sm text-muted">
              Ton adresse est confirmée. Tu peux maintenant profiter pleinement d'ORBITE.
            </p>
            <Link to={user ? "/dashboard" : "/login"} className="btn-primary block w-full text-center">
              {user ? "Aller au tableau de bord" : "Se connecter"}
            </Link>
          </>
        )}
        {state === "error" && (
          <>
            <div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-rose-500/15 text-3xl">⚠️</div>
            <h1 className="text-2xl font-bold">Lien invalide</h1>
            <p className="text-sm text-muted">
              Ce lien de vérification est invalide ou a déjà été utilisé.
            </p>
            <ResendVerification />
            <Link to="/login" className="btn-ghost block w-full text-center">
              Se connecter
            </Link>
          </>
        )}
      </div>
    </div>
  );
}