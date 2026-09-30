import { Outlet, useNavigate } from "react-router-dom";
import { LogOut, UserRound } from "lucide-react";
import { useAuth } from "../auth";
import { navByKey, roleHome, ROLE_LABEL } from "../navigation";
import { Avatar, Dropdown, Navbar } from "../components/ui";
import Brand from "../components/Brand";
import ThemeToggle from "../components/ThemeToggle";
import Footer from "../components/Footer";
import MobileTabBar from "../components/MobileTabBar";
import NotificationBell from "../components/NotificationBell";

export default function SpaceLayout({ route, navKey }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const items = navByKey(navKey);
  const topLinks = [
    { key: "catalogue", to: "/catalogue", label: "Catalogue" },
    ...items.map(({ key, to, label }) => ({ key, to, label })).filter((l) => l.to !== route),
  ];

  function signOut() {
    logout();
    navigate("/");
  }

  const displayName = user?.first_name || user?.username || "ORBITE";

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar
        brand={<Brand />}
        links={topLinks}
        actions={
          <>
            <NotificationBell />
            <span className="hidden rounded-full bg-brand/15 px-2.5 py-1 text-xs font-semibold text-brand sm:block">
              Nv.{user?.level ?? 1} · {user?.xp ?? 0} XP
            </span>
            <ThemeToggle />
            <Dropdown
              align="right"
              trigger={<Avatar name={displayName} />}
              items={[
                { label: displayName, disabled: true },
                { label: ROLE_LABEL[user?.role] || "Membre", disabled: true },
                { separator: true },
                { label: "Mon espace", icon: UserRound, onClick: () => navigate(roleHome(user)) },
                { label: "Déconnexion", icon: LogOut, danger: true, onClick: signOut },
              ]}
            />
          </>
        }
      />

      <div className="mx-auto flex w-full max-w-6xl flex-1 gap-6 px-4 py-8">
        <main className="min-w-0 flex-1 pb-20 lg:pb-0">
          <Outlet />
        </main>
      </div>

      <Footer />
      <MobileTabBar />
    </div>
  );
}