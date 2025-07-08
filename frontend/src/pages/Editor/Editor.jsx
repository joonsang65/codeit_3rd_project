import React, { useState } from 'react';
import Step1Upload from './steps/Step1Upload';
import Step2Background from './steps/Step2Background';
import Step3TextInput from './steps/Step3TextInput';
import Step4TextAdjust from './steps/Step4TextAdjust';
import Step5FinalOutput from './steps/Step5FinalOutput';
import './Editor.css';

const Editor = () => {
  const [step, setStep] = useState(1);

  // 공유 데이터
const [uploadedImage, setUploadedImage] = useState(null); // 상품 이미지
const [imagePosition, setImagePosition] = useState({ x: 100, y: 100 }); // 위치
const [imageSize, setImageSize] = useState({ width: 300, height: 300 }); // 크기
const [bgPrompt, setBgPrompt] = useState('');
const [bgImage, setBgImage] = useState(null);
const [adText, setAdText] = useState('');
const [textImage, setTextImage] = useState(null);
  // ... 필요시 더 추가

  const nextStep = () => setStep((s) => Math.min(s + 1, 5));
  const prevStep = () => setStep((s) => Math.max(s - 1, 1));

  return (
    <div className="editor-container">
      <div className="step-navigation">
        <button onClick={prevStep} disabled={step === 1}>← 이전</button>
        <span>단계 {step} / 5</span>
        <button onClick={nextStep} disabled={step === 5}>다음 →</button>
      </div>

      <div className="step-content">
        {step === 1 && (
          <Step1Upload
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
            adText={adText}
            setAdText={setAdText}
          />
        )}

        {step === 4 && (
          <Step4TextAdjust
            textImage={textImage}
            setTextImage={setTextImage}
          />
        )}

        {step === 5 && (
          <Step5FinalOutput
            uploadedImage={uploadedImage}
            bgImage={bgImage}
            textImage={textImage}
          />
        )}
      </div>
    </div>
  );
};

export default Editor;