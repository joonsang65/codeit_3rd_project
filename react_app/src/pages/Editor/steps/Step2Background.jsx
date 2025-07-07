// src/pages/Editor/steps/Step2Background.jsx
import React, { useState } from 'react';
import './Step2Background.css';

const Step2Background = ({ bgPrompt, setBgPrompt, onGenerateBackground }) => {
  const [localPrompt, setLocalPrompt] = useState(bgPrompt || '');

  const handleGenerate = () => {
    setBgPrompt(localPrompt);
    onGenerateBackground(localPrompt);
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
      <button onClick={handleGenerate}>🖼️ 배경 이미지 AI 생성</button>
    </div>
  );
};

export default Step2Background;
