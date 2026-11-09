import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import DataChart from "./DataChart";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "https://paras-arts-ai-agent.onrender.com/chat";

const suggestions = [
  {
    title: "Track order volume",
    text: "Show me a graph of monthly orders for the last 8 months",
    icon: "↗",
    tone: "coral",
  },
  {
    title: "Understand order status",
    text: "Show a chart of orders by status and tell me what stands out",
    icon: "◒",
    tone: "green",
  },
  {
    title: "Compare sketch types",
    text: "Which sketch type has the most orders?",
    icon: "▤",
    tone: "ochre",
  },
  {
    title: "Update a record",
    text: "Change an order status to completed",
    icon: "↻",
    tone: "slate",
  },
];

const loadingMessages = [
  "Understanding your question",
  "Checking the relevant business data",
  "Putting the answer together",
];

function MongoMark({ className = "" }) {
  return (
    <svg className={className} viewBox="0 0 40 40" role="img" aria-label="MongoDB">
      <path
        d="M20 3.2c-1.8 4.2-9.1 10.1-9.1 19.4 0 6.2 3.7 10.1 8 11.8l1.1 2.4 1.1-2.4c4.4-1.8 8-5.7 8-11.8C29.1 13.3 21.8 7.4 20 3.2Z"
        fill="currentColor"
      />
      <path d="M20 11v24" fill="none" stroke="#f8faf6" strokeLinecap="round" strokeWidth="1.5" opacity=".86" />
      <path d="M20 25c-2.1-1.7-3.5-3.8-4.3-6.3" fill="none" stroke="#f8faf6" strokeLinecap="round" strokeWidth="1.25" opacity=".75" />
    </svg>
  );
}

function AssistantMark() {
  return <div className="assistant-mark" aria-label="Paras Arts assistant">P</div>;
}

function LoadingIndicator({ phase }) {
  return (
    <div className="message-row assistant loading-row">
      <AssistantMark />
      <div className="loading-card" role="status" aria-live="polite">
        <div className="loading-topline">
          <span className="loader-ring" />
          <span className="loading-title">Working with your data</span>
          <span className="loading-pulse"><i /><i /><i /></span>
        </div>
        <div className="loading-progress" aria-hidden="true">
          <span className={phase >= 0 ? "active" : ""} />
          <span className={phase >= 1 ? "active" : ""} />
          <span className={phase >= 2 ? "active" : ""} />
        </div>
        <div className="loading-detail">{loadingMessages[phase]}</div>
      </div>
    </div>
  );
}

function splitPipeCells(line) {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

function isTableSeparator(line) {
  const cells = splitPipeCells(line);
  return cells.length > 1 && cells.every((cell) => /^:?-{3,}:?$/.test(cell));
}

function compactTable(line) {
  const firstPipe = line.indexOf("|");
  const lastPipe = line.lastIndexOf("|");
  if (firstPipe < 0 || lastPipe <= firstPipe) return null;

  const tableText = line.slice(firstPipe, lastPipe + 1);
  const cells = splitPipeCells(tableText).filter(Boolean);
  const separatorIndex = cells.findIndex((cell) => /^:?-{3,}:?$/.test(cell));
  if (separatorIndex < 2) return null;

  const headers = cells.slice(0, separatorIndex);
  const values = cells.slice(separatorIndex + 1).filter((cell) => !/^:?-{3,}:?$/.test(cell));
  const rows = [];
  for (let index = 0; index + headers.length <= values.length; index += headers.length) {
    rows.push(values.slice(index, index + headers.length));
  }

  return {
    prefix: line.slice(0, firstPipe).trim(),
    suffix: line.slice(lastPipe + 1).trim(),
    headers,
    rows,
  };
}

function FormattedAnswer({ content }) {
  const lines = String(content || "").split(/\r?\n/);
  const blocks = [];
  let prose = [];
  const flushProse = () => {
    const value = prose.join("\n").trim();
    if (value) blocks.push({ type: "prose", value });
    prose = [];
  };

  for (let index = 0; index < lines.length;) {
    if (index + 1 < lines.length && isTableSeparator(lines[index + 1]) && lines[index].includes("|")) {
      flushProse();
      const headers = splitPipeCells(lines[index]).filter(Boolean);
      const rows = [];
      index += 2;
      while (index < lines.length && lines[index].includes("|")) {
        if (!isTableSeparator(lines[index])) rows.push(splitPipeCells(lines[index]).filter(Boolean));
        index += 1;
      }
      blocks.push({ type: "table", headers, rows });
      continue;
    }

    const parsed = compactTable(lines[index]);
    if (parsed) {
      flushProse();
      if (parsed.prefix) blocks.push({ type: "prose", value: parsed.prefix });
      blocks.push({ type: "table", headers: parsed.headers, rows: parsed.rows });
      if (parsed.suffix) prose.push(parsed.suffix);
      index += 1;
      continue;
    }

    prose.push(lines[index]);
    index += 1;
  }
  flushProse();

  return blocks.map((block, blockIndex) => {
    if (block.type === "prose") {
      return <ReactMarkdown key={`prose-${blockIndex}`}>{block.value}</ReactMarkdown>;
    }
    return (
      <div className="answer-table-wrap" key={`table-${blockIndex}`}>
        <table className="answer-table">
          <thead><tr>{block.headers.map((header, index) => <th key={`${header}-${index}`}>{header}</th>)}</tr></thead>
          <tbody>
            {block.rows.map((row, rowIndex) => (
              <tr key={`row-${rowIndex}`}>
                {block.headers.map((_, cellIndex) => <td key={`cell-${cellIndex}`}>{row[cellIndex] || "—"}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  });
}

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingPhase, setLoadingPhase] = useState(0);
  const chatEndRef = useRef(null);

  const [sessionId] = useState(() => {
    const existingSession = localStorage.getItem("paras_arts_agent_session");
    if (existingSession) return existingSession;

    const newSession = crypto.randomUUID();
    localStorage.setItem("paras_arts_agent_session", newSession);
    return newSession;
  });

  useEffect(() => {
    if (!loading) return undefined;
    const timer = window.setInterval(() => {
      setLoadingPhase((current) => (current + 1) % loadingMessages.length);
    }, 1700);
    return () => window.clearInterval(timer);
  }, [loading]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  const sendMessage = async (text = message) => {
    const userMessage = text.trim();
    if (!userMessage || loading) return;

    setMessages((previous) => [
      ...previous,
      { id: crypto.randomUUID(), role: "user", content: userMessage },
    ]);
    setMessage("");
    setLoadingPhase(0);
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage, session_id: sessionId }),
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.answer || "The agent could not complete that request.");
      }

      setMessages((previous) => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.answer || "I received your request but did not get a response.",
          visualizations: data.visualizations || [],
        },
      ]);
    } catch (error) {
      setMessages((previous) => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: error.message || "I could not connect to the data assistant right now.",
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setMessage("");
  };

  return (
    <div className="workspace-shell">
      <aside className="workspace-sidebar">
        <div>
          <div className="sidebar-brand">
            <div className="brand-symbol">P</div>
            <div className="brand-copy">
              <strong>Paras Arts</strong>
              <span>Data workspace</span>
            </div>
          </div>

          <button className="new-chat-button" onClick={startNewChat}>
            <span className="new-chat-plus">＋</span>
            <span>New conversation</span>
            <span className="new-chat-shortcut">⌘ K</span>
          </button>

          <div className="sidebar-label">WORKSPACE</div>
          <button className="sidebar-nav-item active">
            <span className="nav-glyph">▤</span>
            <span>Business data</span>
            <span className="nav-chevron">›</span>
          </button>

          <div className="sidebar-label recent-label">RECENT</div>
          {messages.length ? (
            <button className="recent-item">
              <span className="recent-indicator" />
              <span className="recent-title">Current conversation</span>
            </button>
          ) : (
            <p className="sidebar-empty">Your conversations will appear here.</p>
          )}
        </div>

        <div className="sidebar-bottom">
          <div className="database-card">
            <div className="database-card-icon"><MongoMark /></div>
            <div className="database-card-copy">
              <span className="database-card-label">DATABASE SOURCE</span>
              <strong>MongoDB</strong>
              <span className="database-name">Paras Arts business data</span>
            </div>
          </div>
          <div className="sidebar-footnote">Private business workspace</div>
        </div>
      </aside>

      <main className="workspace-main">
        <header className="workspace-header">
          <div className="mobile-brand">
            <div className="brand-symbol small">P</div>
            <span>Paras Arts</span>
          </div>
          <div className="breadcrumb">
            <span>Workspace</span><span className="breadcrumb-slash">/</span><strong>Business data</strong>
          </div>
          <div className="header-database"><MongoMark /><span>MongoDB</span></div>
        </header>

        <section className={`chat-scroll ${messages.length ? "has-messages" : "welcome-state"}`}>
          {messages.length === 0 ? (
            <div className="welcome-panel">
              <div className="welcome-kicker"><span className="kicker-rule" />PARAS ARTS <span className="kicker-divider">/</span> BUSINESS DATA</div>
              <h1>Make sense of<br /><em>your business.</em></h1>
              <p className="welcome-copy">
                Ask a question, explore a trend, or update a record. Your assistant works with the Paras Arts database and shows the data behind its answers.
              </p>

              <div className="welcome-source">
                <div className="source-logo"><MongoMark /></div>
                <div className="source-copy"><strong>MongoDB database</strong><span>Paras Arts business collections</span></div>
              </div>

              <div className="suggestion-heading"><span>START WITH A QUESTION</span><span>Choose a prompt</span></div>
              <div className="suggestion-grid">
                {suggestions.map((suggestion) => (
                  <button className="suggestion-card" key={suggestion.text} onClick={() => sendMessage(suggestion.text)}>
                    <span className={`suggestion-icon ${suggestion.tone}`}>{suggestion.icon}</span>
                    <span className="suggestion-card-copy"><strong>{suggestion.title}</strong><small>{suggestion.text}</small></span>
                    <span className="suggestion-arrow">↗</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="conversation">
              {messages.map((item) => (
                <article className={`message-row ${item.role}`} key={item.id}>
                  {item.role === "assistant" && <AssistantMark />}
                  <div className={`message-content ${item.isError ? "error-message" : ""}`}>
                    {item.role === "assistant" ? (
                      <>
                        <FormattedAnswer content={item.content} />
                        {item.visualizations?.length > 0 && (
                          <div className="charts-stack">
                            {item.visualizations.map((chart, index) => (
                              <DataChart key={`${chart.title}-${index}`} chart={chart} />
                            ))}
                          </div>
                        )}
                      </>
                    ) : item.content}
                  </div>
                </article>
              ))}
              {loading && <LoadingIndicator phase={loadingPhase} />}
              <div ref={chatEndRef} />
            </div>
          )}
        </section>

        <div className="composer-dock">
          <div className="composer-wrap">
            <div className="composer">
              <textarea
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about orders, trends, payments, or your business..."
                rows={1}
                disabled={loading}
                aria-label="Ask the Paras Arts data assistant"
              />
              <div className="composer-actions">
                <span className="composer-context"><MongoMark /><span>Paras Arts database</span></span>
                <button className="send-button" onClick={() => sendMessage()} disabled={!message.trim() || loading} aria-label="Send message">↑</button>
              </div>
            </div>
            <div className="composer-caption">
              <span>Enter to send <i>·</i> Shift + Enter for a new line</span>
              <span>Database changes always ask for confirmation</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
