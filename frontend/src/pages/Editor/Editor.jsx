// frontend/src/pages/Editor/Editor.jsx

import React, { useState, useRef, useEffect} from 'react';
import CanvasStage from '../../components/CanvasStage';
import Step1Upload from './steps/Step1Upload';
import Step2Background from './steps/Step2Background';
import Step3TextAdjust from './steps/Step3TextAdjust';
import Step4TextInput from './steps/Step4TextInput';
import Step5FinalOutput from './steps/Step5FinalOutput';
import './Editor.css';

const Editor = ({ sessionId, platform }) => {
  const [step, setStep] = useState(1);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imagePosition, setImagePosition] = useState({ x: 100, y: 100 });
  const [imageSize, setImageSize] = useState({ width: 300, height: 300 });
  const [bgPrompt, setBgPrompt] = useState('');
  const [bgImage, setBgImage] = useState(null);
  const [adText, setAdText] = useState('');
  const [adTexts, setAdTexts] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [fontName, setFontName] = useState('본고딕_BOLD');
  const [fontSize, setFontSize] = useState(50);
  const [textColor, setTextColor] = useState('#000000');
  const [strokeColor, setStrokeColor] = useState('#FFFFFF');
  const [strokeWidth, setStrokeWidth] = useState(0);
  const [textImage, setTextImage] = useState(null);
  const [textImagePosition, setTextImagePosition] = useState({ x: 150, y: 150 });
  const [textImageSize, setTextImageSize] = useState({ width: 300, height: 100 });
  const [finalImage, setFinalImage] = useState(null);
  const canvasStageRef = useRef(null);
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });

  const [productInfo, setProductInfo] = useState('');

  const nextStep = () => setStep((s) => Math.min(s + 1, 5));
  const prevStep = () => setStep((s) => Math.max(s - 1, 1));

  const handleGenerateNew = () => {
    setStep(1);
    setUploadedImage(null);
    setImagePosition({ x: 100, y: 100 });
    setImageSize({ width: 300, height: 300 });
    setBgPrompt('');
    setBgImage(null);
    setAdText('');
    setAdTexts([]);
    setCurrentIndex(0);
    setFontName('본고딕_BOLD');
    setFontSize(50);
    setTextColor('#000000');
    setStrokeColor('#FFFFFF');
    setStrokeWidth(0);
    setTextImage(null);
    setTextImagePosition({ x: 150, y: 150 });
    setTextImageSize({ width: 300, height: 100 });
    setFinalImage(null);
    setProductInfo('');
  };

  const handleImagesReady = () => {
    if (canvasStageRef.current) {
      const stage = canvasStageRef.current.getStage();
      if (stage) {
        setFinalImage(stage.toDataURL());
      }
    }
  };

  // CanvasStage에 넘길 props 구성
  const canvasProps = {
    bgImage,
    textImage,
    textImagePosition,
    setTextImagePosition,
    textImageSize,
    setTextImageSize,
    platform,
    isEditable: step !== 5,
  };

  const headerTexts = {
  1: { title: '상품 이미지 업로드', subtitle: '광고할 제품을 업로드 해주세요 !' },
  2: { title: '배경 생성', subtitle: '제품과 어울리는 배경을 생성합니다 !' },
  3: { title: '텍스트 이미지 조정', subtitle: '광고에 들어갈 문구 이미지를 조정하세요 !' },
  4: { title: '광고 문구 생성', subtitle: '제품 정보를 바탕으로 텍스트를 만들어보세요 !' },
  5: { title: '최종 결과', subtitle: '최종 이미지를 확인하고 다운로드하세요' },
  };

  const { title, subtitle } = headerTexts[step];

  // step < 3이면 uploadedImage 관련 props도 추가
  if (step < 3) {
    Object.assign(canvasProps, {
      uploadedImage,
      imagePosition,
      setImagePosition,
      imageSize,
      setImageSize,
      setCanvasSize,
      onResizeCanvas: setCanvasSize
    });
  }

  return (
    <div className="editor-container">
      <h1 style={{ marginTop: '0px', marginBottom: '0px' }}>{title}</h1>
      <h3 style={{ marginTop: '0px', marginBottom: '0px' }}>{subtitle}</h3>
      <div className="step-content">
        <CanvasStage
          ref={canvasStageRef}
          {...canvasProps}
          onDrawComplete={step === 5 ? handleImagesReady : null}
        />
        <div className="step-panel">
          {step === 1 && (
            <Step1Upload
              sessionId={sessionId}
              uploadedImage={uploadedImage}
              setUploadedImage={setUploadedImage}
              imagePosition={imagePosition}
              setImagePosition={setImagePosition}
              imageSize={imageSize}
              setImageSize={setImageSize}
              platform={platform}
            />
          )}
          {step === 2 && (
            <Step2Background
              sessionId={sessionId}
              uploadedImage={uploadedImage}
              imagePosition={imagePosition}
              imageSize={imageSize}
              bgPrompt={bgPrompt}
              setBgPrompt={setBgPrompt}
              bgImage={bgImage}
              setBgImage={setBgImage}
              platform={platform}
              canvas={{canvasSize}}
            />
          )}
          {step === 3 && (
            <Step3TextAdjust
              sessionId={sessionId}
              textImage={textImage}
              setTextImage={setTextImage}
              setBgImage={setBgImage}
              adTexts={adTexts}
              setAdTexts={setAdTexts}
              currentIndex={currentIndex}
              setCurrentIndex={setCurrentIndex}
              adText={adText}
              setAdText={setAdText}
              fontName={fontName}
              setFontName={setFontName}
              fontSize={fontSize}
              setFontSize={setFontSize}
              textColor={textColor}
              setTextColor={setTextColor}
              strokeColor={strokeColor}
              setStrokeColor={setStrokeColor}
              strokeWidth={strokeWidth}
              setStrokeWidth={setStrokeWidth}
              productInfo={productInfo}
              setProductInfo={setProductInfo}
            />
          )}
          {step === 4 && (
            <Step4TextInput
              sessionId={sessionId}
              platform={platform}
              productInfo={productInfo}
              setProductInfo={setProductInfo}
              adText={adText}
              setAdText={setAdText}
              setBgImage={setBgImage}
              setAdTexts={setAdTexts}
              setCurrentIndex={setCurrentIndex}
            />
          )}
          {step === 5 && (
            <Step5FinalOutput
              generatedImageUrl={finalImage}
              generatedAdCopy={adText}
              isLoading={!finalImage}
              onGenerateNew={handleGenerateNew}
            />
          )}
        </div>
      </div>
      <div className="step-navigation">
        <button onClick={prevStep} disabled={step === 1}>← 이전</button>
        <span>단계 {step} / 5</span>
        <button onClick={nextStep} disabled={step === 5}>다음 →</button>
      </div>
    </div>
  );
};

export default Editor;

/*
import React, { useState, useRef} from 'react';
import CanvasStage from '../../components/CanvasStage';
import Step1Upload from './steps/Step1Upload';
import Step2Background from './steps/Step2Background';
import Step3TextInput from './steps/Step3TextInput';
import Step4TextAdjust from './steps/Step4TextAdjust';
import Step5FinalOutput from './steps/Step5FinalOutput';
import './Editor.css';

const Editor = ({ sessionId, platform }) => {
  const [step, setStep] = useState(1);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imagePosition, setImagePosition] = useState({ x: 100, y: 100 });
  const [imageSize, setImageSize] = useState({ width: 300, height: 300 });
  const [bgPrompt, setBgPrompt] = useState('');
  const [bgImage, setBgImage] = useState(null);
  const [adText, setAdText] = useState('');
  const [adTexts, setAdTexts] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [fontName, setFontName] = useState('본고딕_BOLD');
  const [fontSize, setFontSize] = useState(50);
  const [textColor, setTextColor] = useState('#000000');
  const [strokeColor, setStrokeColor] = useState('#FFFFFF');
  const [strokeWidth, setStrokeWidth] = useState(0);
  const [textImage, setTextImage] = useState(null);
  const [textImagePosition, setTextImagePosition] = useState({ x: 150, y: 150 });
  const [textImageSize, setTextImageSize] = useState({ width: 300, height: 100 });
  const [finalImage, setFinalImage] = useState(null);
  const canvasStageRef = useRef(null);
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });

  const [productInfo, setProductInfo] = useState('');

  const nextStep = () => setStep((s) => Math.min(s + 1, 5));
  const prevStep = () => setStep((s) => Math.max(s - 1, 1));

  const handleGenerateNew = () => {
    setStep(1);
    setUploadedImage(null);
    setImagePosition({ x: 100, y: 100 });
    setImageSize({ width: 300, height: 300 });
    setBgPrompt('');
    setBgImage(null);
    setAdText('');
    setAdTexts([]);
    setCurrentIndex(0);
    setFontName('본고딕_BOLD');
    setFontSize(50);
    setTextColor('#000000');
    setStrokeColor('#FFFFFF');
    setStrokeWidth(0);
    setTextImage(null);
    setTextImagePosition({ x: 150, y: 150 });
    setTextImageSize({ width: 300, height: 100 });
    setFinalImage(null);
    setProductInfo('');
  };

  const handleImagesReady = () => {
    if (canvasStageRef.current) {
      const stage = canvasStageRef.current.getStage();
      if (stage) {
        setFinalImage(stage.toDataURL());
      }
    }
  };

  // CanvasStage에 넘길 props 구성
  const canvasProps = {
    bgImage,
    textImage,
    textImagePosition,
    setTextImagePosition,
    textImageSize,
    setTextImageSize,
    platform,
    isEditable: step !== 5,
  };

  const headerTexts = {
  1: { title: '상품 이미지 업로드', subtitle: '광고할 제품을 업로드 해주세요 !' },
  2: { title: '배경 생성', subtitle: '제품과 어울리는 배경을 생성합니다 !' },
  3: { title: '광고 문구 생성', subtitle: '제품 정보를 바탕으로 텍스트를 만들어보세요 !' },
  4: { title: '텍스트 이미지 조정', subtitle: '광고에 들어갈 문구 이미지를 조정하세요 !' },
  5: { title: '최종 결과', subtitle: '최종 이미지를 확인하고 다운로드하세요' },
  };

  const { title, subtitle } = headerTexts[step];

  // step < 3이면 uploadedImage 관련 props도 추가
  if (step < 3) {
    Object.assign(canvasProps, {
      uploadedImage,
      imagePosition,
      setImagePosition,
      imageSize,
      setImageSize,
      setCanvasSize,
      onResizeCanvas: setCanvasSize
    });
  }

  return (
    <div className="editor-container">
      <h1 style={{ marginTop: '0px', marginBottom: '0px' }}>{title}</h1>
      <h3 style={{ marginTop: '0px', marginBottom: '0px' }}>{subtitle}</h3>
      <div className="step-content">
        <CanvasStage
          ref={canvasStageRef}
          {...canvasProps}
          onImagesReady={step === 5 ? handleImagesReady : null}
        />
        <div className="step-panel">
          {step === 1 && (
            <Step1Upload
              sessionId={sessionId}
              uploadedImage={uploadedImage}
              setUploadedImage={setUploadedImage}
              imagePosition={imagePosition}
              setImagePosition={setImagePosition}
              imageSize={imageSize}
              setImageSize={setImageSize}
              platform={platform}
            />
          )}
          {step === 2 && (
            <Step2Background
              sessionId={sessionId}
              uploadedImage={uploadedImage}
              imagePosition={imagePosition}
              imageSize={imageSize}
              bgPrompt={bgPrompt}
              setBgPrompt={setBgPrompt}
              bgImage={bgImage}
              setBgImage={setBgImage}
              platform={platform}
              canvas={{canvasSize}}
            />
          )}
          {step === 3 && (
            <Step3TextInput
              sessionId={sessionId}
              platform={platform}
              productInfo={productInfo}
              setProductInfo={setProductInfo}
              adText={adText}
              setAdText={setAdText}
              setBgImage={setBgImage}
            />
          )}
          {step === 4 && (
            <Step4TextAdjust
              sessionId={sessionId}
              textImage={textImage}
              setTextImage={setTextImage}
              setBgImage={setBgImage}
              adTexts={adTexts}
              setAdTexts={setAdTexts}
              currentIndex={currentIndex}
              setCurrentIndex={setCurrentIndex}
              adText={adText}
              setAdText={setAdText}
              fontName={fontName}
              setFontName={setFontName}
              fontSize={fontSize}
              setFontSize={setFontSize}
              textColor={textColor}
              setTextColor={setTextColor}
              strokeColor={strokeColor}
              setStrokeColor={setStrokeColor}
              strokeWidth={strokeWidth}
              setStrokeWidth={setStrokeWidth}
            />
          )}
          {step === 5 && (
            <Step5FinalOutput
              generatedImageUrl={finalImage}
              generatedAdCopy={adText}
              isLoading={!finalImage}
              onGenerateNew={handleGenerateNew}
            />
          )}
        </div>
      </div>
      <div className="step-navigation">
        <button onClick={prevStep} disabled={step === 1}>← 이전</button>
        <span>단계 {step} / 5</span>
        <button onClick={nextStep} disabled={step === 5}>다음 →</button>
      </div>
    </div>
  );
};

export default Editor;
*/