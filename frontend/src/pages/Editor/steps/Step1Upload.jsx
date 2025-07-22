import React, { useRef, useState } from 'react';
import './Step1Upload.css';
import { preprocessImage } from '../../../api/imageAPI';
import ProgressOverlay from '../../../components/ProgressOverlay';

const Step1Upload = ({
  sessionId,
  uploadedImage,
  setUploadedImage,
}) => {
  const inputRef = useRef();
  const [loading, setLoading] = useState(false);
  const [showProgress, setShowProgress] = useState(false);
  const [category, setCategory] = useState('food');
  const DURATION = 1500;

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setShowProgress(true);

    try {
      const response = await preprocessImage(file, sessionId, category);
      const blob = response.data;
      const processedImageUrl = URL.createObjectURL(blob);
      setUploadedImage(processedImageUrl);
    } catch (error) {
      console.error('이미지 전처리 실패:', error);
    } finally {
      setShowProgress(false);
      setLoading(false);
    }
  };

  return (
    <div className="step1-container">
      {showProgress && <ProgressOverlay 
        duration={DURATION}
        customMessage="✂️ 상품 이미지를 깔끔하게 다듬고 있어요..."
 
      />
      }

      <div className="category-selector">
        <label htmlFor="category">카테고리 선택:</label>
        <select
          id="category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          disabled={loading}
        >
          <option value="food">음식 (food)</option>
          <option value="cosmetics">화장품 (cosmetics)</option>
          <option value="furniture">가구 (furniture)</option>
        </select>
      </div>

      <div className="upload-controls">
        <input
          type="file"
          accept="image/*"
          ref={inputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <button
          className="upload-button"
          onClick={() => inputRef.current.click()}
          disabled={loading}
        >
          상품 이미지 업로드
        </button>
      </div>
    </div>
  );
};

export default Step1Upload;
