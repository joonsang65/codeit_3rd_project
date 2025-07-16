// src/api/sessionAPI.js
import axios from "axios";

const BASE_URL = "http://localhost:8000";
const CACHE_API = `${BASE_URL}/cache`;

export const saveAdTypeToSession = async (adType, sessionId) => {
  return axios.post(`${CACHE_API}/update`, {
    session_id: sessionId,
    key: "ad_type",
    value: adType,
  });
};

export const initSession = async (sessionId) => {
  return axios.post(`${CACHE_API}/init-session`, null, {
    headers: { "session-id": sessionId },
  });
};

export const getSessionKeys = async (sessionId) => {
  return axios.get(`${CACHE_API}/session/${sessionId}`);
};
