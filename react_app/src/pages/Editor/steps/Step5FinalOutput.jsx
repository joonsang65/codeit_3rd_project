// src/pages/Editor/steps/Step5FinalOutput.jsx
import React from 'react';
import './Step5FinalOutput.css';

const Step5FinalOutput = ({ finalImageUrl }) => {
  if (!finalImageUrl) {
    return <p>최종 이미지가 생성되어야 합니다.</p>;
  }

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = finalImageUrl;
    link.download = 'final_ad_image.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="step5-container">
      <h3>최종 광고 이미지</h3>
      <img src={finalImageUrl} alt="최종 광고" className="final-image" />
      <button onClick={handleDownload}>💾 이미지 다운로드</button>
    </div>
  );
};

export default Step5FinalOutput;
