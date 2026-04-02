// src/UploadSection.jsx
import React, { useState, useEffect } from "react";

const UploadSection = ({ setVideoName }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState({});
  const [progressPercent, setProgressPercent] = useState({});

  const POLL_INTERVAL = 3000; // 3 seconds
  
  // ⏱ Polling transcription status for all files
  useEffect(() => {
    const interval = setInterval(() => {
      selectedFiles.forEach((file) => {
        const status = uploadStatus[file.name];
        if (status === "Transcribing...") {
          fetch(`http://localhost:8000/status/?video=${encodeURIComponent(file.name)}`)
            .then((res) => res.json())
            .then((data) => {
              if (data.status === "done") {
                setUploadStatus((prev) => ({
                  ...prev,
                  [file.name]: "✅ Done",
                }));
              }
            })
            .catch((err) => {
              console.error("❌ Status check failed:", err);
            });
        }
      });
    }, POLL_INTERVAL);

    return () => clearInterval(interval);
  }, [selectedFiles, uploadStatus]);

  const handleUpload = async () => {
    if (!selectedFiles.length) {
      alert("Please select video files first.");
      return;
    }

    for (const file of selectedFiles) {
      const formData = new FormData();
      formData.append("files", file);

      setUploadStatus((prev) => ({ ...prev, [file.name]: "Uploading..." }));

      try {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "http://localhost:8000/upload/");

        xhr.upload.onprogress = (e) => {
          const percent = Math.round((e.loaded * 100) / e.total);
          setProgressPercent((prev) => ({ ...prev, [file.name]: percent }));
        };

        xhr.onload = () => {
          if (xhr.status === 200) {
            setUploadStatus((prev) => ({ ...prev, [file.name]: "Transcribing..." }));
            setVideoName(file.name); // default first video for chat
          } else {
            setUploadStatus((prev) => ({ ...prev, [file.name]: "❌ Upload Failed" }));
          }
        };

        xhr.onerror = () => {
          setUploadStatus((prev) => ({ ...prev, [file.name]: "❌ Upload Error" }));
        };

        xhr.send(formData);
      } catch (err) {
        console.error("❌ Upload exception:", err);
        setUploadStatus((prev) => ({ ...prev, [file.name]: "❌ Failed" }));
      }
    }
  };

  return (
    <div>
      <input
        type="file"
        webkitdirectory=""
        directory=""
        multiple
        accept=".mp4"
        onChange={(e) => {
          const files = Array.from(e.target.files).filter((f) => f.name.endsWith(".mp4"));
          setSelectedFiles(files);
          setUploadStatus({});
          setProgressPercent({});
        }}
      />
      <button onClick={handleUpload}>Upload</button>
      


      {selectedFiles.length > 0 && (
        <div style={{ marginTop: "10px" }}>
          <h4>📦 File Upload Status</h4>
          <ul>
            {selectedFiles.map((file, index) => (
              <li key={index}>
                <strong>{file.name}</strong>
                <br />
                <progress
                  value={progressPercent[file.name] || 0}
                  max="100"
                  style={{ width: "200px", marginRight: "10px" }}
                />
                <span>{uploadStatus[file.name] || "Not uploaded"}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default UploadSection;
