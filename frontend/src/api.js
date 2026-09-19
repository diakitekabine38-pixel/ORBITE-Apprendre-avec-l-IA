const BASE = (import.meta.env.VITE_API_BASE || "/api/v1").replace(/\/$/, "");

const TOKEN_KEY = "orbite.access";
const REFRESH_KEY = "orbite.refresh";

export const tokens = {
  get access() {
    return localStorage.getItem(TOKEN_KEY);
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY);
  },
  set(access, refresh) {
    access && localStorage.setItem(TOKEN_KEY, access);
    refresh && localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

async function refreshAccess() {
  const refresh = tokens.refresh;
  if (!refresh) throw new Error("non-authentifié");
  const res = await fetch(`${BASE}/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) throw new Error("session expirée");
  const data = await res.json();
  tokens.set(data.access);
  return data.access;
}

export async function api(path, options = {}) {
  let headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (tokens.access) headers.Authorization = `Bearer ${tokens.access}`;

  let res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401 && tokens.refresh) {
    try {
      headers.Authorization = `Bearer ${await refreshAccess()}`;
      res = await fetch(`${BASE}${path}`, { ...options, headers });
    } catch {
      tokens.clear();
      throw new ApiError(401, "Votre session a expiré. Reconnectez-vous.");
    }
  }

  const body = await res.json().catch(() => null);
  if (!res.ok) {
    if (body && typeof body.detail === "string") {
      throw new ApiError(res.status, body.detail);
    }
    const msg = body ? Object.values(body).flat().join(" · ") : res.statusText;
    throw new ApiError(res.status, msg || "Erreur serveur");
  }
  return body;
}

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

export const apiGet = (p) => api(p);
export const apiPost = (p, data) => api(p, { method: "POST", body: JSON.stringify(data || {}) });
export const apiPatch = (p, data) => api(p, { method: "PATCH", body: JSON.stringify(data || {}) });

export const money = (value) =>
  new Intl.NumberFormat("fr-FR", { style: "currency", currency: "XOF", maximumFractionDigits: 0 }).format(
    Number(value || 0)
  );