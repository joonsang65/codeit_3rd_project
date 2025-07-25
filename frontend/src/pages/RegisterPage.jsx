// src/pages/RegisterPage.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import './RegisterPage.css';

// environment variable here: process.env.REACT_APP_API_BASE_URL
const API_BASE_URL = "http://localhost:8000"; 

function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false); 

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (password !== confirmPassword) {
      setError("비밀번호가 일치하지 않습니다."); 
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(`${API_BASE_URL}/users/`, {
        username,
        email,
        password
      });

      setSuccess("회원가입이 성공적으로 완료되었습니다! 이제 로그인할 수 있습니다."); // Korean
      console.log("User created:", response.data);

      setTimeout(() => {
        navigate('/login'); 
      }, 2000);

    } catch (err) {
      console.error("회원가입 오류:", err); // Korean
      if (err.response) {
        setError(err.response.data.detail || "회원가입 실패. 다시 시도해 주세요."); 
      } else if (err.request) {
        setError("서버로부터 응답이 없습니다. 네트워크 또는 서버 상태를 확인하세요."); 
      } else {
        setError("예기치 않은 오류가 발생했습니다. 다시 시도해 주세요."); 
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container"> 
      <h2>계정 등록</h2>
      {error && <p className="register-message error">{error}</p>}
      {success && <p className="register-message success">{success}</p>}
      <form onSubmit={handleSubmit} className="register-form">
        <div className="form-group">
          <label htmlFor="username">사용자 이름:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={loading} 
          />
        </div>
        <div className="form-group">
          <label htmlFor="email">이메일:</label> 
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={loading}
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">비밀번호:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="new-password"
            disabled={loading}
          />
        </div>
        <div className="form-group">
          <label htmlFor="confirmPassword">비밀번호 확인:</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            autoComplete="new-password"
            disabled={loading} 
          />
        </div>
        <button type="submit" className="register-button" disabled={loading}>
          {loading ? '등록 중...' : '회원가입'}
        </button>
      </form>

      <p className="login-link-text">
        이미 계정이 있으십니까? <Link to="/login" className="login-link">여기서 로그인하십시오</Link>
      </p>
    </div>
  );
}

export default RegisterPage;