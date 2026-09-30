import {
  Award,
  BookOpen,
  BookOpenCheck,
  Bot,
  Home as HomeIcon,
  LayoutDashboard,
  LogIn,
  Orbit,
  PlusCircle,
  ShoppingCart,
  Store,
} from "lucide-react";

export const ROLE_HOME = {
  student: "/student",
  instructor: "/teacher",
  admin: "/admin",
  super_admin: "/admin",
};

export const ROLE_LABEL = {
  student: "Apprenant",
  instructor: "Enseignant",
  admin: "Administrateur",
  super_admin: "Super admin",
};

export const SPACE_PATHS = ["/student", "/teacher", "/admin"];

export function isAdmin(user) {
  return ["admin", "super_admin"].includes(user?.role);
}

export function isInstructor(user) {
  return isAdmin(user) || user?.role === "instructor";
}

export function matchesRole(user, required = []) {
  if (!user) return false;
  if (required.includes("admin") && isAdmin(user)) return true;
  return required.includes(user.role);
}

export function roleHome(user) {
  return ROLE_HOME[user?.role] || "/student";
}

export function canAccess(user, path) {
  if (!path) return true;
  const own = roleHome(user);
  const inOwnSpace = path === own || path.startsWith(own + "/") || path.startsWith(own + "?");
  const isPublic = !SPACE_PATHS.some((prefix) => path.startsWith(prefix));
  return isPublic || inOwnSpace;
}

export function resolvePostLogin(user, from) {
  const home = roleHome(user);
  if (!from || from === "/login") return home;
  if (SPACE_PATHS.some((prefix) => from.startsWith(prefix))) {
    return canAccess(user, from) ? from : home;
  }
  return home;
}

export const COURSE_STATUS = {
  draft: { label: "Brouillon", variant: "neutral" },
  submitted: { label: "Soumis", variant: "info" },
  in_review: { label: "En révision", variant: "warning" },
  approved: { label: "Approuvé", variant: "brand" },
  published: { label: "Publié", variant: "success" },
};

export const COURSE_LEVELS = {
  beginner: "Débutant",
  intermediate: "Intermédiaire",
  advanced: "Avancé",
};

export function studentNav() {
  return [
    { key: "dashboard", to: "/student", label: "Tableau de bord", icon: LayoutDashboard, end: true },
    { key: "orbite", to: "/student/orbite", label: "Mon Orbite", icon: Orbit },
    { key: "certificats", to: "/student/certificats", label: "Mes certificats", icon: Award },
    { key: "panier", to: "/student/panier", label: "Panier", icon: ShoppingCart },
  ];
}

export function teacherNav() {
  return [
    { key: "dashboard", to: "/teacher", label: "Tableau de bord", icon: LayoutDashboard, end: true },
    { key: "courses", to: "/teacher/cours", label: "Mes formations", icon: BookOpen },
    { key: "new", to: "/teacher/cours/nouveau", label: "Créer une formation", icon: PlusCircle },
  ];
}

export function adminNav() {
  return [
    { key: "dashboard", to: "/admin", label: "Tableau de bord", icon: LayoutDashboard, end: true },
    { key: "courses", to: "/admin/cours", label: "Flux de validation", icon: BookOpenCheck },
    { key: "agents", to: "/admin/agents", label: "Agents IA", icon: Bot },
  ];
}

export function navFor(user) {
  if (isAdmin(user)) return adminNav();
  if (user?.role === "instructor") return teacherNav();
  return studentNav();
}

export function navByKey(key) {
  if (key === "teacher") return teacherNav();
  if (key === "admin") return adminNav();
  return studentNav();
}

export function publicNavLinks(user) {
  if (!user) {
    return [{ to: "/catalogue", label: "Catalogue" }];
  }
  if (isAdmin(user)) {
    return [
      { to: "/catalogue", label: "Catalogue" },
      { to: "/admin", label: "Mon espace" },
      { to: "/admin/cours", label: "Formations" },
      { to: "/admin/agents", label: "Agents IA" },
    ];
  }
  if (user.role === "instructor") {
    return [
      { to: "/catalogue", label: "Catalogue" },
      { to: "/teacher", label: "Mon espace" },
      { to: "/teacher/cours", label: "Mes formations" },
    ];
  }
  return [
    { to: "/catalogue", label: "Catalogue" },
    { to: "/student", label: "Mon espace" },
    { to: "/student/orbite", label: "Mon Orbite" },
    { to: "/student/certificats", label: "Certificats" },
  ];
}

export function mobileItemsFor(user) {
  const items = [
    { key: "home", label: "Accueil", to: "/", icon: HomeIcon },
    { key: "catalog", label: "Catalogue", to: "/catalogue", icon: Store },
  ];
  if (!user) {
    items.push({ key: "login", label: "Connexion", to: "/login", icon: LogIn });
    return items;
  }
  for (const item of navFor(user)) {
    if (item.key === "certificats") continue;
    items.push({ key: item.key, label: item.label, to: item.to, icon: item.icon });
  }
  return items;
}