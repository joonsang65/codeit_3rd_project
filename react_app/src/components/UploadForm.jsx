// src/components/UploadForm.jsx
import React from "react";

function UploadForm({ image, setImage, bgPrompt, setBgPrompt, adPrompt, setAdPrompt, onSubmit }) {
  return (
    <div className="form-container">
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setImage(URL.createObjectURL(e.target.files[0]))}
      />
      <br />

      <textarea
        placeholder="배경 스타일 (예: 여름 바닷가)"
        value={bgPrompt}
        onChange={(e) => setBgPrompt(e.target.value)}
      />
      <br />

      <textarea
        placeholder="광고 문구 스타일 (예: 감성적인 문구)"
        value={adPrompt}
        onChange={(e) => setAdPrompt(e.target.value)}
      />
      <br />

      <button onClick={onSubmit}>🪄 광고 이미지 생성하기</button>
    </div>
  );
}

export default UploadForm;