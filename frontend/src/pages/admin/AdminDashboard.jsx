import { useEffect, useState } from "react";
import { api } from "../../api";
import { useAuth } from "../../auth";
import { Button, Card, LoadingState } from "../../components/ui";
import {
  Activity,
  Bot,
  BookOpenCheck,
  GraduationCap,
  Newspaper,
  ShoppingBag,
  Star,
  Users,
  Wallet,
} from "lucide-react";

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/analytics/stats/overview/")
      .then(setStats)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="text-error">{error}</p>;
  if (!stats) return <LoadingState label="Chargement des statistiques…" />;

  const cards = [
    { icon: Users, label: "Utilisateurs", value: stats.users },
    { icon: GraduationCap, label: "Apprenants", value: stats.students },
    { icon: BookOpenCheck, label: "Formations publiées", value: stats.published_courses },
    { icon: Newspaper, label: "Inscriptions", value: stats.enrollments },
    { icon: ShoppingBag, label: "Commandes payées", value: stats.orders_total },
    { icon: Wallet, label: "Revenu", value: `${(stats.revenue || 0).toLocaleString("fr-FR")} FCFA` },
    { icon: Star, label: "Avis validés", value: stats.reviews },
    { icon: Activity, label: "Événements / 24h", value: stats.events_24h },
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold">
            Bonjour, {user?.first_name || user?.username}
          </h1>
          <p className="mt-1 text-sm text-muted">Espace administrateur — supervision de la plateforme.</p>
        </div>
        <div className="flex gap-3">
          <Button to="/admin/agents" variant="secondary" icon={Bot}>
            Agents IA
          </Button>
          <Button to="/admin/cours" icon={BookOpenCheck}>
            Valider des formations
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((s) => (
          <Card key={s.label} padding={false} className="p-5">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-orbital-100 text-orbital-600">
                <s.icon className="h-4 w-4" />
              </span>
              <div className="min-w-0">
                <p className="truncate font-display text-xl font-bold leading-none">{s.value}</p>
                <p className="mt-1 truncate text-xs text-muted">{s.label}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}