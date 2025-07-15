// react_app/src/App.jsx
import React, { useEffect, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Gallery from './pages/Gallery';
import Editor from './pages/Editor/Editor';
import Sidebar from './components/Sidebar';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [error, setError] = useState('');

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
        // setMessage(response.data.message);
        console.log('세션 초기화 성공:', response.data.message);
      })
      .catch((error) => {
        const errorMsg = error.response?.data?.detail || '세션 초기화 실패';
        setError(errorMsg);
        console.error('세션 초기화 에러:', error);
      });
  }, []);

  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <div className="main-content">
          {error && <div className="error-message">{error}</div>}
          {message && <div className="success-message">{message}</div>}
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/gallery" element={<Gallery />} />
            <Route
              path="/editor"
              element={sessionId ? <Editor sessionId={sessionId} /> : <div>Loading...</div>}
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;