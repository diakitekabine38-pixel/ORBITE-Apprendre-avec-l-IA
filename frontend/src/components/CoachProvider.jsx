import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { Bot, ChevronDown, MessageSquarePlus, Send, X } from "lucide-react";
import { api, apiPost } from "../api";
import { useAuth } from "../auth";
import Markdown from "./Markdown";
import { Avatar, Button } from "./ui";
import { cn } from "./ui/cn";

const AGENT_GRADIENTS = ["kodex", "kora", "nova", "pixel"];
const AGENT_KEY = "orbite.chat.agent";

const CoachContext = createContext({ open: false, openCoach: () => {} });

export function useCoach() {
  return useContext(CoachContext);
}

function agentGradient(agent) {
  const key = (agent?.code || agent?.name || "").toLowerCase();
  return AGENT_GRADIENTS.includes(key) ? key : "orbital";
}

function timeAgo(iso) {
  if (!iso) return "";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "à l'instant";
  if (mins < 60) return `${mins} min`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours} h`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days} j`;
  return new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
}

export function CoachProvider({ children }) {
  const { user } = useAuth();

  const [open, setOpen] = useState(false);
  const [agents, setAgents] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [loadingAgents, setLoadingAgents] = useState(true);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [agentId, setAgentId] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [showAgents, setShowAgents] = useState(false);
  const scrollRef = useRef(null);

  const currentAgent = agents.find((a) => a.id === agentId) || null;
  const agentSessions = sessions
    .filter((s) => s.agent && s.agent.id === agentId)
    .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, busy]);

  const loadSessions = useCallback(() => {
    return api("/ai/sessions/")
      .then((d) => setSessions(d.results || []))
      .catch(() => {})
      .finally(() => setLoadingSessions(false));
  }, []);

  useEffect(() => {
    if (!user) return;
    loadSessions();
    api("/ai/agents/")
      .then((d) => {
        const list = d.results || [];
        setAgents(list);
        setLoadingAgents(false);
        if (!list.length) return;
        const saved = localStorage.getItem(AGENT_KEY);
        setAgentId(list.some((a) => a.id === Number(saved)) ? Number(saved) : list[0].id);
      })
      .catch(() => setLoadingAgents(false));
  }, [user, loadSessions]);

  useEffect(() => {
    if (!open || !agentId) return;
    setShowAgents(false);
    if (sessionId) return;
    if (!agentSessions.length) {
      setMessages([]);
      return;
    }
    const last = agentSessions[0];
    setSessionId(last.id);
    setMessages(
      (last.messages || []).map((m) => ({
        role: m.role === "user" ? "user" : "assistant",
        content: m.content,
      }))
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, agentId]);

  const openCoach = useCallback(() => setOpen(true), []);

  const openSession = useCallback((id) => {
    const found = sessions.find((s) => s.id === id);
    setSessionId(id);
    setError("");
    setMessages(
      found && found.messages
        ? found.messages.map((m) => ({ role: m.role === "user" ? "user" : "assistant", content: m.content }))
        : []
    );
  }, [sessions]);

  const pickAgent = useCallback((id) => {
    setAgentId(id);
    localStorage.setItem(AGENT_KEY, String(id));
    setSessionId(null);
    setMessages([]);
    setError("");
    setShowAgents(false);
  }, []);

  const newDiscussion = useCallback(() => {
    setSessionId(null);
    setMessages([]);
    setError("");
  }, []);

  const ask = useCallback(async () => {
    const content = input.trim();
    if (!content || busy || !agentId) return;
    setInput("");
    setError("");
    setBusy(true);
    setMessages((prev) => [...prev, { role: "user", content }]);
    try {
      const payload = { content, agent_id: agentId };
      if (sessionId) payload.session_id = sessionId;
      const res = await apiPost("/ai/sessions/ask/", payload);
      setSessionId(res.session.id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.answer }]);
      loadSessions();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [input, busy, agentId, sessionId, loadSessions]);

  const onEnter = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      ask();
    }
  };

  if (!user) {
    return <CoachContext.Provider value={{ open, openCoach }}>{children}</CoachContext.Provider>;
  }
  const avatarEl = loadingAgents ? (
    <Avatar name="IA" gradient="orbital" size="lg" />
  ) : (
    <Avatar name={currentAgent?.name || "IA"} gradient={agentGradient(currentAgent)} size="lg" />
  );

  return (
    <CoachContext.Provider value={{ open, openCoach }}>
      {children}

      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Fermer le Coach IA" : "Ouvrir le Coach IA"}
        title="Coach IA"
        className="fixed bottom-5 right-5 z-50 rounded-full shadow-lg shadow-orbital-900/20 transition hover:scale-105 active:scale-95"
      >
        {avatarEl}
        <span className="absolute -right-0.5 -bottom-0.5 h-3.5 w-3.5 rounded-full border-2 border-white bg-success" />
      </button>

      {open && (
        <div className="fixed right-5 bottom-[4.75rem] z-50 flex h-[32rem] w-[22rem] max-w-[calc(100vw-2.5rem)] flex-col overflow-hidden rounded-2xl border border-line bg-paper shadow-2xl">
          <div className="flex items-center gap-2 border-b border-line p-3">
            <span className="font-display text-sm font-bold text-ink-deep">Coach IA</span>
            <button
              type="button"
              onClick={() => setShowAgents((v) => !v)}
              className={cn(
                "flex min-w-0 flex-1 items-center gap-2 rounded-xl border px-2.5 py-1.5 text-left text-sm transition",
                showAgents
                  ? "border-brand bg-brand/10 text-ink-deep"
                  : "border-line bg-paper-soft text-ink-deep hover:border-orbital-300"
              )}
            >
              <Avatar name={currentAgent?.name || "IA"} gradient={agentGradient(currentAgent)} size="xs" />
              <span className="min-w-0 flex-1 truncate">{currentAgent?.name || "Chargement…"}</span>
              <ChevronDown className="h-4 w-4 shrink-0 text-muted" />
            </button>
            <Button variant="ghost" size="sm" onClick={() => setOpen(false)} icon={X} aria-label="Fermer" />
          </div>

          {showAgents && (
            <div className="max-h-56 space-y-1 overflow-y-auto border-b border-line p-2">
              {loadingAgents ? (
                <p className="px-2 py-1 text-xs text-muted">Chargement des coachs…</p>
              ) : (
                agents.map((agent) => (
                  <button
                    key={agent.id}
                    type="button"
                    onClick={() => pickAgent(agent.id)}
                    className={cn(
                      "flex w-full items-center gap-3 rounded-xl border p-2 text-left transition",
                      agentId === agent.id
                        ? "border-brand bg-brand/10"
                        : "border-line bg-paper hover:bg-paper-soft"
                    )}
                  >
                    <Avatar name={agent.name} gradient={agentGradient(agent)} size="sm" />
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium text-ink-deep">{agent.name}</span>
                      <span className="block truncate text-xs text-muted">{agent.specialty}</span>
                    </span>
                  </button>
                ))
              )}
            </div>
          )}

          <div className="flex items-center gap-2 border-b border-line px-3 py-2">
            <select
              value={sessionId ?? ""}
              onChange={(e) => (e.target.value ? openSession(Number(e.target.value)) : newDiscussion())}
              className="input flex-1 text-sm"
              title="Discussions"
            >
              <option value="">+ Nouvelle discussion</option>
              {loadingSessions &&
                agentSessions.length === 0 && <option disabled>Chargement…</option>}
              {agentSessions.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.title || "Discussion"} · {timeAgo(s.updated_at)}
                </option>
              ))}
            </select>
            <Button variant="outline" size="sm" onClick={newDiscussion} icon={MessageSquarePlus} />
          </div>

          <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto p-3">
            {messages.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center gap-2 px-4 text-center">
                <Avatar name={currentAgent?.name || "IA"} gradient={agentGradient(currentAgent)} size="lg" />
                <p className="text-sm font-medium text-ink-deep">
                  {currentAgent ? `Discute avec ${currentAgent.name}` : "Discute avec ton coach"}
                </p>
                <p className="text-xs text-muted">
                  {currentAgent?.expertise ||
                    "Présente-toi, partage ton objectif : le coach adapte ses réponses à toi."}
                </p>
              </div>
            ) : (
              messages.map((m, i) => (
                <div
                  key={i}
                  className={cn(
                    "max-w-[85%] rounded-xl px-3 py-2 text-sm",
                    m.role === "user"
                      ? "ml-auto whitespace-pre-wrap bg-brand text-white"
                      : "border border-line bg-paper-soft"
                  )}
                >
                  {m.role === "assistant" ? <Markdown>{m.content}</Markdown> : m.content}
                </div>
              ))
            )}
            {busy && <p className="text-xs text-glow">… {currentAgent?.name || "coach"} réfléchit</p>}
            {error && <p className="text-xs text-rose-600">{error}</p>}
          </div>

          <div className="flex gap-2 border-t border-line p-3">
            <textarea
              className="input flex-1 resize-none"
              rows={2}
              placeholder={`Écris à ${currentAgent?.name || "ton coach"}…`}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onEnter}
            />
            <Button className="self-end" onClick={ask} disabled={busy || !agentId} icon={Send} />
          </div>
        </div>
      )}
    </CoachContext.Provider>
  );
}