// react_app/src/App.jsx
import React, { useEffect, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Home from './pages/Home';
import Gallery from './pages/Gallery';
import SelectPlatform from './pages/Editor/steps/SelectPlatform';
import Editor from './pages/Editor/Editor';
import Sidebar from './components/Sidebar';
import './App.css';
import './Theme.css';  /* 하위 파일에 전부 import 시켜줌*/


function App() {
  const [message, setMessage] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [error, setError] = useState('');
  const [platform, setPlatform] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    let id = localStorage.getItem('sessionId');
    if (!id) {
      id = uuidv4();
      localStorage.setItem('sessionId', id);
      console.log('새 세션 ID 생성:', id);
    } else {
      console.log('기존 세션 ID 사용:', id);
    }
    setSessionId(id);

    axios
      .post('http://localhost:8000/cache/init-session', null, {
        headers: { 'session-id': id },
      })
      .then((response) => {
        setMessage(""); // 경고문 회피용
        // setMessage(response.data.message);
        console.log('세션 초기화 성공:', response.data.message);
      })
      .catch((error) => {
        const errorMsg = error.response?.data?.detail || '세션 초기화 실패';
        setError(errorMsg);
        console.error('세션 초기화 에러:', error);
      });
  }, []);

  const toggleTheme = () => {
    const html = document.documentElement;
    const isDark = html.classList.toggle('dark');
    setIsDarkMode(isDark);
  };

  return (
    <Router>
      <div className="app-container">
        <button className="theme-toggle-button" onClick={toggleTheme}>
          {isDarkMode ? '☀️ Light' : '🌙 Dark'}
        </button>
        <Sidebar />
        <div className="main-content">
          {error && <div className="error-message">{error}</div>}
          {message && <div className="success-message">{message}</div>}
          <Routes>
            <Route path="/" element={<Home />} />

            <Route path="/gallery" element={<Gallery />} />

            <Route path="/select-platform" 
              element={
                <SelectPlatform 
                  setPlatform={setPlatform}
                  sessionId={sessionId} />}/>
                  
            <Route path="/editor"
              element={
                sessionId && platform ? (
                  <Editor sessionId={sessionId} platform={platform} />
                ) : (
                  <div>광고 플랫폼을 먼저 선택하세요.</div>
                )
              }
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;