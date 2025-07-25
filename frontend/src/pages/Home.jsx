import React from "react";
import "./Home.css";
import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="container home-container">
      <h1>에드잇</h1>
      <h3>광고 목적에 맞는 예시를 보고 원하는 형식의 광고를 만들어보세요</h3>

      {/* ✅ circular-card 삽입 */}
      <div className="circular-card">
        <div style={{ textAlign: "center" }}>
          <div className="logo-text">🗯️ ad-it</div>
          <div className="subheading">ad generator</div>
          <div className="main-title">Ad-it</div>
      <div className="team-members">노준상, 구극모, 배동우, 임성은, 정재의</div>

          <div className="tag">codeit; AI</div>
        </div>
      </div>

      {/* ✅ 버튼 그룹 */}
      <div className="button-group">
        <button className="start-button" onClick={() => navigate("/select-platform")}>시작하기</button>
        <button className="plan-button" onClick={() => navigate("/pricing")}>로그인</button>
      </div>

    </div>
  );
}

export default Home;
