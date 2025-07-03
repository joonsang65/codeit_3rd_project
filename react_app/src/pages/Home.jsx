import React from "react";
import Card from "../components/Card";
import { useNavigate } from "react-router-dom";

import blogAdImg from "../assets/images/blog_ad.png";
import instaAdImg from "../assets/images/instagram_ad.png";
import posterAdImg from "../assets/images/poster_ad.png";

function Home() {
  const navigate = useNavigate();

  const cards = [
    {
      title: "Blog",
      caption: "예시: 블로그 광고 이미지",
      image: blogAdImg,
      route: "/editor",
      icon: "",
      bgColor: "linear-gradient(135deg, #e0e0e0, #ffffff)",
      adType: "blog",  // 여기에 광고 타입 정의
    },
    {
      title: "Instagram",
      caption: "예시: 인스타그램 광고 이미지",
      image: instaAdImg,
      route: "/editor",
      icon: "",
      bgColor: "linear-gradient(135deg, #d9d9d9, #f5f5f5)",
      adType: "instagram",
    },
    {
      title: "Poster",
      caption: "예시: 포스터 광고 이미지",
      image: posterAdImg,
      route: "/editor",
      icon: "",
      bgColor: "linear-gradient(135deg, #cccccc, #eaeaea)",
      adType: "poster",
    },
  ];

  const handleCardClick = (card) => {
    navigate(card.route, { state: { adType: card.adType } });
  };

  return (
    <div className="container home-container">
      <h1>생성형 AI 광고 제작 </h1>
      <h3>광고 목적에 맞는 예시를 보고 원하는 형식의 광고를 만들어보세요</h3>
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

export default Home;
