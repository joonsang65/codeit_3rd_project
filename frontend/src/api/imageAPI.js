// src/api/imageAPI.js

import axios from "axios";

const BASE_URL = "http://localhost:8000"; // FastAPI 주소 (change this to GCP external IP)
const IMAGE_API = `${BASE_URL}/image`;

export const initSession = async (sessionId) => {
  return axios.post(`${IMAGE_API}/init-session`, null, {
    headers: { "session-id": sessionId },  // 일관성 맞춤
  });
};

export const preprocessImage = async (file, sessionId, category) => {
  const formData = new FormData();
  formData.append("file", file);

  return axios.post(`${IMAGE_API}/preprocess`, formData, {
    headers: {
      "session-id": sessionId,
      "category": category,
      // "Content-Type": "multipart/form-data", // 자동 처리
    },
    responseType: "blob",
  });
};

export const generateBackground = async (mode, title, description, sessionId) => {
  const formData = new FormData();
  formData.append("mode", mode);
  formData.append("title", title);
  formData.append("description", description);

  return axios.post(`${IMAGE_API}/generate-background`, formData, {
    headers: { "session-id": sessionId },
    // responseType: 'blob', // 백엔드 응답 타입에 따라 추가
  });
};

export async function getGeneratedBackground(sessionId) {
  const response = await axios.get(`${IMAGE_API}/generated-background`, {
    headers: {
      "session-id": sessionId,
    },
    responseType: "blob",
  });
  return URL.createObjectURL(response.data);
}
