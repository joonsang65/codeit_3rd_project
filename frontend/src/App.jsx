// react_app/src/App.jsx
import React, { useEffect, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { initializeSession } from './api/sessionAPI'; 

import Home from './pages/Home';
import Gallery from './pages/Gallery';
import SelectPlatform from './pages/Editor/steps/SelectPlatform';
import Editor from './pages/Editor/Editor';
import Sidebar from './components/Sidebar';
import RegisterPage from './pages/RegisterPage'; 
import LoginPage from './pages/LoginPage';    
import { AuthProvider, useAuth } from './context/AuthContext'; 
import './App.css';
import './Theme.css'; 

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loadingAuth } = useAuth();
  if (loadingAuth) {
    return <div>로딩 중...</div>; 
  }
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function AppContent() {
  const [sessionId, setSessionId] = useState('');
  const [platform, setPlatform] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false); 

  const { user, isAuthenticated, loadingAuth } = useAuth();

  useEffect(() => {
    if (loadingAuth) {
      return;
    }

    let id = localStorage.getItem('sessionId');
    if (!id) {
      id = uuidv4();
      localStorage.setItem('sessionId', id);
      console.log('새 세션 ID 생성:', id);
    } else {
      console.log('기존 세션 ID 사용:', id);
    }
    setSessionId(id);

    const userIdToPass = isAuthenticated && user ? user.id : null;
    initializeSession(id, userIdToPass)
      .then((response) => {
        console.log('세션 초기화 성공:', response.data.message || '세션 데이터 수신');
      })
      .catch((error) => {
        const errorMsg = error.response?.data?.detail || '세션 초기화 실패';
        console.error('세션 초기화 오류:', error);
      });
  }, [isAuthenticated, user, loadingAuth]);

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
          
          <Routes>
            <Route path="/" element={<Home />} />

            <Route path="/gallery" element={<Gallery />} />

            <Route path="/register" element={isAuthenticated ? <Navigate to="/" replace /> : <RegisterPage />} />
            <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />} />

            <Route path="/select-platform" 
              element={
                <PrivateRoute>
                  <SelectPlatform setPlatform={setPlatform} sessionId={sessionId} />
                </PrivateRoute>
              }
            />
            <Route path="/editor"
              element={
                <PrivateRoute>
                  {sessionId && platform ? (
                    <Editor sessionId={sessionId} platform={platform} />
                  ) : (
                    <Navigate to="/select-platform" replace /> 
                  )}
                </PrivateRoute>
              }
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

function App() {
    return (
      <AuthProvider> 
        <AppContent /> 
      </AuthProvider>
    );
}

export default App;