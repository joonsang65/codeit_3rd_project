import React from "react";
import "./Home.css";
import Card from "../components/Card";
import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="container home-container">
      <h1>에드잇</h1>
      <h3>광고 목적에 맞는 예시를 보고 원하는 형식의 광고를 만들어보세요</h3>


      <div className="button-group">
        <button className="start-button" onClick={() => navigate("/select-platform")}>시작하기</button>
        <button className="plan-button" onClick={() => navigate("/pricing")}>플랜 선택</button>
      </div>
    </div>
  );
}

export default Home;
