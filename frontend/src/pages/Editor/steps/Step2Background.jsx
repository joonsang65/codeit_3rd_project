import React, { useState } from 'react';
import './Step2Background.css';
import { generateBackground, getGeneratedBackground } from '../../../api/imageAPI';
import ProgressOverlay from '../../../components/ProgressOverlay';

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
  const [showProgress, setShowProgress] = useState(false);
  const DURATION = 25000;

  const handleGenerate = async () => {
    if (!localPrompt.trim()) {
      setMessage('❗ 프롬프트를 입력해 주세요.');
      return;
    }

    setBgPrompt(localPrompt);
    setMessage('');
    setLoading(true);
    setShowProgress(true);

    const productBox = {
      x: parseFloat(imagePosition.x),
      y: parseFloat(imagePosition.y),
      width: parseFloat(imageSize.width),
      height: parseFloat(imageSize.height),
    };

    try {
      await generateBackground({
        mode: 'inpaint',
        sessionId,
        prompt: localPrompt,
        productBox,
      });

      const imageUrl = await getGeneratedBackground(sessionId);
      setBgImage(imageUrl);
      setMessage('✅ 배경 이미지 생성 완료');
    } catch (err) {
      console.error(err);
      setMessage('❌ 배경 생성 실패');
    } finally {
      setShowProgress(false); // ✅ 이미지 준비 완료와 동시에 바 제거
      setLoading(false);
    }
  };

  return (
    <div className="step2-container">
      {showProgress && <ProgressOverlay 
        duration={DURATION} 
        customMessage="🌄 배경 이미지를 자연스럽게 만들어내고 있어요..."

      />
      }

      <label htmlFor="bgPrompt">어떤 느낌의 배경 이미지를 만들어 볼까요 ?</label>
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
