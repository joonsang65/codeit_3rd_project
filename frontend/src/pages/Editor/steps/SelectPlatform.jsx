// src/pages/Editor/steps/SelectPlatform.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import Card from "../../../components/Card";

import blogAdImg from "../../../assets/images/blog_ad.png";
import instaAdImg from "../../../assets/images/instagram_ad.png";
import posterAdImg from "../../../assets/images/poster_ad.png";
import { saveAdTypeToSession } from "../../../api/sessionAPI";


function SelectPlatform({ setPlatform, sessionId }) {
  const navigate = useNavigate();

  const cards = [
    {
      title: "Blog",
      caption: "예시: 블로그 광고 이미지",
      image: blogAdImg,
      bgColor: "linear-gradient(135deg, #e0e0e0, #ffffff)",
      adType: "blog",
    },
    {
      title: "Instagram",
      caption: "예시: 인스타그램 광고 이미지",
      image: instaAdImg,
      bgColor: "linear-gradient(135deg, #d9d9d9, #f5f5f5)",
      adType: "instagram",
    },
    {
      title: "Poster",
      caption: "예시: 포스터 광고 이미지",
      image: posterAdImg,
      bgColor: "linear-gradient(135deg, #cccccc, #eaeaea)",
      adType: "poster",
    },
  ];

    const handleCardClick = async (card) => {
    try {
        setPlatform(card.adType);                  // 상태 반영
        await saveAdTypeToSession(card.adType, sessionId);  // 세션 저장
        navigate("/editor");
    } catch (err) {
        console.error("ad_type 세션 저장 실패:", err);
    }
    };

  return (
    <div className="container home-container">
      <h1>광고 플랫폼 선택</h1>
      <h3>원하는 광고 플랫폼을 선택하세요</h3>
      <div className="card-row">
        {cards.map((card, i) => (
          <div key={i} onClick={() => handleCardClick(card)} style={{ cursor: "pointer" }}>
            <Card {...card} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default SelectPlatform;
