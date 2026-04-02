// src/api.js
export const uploadVideo = async (file) => {
  const formData = new FormData();
  formData.append("file", file, file.webkitRelativePath); // 👈 preserve folder path
  return fetch("http://localhost:8000/upload/", {
    method: "POST",
    body: formData,
  });
};

export const sendChat = async (prompt, video) => {
  const form = new FormData();
  form.append("prompt", prompt);
  form.append("video", video);
  const res = await fetch("http://localhost:8000/chat/", {
    method: "POST",
    body: form,
  });
  return res.json();
};

export const deleteVideo = async (video) => {
  return fetch(`http://localhost:8000/delete/?video=${video}`, {
    method: "DELETE",
  });
};
