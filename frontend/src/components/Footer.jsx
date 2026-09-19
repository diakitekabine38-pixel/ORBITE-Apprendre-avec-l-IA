import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="border-t border-line">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 py-8 text-sm text-muted md:flex-row">
        <p>
          <span className="font-display font-semibold text-white">ORBITE</span> — Apprendre avec
          l'IA, en Afrique et partout ailleurs.
        </p>
        <div className="flex gap-5">
          <Link to="/catalogue" className="hover:text-white">Catalogue</Link>
          <Link to="/inscription" className="hover:text-white">Créer un compte</Link>
        </div>
      </div>
    </footer>
  );
}