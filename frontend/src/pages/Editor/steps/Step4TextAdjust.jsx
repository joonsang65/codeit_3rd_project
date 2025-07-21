import React, { useState } from 'react';
import { Rnd } from 'react-rnd';
import { generateAdText } from "../../../api/textAPI";
import { generateTextImage } from "../../../api/text_images_API";
import './Step4TextAdjust.css';

const Step4TextAdjust = ({
  sessionId,
  position: propPosition,
  setPosition: propSetPosition,
  size: propSize,
  setSize: propSetSize,
}) => {
  const [position, setLocalPosition] = useState(propPosition || { x: 50, y: 50 });
  const [size, setLocalSize] = useState(propSize || { width: 200, height: 100 });

  const setPosition = propSetPosition || setLocalPosition;
  const setSize = propSetSize || setLocalSize;

  const [productInfo, setProductInfo] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [adTexts, setAdTexts] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [adText, setAdText] = useState('');
  const [adTextImage, setAdTextImage] = useState(null);

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
      setAdTextImage(null);
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

      const base64Image = `data:image/png;base64,${imageResult.image_base64}`;
      setAdTextImage(base64Image);
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
      setAdTextImage(null);
      setMessage('');
    }
  };

  const handleNext = () => {
    if (currentIndex < adTexts.length - 1) {
      const newIndex = currentIndex + 1;
      setCurrentIndex(newIndex);
      setAdText(adTexts[newIndex]);
      setAdTextImage(null);
      setMessage('');
    }
  };

  return (
    <div className="step4-container">
      {/* 메인 컨텐츠 영역: 좌우 분할 */}
      <div className="main-content">
        {/* 좌측: 이미지 미리보기 영역 */}
        <div className="image-preview-area">
          <h3>생성된 이미지 미리보기</h3>
          <div className="canvas-area">
            {adTextImage ? (
              <Rnd
                bounds="parent"
                size={size}
                position={position}
                onDragStop={(e, d) => setPosition({ x: d.x, y: d.y })}
                onResizeStop={(e, direction, ref, delta, pos) => {
                  setSize({
                    width: parseInt(ref.style.width),
                    height: parseInt(ref.style.height),
                  });
                  setPosition(pos);
                }}
                style={{
                  border: '2px solid #5a7fff',
                  borderRadius: '4px'
                }}
              >
                <img
                  src={adTextImage}
                  alt="광고 문구 이미지"
                  style={{ 
                    width: '100%', 
                    height: '100%', 
                    objectFit: 'contain',
                    cursor: 'move',
                    display: 'block'
                  }}
                  onLoad={() => console.log('이미지 로드 완료')}
                  onError={(e) => console.error('이미지 로드 실패:', e)}
                />
              </Rnd>
            ) : (
              <div className="empty-canvas">
                <p>이미지를 생성하면 여기에 표시됩니다</p>
                <p style={{ fontSize: '0.9rem', opacity: '0.7' }}>드래그로 위치 조정, 모서리로 크기 조정 가능</p>
                {adText && <p style={{ fontSize: '0.8rem', color: '#5a7fff' }}>👆 위의 "선택한 문구로 이미지 생성" 버튼을 클릭하세요</p>}
                <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '10px' }}>
                  <p>디버그 정보:</p>
                  <p>adTextImage: {adTextImage ? '있음' : '없음'}</p>
                  <p>adText: {adText ? `"${adText}"` : '없음'}</p>
                  <p>loading: {loading ? '예' : '아니오'}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 우측: 컨트롤 영역 */}
        <div className="controls-area">
          {/* 상품 세부 정보 입력 */}
          <label>
            상품 세부 정보 입력:
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

          {message && <p style={{ color: message.includes('✅') ? '#4ade80' : message.includes('❌') ? '#f87171' : '#eee', marginBottom: '1rem' }}>{message}</p>}

          {/* 텍스트 네비게이션 */}
          {adTexts.length > 0 && (
            <div className="text-nav">
              <button onClick={handlePrev} disabled={currentIndex === 0 || loading}>이전</button>
              <span>
                {currentIndex + 1} / {adTexts.length}
              </span>
              <button onClick={handleNext} disabled={currentIndex === adTexts.length - 1 || loading}>다음</button>
            </div>
          )}
          
          {/* 텍스트 편집 */}
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

          {/* 이미지 설정 */}
          {adText && (
            <div className="image-settings">
              <label>
                폰트:
                <select value={fontName} onChange={(e) => setFontName(e.target.value)} disabled={loading}>
                  <option value="본고딕_BOLD">본고딕_BOLD</option>
                  <option value="나눔스퀘어">나눔스퀘어</option>
                  <option value="맑은고딕">맑은고딕</option>
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

          {/* 이미지 생성 버튼 */}
          {adText && (
            <button onClick={handleGenerateImage} disabled={loading} className="generate-image-btn">
              {loading ? '이미지 생성 중...' : '선택한 문구로 이미지 생성'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Step4TextAdjust;