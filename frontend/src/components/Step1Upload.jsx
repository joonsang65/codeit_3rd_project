// src/components/Step1Upload.jsx
import React, { useRef } from 'react';
import { Rnd } from 'react-rnd';
import './StepStyles.css';

const Step1Upload = ({
  uploadedImage,
  setUploadedImage,
  imagePosition,
  setImagePosition,
  imageSize,
  setImageSize,
}) => {
  const inputRef = useRef();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setUploadedImage(imageUrl);
      setImagePosition({ x: 100, y: 100 });
      setImageSize({ width: 300, height: 300 });
    }
  };

  return (
    <>
      <div className="floating-card">
        <h3>상품 이미지 업로드</h3>
        <input
          type="file"
          accept="image/*"
          ref={inputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <button onClick={() => inputRef.current.click()} className="upload-btn">
          📤 업로드
        </button>
      </div>

      <div className="canvas-area">
        <div className="canvas-wrapper">
          {uploadedImage && (
            <Rnd
              bounds="parent"
              size={imageSize}
              position={imagePosition}
              onDragStop={(e, d) => setImagePosition({ x: d.x, y: d.y })}
              onResizeStop={(e, direction, ref, delta, position) => {
                setImageSize({
                  width: parseInt(ref.style.width),
                  height: parseInt(ref.style.height),
                });
                setImagePosition(position);
              }}
              enableResizing={{
                top: true,
                right: true,
                bottom: true,
                left: true,
                topRight: true,
                bottomRight: true,
                bottomLeft: true,
                topLeft: true,
              }}
              dragGrid={[1, 1]}
              resizeGrid={[1, 1]}
              // 드래그 홀드 유지
            >
              <img
                src={uploadedImage}
                alt="상품 이미지"
                style={{ width: '100%', height: '100%', objectFit: 'contain', userSelect: 'none' }}
                draggable={false}
              />
            </Rnd>
          )}
        </div>
      </div>
    </>
  );
};

export default Step1Upload;
