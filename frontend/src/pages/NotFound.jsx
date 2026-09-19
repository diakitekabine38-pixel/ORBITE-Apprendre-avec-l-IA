import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="mx-auto grid min-h-[60vh] max-w-4xl place-items-center px-4 text-center">
      <div>
        <p className="font-display text-7xl font-bold text-brand-soft">404</p>
        <h1 className="mt-2 text-2xl font-bold">Page introuvable</h1>
        <p className="mt-2 text-muted">Cette page n'existe pas ou a été déplacée.</p>
        <Link to="/" className="btn-primary mt-6">Retour à l'accueil</Link>
      </div>
    </div>
  );
}