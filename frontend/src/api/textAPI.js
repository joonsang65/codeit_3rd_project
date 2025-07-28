// src/api/textAPI.js

import axios from "axios";

const BASE_URL = "http://34.135.93.123:8000";
//const BASE_URL = "http://localhost:8000"; // FastAPI 주소
const TEXT_API = `${BASE_URL}/text`;
const ADS_API = `${BASE_URL}/advertisements`;

/**
 * 광고 문구 생성 API 호출
 * @param {Object} params - 요청 파라미터
 * @param {string} params.ad_type - 광고 유형 (blog, instagram, poster)
 * @param {string} params.model_type - 모델 종류 (mini, nano)
 * @param {string} params.user_prompt - 사용자 입력 설명
 * @param {string} params.session_id - 세션 ID
 */
export const generateAdText = async ({ ad_type, model_type, user_prompt, session_id }) => {
  const response = await axios.post(`${TEXT_API}/generate`, {
    ad_type,
    model_type,
    user_prompt,
    session_id,
  });

  return response.data.result;
};

/**
 * 생성된 광고 문구를 백엔드에 저장하는 API 호출
 * @param {number} adId - 관련 광고의 ID
 * @param {string} copyText - 저장할 광고 문구 내용
 * @param {string} adType - 광고 유형 (e.g., 'instagram', 'blog', 'poster')
 * @param {string} userPromptForGeneration - 광고 문구 생성에 사용된 사용자 프롬프트
 */
export const saveAdCopy = async (adId, copyText, adType, userPromptForGeneration) => {
    const payload = {
        copy_text: copyText,
        ad_type: adType,
        user_prompt_for_generation: userPromptForGeneration,
    };
    console.log("DEBUG (textAPI.js): Saving ad copy payload:", payload); 

    try {
        const response = await axios.post(`${ADS_API}/${adId}/copies`, payload, { 
            headers: {
                "Content-Type": "application/json",
            },
        });
        return response.data; // AdvertisementCopyRead 객체 반환
    } catch (error) {
        console.error("광고 문구 저장 오류:", error.response?.data?.detail || error.message);
        throw error;
    }
};
