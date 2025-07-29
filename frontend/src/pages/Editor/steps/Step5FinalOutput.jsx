import React, { useState, useEffect } from 'react';
import './Step5FinalOutput.css';
import ProgressOverlay from '../../../components/ProgressOverlay';
import { finalizeAdvertisement } from '../../../api/imageAPI';

function Step5FinalOutput({
  generatedImageUrl,
  generatedAdCopy,
  isLoading,
  onGenerateNew,
  sessionId,
  advertisementId,
}) {
  const [isSavingFinal, setIsSavingFinal] = useState(false);
  const [hasSavedSuccessfully, setHasSavedSuccessfully] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  useEffect(() => {
    const autoSaveAdvertisement = async () => {
      const conditionMet = generatedImageUrl && generatedAdCopy && sessionId && !isSavingFinal && !hasSavedSuccessfully;
      console.log("[Step5 useEffect] Auto-save condition check:", conditionMet);

      if (conditionMet) {
        console.log("[Step5] ATTEMPTING to call finalizeAdvertisement with sessionId:", sessionId, "and image data length:", generatedImageUrl.length);
        setIsSavingFinal(true);
        setSaveMessage('최종 광고 이미지를 저장 중...');
        try {
          const response = await finalizeAdvertisement({
            sessionId: sessionId,
            finalImageData: generatedImageUrl 
          });
          console.log("[Step5] finalizeAdvertisement SUCCESS:", response.data);
          setHasSavedSuccessfully(true);
          setSaveMessage('✅ 최종 광고 이미지 저장 완료!');
        } catch (error) {
          console.error('[Step5] finalizeAdvertisement FAILED:', error.response?.data?.detail || error.message || error);
          setSaveMessage(`❌ 최종 광고 이미지 저장 실패: ${error.response?.data?.detail || error.message}`);
          setHasSavedSuccessfully(false);
        } finally {
          setIsSavingFinal(false);
          setTimeout(() => {
              if (hasSavedSuccessfully) {
                  setSaveMessage('');
              }
          }, 3000); 
        }
      } else {
        console.log("[Step5 useEffect] Auto-save condition NOT met. Skipping API call.");
      }
    };
    autoSaveAdvertisement();
  }, [generatedImageUrl, generatedAdCopy, sessionId, isSavingFinal, hasSavedSuccessfully]);

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
  
  const handleSaveFinalImage = async () => {
    if (isSavingFinal || hasSavedSuccessfully) {
      alert("이미 저장 중이거나 저장이 완료되었습니다.");
      return;
    }
    if (!generatedImageUrl || !generatedAdCopy || !sessionId || !advertisementId) {
      alert("저장할 이미지 또는 정보가 부족합니다.");
      return;
    }
    
    setIsSavingFinal(true);
    setSaveMessage('최종 광고 이미지를 저장 중...');
    try {
      const response = await finalizeAdvertisement({
        sessionId: sessionId,
        finalImageData: generatedImageUrl,
      });
      console.log("[Step5] Explicit save finalizeAdvertisement SUCCESS:", response.data);
      setHasSavedSuccessfully(true);
      setSaveMessage('✅ 최종 광고 이미지 저장 완료!');
    } catch (error) {
      console.error('[Step5] Explicit save finalizeAdvertisement FAILED:', error.response?.data?.detail || error.message || error);
      setSaveMessage(`❌ 최종 광고 이미지 저장 실패: ${error.response?.data?.detail || error.message}`);
      setHasSavedSuccessfully(false);
    } finally {
      setIsSavingFinal(false);
      setTimeout(() => setSaveMessage(''), 3000);
    }
  };

  return (
    <div className="step5-container">
      {(isLoading || isSavingFinal) && <ProgressOverlay customMessage={saveMessage || "최종 이미지를 준비 중입니다..."}/>}
      <h2>최종 결과물</h2>
      <div className="image-display-area">
        {generatedImageUrl ? (
          <img src={generatedImageUrl} alt="Generated Ad" className="generated-image" />
        ) : (
          <p>이미지가 생성되지 않았습니다.</p>
        )}
      </div>
      <div className="ad-copy-display-area">
          <h3>광고 문구:</h3>
          <p>{generatedAdCopy}</p>
          {saveMessage && <p className={`save-status-message ${saveMessage.includes('✅') ? 'success' : saveMessage.includes('❌') ? 'error' : ''}`}>{saveMessage}</p>}
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
          <button 
            onClick={handleSaveFinalImage} 
            className="save-final-button"
            disabled={isSavingFinal || hasSavedSuccessfully || isLoading || !generatedImageUrl}
          >
            {isSavingFinal ? '저장 중...' : hasSavedSuccessfully ? '✅ 저장 완료' : '최종 광고 저장'}
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
