import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api, apiPost, tokens } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!tokens.access) {
      setLoading(false);
      return;
    }
    apiGetMe()
      .then(setUser)
      .catch(() => {
        tokens.clear();
      })
      .finally(() => setLoading(false));
  }, []);

  async function apiGetMe() {
    const me = await api("/auth/me/");
    const profileRes = await api("/users/profile/me/").catch(() => null);
    return { ...me, profile: profileRes || {} };
  }

  async function login(email, password) {
    const data = await apiPost("/auth/login/", { email, password });
    return enterSession(data);
  }

  async function enterSession(data) {
    tokens.set(data.access, data.refresh);
    const me = await apiGetMe();
    setUser(me);
    return me;
  }

  async function register(payload) {
    await apiPost("/auth/register/", {
      ...payload,
      password2: payload.password,
    });
  }

  async function logout() {
    tokens.clear();
    setUser(null);
  }

  useEffect(() => {
    function onStorage(e) {
      if (e.storageArea !== localStorage || !(e.key || "").startsWith("orbite.")) return;
      if (tokens.access) {
        apiGetMe().then(setUser).catch(() => tokens.clear());
      } else {
        setUser(null);
      }
    }
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, register, logout, enterSession, refresh: apiGetMe }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth doit être utilisé dans <AuthProvider>");
  return ctx;
}