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

export const getCanvasSize = (platform) => {
    switch (platform) {
      case 'instagram':
        return { width: 1024, height: 1024 };
      case 'poster':
        return { width: 768, height: 1152 };
      case 'blog':
      default:
        return { width: 1152, height: 704 };
    }
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
  onResizeCanvas,
  isEditable = true,
  onDrawComplete,
  displayUploadedImage = true,
}, ref) => {
  const canvasRef = useRef(null);
  const [drawUIElements, setDrawUIElements] = useState(true); 

  useImperativeHandle(ref, () => ({
    getStage: () => {
      return canvasRef.current;
    },
    getCleanImageDataURL: () => {
      const canvas = canvasRef.current;
      if (!canvas) return null;
      
      setDrawUIElements(false);
      return new Promise(resolve => {
        setTimeout(() => {
          const dataURL = canvas.toDataURL('image/png');
          setDrawUIElements(true);
          resolve(dataURL);
        }, 50); 
      });
    }
  }));
  const [dragging, setDragging] = useState(false);
  const [resizing, setResizing] = useState(false);
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  // 텍스트 이미지용 상태
  const [draggingText, setDraggingText] = useState(false);
  const [resizingText, setResizingText] = useState(false);
  const [offsetText, setOffsetText] = useState({ x: 0, y: 0 });

  const windowSize = useWindowSize();

  const HANDLE_SIZE = 12;

  const { width: defaultWidth, height: defaultHeight } = getCanvasSize(platform);
  const canvasWidth = Math.min(defaultWidth, windowSize.width * 0.9);
  const canvasHeight = Math.min(defaultHeight, windowSize.height * 0.7);

  useEffect(() => {
    const canvas = canvasRef.current;
    const rect = canvasRef.current.getBoundingClientRect();
    onResizeCanvas?.({ width: rect.width, height: rect.height });

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

      if (uploadedImg && displayUploadedImage) {
        ctx.drawImage(uploadedImg, imagePosition.x, imagePosition.y, imageSize.width, imageSize.height);

        if (isEditable  && drawUIElements) {
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

        if (isEditable  && drawUIElements) {
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
      onDrawComplete?.();
    });
  }, [
    uploadedImage, imagePosition, imageSize,
    bgImage, textImage, textImagePosition, textImageSize,
    canvasWidth, canvasHeight, onResizeCanvas, isEditable,
    drawUIElements, displayUploadedImage
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
    if (!pos || !size) return false; // 추가된 null/undefined 체크
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
    if (!pos || !size) return false; // 추가된 null/undefined 체크
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

    // 텍스트 이미지 클릭 감지 (textImage가 존재할 때만)
    if (textImage && textImagePosition && textImageSize && isEditable) {
      if (isInResizeHandle(x, y, textImagePosition, textImageSize)) {
        setResizingText(true);
        return; // 텍스트 이미지 핸들을 잡았으면 다른 객체 확인 불필요
      } else if (isInBox(x, y, textImagePosition, textImageSize)) {
        setDraggingText(true);
        setOffsetText({ x: x - textImagePosition.x, y: y - textImagePosition.y });
        return; // 텍스트 이미지를 잡았으면 다른 객체 확인 불필요
      }
    }

    // 업로드된 이미지 클릭 감지 (uploadedImage가 존재할 때만)
    if (uploadedImage && imagePosition && imageSize && isEditable && displayUploadedImage) {
      if (isInResizeHandle(x, y, imagePosition, imageSize)) {
        setResizing(true);
      } else if (isInBox(x, y, imagePosition, imageSize)) {
        setDragging(true);
        setOffset({ x: x - imagePosition.x, y: y - imagePosition.y });
      }
    }
  };

  const handleMouseMove = (e) => {
    if (!isEditable) return;
    const { x, y } = getRelativePosition(e);

    if (dragging && displayUploadedImage) {
      setImagePosition({
        x: Math.max(0, Math.min(x - offset.x, canvasRef.current.width - imageSize.width)),
        y: Math.max(0, Math.min(y - offset.y, canvasRef.current.height - imageSize.height)),
      });
    } else if (resizing && displayUploadedImage) {
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
        onMouseDown={isEditable ? handleMouseDown : null}
        onMouseMove={isEditable ? handleMouseMove : null}
        onMouseUp={isEditable ? handleMouseUp : null}
        onMouseLeave={isEditable ? handleMouseUp : null}
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

/*
import React, { useRef, useEffect, useState, forwardRef, useImperativeHandle } from 'react';
import './CanvasStage.css';

// Custom hook to get window size for responsive canvas sizing
const useWindowSize = () => {
  const [windowSize, setWindowSize] = useState({ width: window.innerWidth, height: window.innerHeight });
  useEffect(() => {
    const handleResize = () => setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  return windowSize;
};

// Utility function to determine canvas dimensions based on platform
export const getCanvasSize = (platform) => {
  switch (platform) {
    case 'instagram':
      return { width: 1024, height: 1024 }; // Standard Instagram square ad
    case 'poster':
      return { width: 768, height: 1152 }; // Common poster aspect ratio (2:3)
    case 'blog':
    default:
      return { width: 1152, height: 704 }; // Common blog banner aspect ratio (16:9 like)
  }
};

const CanvasStage = forwardRef(({
  uploadedImage, // URL of the uploaded product image
  imagePosition, // {x, y} position of the product image
  setImagePosition, // Setter for product image position
  imageSize, // {width, height} size of the product image
  setImageSize, // Setter for product image size
  bgImage, // URL of the generated background image
  textImage, // URL of the generated text image
  textImagePosition, // {x, y} position of the text image
  setTextImagePosition, // Setter for text image position
  textImageSize, // {width, height} size of the text image
  setTextImageSize, // Setter for text image size
  platform, // The target platform (e.g., 'instagram', 'poster', 'blog')
  onResizeCanvas, // Callback when canvas dimensions are determined
  isEditable = true, // Boolean to enable/disable drag & resize interactions
  onImagesReady, // Callback when all images (bg, uploaded, text) are loaded
}, ref) => {
  const canvasRef = useRef(null);
  const [dragging, setDragging] = useState(false); // State for dragging product image
  const [resizing, setResizing] = useState(false); // State for resizing product image
  const [offset, setOffset] = useState({ x: 0, y: 0 }); // Offset for product image dragging

  // States for text image manipulation
  const [draggingText, setDraggingText] = useState(false); // State for dragging text image
  const [resizingText, setResizingText] = useState(false); // State for resizing text image
  const [offsetText, setOffsetText] = useState({ x: 0, y: 0 }); // Offset for text image dragging

  const windowSize = useWindowSize(); // Get current window dimensions

  const HANDLE_SIZE = 12; // Size of the resize handles

  // Determine canvas size based on platform, constrained by window size
  const { width: defaultWidth, height: defaultHeight } = getCanvasSize(platform);
  const canvasWidth = Math.min(defaultWidth, windowSize.width * 0.9);
  const canvasHeight = Math.min(defaultHeight, windowSize.height * 0.7);

  // Expose the canvas DOM element to parent components via ref
  useImperativeHandle(ref, () => ({
    getStage: () => canvasRef.current,
  }));

  // Effect hook for drawing on the canvas whenever dependencies change
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return; // Ensure canvas exists

    const rect = canvas.getBoundingClientRect();
    // Callback to inform parent about the actual rendered canvas size
    onResizeCanvas?.({ width: rect.width, height: rect.height });

    // Set internal canvas resolution (important for clear rendering)
    canvas.width = canvasWidth;
    canvas.height = canvasHeight;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear canvas before redrawing

    // Helper function to load images
    const loadImage = (src) => {
      return new Promise((resolve) => {
        if (!src) {
          resolve(null); // Resolve with null if no source is provided
          return;
        }
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => {
          console.error(`Failed to load image: ${src}`);
          resolve(null); // Resolve with null on error
        };
        img.src = src;
      });
    };

    // Load all images concurrently
    Promise.all([
      loadImage(bgImage),
      loadImage(uploadedImage),
      loadImage(textImage),
    ]).then(([bgImg, uploadedImg, textImg]) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear again after potential initial draw

      // Draw background image (fills the entire canvas)
      if (bgImg) ctx.drawImage(bgImg, 0, 0, canvas.width, canvasHeight);

      // Draw uploaded product image
      if (uploadedImg) {
        ctx.drawImage(uploadedImg, imagePosition.x, imagePosition.y, imageSize.width, imageSize.height);

        if (isEditable) {
          // Draw dashed border for product image
          ctx.strokeStyle = '#5a7fff'; // Blue color
          ctx.lineWidth = 2;
          ctx.setLineDash([6, 4]); // Dashed line
          ctx.strokeRect(imagePosition.x, imagePosition.y, imageSize.width, imageSize.height);
          ctx.setLineDash([]); // Reset line dash

          // Define positions for resize handles
          const handlePositions = [
            { x: imagePosition.x, y: imagePosition.y }, // Top-left
            { x: imagePosition.x + imageSize.width, y: imagePosition.y }, // Top-right
            { x: imagePosition.x, y: imagePosition.y + imageSize.height }, // Bottom-left
            { x: imagePosition.x + imageSize.width, y: imagePosition.y + imageSize.height }, // Bottom-right
          ];

          // Render resize handles
          ctx.fillStyle = '#5a7fff'; // Blue color
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

      // Draw text image
      if (textImg) {
        ctx.drawImage(textImg, textImagePosition.x, textImagePosition.y, textImageSize.width, textImageSize.height);

        if (isEditable) {
          // Draw dashed border for text image
          ctx.strokeStyle = '#f47c7c'; // Reddish color
          ctx.lineWidth = 2;
          ctx.setLineDash([6, 4]);
          ctx.strokeRect(textImagePosition.x, textImagePosition.y, textImageSize.width, textImageSize.height);
          ctx.setLineDash([]);

          // Define positions for text image resize handles
          const textHandlePositions = [
            { x: textImagePosition.x, y: textImagePosition.y },
            { x: textImagePosition.x + textImageSize.width, y: textImagePosition.y },
            { x: textImagePosition.x, y: textImagePosition.y + textImageSize.height },
            { x: textImagePosition.x + textImageSize.width, y: textImagePosition.y + textImageSize.height },
          ];

          // Render text image resize handles
          ctx.fillStyle = '#f47c7c'; // Reddish color
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

      // Callback to inform parent that all images have been drawn
      if (onImagesReady) {
        onImagesReady();
      }
    });
  }, [
    uploadedImage, imagePosition, imageSize, // Product image dependencies
    bgImage, textImage, textImagePosition, textImageSize, // Background & text image dependencies
    onImagesReady, canvasWidth, canvasHeight, // Canvas/sizing dependencies
    onResizeCanvas, isEditable, // Interaction/utility dependencies
  ]);

  // Converts mouse/touch event coordinates to canvas-relative coordinates
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

  // Checks if coordinates are within a resize handle of a given box
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

  // Checks if coordinates are within the main bounding box of an item
  const isInBox = (x, y, pos, size) => {
    return (
      x >= pos.x &&
      x <= pos.x + size.width &&
      y >= pos.y &&
      y <= pos.y + size.height
    );
  };

  // Handles mouse down event to initiate dragging or resizing
  const handleMouseDown = (e) => {
    if (!isEditable) return;
    const { x, y } = getRelativePosition(e);

    // Prioritize text image interaction
    if (isInResizeHandle(x, y, textImagePosition, textImageSize)) {
      setResizingText(true);
      // Determine which handle was clicked for smarter resizing (currently assumes bottom-right)
    } else if (isInBox(x, y, textImagePosition, textImageSize)) {
      setDraggingText(true);
      setOffsetText({ x: x - textImagePosition.x, y: y - textImagePosition.y });
    }
    // Then check product image interaction
    else if (isInResizeHandle(x, y, imagePosition, imageSize)) {
      setResizing(true);
      // Determine which handle was clicked for smarter resizing (currently assumes bottom-right)
    } else if (isInBox(x, y, imagePosition, imageSize)) {
      setDragging(true);
      setOffset({ x: x - imagePosition.x, y: y - imagePosition.y });
    }
  };

  // Handles mouse move event for dragging and resizing
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

  // Handles mouse up/leave events to stop dragging/resizing
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
        onMouseLeave={handleMouseUp} // Stop interaction if mouse leaves canvas
        className="canvas"
        style={{
          cursor: isEditable // Dynamic cursor based on interaction state
            ? (resizing || resizingText
                ? 'nwse-resize' // For resizing (bottom-right handle)
                : (dragging || draggingText ? 'grabbing' : 'default')) // For dragging
            : 'default', // Default cursor if not editable
          display: 'block',
          width: '100%', // Make canvas fill its container for responsiveness
          height: '100%',
        }}
        aria-label="광고 이미지 편집 캔버스" // Accessibility label
      />
    </div>
  );
});

export default CanvasStage;
*/