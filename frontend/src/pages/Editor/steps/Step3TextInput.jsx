// src/pages/Editor/steps/Step3TextInput.jsx
import React, { useState } from 'react';
import './Step3TextInput.css';

const Step3TextInput = ({ productInfo, setProductInfo, adText, setAdText }) => {
  return (
    <div className="step3-container">
      <label>상품 세부 정보 입력:</label>
      <textarea
        value={productInfo}
        onChange={(e) => setProductInfo(e.target.value)}
        placeholder="상품 이름, 특징, 가격 등"
      />

      <label>광고 문구 입력:</label>
      <textarea
        value={adText}
        onChange={(e) => setAdText(e.target.value)}
        placeholder="광고에 들어갈 감성 문구나 설명을 작성하세요."
      />
    </div>
  );
};

export default Step3TextInput;
