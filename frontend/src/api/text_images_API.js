// src/api/text_images_API.js

import axios from "axios";

const BASE_URL = "http://localhost:8000"; // FastAPI 서버 주소
const TEXTIMAGES_API = `${BASE_URL}/text-image`;

/**
 * 광고 문구 이미지를 생성하는 API 호출
 * @param {Object} params - 텍스트 이미지 생성 파라미터
 * @param {string} params.text - 광고 문구 텍스트
 * @param {string} params.font_name - 폰트 이름
 * @param {number} params.font_size - 폰트 크기
 * @param {string} params.text_colors - 텍스트 색상 (hex)
 * @param {string} params.stroke_colors - 외곽선 색상 (hex)
 * @param {number} params.stroke_width - 외곽선 두께
 * @param {boolean} params.word_based_colors - 단어별 색상 사용 여부
 * @param {number[]} params.background_size - 배경 크기 [width, height]
 * @param {number[]} params.background_color - 배경 색상 [r, g, b, a]
 * @param {string} params.output_format - 출력 형식 (예: "PNG")
 * @returns {Promise<string>} - base64로 인코딩된 이미지 (data:image/png;base64,...)
 */

export const generateTextImage = async (params) => {
  const response = await axios.post(`${TEXTIMAGES_API}/generate`, params);
  return response.data; // image_base64를 포함한 객체 반환
};