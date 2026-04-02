import React, { useEffect, useState } from "react";
import UploadSection from "./UploadSection";
import ChatBox from "./ChatBox";
import VideoPlayer from "./VideoPlayer";
import { sendChat } from "./api";
import "./styles.css";

const App = () => {
  const [videoName, setVideoName] = useState("");
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [clip, setClip] = useState(null);

  const timeToSec = (timeStr) => {
    if (!timeStr || typeof timeStr !== "string") return 0;
    const parts = timeStr.split(":").map(Number);
    return parts[0] * 3600 + parts[1] * 60 + parts[2];
  };

  const handleTimestampClick = (start, end) => {
    document.querySelector(".video-column")?.scrollIntoView({ behavior: "smooth" });
    setClip((prev) => ({
      ...prev,
      start: timeToSec(start),
      end: timeToSec(end),
    }));
  };

  useEffect(() => {
    window.handleTimestampClick = handleTimestampClick;
  }, []);

  const handleSend = async () => {
    const userMsg = { role: "user", text: prompt };
    const response = await sendChat(prompt, videoName);

    const botMsg = {
      role: "bot",
      text: response.answer,
      source: response.source,
    };

    setMessages((prev) => [...prev, userMsg, botMsg]);
    setPrompt("");

    if (response.source && response.source.length > 0) {
      const first = response.source[0];
      const cleanVideo = first.video;
      setVideoName(cleanVideo); // ✅ always set correct video name
      setClip({
        videoName: cleanVideo,
        start: timeToSec(first.start),
        end: timeToSec(first.end),
      });
    }
  };

  const handlePlayFull = () => {
    setClip({
      videoName,
      start: null,
      end: null
    });
  };

  return (
    <div className="app-container">
      <UploadSection setVideoName={setVideoName} />

      <div className="main-content">
        <div className="video-column">
          <h3>🎥 Video Player</h3>
          {videoName && (
            <VideoPlayer
              videoName={videoName}
              start={clip?.start}
              end={clip?.end}
            />
          )}
          {clip && (
            <button onClick={handlePlayFull} style={{ marginTop: "10px" }}>
              🔄 Play Full Video
            </button>
          )}
        </div>

        <div className="chat-column">
          <h3>Chat with Video</h3>
          <ChatBox messages={messages} />
          <div className="chat-input">
            <input
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask a question about the video..."
            />
            <button onClick={handleSend}>Send</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
