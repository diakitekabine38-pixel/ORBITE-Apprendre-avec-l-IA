import { ShieldAlert } from "lucide-react";
import { Button } from "../components/ui";
import { useAuth } from "../auth";
import { roleHome } from "../navigation";

export default function Forbidden() {
  const { user } = useAuth();

  return (
    <div className="mx-auto grid min-h-[75vh] max-w-6xl place-items-center px-4 py-10">
      <div className="flex w-full max-w-md flex-col items-center gap-3 text-center">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-error-soft text-error">
          <ShieldAlert className="h-10 w-10" />
        </div>
        <p className="mt-2 font-mono text-xs tracking-widest text-muted">403</p>
        <h1 className="font-display text-3xl font-bold">Accès refusé</h1>
        <p className="text-sm text-ink-soft">
          Tu n'as pas la permission de consulter cet espace. Si tu penses qu'il s'agit d'une erreur,
          contacte un administrateur.
        </p>
        <div className="mt-4 flex flex-wrap justify-center gap-3">
          <Button to={user ? roleHome(user) : "/login"}>
            {user ? "Retour à mon espace" : "Se connecter"}
          </Button>
          <Button to="/" variant="secondary">
            Accueil
          </Button>
        </div>
      </div>
    </div>
  );
}