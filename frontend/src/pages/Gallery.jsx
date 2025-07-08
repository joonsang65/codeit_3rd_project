// src/pages/Gallery.jsx 예제
import React from 'react';

import result1 from '../assets/results/1.jpg';
import result2 from '../assets/results/2.jpg';
import result3 from '../assets/results/3.jpg';
import result4 from '../assets/results/4.jpg';
import result5 from '../assets/results/5.jpg';
import result6 from '../assets/results/6.jpg';
import result7 from '../assets/results/7.jpg';
import result8 from '../assets/results/8.jpg';

const sampleImages = [result1, result2, result3, result4, result5, result6, result7, result8];

const Gallery = () => {
  return (
    <div>
      <h2>갤러리</h2>
      <div
        style={{
          columnCount: 4,         // 컬럼 개수 조절 가능 (3~4 권장)
          columnGap: '20px',      // 컬럼 사이 간격
        }}
      >
        {sampleImages.map((src, index) => (
          <div
            key={index}
            style={{
              breakInside: 'avoid',   // 컬럼 내 이미지 깨짐 방지
              marginBottom: '20px',   // 이미지간 아래 여백
              background: '#222',
              borderRadius: '12px',
              overflow: 'hidden',
            }}
          >
            <img
              src={src}
              alt={`ad-${index}`}
              style={{ width: '100%', display: 'block', borderRadius: '8px' }}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default Gallery;


// Fastapi 연동 시 코드
// import React, { useEffect, useState } from "react";

// const Gallery = () => {
//   const [images, setImages] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   useEffect(() => {
//     fetch("http://localhost:8000/api/results")  // FastAPI 서버 주소에 맞게 조정
//       .then((res) => {
//         if (!res.ok) throw new Error("네트워크 응답이 좋지 않습니다.");
//         return res.json();
//       })
//       .then((data) => {
//         setImages(data);
//         setLoading(false);
//       })
//       .catch((err) => {
//         setError(err.message);
//         setLoading(false);
//       });
//   }, []);

//   if (loading) return <p>이미지 로딩 중...</p>;
//   if (error) return <p>오류 발생: {error}</p>;
//   if (images.length === 0) return <p>생성된 이미지가 없습니다.</p>;

//   return (
//     <div>
//       <h2>갤러리</h2>
//       <div style={{ display: "flex", gap: "20px", flexWrap: "wrap" }}>
//         {images.map((src, index) => (
//           <div
//             key={index}
//             style={{
//               width: "280px",
//               background: "#222",
//               padding: "16px",
//               borderRadius: "12px",
//             }}
//           >
//             <img
//               src={`http://localhost:8000${src}`}
//               alt={`ad-${index}`}
//               style={{ width: "100%", borderRadius: "8px" }}
//             />
//             <p style={{ color: "#ccc", marginTop: "10px" }}>
//               광고 이미지 {index + 1}
//             </p>
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// };

// export default Gallery;
