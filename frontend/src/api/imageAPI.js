// src/api/imageAPI.js

import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://34.135.93.123:8000"; 
const IMAGE_API = `${BASE_URL}/image`; 

export const preprocessImage = async (file, sessionId, category) => {
  const formData = new FormData();
  formData.append("file", file);

  return axios.post(`${IMAGE_API}/preprocess`, formData, {
    headers: {
      "session-id": sessionId,
      "category": category,
    },
    responseType: "blob",
  });
};

export const generateBackground = async ({ mode, sessionId, prompt, productBox = null }) => {
  console.log("DEBUG: prompt before API call:", prompt);
  return axios.post(
    `${IMAGE_API}/generate-background`,
    {
      mode: mode,
      prompt: prompt,
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

export const finalizeAdvertisement = async ({ sessionId, finalImageData }) => { 
    const response = await axios.post(
        `${IMAGE_API}/finalize-advertisement`,
        { 
            final_image_data: finalImageData
        },
        {
            headers: {
                "session-id": sessionId,
                "Content-Type": "application/json",
            },
        }
    );
    return response.data;
};