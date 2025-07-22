// components/CanvasStage.jsx
import React, { useRef, useEffect, useState, forwardRef, useImperativeHandle } from 'react';
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

const CanvasStage = forwardRef(({
  uploadedImage,
  imagePosition,
  setImagePosition,
  imageSize,
  setImageSize,
  bgImage,
  textImage,
  textImagePosition,
  setTextImagePosition,
  textImageSize,
  setTextImageSize,
  platform,
  isEditable = true,
  onImagesReady,
}, ref) => {
  const canvasRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [resizing, setResizing] = useState(false);
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  // 텍스트 이미지용 상태
  const [draggingText, setDraggingText] = useState(false);
  const [resizingText, setResizingText] = useState(false);
  const [offsetText, setOffsetText] = useState({ x: 0, y: 0 });

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

  useImperativeHandle(ref, () => ({
    getStage: () => canvasRef.current,
  }));

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
        ctx.drawImage(textImg, textImagePosition.x, textImagePosition.y, textImageSize.width, textImageSize.height);

        if (isEditable) {
          ctx.strokeStyle = '#f47c7c';
          ctx.lineWidth = 2;
          ctx.setLineDash([6, 4]);
          ctx.strokeRect(textImagePosition.x, textImagePosition.y, textImageSize.width, textImageSize.height);
          ctx.setLineDash([]);

          const textHandlePositions = [
            { x: textImagePosition.x, y: textImagePosition.y },
            { x: textImagePosition.x + textImageSize.width, y: textImagePosition.y },
            { x: textImagePosition.x, y: textImagePosition.y + textImageSize.height },
            { x: textImagePosition.x + textImageSize.width, y: textImagePosition.y + textImageSize.height },
          ];

          ctx.fillStyle = '#f47c7c';
          textHandlePositions.forEach(pos => {
            ctx.fillRect(
              pos.x - HANDLE_SIZE / 2,
              pos.y - HANDLE_SIZE / 2,
              HANDLE_SIZE,
              HANDLE_SIZE
            );
          });
        }
      }

      if (onImagesReady) {
        onImagesReady();
      }
    });
  }, [
    uploadedImage, imagePosition, imageSize,
    bgImage, textImage, textImagePosition, textImageSize,
    canvasWidth, canvasHeight, isEditable, onImagesReady,
  ]);

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

  const isInResizeHandle = (x, y, pos, size) => {
    const handleCenters = [
      { x: pos.x, y: pos.y },
      { x: pos.x + size.width, y: pos.y },
      { x: pos.x, y: pos.y + size.height },
      { x: pos.x + size.width, y: pos.y + size.height },
    ];
    return handleCenters.some(center =>
      x >= center.x - HANDLE_SIZE / 2 &&
      x <= center.x + HANDLE_SIZE / 2 &&
      y >= center.y - HANDLE_SIZE / 2 &&
      y <= center.y + HANDLE_SIZE / 2
    );
  };

  const isInBox = (x, y, pos, size) => {
    return (
      x >= pos.x &&
      x <= pos.x + size.width &&
      y >= pos.y &&
      y <= pos.y + size.height
    );
  };

  const handleMouseDown = (e) => {
    if (!isEditable) return;
    const { x, y } = getRelativePosition(e);

    if (isInResizeHandle(x, y, textImagePosition, textImageSize)) {
      setResizingText(true);
    } else if (isInBox(x, y, textImagePosition, textImageSize)) {
      setDraggingText(true);
      setOffsetText({ x: x - textImagePosition.x, y: y - textImagePosition.y });
    } else if (isInResizeHandle(x, y, imagePosition, imageSize)) {
      setResizing(true);
    } else if (isInBox(x, y, imagePosition, imageSize)) {
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
    } else if (draggingText) {
      setTextImagePosition({
        x: Math.max(0, Math.min(x - offsetText.x, canvasRef.current.width - textImageSize.width)),
        y: Math.max(0, Math.min(y - offsetText.y, canvasRef.current.height - textImageSize.height)),
      });
    } else if (resizingText) {
      setTextImageSize({
        width: Math.max(50, Math.min(x - textImagePosition.x, canvasRef.current.width - textImagePosition.x)),
        height: Math.max(50, Math.min(y - textImagePosition.y, canvasRef.current.height - textImagePosition.y)),
      });
    }
  };

  const handleMouseUp = () => {
    setDragging(false);
    setResizing(false);
    setDraggingText(false);
    setResizingText(false);
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
          cursor: isEditable
            ? (resizing || resizingText
                ? 'nwse-resize'
                : (dragging || draggingText ? 'grabbing' : 'default'))
            : 'default',
          display: 'block',
          width: '100%',
          height: '100%',
        }}
        aria-label="광고 이미지 편집 캔버스"
      />
    </div>
  );
});

export default CanvasStage;
