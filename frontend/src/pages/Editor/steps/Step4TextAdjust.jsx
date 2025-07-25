// src/pages/Editor/steps/Step4TextAdjust.jsx
import React, { useState, useEffect } from 'react';
import { Rnd } from 'react-rnd'; 
import { generateTextImage } from '../../../api/text_images_API';
import ProgressOverlay from '../../../components/ProgressOverlay'; 
import './Step4TextAdjust.css';

const FONT_OPTIONS = [
  "본고딕_BOLD", "본고딕_EXTRALIGHT", "본고딕_HEAVY", "본고딕_LIGHT", "본고딕_MEDIUM",
  "본고딕_NORMAL", "본고딕_REGULAR", "BagelFatOne-Regular", "나눔손글씨 고딕 아니고 고딩",
  "나눔손글씨 갈맷글", "나눔손글씨 강인한 위로", "파셜산스", "날씨", "베이글",
  "쿠키런 블랙", "쿠키런 볼드", "쿠키런 레귤러"
];

const Step4TextAdjust = ({
  adText, 
  setAdText, 
  adTextImage,
  setAdTextImage, 
  setTextImage,
  position,
  setPosition,
  size, 
  setSize,
  sessionId,
}) => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(''); 
  const [showProgress, setShowProgress] = useState(false); 
  const [isProcessDone, setIsProcessDone] = useState(false);
  const DURATION = 5000; 


  const [localAdText, setLocalAdText] = useState(adText || ''); 
  const [fontName, setFontName] = useState('본고딕_BOLD');
  const [fontSize, setFontSize] = useState(50);
  const [textColor, setTextColor] = useState('#000000');
  const [strokeColor, setStrokeColor] = useState('#FFFFFF');
  const [strokeWidth, setStrokeWidth] = useState(0);


  useEffect(() => {
    if (adText && adText !== localAdText) {
      setLocalAdText(adText);
      setTextImage(null); 
      setMessage('');
    }
  }, [adText]);


  const handleGenerateImage = async () => {
    if (!localAdText.trim()) {
      setMessage("❌ 문구를 입력해주세요.");
      return;
    }

    setLoading(true);
    setShowProgress(true);
    setIsProcessDone(false);
    setMessage("이미지 생성 중...");

    try {
      const imageResult = await generateTextImage({
        text: localAdText, 
        font_name: fontName,
        font_size: fontSize,
        text_colors: textColor,
        stroke_colors: strokeColor,
        stroke_width: strokeWidth,
        word_based_colors: false,
        background_size: [800, 400], 
        background_color: [255, 255, 255, 0], 
        padding: 80, 
        output_format: "PNG",
        session_id: sessionId, 
      });

      setTextImage(imageResult);
      setMessage("✅ 이미지가 생성되었습니다!");
    } catch (err) {
      console.error("❌ 이미지 생성 오류:", err);
      const errorMessage = err.response?.data?.detail || err.message || "텍스트 이미지 생성 중 오류가 발생했습니다.";
      setMessage(`❌ ${errorMessage}`);
    } finally {
      setIsProcessDone(true);
      setTimeout(() => setShowProgress(false), 300);
      setLoading(false);
    }
  };


  const handleLocalTextChange = (e) => {
    setLocalAdText(e.target.value);
    setAdText(e.target.value);
  };


  return (
    <div className="step4-container">
      {showProgress && (
        <ProgressOverlay
          duration={DURATION}
          processDone={isProcessDone}
          customMessage="🎨 문구를 이미지로 예쁘게 변환 중입니다..."
        />
      )}
      <div className="controls-area">
        <h2>광고 문구 디자인</h2>

        <label htmlFor="localAdText">선택된 광고 문구:</label>
        <textarea
          id="localAdText"
          value={localAdText}
          onChange={handleLocalTextChange}
          placeholder="AI가 생성한 문구가 여기에 표시됩니다. 필요하면 직접 수정 가능."
          rows="4"
          disabled={loading}
        />

        {/* Text styling options */}
        <div className="image-settings">
          <label>
            폰트:
            <select value={fontName} onChange={(e) => setFontName(e.target.value)} disabled={loading}>
              {FONT_OPTIONS.map(font => (
                <option key={font} value={font}>{font}</option>
              ))}
            </select>
          </label>

          <label>
            폰트 크기:
            <input
              type="number"
              min={10}
              max={150} 
              value={fontSize}
              onChange={(e) => setFontSize(Number(e.target.value))}
              disabled={loading}
            />
          </label>

          <label>
            텍스트 색상:
            <input type="color" value={textColor} onChange={(e) => setTextColor(e.target.value)} disabled={loading} />
          </label>

          <label>
            테두리 색상:
            <input type="color" value={strokeColor} onChange={(e) => setStrokeColor(e.target.value)} disabled={loading} />
          </label>

          <label>
            테두리 두께:
            <input
              type="number"
              min={0}
              max={20}
              value={strokeWidth}
              onChange={(e) => setStrokeWidth(Number(e.target.value))}
              disabled={loading}
            />
          </label>
        </div>

        <button onClick={handleGenerateImage} disabled={loading || !localAdText.trim()} className="generate-image-btn">
          {loading ? '이미지 생성 중...' : '🎨 선택 문구로 이미지 생성'}
        </button>

        {message && <p className={`status-message ${message.startsWith('❌') ? 'error-message' : ''}`}>{message}</p>}
      </div>

      <div className="canvas-area">
        {adTextImage ? (
          <Rnd
            bounds="parent"
            size={size}
            position={position}
            onDragStop={(e, d) => setPosition({ x: d.x, y: d.y })}
            onResizeStop={(e, direction, ref, delta, newPosition) => {
              setSize({
                width: parseInt(ref.style.width),
                height: parseInt(ref.style.height),
              });
              setPosition(newPosition);
            }}
          >
            <img
              src={adTextImage}
              alt="광고 문구 이미지"
              style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            />
          </Rnd>
        ) : (
          <p className="placeholder-message">문구를 입력하고 '이미지 생성' 버튼을 눌러보세요!</p>
        )}
      </div>
    </div>
  );
};

export default Step4TextAdjust;

/*
import React, { useState } from 'react';
import { generateAdText } from "../../../api/textAPI";
import { generateTextImage } from "../../../api/text_images_API";
import './Step4TextAdjust.css';

const FONT_OPTIONS = [
  "본고딕_BOLD", "본고딕_EXTRALIGHT", "본고딕_HEAVY", "본고딕_LIGHT", "본고딕_MEDIUM",
  "본고딕_NORMAL", "본고딕_REGULAR", "BagelFatOne-Regular", "나눔손글씨 고딕 아니고 고딩",
  "나눔손글씨 갈맷글", "나눔손글씨 강인한 위로", "파셜산스", "날씨", "베이글",
  "쿠키런 블랙", "쿠키런 볼드", "쿠키런 레귤러"
];

const Step4TextAdjust = ({
  sessionId,
  textImage,
  setTextImage
}) => {
  const [productInfo, setProductInfo] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [adTexts, setAdTexts] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [adText, setAdText] = useState('');

  const [fontName, setFontName] = useState('본고딕_BOLD');
  const [fontSize, setFontSize] = useState(50);
  const [textColor, setTextColor] = useState('#000000');
  const [strokeColor, setStrokeColor] = useState('#FFFFFF');
  const [strokeWidth, setStrokeWidth] = useState(0);

  const parseGeneratedResult = (rawResult, chunkCount = 8) => {
    const result = [];
    for (const entry of rawResult) {
      if (Array.isArray(entry) && typeof entry[1] === "string") {
        result.push(entry[1].trim());
        if (result.length >= chunkCount) break;
      }
    }
    return result;
  };

  const handleGenerateText = async () => {
    if (!productInfo.trim()) {
      setMessage('❌ 상품 세부 정보를 입력해주세요.');
      return;
    }

    setLoading(true);
    setMessage('광고 문구 생성 중...');

    try {
      const rawResult = await generateAdText({
        ad_type: "poster",
        model_type: "mini",
        user_prompt: productInfo.trim(),
        session_id: sessionId,
      });

      const parsedTexts = parseGeneratedResult(rawResult, 8);
      if (parsedTexts.length === 0) throw new Error("문구를 파싱할 수 없습니다.");

      setAdTexts(parsedTexts);
      setCurrentIndex(0);
      setAdText(parsedTexts[0]);
      setMessage('✅ 광고 문구가 생성되었습니다!');
      setTextImage(null);
    } catch (err) {
      console.error(err);
      setMessage(`❌ 오류: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateImage = async () => {
    if (!adText.trim()) {
      setMessage("❌ 문구를 선택해주세요.");
      return;
    }

    setLoading(true);
    setMessage("이미지 생성 중...");

    try {
      const imageResult = await generateTextImage({
        text: adText,
        font_name: fontName,
        font_size: fontSize,
        text_colors: textColor,
        stroke_colors: strokeColor,
        stroke_width: strokeWidth,
        word_based_colors: false,
        background_size: [800, 400],
        background_color: [255, 255, 255, 0],
        padding: 80,
        output_format: "PNG",
      });

      setTextImage(imageResult);
      setMessage("✅ 이미지가 생성되었습니다!");
    } catch (err) {
      console.error(err);
      setMessage("❌ 이미지 생성 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const handleTextChange = (e) => {
    const newText = e.target.value;
    const updatedTexts = [...adTexts];
    updatedTexts[currentIndex] = newText;
    setAdTexts(updatedTexts);
    setAdText(newText);
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      const newIndex = currentIndex - 1;
      setCurrentIndex(newIndex);
      setAdText(adTexts[newIndex]);
      setTextImage(null);
      setMessage('');
    }
  };

  const handleNext = () => {
    if (currentIndex < adTexts.length - 1) {
      const newIndex = currentIndex + 1;
      setCurrentIndex(newIndex);
      setAdText(adTexts[newIndex]);
      setTextImage(null);
      setMessage('');
    }
  };

  return (
    <div className="step4-container">
      <div className="controls-area">
        <label>
          상품의 세부 정보를 입력해주세요 !
          <textarea
            value={productInfo}
            onChange={(e) => setProductInfo(e.target.value)}
            rows={3}
            placeholder="상품 설명을 입력하세요"
            disabled={loading}
          />
        </label>

        <button onClick={handleGenerateText} disabled={loading}>
          {loading ? '생성 중...' : '광고 문구 8개 생성'}
        </button>

        {message && (
          <p
            style={{
              color: message.includes('✅') ? '#4ade80' : message.includes('❌') ? '#f87171' : '#eee',
              marginBottom: '1rem'
            }}
          >
            {message}
          </p>
        )}

        {adTexts.length > 0 && (
          <div className="text-nav">
            <button onClick={handlePrev} disabled={currentIndex === 0 || loading}>이전</button>
            <span>{currentIndex + 1} / {adTexts.length}</span>
            <button onClick={handleNext} disabled={currentIndex === adTexts.length - 1 || loading}>다음</button>
          </div>
        )}

        {adText && (
          <div className="text-edit-section">
            <label>
              선택된 광고 문구:
              <textarea
                value={adText}
                onChange={handleTextChange}
                rows={3}
                disabled={loading}
              />
            </label>
          </div>
        )}

        {adText && (
          <div className="image-settings">
            <label>
              폰트:
              <select value={fontName} onChange={(e) => setFontName(e.target.value)} disabled={loading}>
                {FONT_OPTIONS.map(font => (
                  <option key={font} value={font}>{font}</option>
                ))}
              </select>
            </label>

            <label>
              폰트 크기:
              <input
                type="number"
                min={10}
                max={100}
                value={fontSize}
                onChange={(e) => setFontSize(Number(e.target.value))}
                disabled={loading}
              />
            </label>

            <label>
              텍스트 색상:
              <input type="color" value={textColor} onChange={(e) => setTextColor(e.target.value)} disabled={loading} />
            </label>

            <label>
              테두리 색상:
              <input type="color" value={strokeColor} onChange={(e) => setStrokeColor(e.target.value)} disabled={loading} />
            </label>

            <label>
              테두리 두께:
              <input
                type="number"
                min={0}
                max={20}
                value={strokeWidth}
                onChange={(e) => setStrokeWidth(Number(e.target.value))}
                disabled={loading}
              />
            </label>
          </div>
        )}

        {adText && (
          <button onClick={handleGenerateImage} disabled={loading} className="generate-image-btn">
            {loading ? '이미지 생성 중...' : '선택한 문구로 이미지 생성'}
          </button>
        )}
      </div>
    </div>
  );
};

export default Step4TextAdjust;
*/