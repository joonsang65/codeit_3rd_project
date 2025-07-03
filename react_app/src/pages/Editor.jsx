// src/pages/Editor.jsx
import React, { useState } from 'react';
import UploadForm from '../components/UploadForm';
import ResultGallery from '../components/ResultGallery';

const Editor = () => {
  const [adType, setAdType] = useState('blog');
  const [uploadedImage, setUploadedImage] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [results, setResults] = useState([]);

  const handleGenerate = () => {
    if (!uploadedImage || !prompt) return;
    const dummyResults = [uploadedImage, uploadedImage];
    setResults(dummyResults);
  };

  return (
    <div>
      <h2>✏️ 광고 편집</h2>

      <label htmlFor="adType">광고 유형 선택:</label>
      <select id="adType" value={adType} onChange={(e) => setAdType(e.target.value)}>
        <option value="blog">블로그 광고</option>
        <option value="instagram">인스타그램 광고</option>
        <option value="poster">포스터 광고</option>
      </select>

      <UploadForm
        prompt={prompt}
        setPrompt={setPrompt}
        uploadedImage={uploadedImage}
        setUploadedImage={setUploadedImage}
        onGenerate={handleGenerate}
      />

      <ResultGallery results={results} />
    </div>
  );
};

export default Editor;