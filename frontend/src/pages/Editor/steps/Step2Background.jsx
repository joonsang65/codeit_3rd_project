// src/pages/Editor/steps/Step2Background.jsx
import React, { useState } from 'react';
import './Step2Background.css';
import { generateBackground, getGeneratedBackground } from '../../../api/imageAPI';

const Step2Background = ({
  bgPrompt,
  setBgPrompt,
  sessionId,
  setBgImage,
  adTitle,
  setAdTitle,
  adDescription,
  setAdDescription,
}) => {
  const [localPrompt, setLocalPrompt] = useState(bgPrompt || '');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleGenerate = async () => {
    // 입력값 검증
    if (!adTitle.trim()) {
      setMessage('❌ 광고 제목을 입력해주세요.');
      return;
    }
    if (!adDescription.trim()) {
      setMessage('❌ 광고 설명을 입력해주세요.');
      return;
    }
    if (!localPrompt.trim()) {
      setMessage('❌ 배경 이미지 프롬프트를 입력해주세요.');
      return;
    }

    // 상태 업데이트
    setBgPrompt(localPrompt);
    setLoading(true);
    setMessage('배경 이미지 생성 중...');
    try {
      const mode = 'inpaint'; // 배경 생성 모드 설정
      const response = await generateBackground(mode, adTitle, adDescription, sessionId); // 배경 생성 요청
      console.log('배경 생성 응답:', response.data);
      const imageUrl = await getGeneratedBackground(sessionId); // 이미지 URL 얻기
      setBgImage(imageUrl); // 부모(Editor.jsx)로 전달
      setMessage('✅ 배경 이미지 생성 완료');
    } catch (err) {
      console.error('❌ 배경 생성 오류', err);
      const errorMessage = err.response?.data?.detail || '배경 이미지 생성 실패';
      setMessage(`❌ ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="step2-container">
      <div className="input-group">
        <label htmlFo="adTitle">광고 제목:</label>
        <input
          id="adTitle"
          type="text"
          value={adTitle}
          onChange={(e) => setAdTitle(e.target.value)}
          placeholder="예: 여름 세일, 신제품 출시"
          disabled={loading}
        />
      </div>

      <div className="input-group">
        <label htmlFor="adDescription">광고 설명:</label>
        <textarea
          id="adDescription"
          value={adDescription}
          onChange={(e) => setAdDescription(e.target.value)}
          placeholder="여기에 광고 설명을 입력하세요 (예: 제품 특징, 타겟 고객)"
          rows="3"
          disabled={loading}
        />
      </div>

      <div className="input-group">
        <label htmlFor="bgPrompt">배경 이미지 프롬프트:</label>
        <input
          id="bgPrompt"
          type="text"
          value={localPrompt}
          onChange={(e) => setLocalPrompt(e.target.value)}
          placeholder="예: 여름 바닷가, 도시 야경"
          disabled={loading}
        />
      </div>
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? '배경 이미지 생성 중...' : '🖼️ 배경 이미지 AI 생성'}
      </button>
      {message && <p className="status-message">{message}</p>}
    </div>
  );
};

export default Step2Background;