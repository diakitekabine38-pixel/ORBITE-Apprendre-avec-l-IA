import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "./api";
import { useAuth } from "./auth";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState(null);

  const refresh = useCallback(async () => {
    const data = await api("/cart/summary/").catch(() => null);
    setCart(data);
    return data;
  }, []);

  useEffect(() => {
    if (user) refresh();
    else setCart(null);
  }, [user?.id, refresh]);

  const cartCount = cart?.items?.reduce((n, item) => n + (item.quantity || 1), 0) || 0;

  return (
    <CartContext.Provider value={{ cart, cartCount, refresh }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart doit être utilisé dans <CartProvider>");
  return ctx;
}