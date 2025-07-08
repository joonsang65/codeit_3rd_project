// src/pages/Editor/steps/Step4TextAdjust.jsx
import React from 'react';
import { Rnd } from 'react-rnd';
import './Step4TextAdjust.css';

const Step4TextAdjust = ({ adTextImage, position, setPosition, size, setSize }) => {
  if (!adTextImage) {
    return <p>광고 문구 이미지가 생성되어야 합니다.</p>;
  }

  return (
    <div className="step4-container">
      <div className="canvas-area">
        <Rnd
          bounds="parent"
          size={size}
          position={position}
          onDragStop={(e, d) => setPosition({ x: d.x, y: d.y })}
          onResizeStop={(e, direction, ref, delta, position) => {
            setSize({
              width: parseInt(ref.style.width),
              height: parseInt(ref.style.height),
            });
            setPosition(position);
          }}
        >
          <img
            src={adTextImage}
            alt="광고 문구 이미지"
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
        </Rnd>
      </div>
    </div>
  );
};

export default Step4TextAdjust;
