// frontend/src/pages/Editor/steps/Step1Upload.jsx

import React, { useRef, useState } from 'react';
import './Step1Upload.css';
import { preprocessImage } from '../../../api/imageAPI';

const Step1Upload = ({
  sessionId,
  uploadedImage,
  setUploadedImage,
}) => {

  const inputRef = useRef();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [category, setCategory] = useState('food'); // 기본 카테고리 설정

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setLoading(true);
      setMessage(''); // 경고문 회피용
      // setMessage('이미지 전처리 중...');

      try {
        const response = await preprocessImage(file, sessionId, category);
        const blob = response.data;
        const processedImageUrl = URL.createObjectURL(blob);
        setUploadedImage(processedImageUrl);
        // setMessage('✅ 이미지 전처리 완료');
      } catch (error) {
        console.error(error);
        // setMessage('❌ 전처리 실패');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="step1-container">
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
        {message && <p>{message}</p>}
      </div>
    </div>
  );
};

export default Step1Upload;
