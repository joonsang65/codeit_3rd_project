import React, { useRef } from 'react';
import { Rnd } from 'react-rnd';
import './Step1Upload.css';

const Step1Upload = ({
  uploadedImage,
  setUploadedImage,
  imageSize,
  setImageSize,
  imagePosition,
  setImagePosition,
}) => {
  const inputRef = useRef();

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setUploadedImage(imageUrl);
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
        <button className="upload-button" onClick={() => inputRef.current.click()}>
          <span className="upload-icon">📤</span> 상품 이미지 업로드
        </button>
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
