// src/components/ResultGallery.jsx
import React from 'react';

const ResultGallery = ({ results }) => {
  if (!results || results.length === 0) {
    return <p>생성된 이미지가 없습니다.</p>;
  }

  return (
    <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
      {results.map((imgSrc, index) => (
        <img
          key={index}
          src={typeof imgSrc === 'string' ? imgSrc : URL.createObjectURL(imgSrc)}
          alt={`result-${index}`}
          style={{ width: '240px', borderRadius: '8px' }}
        />
      ))}
    </div>
  );
};

export default ResultGallery;
