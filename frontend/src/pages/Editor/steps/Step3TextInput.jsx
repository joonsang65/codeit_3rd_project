// src/pages/Editor/steps/Step3TextInput.jsx
import React, { useState } from 'react';
import './Step3TextInput.css';

const Step3TextInput = ({ productInfo, setProductInfo, adText, setAdText, sessionId, platform }) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleGenerateText = async () => {
    if (!productInfo) {
      setMessage('❌ 상품 세부 정보를 입력해주세요.');
      return;
    }

    setLoading(true);
    setMessage('광고 문구 생성 중...');

    try {
      const response = await fetch('/text/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ad_type: platform, // blog, instagram, poster
          model_type: 'mini', // 기본값으로 mini 사용
          user_prompt: productInfo,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error('API 호출 실패');
      }

      const data = await response.json();
      setAdText(data.result); // 생성된 문구를 adText에 설정
      setMessage('✅ 광고 문구 생성 완료');
    } catch (err) {
      console.error(err);
      setMessage(`❌ 광고 문구 생성 실패: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="step3-container">
      <label htmlFor="productInfo">상품 세부 정보 입력:</label>
      <textarea
        id="productInfo"
        value={productInfo}
        onChange={(e) => setProductInfo(e.target.value)}
        placeholder="상품 이름, 특징, 가격 등 (예: '수제 양초, 100% 천연 왁스, 20,000원')"
        aria-label="상품 세부 정보 입력"
      />

      <button onClick={handleGenerateText} disabled={loading || !productInfo}>
        🖋️ AI로 광고 문구 생성
      </button>

      <label htmlFor="adText">광고 문구:</label>
      <textarea
        id="adText"
        value={adText}
        onChange={(e) => setAdText(e.target.value)}
        placeholder="AI가 생성한 문구가 여기에 표시되거나, 직접 입력하세요."
        aria-label="광고 문구 입력"
      />

      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default Step3TextInput;