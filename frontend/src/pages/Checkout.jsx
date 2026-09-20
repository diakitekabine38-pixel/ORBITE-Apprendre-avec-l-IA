import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, apiPost, money } from "../api";

export default function Checkout() {
  const navigate = useNavigate();
  const [cart, setCart] = useState(null);
  const [methods, setMethods] = useState([]);
  const [provider, setProvider] = useState("manual");
  const [coupon, setCoupon] = useState("");
  const [order, setOrder] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [paid, setPaid] = useState(false);

  useEffect(() => {
    api("/cart/summary/").then(setCart).catch(() => setCart({ items: [] }));
    api("/payments/methods/").then((d) => {
      const list = d.results || [];
      setMethods(list);
      if (list.length) setProvider(list[0].code);
    }).catch(() => {});
  }, []);

  const placeOrder = useCallback(async () => {
    const itemCards = cart?.items || [];
    if (!itemCards.length) return;
    setBusy(true);
    setError("");
    try {
      const courseIds = itemCards.map((i) => i.course_id ?? i.course);
      const created = await apiPost("/orders/checkout/", {
        course_ids: courseIds,
        coupon_code: coupon.trim() || "",
      });
      const started = await apiPost("/payments/payments/start/", {
        order_reference: created.reference,
        provider,
      }).catch(() => null);
      // Fallback confirmation through the "manual" flow (Orange Money / vérification).
      const confirmed = await apiPost("/payments/payments/confirm/", {
        order_reference: created.reference,
        reference: started?.reference || "MOBILE-PAY",
      }).catch(() => null);
      setOrder(created);
      setPaid(Boolean(confirmed && confirmed.order_status === "paid"));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [cart, coupon, provider]);

  const itemCards = cart?.items || [];

  if (order) {
    return (
      <div className="mx-auto max-w-xl px-4 py-16 text-center">
        <p className="text-5xl">{paid ? "🎉" : "⏳"}</p>
        <h1 className="mt-4 text-2xl font-bold">{paid ? "Paiement confirmé !" : "Commande créée"}</h1>
        <p className="mt-2 text-muted">
          {paid
            ? "Tes formations sont maintenant disponibles dans ton espace."
            : "Logisticas varies — un.e conseiller.ère validera le paiement."}
        </p>
        <p className="mt-4 font-mono text-sm text-glow">Référence {order.reference}</p>
        <div className="mt-6 flex justify-center gap-3">
          <Link to="/dashboard" className="btn-primary">Aller à mon espace</Link>
          <Link to="/catalogue" className="btn-ghost">Catalogue</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-3xl font-bold">Paiement</h1>

      <div className="glass mt-6 space-y-3 p-6">
        {itemCards.length === 0 ? (
          <p className="text-muted">Aucun article. <Link to="/catalogue" className="link">Aller au catalogue</Link></p>
        ) : (
          itemCards.map((item) => (
            <div key={item.course_id ?? item.course} className="flex justify-between text-sm">
              <span>{item.course_title ?? item.course}</span>
              <span>{money(item.unit_price ?? item.course_price)}</span>
            </div>
          ))
        )}
        <div className="flex items-center justify-between border-t border-line pt-3">
          <input
            className="input max-w-[10rem] !py-2"
            placeholder="Code promo"
            value={coupon}
            onChange={(e) => setCoupon(e.target.value)}
          />
          <p className="font-display text-lg">Total : {money(cart?.total)}</p>
        </div>
      </div>

      {methods.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {methods.map((m) => (
            <button
              key={m.id}
              onClick={() => setProvider(m.code)}
              className={`rounded-xl border px-4 py-2 text-sm transition ${
                provider === m.code ? "border-brand bg-brand/15 text-ink-deep" : "border-line text-muted hover:text-ink-deep"
              }`}
            >
              {m.name}
            </button>
          ))}
        </div>
      )}

      {error && <p className="mt-4 text-sm text-rose-600">{error}</p>}

      <button className="btn-primary mt-6 w-full" disabled={busy || !itemCards.length} onClick={placeOrder}>
        {busy ? "Paiement en cours…" : "Confirmer et payer"}
      </button>
      <p className="mt-3 text-center text-xs text-muted">
        En démo, le paiement "vérification manuelle" est confirmé immédiatement.
      </p>
    </div>
  );
}