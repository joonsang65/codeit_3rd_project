// src/components/Card.jsx
import React from "react";
import "./Card.css";
import { useNavigate } from "react-router-dom";

function Card({ title, caption, image, route, icon, bgColor, adType}) {
  const navigate = useNavigate();

  return (
    <div
      className="clickable-card"
      style={{ backgroundColor: bgColor }}
      onClick={() => navigate(route)}
    >
      <h4>{icon} {title}</h4>
      <img src={image} alt={caption} />
      <p>{caption}</p>
    </div>
  );
}

export default Card;