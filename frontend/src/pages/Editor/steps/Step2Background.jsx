import React, { useState } from 'react';
import './Step2Background.css';
import { generateBackground, getGeneratedBackground } from '../../../api/imageAPI';
import ProgressOverlay from '../../../components/ProgressOverlay';
import { getCanvasSize } from '../../../components/CanvasStage';

const Step2Background = ({
  bgPrompt,
  setBgPrompt,
  sessionId,
  imagePosition,
  imageSize,
  setBgImage,
  platform,
  canvas
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

    const sdCanvType = {
        instagram: { width: 512, height: 512 },
        poster: { width: 512, height: 768 },
        blog: { width: 768, height: 448 },
    };

    const renderedWidth = canvas?.canvasSize?.width;
    const renderedHeight = canvas?.canvasSize?.height;
    const designCanvas = getCanvasSize(platform);
    const targetSD = sdCanvType[platform];
    
    const scaleRenderToDesignX = designCanvas.width / (renderedWidth);
    const scaleRenderToDesignY = designCanvas.height / renderedHeight;

    const scaleDesignToSDX = targetSD.width / designCanvas.width;
    const scaleDesignToSDY = targetSD.height / designCanvas.height;

    const scaleX = scaleRenderToDesignX * scaleDesignToSDX;
    const scaleY = scaleRenderToDesignY * scaleDesignToSDY;

    const productBox = {
      canvas_type: platform,
      x: Math.round(imagePosition.x * scaleX),
      y: Math.round(imagePosition.y * scaleY),
      width: Math.round(imageSize.width * scaleX),
      height: Math.round(imageSize.height * scaleY),
    };

    console.log("🟡 선택된 플랫폼:", platform);
    console.log("🟡 반응형 캔버스 사이즈:", renderedWidth, renderedHeight);
    console.log("🟡 사용자 변경 x, y 포지션:", imagePosition.x, imagePosition.y);
    console.log("🟡 scaleX:", scaleX);
    console.log("🟡 scaleY:", scaleY);
    console.log("🟡 보낼 productBox 값:", productBox);
    console.log("🟡 sessionId:", sessionId);
    console.log("🟡 prompt:", localPrompt);
    
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
