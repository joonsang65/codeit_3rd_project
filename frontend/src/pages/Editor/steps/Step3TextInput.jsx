// src/pages/Editor/steps/Step3Textinput.jsx

import React, { useState } from 'react';
import { generateAdText } from "../../../api/textAPI";
import './Step3TextInput.css';
import ProgressOverlay from '../../../components/ProgressOverlay';

const Step3TextInput = ({ productInfo, setProductInfo, adText, setAdText, sessionId, platform }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [adTexts, setAdTexts] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showProgress, setShowProgress] = useState(false);
  const [isProcessDone, setIsProcessDone] = useState(false);
  const DURATION = platform === 'poster' ? 2000 : 4000;

  // rawResult는 2차원 배열 [ [number, string, number], ... ] 형태
  const parseGeneratedResult = (rawResult, chunkCount = 8) => {
    console.log("Raw result received:", rawResult);

    if (!Array.isArray(rawResult)) return [];

    const result = [];

    for (const entry of rawResult) {
      if (
        Array.isArray(entry) &&
        entry.length >= 2 &&
        typeof entry[1] === "string"
      ) {
        result.push(entry[1].trim());
        if (result.length >= chunkCount) break;
      }
    }

    return result;
  };

  const handleGenerateText = async () => {
    if (!productInfo.trim()) {
      setMessage('❌ 상품 세부 정보를 입력해주세요.');
      return;
    }

    setLoading(true);
    setShowProgress(true);
    setIsProcessDone(false);
    setMessage('광고 문구 생성 중...');

    try {
      const rawResult = await generateAdText({
        ad_type: platform,
        model_type: "mini",
        user_prompt: productInfo.trim(),
        session_id: sessionId,
      });

      const parsedTexts = parseGeneratedResult(rawResult, 8);

      if (parsedTexts.length === 0) {
        throw new Error("문구를 파싱할 수 없습니다.");
      }

      setAdTexts(parsedTexts);
      setCurrentIndex(0);
      setAdText(parsedTexts[0]);
      setMessage('✅ 광고 문구가 성공적으로 생성되었습니다!');
    } catch (err) {
      console.error('텍스트 생성 오류:', err);
      const errorMessage = err.response?.data?.detail || err.message || '알 수 없는 오류';
      setMessage(`❌ 오류: ${errorMessage}`);
    } finally {
      setIsProcessDone(true);
      setTimeout(() => setShowProgress(false), 300);
      setLoading(false);
    }
  };

  const handleTextChange = (e) => {
    const newText = e.target.value;
    const updatedTexts = [...adTexts];
    updatedTexts[currentIndex] = newText;
    setAdTexts(updatedTexts);
    setAdText(newText);
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      const newIndex = currentIndex - 1;
      setCurrentIndex(newIndex);
      // 안전하게 adTexts[newIndex]가 존재하는지 확인 후 setAdText
      if (adTexts[newIndex]) {
        setAdText(adTexts[newIndex]);
      }
    }
  };

  const handleNext = () => {
    if (currentIndex < adTexts.length - 1) {
      const newIndex = currentIndex + 1;
      setCurrentIndex(newIndex);
      if (adTexts[newIndex]) {
        setAdText(adTexts[newIndex]);
      }
    }
  };

  return (
    <div className="step3-container">
      {showProgress && (
        <ProgressOverlay
          duration={DURATION}
          processDone={isProcessDone}
          customMessage= "💡 브랜드에 딱 맞는 문구를 신중하게 생성 중입니다..."
        />
      )}
      <h2>광고 문구 생성</h2>

      <label htmlFor="productInfo">상품의 세부 정보를 입력해주세요 !</label>
      <textarea
        id="productInfo"
        value={productInfo}
        onChange={(e) => setProductInfo(e.target.value)}
        placeholder="예: 수제 양초, 100% 천연 왁스, 부드러운 라벤더 향, 20,000원"
        aria-label="상품의 세부 정보를 입력해주세요"
        rows="4"
        disabled={loading}
      />

      <button
        onClick={handleGenerateText}
        disabled={loading || !productInfo.trim()}
        className={loading || !productInfo.trim() ? 'disabled' : ''}
      >
        {loading ? '생성 중...' : '🖋️ AI로 광고 문구 생성'}
      </button>

      <label htmlFor="adText">
        생성된 광고 문구 ({adTexts.length > 0 ? currentIndex + 1 : 0} / {adTexts.length})
      </label>
      <textarea
        id="adText"
        value={adText}
        onChange={handleTextChange}
        placeholder="AI가 생성한 문구가 여기에 표시됩니다. 필요하면 직접 수정 가능."
        aria-label="광고 문구 출력"
        rows="4"
        disabled={loading}
      />

      <div className="nav-buttons">
        <button onClick={handlePrev} disabled={currentIndex === 0 || loading}>
          ◀ 이전
        </button>
        <button onClick={handleNext} disabled={currentIndex >= adTexts.length - 1 || loading}>
          다음 ▶
        </button>
      </div>

      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default Step3TextInput;
