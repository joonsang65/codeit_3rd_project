// frontend/src/pages/Editor/Editor.jsx
import React, { useState } from 'react';
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
  const [adText, setAdText] = useState('');  // step3 광고 문구
  const [adTexts, setAdTexts] = useState([]);  // step4 텍스트 이미지용 문구
  const [currentIndex, setCurrentIndex] = useState(0);
  const [fontName, setFontName] = useState('본고딕_BOLD');
  const [fontSize, setFontSize] = useState(50);
  const [textColor, setTextColor] = useState('#000000');
  const [strokeColor, setStrokeColor] = useState('#FFFFFF');
  const [strokeWidth, setStrokeWidth] = useState(0);
  const [textImage, setTextImage] = useState(null);
  const [textImagePosition, setTextImagePosition] = useState({ x: 150, y: 150 });
  const [textImageSize, setTextImageSize] = useState({ width: 300, height: 100 });

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
    setProductInfo('');
  };

  return (
    <div className="editor-container">
      <div className="step-navigation">
        <button onClick={prevStep} disabled={step === 1}>← 이전</button>
        <span>단계 {step} / 5</span>
        <button onClick={nextStep} disabled={step === 5}>다음 →</button>
      </div>

      <div className="step-content">
        <CanvasStage
          uploadedImage={uploadedImage}
          imagePosition={imagePosition}
          setImagePosition={setImagePosition}
          imageSize={imageSize}
          setImageSize={setImageSize}
          bgImage={bgImage}
          textImage={textImage}
          textImagePosition={textImagePosition}
          setTextImagePosition={setTextImagePosition}
          textImageSize={textImageSize}
          setTextImageSize={setTextImageSize}
          platform={platform}
          isEditable={step !== 5}
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
              generatedImageUrl={textImage} // Assuming textImage is the final combined image URL
              generatedAdCopy={adText}
              isLoading={false} // You might want to manage loading state here if needed
              onGenerateNew={handleGenerateNew}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Editor;