import { useCallback, useEffect, useRef, useState } from "react";
import { api, apiPost } from "../api";
import Markdown from "../components/Markdown";

export default function Chat() {
  const [agents, setAgents] = useState([]);
  const [agentId, setAgentId] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, busy]);

  useEffect(() => {
    api("/ai/agents/")
      .then((d) => {
        const list = d.results || [];
        setAgents(list);
        if (!list.length) return;
        const first = list[0].id;
        setAgentId(first);
        // Reprend la dernière conversation ouverte du coach (pour ne pas oublier).
        return api("/ai/sessions/").then((sd) => {
          const match = (sd.results || []).find(
            (s) => s.status === "open" && s.agent && s.agent.id === first
          );
          if (!match) return;
          setSessionId(match.id);
          setMessages(
            (match.messages || []).map((m) => ({
              role: m.role === "user" ? "user" : "assistant",
              content: m.content,
            }))
          );
        });
      })
      .catch(() => {});
  }, []);

  const ask = useCallback(async () => {
    const content = input.trim();
    if (!content || busy) return;
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
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }, [input, busy, agentId, sessionId]);

  const pickAgent = (id) => {
    setAgentId(id);
    setSessionId(null);
    setMessages([]);
    setError("");
  };

  const onEnter = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      ask();
    }
  };

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="text-3xl font-bold">Coach IA</h1>
      <p className="mt-1 text-muted">
        KODEX, NOVA, PIXEL… chaque coach maîtrise un domaine. Pose tes questions en toute liberté.
      </p>

      <div className="mt-6 flex flex-wrap gap-2">
        {agents.map((agent) => (
          <button
            key={agent.id}
            onClick={() => pickAgent(agent.id)}
            className={`rounded-xl border px-4 py-2 text-sm transition ${
              agentId === agent.id
                ? "border-brand bg-brand/15 text-brand"
                : "border-line bg-paper text-muted hover:text-ink-deep"
            }`}
          >
            {agent.name}
            <span className="ml-1 text-xs opacity-70">· {agent.specialty}</span>
          </button>
        ))}
      </div>

<div className="glass mt-6 flex h-[70vh] flex-col">
        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-5">
          {messages.length === 0 && (
            <p className="pt-10 text-center text-muted">
              {agents.length ? `Discute avec ${agents.find((a) => a.id === agentId)?.name || "ton coach"}.` : "Chargement des coachs…"}
            </p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`max-w-[85%] rounded-xl px-4 py-3 text-sm ${
              m.role === "user"
                ? "ml-auto whitespace-pre-wrap bg-brand text-white"
                : "border border-line bg-paper-soft"
            }`}>
              {m.role === "assistant" ? <Markdown>{m.content}</Markdown> : m.content}
            </div>
          ))}
          {busy && <p className="text-sm text-glow">… {agents.find((a) => a.id === agentId)?.name} réfléchit</p>}
          {error && <p className="text-sm text-rose-600">{error}</p>}
        </div>

        <div className="border-t border-line p-4">
          <div className="flex gap-2">
            <textarea
              className="input flex-1 resize-none"
              rows={2}
              placeholder="Ex. : Explique-moi ce qu'est une boucle en Python, simplement."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onEnter}
            />
            <button className="btn-primary self-end" onClick={ask} disabled={busy}>
              Envoyer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}