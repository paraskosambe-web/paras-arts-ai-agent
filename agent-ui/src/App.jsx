import { useState } from "react";
import "./App.css";

const API_URL = "https://paras-arts-ai-agent.onrender.com/chat";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const suggestions = [
    "How many orders do I have?",
    "Show accepted orders",
    "Give me a business summary",
    "Analyze my artwork data",
  ];

  const sendMessage = async (text = message) => {
    const userMessage = text.trim();

    if (!userMessage || loading) return;

    setMessages((prev) => [
      ...prev,
      {
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
        "Something went wrong."
      );
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
        },
      ]);
    } catch (error) {
  setMessages((prev) => [
    ...prev,
    {
      role: "assistant",
      content:
        error.message ||
        "I couldn't connect to the AI service right now. Please try again later.",
    },
  ]);

  console.error("Chat error:", error);
}finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">P</div>

          <div>
            <h2>Paras Arts</h2>
            <span>AI Data Agent</span>
          </div>
        </div>

        <button
          className="new-chat"
          onClick={() => setMessages([])}
        >
          <span>＋</span>
          New chat
        </button>

        <div className="sidebar-section">
          <p>Recent</p>

          {messages.length > 0 ? (
            <div className="history-item">
              Current conversation
            </div>
          ) : (
            <div className="history-item">
              No conversations yet
            </div>
          )}
        </div>

        <div className="sidebar-bottom">
          <div className="status">
            <span className="status-dot"></span>
            Agent online
          </div>

          <div className="database">
            MongoDB • Read-only
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h3>Paras Arts AI Data Agent</h3>
            <span>Connected to your business data</span>
          </div>

          <div className="top-status">
            <span className="status-dot"></span>
            Online
          </div>
        </header>

        <section className="chat-area">
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-icon">✦</div>

              <h1>How can I help you?</h1>

              <p>
                Ask questions about your Paras Arts orders,
                artworks, services, FAQs, or business data.
              </p>

              <div className="suggestions">
                {suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => sendMessage(suggestion)}
                  >
                    {suggestion}
                    <span>→</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((item, index) => (
                <div
                  key={index}
                  className={`message-row ${item.role}`}
                >
                  <div className="message-content">
                    {item.content}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message-row assistant">
                  <div className="message-content typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        <div className="composer-wrapper">
          <div className="composer">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your Paras Arts data..."
              rows="1"
              disabled={loading}
            />

            <button
              className="send-button"
              onClick={() => sendMessage()}
              disabled={!message.trim() || loading}
            >
              ↑
            </button>
          </div>

          <p className="disclaimer">
            Paras Arts AI Data Agent • Read-only access to business data
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;