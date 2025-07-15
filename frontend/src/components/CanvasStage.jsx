// components/CanvasStage.jsx
import React, { useRef, useEffect, useState } from 'react';
import './CanvasStage.css';

const useWindowSize = () => {
  const [windowSize, setWindowSize] = useState({ width: window.innerWidth, height: window.innerHeight });
  useEffect(() => {
    const handleResize = () => setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  return windowSize;
};

const CanvasStage = ({
  uploadedImage,
  imagePosition,
  setImagePosition,
  imageSize,
  setImageSize,
  bgImage,
  textImage,
  platform,
  isEditable = true,
}) => {
  const canvasRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [resizing, setResizing] = useState(false);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const windowSize = useWindowSize();

  const HANDLE_SIZE = 12;

  const getCanvasSize = (platform) => {
    switch (platform) {
      case 'instagram':
        return { width: 1080, height: 1080 };
      case 'poster':
        return { width: 794, height: 1123 };
      case 'blog':
      default:
        return { width: 1200, height: 700 };
    }
  };

  const { width: defaultWidth, height: defaultHeight } = getCanvasSize(platform);
  const canvasWidth = Math.min(defaultWidth, windowSize.width * 0.9);
  const canvasHeight = Math.min(defaultHeight, windowSize.height * 0.7);

  useEffect(() => {
    const canvas = canvasRef.current;
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const loadImage = (src) => {
      return new Promise((resolve) => {
        if (!src) resolve(null);
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => resolve(null);
        img.src = src;
      });
    };

    Promise.all([
      loadImage(bgImage),
      loadImage(uploadedImage),
      loadImage(textImage),
    ]).then(([bgImg, uploadedImg, textImg]) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (bgImg) ctx.drawImage(bgImg, 0, 0, canvas.width, canvasHeight);
      if (uploadedImg) {
        ctx.drawImage(uploadedImg, imagePosition.x, imagePosition.y, imageSize.width, imageSize.height);

        if (isEditable) {
          // 점선 테두리
          ctx.strokeStyle = '#5a7fff';
          ctx.lineWidth = 2;
          ctx.setLineDash([6, 4]);
          ctx.strokeRect(imagePosition.x, imagePosition.y, imageSize.width, imageSize.height);
          ctx.setLineDash([]);

          // 핸들 위치 배열
          const handlePositions = [
            { x: imagePosition.x, y: imagePosition.y }, // 좌상
            { x: imagePosition.x + imageSize.width, y: imagePosition.y }, // 우상
            { x: imagePosition.x, y: imagePosition.y + imageSize.height }, // 좌하
            { x: imagePosition.x + imageSize.width, y: imagePosition.y + imageSize.height }, // 우하
          ];

          // 핸들 렌더링
          ctx.fillStyle = '#5a7fff';
          handlePositions.forEach(pos => {
            ctx.fillRect(
              pos.x - HANDLE_SIZE / 2,
              pos.y - HANDLE_SIZE / 2,
              HANDLE_SIZE,
              HANDLE_SIZE
            );
          });
        }
      }

      if (textImg) {
        ctx.drawImage(textImg, 100, 500, 600, 100);
      }
    });
  }, [uploadedImage, imagePosition, imageSize, bgImage, textImage, canvasWidth, canvasHeight, isEditable]);

  const getRelativePosition = (e, isTouch = false) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const scaleX = canvasRef.current.width / rect.width;
    const scaleY = canvasRef.current.height / rect.height;

    const clientX = isTouch ? e.touches[0].clientX : e.clientX;
    const clientY = isTouch ? e.touches[0].clientY : e.clientY;

    const x = (clientX - rect.left) * scaleX;
    const y = (clientY - rect.top) * scaleY;

    return { x, y };
  };

  const isInResizeHandle = (x, y) => {
    const handleCenters = [
      { x: imagePosition.x, y: imagePosition.y },
      { x: imagePosition.x + imageSize.width, y: imagePosition.y },
      { x: imagePosition.x, y: imagePosition.y + imageSize.height },
      { x: imagePosition.x + imageSize.width, y: imagePosition.y + imageSize.height },
    ];

    return handleCenters.some(center => (
      x >= center.x - HANDLE_SIZE / 2 &&
      x <= center.x + HANDLE_SIZE / 2 &&
      y >= center.y - HANDLE_SIZE / 2 &&
      y <= center.y + HANDLE_SIZE / 2
    ));
  };

  const isInImage = (x, y) => {
    return (
      x >= imagePosition.x &&
      x <= imagePosition.x + imageSize.width &&
      y >= imagePosition.y &&
      y <= imagePosition.y + imageSize.height
    );
  };

  const handleMouseDown = (e) => {
    if (!isEditable) return;
    const { x, y } = getRelativePosition(e);
    if (isInResizeHandle(x, y)) {
      setResizing(true);
    } else if (isInImage(x, y)) {
      setDragging(true);
      setOffset({ x: x - imagePosition.x, y: y - imagePosition.y });
    }
  };

  const handleMouseMove = (e) => {
    if (!isEditable) return;
    const { x, y } = getRelativePosition(e);
    if (dragging) {
      setImagePosition({
        x: Math.max(0, Math.min(x - offset.x, canvasRef.current.width - imageSize.width)),
        y: Math.max(0, Math.min(y - offset.y, canvasRef.current.height - imageSize.height)),
      });
    } else if (resizing) {
      setImageSize({
        width: Math.max(50, Math.min(x - imagePosition.x, canvasRef.current.width - imagePosition.x)),
        height: Math.max(50, Math.min(y - imagePosition.y, canvasRef.current.height - imagePosition.y)),
      });
    }
  };

  const handleMouseUp = () => {
    setDragging(false);
    setResizing(false);
  };

  return (
    <div className="canvas-container" style={{ width: canvasWidth, height: canvasHeight }}>
      <canvas
        ref={canvasRef}
        width={canvasWidth}
        height={canvasHeight}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        className="canvas"
        style={{
          cursor: isEditable ? (resizing ? 'nwse-resize' : dragging ? 'grabbing' : 'default') : 'default',
          display: 'block',
          width: '100%',
          height: '100%',
        }}
        aria-label="광고 이미지 편집 캔버스"
      />
    </div>
  );
};

export default CanvasStage;
