// src/pages/LoginPage.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import './LoginPage.css';

// process.env.REACT_APP_API_BASE_URL
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://34.135.93.123:8000"; 

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false); 

  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true); 

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/login`, {
        email,
        password
      });

      const { access_token, user } = response.data;
      await login(access_token, user); 

      setSuccess("로그인 성공!");
      console.log("로그인한 사용자:", user);

      setTimeout(() => {
        navigate('/'); 
      }, 1500);

    } catch (err) {
      console.error("로그인 오류:", err);
      if (err.response) {
        setError(err.response.data.detail || "로그인 실패. 자격 증명을 확인하세요.");
      } else if (err.request) {
        setError("서버로부터 응답이 없습니다. 네트워크 또는 서버 상태를 확인하세요.");
      } else {
        setError("로그인 중 예기치 않은 오류가 발생했습니다.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>로그인</h2>
      {error && <p className="login-message error">{error}</p>}
      {success && <p className="login-message success">{success}</p>}
      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-group">
          <label htmlFor="loginEmail">이메일:</label>
          <input
            type="email"
            id="loginEmail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
          />
        </div>
        <div className="form-group">
          <label htmlFor="loginPassword">비밀번호:</label>
          <input
            type="password"
            id="loginPassword"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password" 
            disabled={loading} 
          />
        </div>
        <button type="submit" className="login-button" disabled={loading}>
          {loading ? '로그인 중...' : 'Login'}
        </button>
      </form>

      <p className="register-link-text">
        계정이 없으십니까? <Link to="/register" className="register-link">여기서 가입하십시오</Link>
      </p>
    </div>
  );
}

export default LoginPage;