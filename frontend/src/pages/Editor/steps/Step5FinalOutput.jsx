import React from 'react';
import './Step5FinalOutput.css';
import ProgressOverlay from '../../../components/ProgressOverlay';

function Step5FinalOutput({
  generatedImageUrl,
  generatedAdCopy,
  isLoading,
  onGenerateNew,
}) {
  const handleDownload = () => {
    if (generatedImageUrl) {
      const link = document.createElement('a');
      link.href = generatedImageUrl;
      link.download = 'generated_ad.png';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };
  
  const handleCopyText = (showAlert = true) => {
    if (!generatedAdCopy) {
      if (showAlert) alert('복사할 광고 문구가 없습니다.');
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(generatedAdCopy)
      .then(() => {
        if (showAlert) alert('광고 문구가 복사되었습니다!');
      })
      .catch(err => {
        console.error('Clipboard API write failed, falling back:', err);
        fallbackCopyTextToClipboard(generatedAdCopy, showAlert);
      });
    } else {
      console.warn('Clipboard API not available or context is insecure. Using fallback copy method.');
      fallbackCopyTextToClipboard(generatedAdCopy, showAlert);
    }
  };
  
  const fallbackCopyTextToClipboard = (text, showAlert) => {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    
    textArea.style.position = "fixed";
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.opacity = "0";
    textArea.style.pointerEvents = "none";
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
      const successful = document.execCommand('copy');
      if (successful) {
        if (showAlert) alert('광고 문구가 복사되었습니다!');
      } else {
        if (showAlert) alert('텍스트 복사에 실패했습니다.');
      }
    } catch (err) {
      console.error('Fallback copy failed:', err);
      if (showAlert) alert('텍스트 복사에 실패했습니다.');
    }
    document.body.removeChild(textArea);
  };

  const handleShare = (platform) => {
    if (!generatedImageUrl || !generatedAdCopy) {
      alert('공유할 이미지나 텍스트가 없습니다.');
      return;
    }

    handleDownload();
    handleCopyText(false);

    let url = '';
    let platformName = '';
    switch (platform) {
      case 'instagram':
        url = 'https://www.instagram.com/';
        platformName = '인스타그램';
        break;
      case 'twitter':
        url = 'https://twitter.com/';
        platformName = '트위터';
        break;
      case 'naver_blog':
        url = 'https://blog.naver.com/';
        platformName = '네이버 블로그';
        break;
      default:
        return;
    }

    window.open(url, '_blank');
    alert(`이미지 다운로드 및 광고 문구 복사가 완료되었습니다. 새로 열린 ${platformName} 탭에서 게시물을 올려주세요!`);
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
        <div className="button-row">
          <button onClick={() => handleShare('instagram')} className="instagram-share-button">
            인스타그램 공유
          </button>
          <button onClick={() => handleShare('twitter')} className="twitter-share-button">
            트위터 공유
          </button>
          <button onClick={() => handleShare('naver_blog')} className="naver-blog-share-button">
            블로그 공유
          </button>
        </div>
        <div className="button-row">
          <button onClick={handleDownload} className="download-button">
            이미지 다운로드
          </button>
          <button onClick={() => handleCopyText(true)} className="copy-text-button">
            글 복사하기
          </button>
          <button onClick={onGenerateNew} className="generate-new-button">
            새로운 이미지 생성
          </button>
        </div>
      </div>
    </div>
  );
}

export default Step5FinalOutput;
