import React, { useEffect, useRef } from "react";

const VideoPlayer = ({ videoName, start, end }) => {
  const videoRef = useRef();
  const clipEndedRef = useRef(false); // 🔁 Track if clip has ended

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const inClipMode = typeof start === "number" && typeof end === "number";

    const seekAndPlay = () => {
      clipEndedRef.current = false; // reset on new load
      if (inClipMode) {
        video.currentTime = start;
        video.play();
      } else {
        video.currentTime = 0;
        video.play();
      }
    };

    const stopAtEnd = () => {
      if (inClipMode && !clipEndedRef.current && video.currentTime >= end) {
        video.pause();
        clipEndedRef.current = true;
      }
    };

    video.addEventListener("loadedmetadata", seekAndPlay);
    video.addEventListener("timeupdate", stopAtEnd);

    return () => {
      video.removeEventListener("loadedmetadata", seekAndPlay);
      video.removeEventListener("timeupdate", stopAtEnd);
    };
  }, [videoName, start, end]);

  return (
    <div>
      <video
        ref={videoRef}
        width="100%"
        height="auto"
        controls
        key={videoName + "-" + start}
        src={`http://localhost:8000/uploaded_videos/${videoName}`}
      >
        Your browser does not support the video tag.
      </video>
    </div>
  );
};

export default VideoPlayer;
