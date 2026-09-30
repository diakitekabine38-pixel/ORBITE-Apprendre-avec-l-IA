import { useEffect } from "react";
import { Route, Routes, useNavigate, useParams } from "react-router-dom";
import Private from "./components/Private";
import { useAuth } from "./auth";
import { roleHome } from "./navigation";
import PublicLayout from "./layouts/PublicLayout";
import SpaceLayout from "./layouts/SpaceLayout";
import Home from "./pages/Home";
import Catalog from "./pages/Catalog";
import CourseDetail from "./pages/CourseDetail";
import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";
import Forbidden from "./pages/Forbidden";
import Dashboard from "./pages/Dashboard";
import Learn from "./pages/Learn";
import Certificates from "./pages/Certificates";
import Orbite from "./pages/Orbite";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";
import VerifyCertificate from "./pages/VerifyCertificate";
import NotFound from "./pages/NotFound";
import TeacherDashboard from "./pages/teacher/TeacherDashboard";
import TeacherCourses from "./pages/teacher/TeacherCourses";
import TeacherCourseForm from "./pages/teacher/TeacherCourseForm";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminCourses from "./pages/admin/AdminCourses";
import AdminAgents from "./pages/AdminAgents";

function StaleLink({ target }) {
  const { user } = useAuth();
  const params = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    navigate(typeof target === "function" ? target(user, params) : target(user), { replace: true });
  }, [user, params, target, navigate]);

  return null;
}

export default function App() {
  return (
    <Routes>
      {/* ——— Espace public ——— */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/catalogue" element={<Catalog />} />
        <Route path="/formations/:slug" element={<CourseDetail />} />
        <Route path="/login" element={<Login />} />
        <Route path="/inscription" element={<Register />} />
        <Route path="/verification-email/:token" element={<VerifyEmail />} />
        <Route path="/verification/:certificateId" element={<VerifyCertificate />} />
        <Route path="/acces-refuse" element={<Forbidden />} />

        {/* Anciens chemins apprenant → espace par rôle */}
        <Route path="/dashboard" element={<StaleLink target={(u) => roleHome(u)} />} />
        <Route path="/app/orbite" element={<StaleLink target={(u) => roleHome(u)} />} />
        <Route path="/chat" element={<StaleLink target={(u) => roleHome(u)} />} />
        <Route path="/certificats" element={<StaleLink target={(u) => roleHome(u)} />} />
        <Route path="/panier" element={<StaleLink target={(u) => roleHome(u)} />} />
        <Route path="/paiement" element={<StaleLink target={(u) => roleHome(u)} />} />
        <Route
          path="/apprentissage/:slug"
          element={
            <StaleLink
              target={(u, p) =>
                u?.role === "student" ? `/student/apprentissage/${p.slug}` : roleHome(u)
              }
            />
          }
        />
        <Route path="*" element={<NotFound />} />
      </Route>

      {/* ——— Espace apprenant /student/* ——— */}
      <Route
        path="/student/*"
        element={
          <Private roles={["student"]}>
            <SpaceLayout route="/student" navKey="student" />
          </Private>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="apprentissage/:slug" element={<Learn />} />
        <Route path="orbite" element={<Orbite />} />
        <Route path="certificats" element={<Certificates />} />
        <Route path="panier" element={<Cart />} />
        <Route path="paiement" element={<Checkout />} />
      </Route>

      {/* ——— Espace enseignant /teacher/* ——— */}
      <Route
        path="/teacher/*"
        element={
          <Private roles={["instructor", "admin"]}>
            <SpaceLayout route="/teacher" navKey="teacher" />
          </Private>
        }
      >
        <Route index element={<TeacherDashboard />} />
        <Route path="cours" element={<TeacherCourses />} />
        <Route path="cours/nouveau" element={<TeacherCourseForm />} />
      </Route>

      {/* ——— Espace administrateur /admin/* ——— */}
      <Route
        path="/admin/*"
        element={
          <Private roles={["admin"]}>
            <SpaceLayout route="/admin" navKey="admin" />
          </Private>
        }
      >
        <Route index element={<AdminDashboard />} />
        <Route path="cours" element={<AdminCourses />} />
        <Route path="agents" element={<AdminAgents />} />
      </Route>
    </Routes>
  );
}