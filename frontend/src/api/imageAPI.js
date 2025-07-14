import axios from "axios";

const BASE_URL = "http://localhost:8000"; // FastAPI 주소
const IMAGE_API = `${BASE_URL}/image`;

export const initSession = async (sessionId) => {
  return axios.post(`${IMAGE_API}/init-session`, null, {
    headers: { session_id: sessionId },
  });
};


export const preprocessImage = async (file, sessionId) => {
  const formData = new FormData();
  formData.append("file", file);

  return axios.post(`${IMAGE_API}/preprocess`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
      "session-id": sessionId,
    },
  });
};


export const generateBackground = async (mode, sessionId) => {
  const formData = new FormData();
  formData.append("mode", mode);

  return axios.post(`${IMAGE_API}/generate-background`, formData, {
    headers: { "session-id": sessionId },
  });
};


export async function getGeneratedBackground(sessionId) {
  const response = await axios.get('http://localhost:8000/image/generated-background', {
    headers: {
      'session-id': sessionId
    },
    responseType: 'blob'  // 이미지니까
  });
  return URL.createObjectURL(response.data);
}