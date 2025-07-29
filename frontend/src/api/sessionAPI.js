// src/api/sessionAPI.js
import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://34.135.93.123:8000";
const SESSION_API = `${BASE_URL}/sessions`;

export const initializeSession = async (sessionId, userId = null) => {
  const headers = { "session-id": sessionId };
  if (userId !== null) {
    headers["user-id"] = userId;
  }
  return axios.post(`${SESSION_API}/init`, null, { headers: headers });
};

export const getSessionData = async (sessionId) => {
  return axios.get(`${SESSION_API}/${sessionId}`);
};

export const updateSessionDataKey = async (sessionId, key, value) => {
  const dataToPatch = {};
  dataToPatch[key] = value;
  return axios.patch(`${SESSION_API}/${sessionId}/data`, dataToPatch);
};

export const updateSessionData = async (sessionId, dataToUpdate) => {
  return axios.patch(`${SESSION_API}/${sessionId}/data`, dataToUpdate);
};
