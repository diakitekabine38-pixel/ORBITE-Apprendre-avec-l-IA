import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth";
import { matchesRole } from "../navigation";
import { LoadingState } from "./ui";
import Forbidden from "../pages/Forbidden";

export default function Private({ children, roles = null }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingState size="lg" />
      </div>
    );
  }
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;
  if (roles && !matchesRole(user, roles)) return <Forbidden />;
  return children;
}