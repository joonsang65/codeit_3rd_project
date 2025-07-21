// src/api/textAPI.js

import axios from "axios";

const BASE_URL = "http://localhost:8000"; // FastAPI 주소
const TEXT_API = `${BASE_URL}/text`;

/**
 * 광고 문구 생성 API 호출
 * @param {Object} params - 요청 파라미터
 * @param {string} params.ad_type - 광고 유형 (blog, instagram, poster)
 * @param {string} params.user_prompt - 사용자 입력 설명
 * @param {string} params.session_id - 세션 ID
 */
export const generateAdText = async ({ ad_type, user_prompt, session_id }) => {
  const response = await axios.post(`${TEXT_API}/generate`, {
    ad_type,
    user_prompt,
    session_id,
  });

  return response.data;
  // return response.data.result;
};
