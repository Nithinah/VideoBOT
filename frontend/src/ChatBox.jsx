// src/ChatBox.jsx
import React from "react";
import "./styles.css";

const ChatBox = ({ messages }) => {
  const parseMessage = (msg) => {
    if (msg.role !== "bot") return <div className="bubble-user">{msg.text}</div>;

    const lines = msg.text.split("\n").filter(Boolean);
    const summary = lines.find((line) => line.startsWith("Summary:"));
    const video = lines.find((line) => line.startsWith("📍 Video:"));
    const timestamp = lines.find((line) => line.startsWith("⏱ Timestamp:"));
    const subtitle = lines.find((line) => line.startsWith("🗒 Subtitle:"));

    let clickableSpan = null;
    if (timestamp) {
      const match = timestamp.match(/(\d{1,2}:\d{2}(?::\d{2})?) - (\d{1,2}:\d{2}(?::\d{2})?)/);
      if (match) {
        const normalize = (str) => {
          const parts = str.split(":");
          return parts.length === 2
            ? `00:${parts[0].padStart(2, "0")}:${parts[1].padStart(2, "0")}`
            : str;
        };
        const [, startRaw, endRaw] = match;
        const start = normalize(startRaw);
        const end = normalize(endRaw);

        clickableSpan = (
          <span
            onClick={() => window.handleTimestampClick(start, end)}
            className="clickable-timestamp"
          >
            ⏱ Timestamp: {startRaw} - {endRaw}
          </span>
        );
      } else {
        clickableSpan = <span>{timestamp}</span>;
      }
    }

    return (
      <div className="bubble-bot">
        {summary && <div><strong>{summary}</strong></div>}
        {video && <div>{video}</div>}
        {clickableSpan && <div>{clickableSpan}</div>}
        {subtitle && <div>{subtitle}</div>}
      </div>
    );
  };

  return (
    <div className="chat-container">
      {messages.map((msg, idx) => (
        <div
          key={idx}
          className={msg.role === "user" ? "chat-bubble left" : "chat-bubble right"}
        >
          {parseMessage(msg)}
        </div>
      ))}
    </div>
  );
};

export default ChatBox;
