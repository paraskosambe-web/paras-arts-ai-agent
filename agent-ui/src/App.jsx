import { useState } from "react";
import "./App.css";

const API_URL = "https://paras-arts-ai-agent.onrender.com/chat";

const suggestions = [
  {
    title: "Explore orders",
    text: "How many orders do I have?",
    icon: "⌁",
  },
  {
    title: "Order status",
    text: "Show accepted orders",
    icon: "◷",
  },
  {
    title: "Business overview",
    text: "Give me a business summary",
    icon: "✦",
  },
  {
    title: "Artwork insights",
    text: "Analyze my artwork data",
    icon: "◇",
  },
];

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async (text = message) => {
    const userMessage = text.trim();

    if (!userMessage || loading) return;

    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: userMessage,
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.answer ||
            "Something went wrong while contacting the AI agent."
        );
      }

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            data.answer ||
            "I received your request but didn't get a response.",
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            error.message ||
            "I couldn't connect to the AI service right now. Please try again later.",
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
    <div className="app-shell">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="brand">
            <div className="brand-mark">P</div>

            <div className="brand-text">
              <div className="brand-name">Paras Arts</div>
              <div className="brand-subtitle">AI Data Agent</div>
            </div>
          </div>

          <button className="new-chat-button" onClick={startNewChat}>
            <span className="new-chat-icon">+</span>
            <span>New chat</span>
          </button>

          <div className="sidebar-section">
            <div className="section-label">Recent</div>

            {messages.length > 0 ? (
              <button className="conversation-item">
                <span className="conversation-icon">◌</span>
                <span className="conversation-text">
                  Current conversation
                </span>
              </button>
            ) : (
              <div className="empty-history">No conversations yet</div>
            )}
          </div>
        </div>

        <div className="sidebar-bottom">
          <div className="connection-status">
            <span className="online-dot" />
            <span>Agent online</span>
          </div>

          <div className="database-status">
            <span className="database-icon">◈</span>
            <span>MongoDB · Read-only</span>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="main">
        {/* Header */}
        <header className="topbar">
          <div className="topbar-title">
            <div className="mobile-brand-mark">P</div>

            <div>
              <h1>Paras Arts AI Data Agent</h1>
              <p>Connected to your business data</p>
            </div>
          </div>

          <div className="topbar-status">
            <span className="online-dot" />
            <span>Online</span>
          </div>
        </header>

        {/* Conversation */}
        <div className={`chat-area ${messages.length === 0 ? "empty" : ""}`}>
          {messages.length === 0 ? (
            <section className="welcome">
              <div className="welcome-mark">
                <span>P</span>
              </div>

              <h2>How can I help you?</h2>

              <p className="welcome-description">
                Ask questions about your Paras Arts orders, artworks,
                services, FAQs, and business data.
              </p>

              <div className="suggestions">
                {suggestions.map((suggestion) => (
                  <button
                    className="suggestion-card"
                    key={suggestion.text}
                    onClick={() => sendMessage(suggestion.text)}
                  >
                    <div className="suggestion-left">
                      <span className="suggestion-icon">
                        {suggestion.icon}
                      </span>

                      <span>
                        <strong>{suggestion.title}</strong>
                        <small>{suggestion.text}</small>
                      </span>
                    </div>

                    <span className="suggestion-arrow">→</span>
                  </button>
                ))}
              </div>
            </section>
          ) : (
            <section className="conversation">
              {messages.map((item) => (
                <div
                  className={`message-row ${item.role}`}
                  key={item.id}
                >
                  {item.role === "assistant" && (
                    <div className="assistant-avatar">P</div>
                  )}

                  <div
                    className={`message-content ${
                      item.isError ? "error-message" : ""
                    }`}
                  >
                    {item.content}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message-row assistant">
                  <div className="assistant-avatar">P</div>

                  <div className="message-content typing">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              )}
            </section>
          )}
        </div>

        {/* Composer */}
        <div className="composer-area">
          <div className="composer">
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your Paras Arts data..."
              rows={1}
              disabled={loading}
            />

            <button
              className="send-button"
              onClick={() => sendMessage()}
              disabled={!message.trim() || loading}
              aria-label="Send message"
            >
              ↑
            </button>
          </div>

          <div className="composer-footer">
            <span>
              Paras Arts AI · Read-only access to business data
            </span>

            <span className="keyboard-hint">
              Enter to send · Shift + Enter for new line
            </span>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;