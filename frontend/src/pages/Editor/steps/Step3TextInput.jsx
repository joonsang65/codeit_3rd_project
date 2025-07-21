// src/pages/Editor/steps/Step3TextInput.jsx
import React, { useState } from 'react';
import { generateAdText } from "../../../api/textAPI";
import './Step3TextInput.css';

const Step3TextInput = ({ productInfo, setProductInfo, adText, setAdText, sessionId, platform }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleGenerateText = async () => {
    if (!productInfo.trim()) {
      setMessage('❌ 상품 세부 정보를 입력해주세요.');
      return;
    }

    setLoading(true);
    setMessage('광고 문구 생성 중...');
    
    console.log("✅ 광고 문구 요청 데이터:", {
      ad_type: platform,
      user_prompt: productInfo.trim(),
      session_id: sessionId,
    });


    try {
      const result = await generateAdText({
        ad_type: platform,
        user_prompt: productInfo.trim(),
        session_id: sessionId,
      });

      setAdText(result);
      setMessage('✅ 광고 문구가 성공적으로 생성되었습니다!');
    } catch (err) {
      console.error('텍스트 생성 오류:', err);
      const errorMessage = err.response?.data?.detail || err.message || '알 수 없는 오류';
      setMessage(`❌ 오류: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="step3-container">
      <h2>광고 문구 생성</h2>
      <label htmlFor="productInfo">상품 세부 정보 입력:</label>
      <textarea
        id="productInfo"
        value={productInfo}
        onChange={(e) => setProductInfo(e.target.value)}
        placeholder="예: 수제 양초, 100% 천연 왁스, 부드러운 라벤더 향, 20,000원"
        aria-label="상품 세부 정보 입력"
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

      <label htmlFor="adText">생성된 광고 문구:</label>
      <textarea
        id="adText"
        value={adText}
        onChange={(e) => setAdText(e.target.value)}
        placeholder="AI가 생성한 문구가 여기에 표시됩니다. 필요하면 직접 수정 가능."
        aria-label="광고 문구 출력"
        rows="4"
        disabled={loading}
      />

      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default Step3TextInput;