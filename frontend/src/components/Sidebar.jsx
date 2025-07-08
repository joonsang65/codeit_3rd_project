import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <h2>AI 광고 제작</h2>
      <nav>
        <NavLink to="/" end>✲ 홈</NavLink>
        <NavLink to="/gallery">❐ 갤러리</NavLink>
        <NavLink to="/editor">✎ 편집</NavLink>
      </nav>
    </div>
  );
};

export default Sidebar;
