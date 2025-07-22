import React, { useState, useEffect } from 'react';
import './Step5FinalOutput.css';
import { useNavigate } from 'react-router-dom';
import ProgressOverlay from '../../../components/ProgressOverlay';

function Step5FinalOutput({
  generatedImageUrl,
  generatedAdCopy, // Add this new prop
  isLoading,
  onReset,
  onGenerateNew,
}) {
  const navigate = useNavigate();

  const handleDownload = () => {
    if (generatedImageUrl) {
      const link = document.createElement('a');
      link.href = generatedImageUrl;
      link.download = 'generated_ad.png'; // You can make this dynamic if needed
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleCopyText = () => {
    if (generatedAdCopy) {
      navigator.clipboard.writeText(generatedAdCopy)
        .then(() => {
          alert('광고 문구가 복사되었습니다!');
        })
        .catch(err => {
          console.error('텍스트 복사 실패:', err);
          alert('텍스트 복사에 실패했습니다.');
        });
    } else {
      alert('복사할 광고 문구가 없습니다.');
    }
  };

  return (
    <div className="step5-container">
      {isLoading && <ProgressOverlay />}
      <h2>최종 결과물</h2>
      <div className="image-display-area">
        {generatedImageUrl ? (
          <img src={generatedImageUrl} alt="Generated Ad" className="generated-image" />
        ) : (
          <p>이미지가 생성되지 않았습니다.</p>
        )}
      </div>
      <div className="button-group">
        <button onClick={handleDownload} className="download-button">
          이미지 다운로드
        </button>
        <button onClick={handleCopyText} className="copy-text-button">
          글 복사하기
        </button>
        <button onClick={onGenerateNew} className="generate-new-button">
          새로운 이미지 생성
        </button>
      </div>
    </div>
  );
}

export default Step5FinalOutput;
