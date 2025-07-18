// src/pages/Editor/steps/Step2Background.jsx

import React, { useState } from 'react';
import './Step2Background.css';
import { generateBackground, getGeneratedBackground } from '../../../api/imageAPI';

const Step2Background = ({
  bgPrompt,
  setBgPrompt,
  sessionId,
  imagePosition,
  imageSize,
  setBgImage,
}) => {
  const [localPrompt, setLocalPrompt] = useState(bgPrompt || '');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleGenerate = async () => {
    // 입력값 검증
    if (!localPrompt.trim()) {
      setMessage("❗ 프롬프트를 입력해 주세요.");
      return;
    }
    setBgPrompt(localPrompt);
    setLoading(true);
    setMessage('배경 이미지 생성 중...');

  const productBox = {
    x: parseFloat(imagePosition.x),
    y: parseFloat(imagePosition.y),
    width: parseFloat(imageSize.width),
    height: parseFloat(imageSize.height),
  };

  console.log("🟡 보낼 productBox 값:", productBox);
  console.log("🟡 sessionId:", sessionId);
  console.log("🟡 prompt:", localPrompt);
  
    try {
      await generateBackground({
        mode: 'inpaint',
        sessionId,
        prompt: localPrompt,
        productBox: productBox, 
      });
      const imageUrl = await getGeneratedBackground(sessionId); // 이미지 URL 얻기
      setBgImage(imageUrl); // 부모(Editor.jsx)로 전달
      setMessage('✅ 배경 이미지 생성 완료');
    } catch (err) {
      console.error(err);
      setMessage('❌ 배경 생성 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="step2-container">
      <label htmlFor="bgPrompt">배경 이미지 프롬프트 입력:</label>
      <input
        id="bgPrompt"
        type="text"
        value={localPrompt}
        onChange={(e) => setLocalPrompt(e.target.value)}
        placeholder="예: 여름 바닷가, 도시 야경"
      />
      <button onClick={handleGenerate} disabled={loading}>
        🖼️ 배경 이미지 AI 생성
      </button>
      {message && <p>{message}</p>}
    </div>
  );
};

export default Step2Background;