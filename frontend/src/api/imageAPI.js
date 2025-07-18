// src/api/imageAPI.js

import axios from "axios";

const BASE_URL = "http://localhost:8000"; // FastAPI 주소
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
      // "Content-Type": "multipart/form-data", // 자동 처리
      "session-id": sessionId,
      "category": category,
    },
    responseType: "blob",
  });
};

export const generateBackground = async ({ mode, sessionId, prompt, productBox }) => {
  return axios.post(
    `${IMAGE_API}/generate-background`,
    {
      mode,
      prompt,
      product_box: productBox,
    },
    {
      headers: {
        "session-id": sessionId,
        "Content-Type": "application/json",
      },
    }
  );
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
