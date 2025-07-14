// frontend/src/pages/Editor/steps/Step1Upload.jsx
import React, { useRef, useState } from 'react';
import { Rnd } from 'react-rnd';
import './Step1Upload.css';
import { preprocessImage } from '../../../api/imageAPI';

const Step1Upload = ({
  sessionId,
  uploadedImage,
  setUploadedImage,
  imageSize,
  setImageSize,
  imagePosition,
  setImagePosition,
}) => {

  // sessionId 확인 로그
  console.log('Session ID:', sessionId);
  
  const inputRef = useRef();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setUploadedImage(imageUrl);

      setLoading(true);
      setMessage('이미지 전처리 중...');
      try {
        await preprocessImage(file, sessionId);
        setMessage('✅ 이미지 전처리 완료');
      } catch (error) {
        console.error(error);
        setMessage('❌ 전처리 실패');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="step1-container">
      <div className="upload-controls">
        <input
          type="file"
          accept="image/*"
          ref={inputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <button className="upload-button" onClick={() => inputRef.current.click()} disabled={loading}>
          <span className="upload-icon">📤</span> 상품 이미지 업로드
        </button>
        {message && <p>{message}</p>}
      </div>

      <div className="canvas-area">
        <div className="canvas-wrapper">
          {uploadedImage && (
            <Rnd
              bounds="parent"
              size={imageSize}
              position={imagePosition}
              enableResizing={true}
              onDragStop={(e, d) => setImagePosition({ x: d.x, y: d.y })}
              onResizeStop={(e, direction, ref, delta, position) => {
                setImageSize({
                  width: parseInt(ref.style.width),
                  height: parseInt(ref.style.height),
                });
                setImagePosition(position);
              }}
            >
              <img
                src={uploadedImage}
                alt="상품 이미지"
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'contain',
                  border: '2px dashed #888',
                  borderRadius: '8px',
                }}
              />
            </Rnd>
          )}
        </div>
      </div>
    </div>
  );
};

export default Step1Upload;

