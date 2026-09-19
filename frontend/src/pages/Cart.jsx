import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, apiPost, money } from "../api";

export default function Cart() {
  const [cart, setCart] = useState(null);

  const load = useCallback(async () => {
    const data = await api("/cart/summary/").catch(() => null);
    setCart(data);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function remove(courseId) {
    const data = await apiPost("/cart/remove/", { course_id: courseId }).catch(() => null);
    setCart(data || cart);
  }

  if (!cart) return <div className="mx-auto max-w-4xl px-4 py-16 text-muted">Chargement du panier…</div>;

  const items = cart.items || [];

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="text-3xl font-bold">Mon panier</h1>

      {items.length === 0 ? (
        <div className="glass mt-6 p-10 text-center">
          <p className="text-4xl">🛒</p>
          <p className="mt-3 text-muted">Ton panier est vide.</p>
          <Link to="/catalogue" className="btn-primary mt-4">Explorer le catalogue</Link>
        </div>
      ) : (
        <>
          <div className="mt-6 space-y-4">
            {items.map((item) => (
              <div key={item.id} className="glass flex items-center justify-between gap-4 p-4">
                <div>
                  <p className="font-semibold">{item.course_title || item.course}</p>
                  <p className="text-sm text-muted">{money(item.unit_price ?? item.course_price)}</p>
                </div>
                <button onClick={() => remove(item.course_id ?? item.course)} className="btn-ghost !px-3 !py-1 text-xs">
                  Retirer
                </button>
              </div>
            ))}
          </div>
          <div className="mt-6 flex items-center justify-between">
            <p className="font-display text-xl">
              Total : <span className="font-bold">{money(cart.total)}</span>
            </p>
            <Link to="/paiement" className="btn-primary">Procéder au paiement →</Link>
          </div>
        </>
      )}
    </div>
  );
}