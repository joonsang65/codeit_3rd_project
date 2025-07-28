// src/components/Sidebar.jsx
import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; 
import './Sidebar.css';

const Sidebar = () => {
    const { isAuthenticated, user, logout } = useAuth(); 
    const navigate = useNavigate(); 

    const handleLogout = () => {
        logout(); 
        navigate('/login'); 
    };

    return (
        <div className="sidebar">
            <h2>에드잇</h2>
            <nav>
                <NavLink to="/" end>✲ 홈</NavLink>
                <NavLink to="/gallery">❐ 갤러리</NavLink>
                <NavLink to="/editor">✎ 편집</NavLink>

                {!isAuthenticated ? (
                    // 인증이 안된 상태에서 회원가입과 로그인 링크를 보여줌
                    <>
                        <NavLink to="/register">🗣 회원가입</NavLink>
                        <NavLink to="/login">🗝 로그인</NavLink>
                    </>
                ) : (
                    // 인증이 된 상태에서 사용자 정보와 로그아웃 링크를 보여줌
                    <>
                        {user && ( 
                            <div className="sidebar-user-info" style={{ 
                                color: '#eee', 
                                padding: '10px 15px', 
                                fontSize: '0.9em', 
                                borderBottom: '1px solid #444', 
                                marginBottom: '10px' 
                            }}>
                                <span>환영합니다,</span><br/>
                                <strong>{user.email}</strong>님!
                            </div>
                        )}
                        <NavLink to="#" onClick={handleLogout}>🚪 로그아웃</NavLink>
                    </>
                )}
            </nav>
        </div>
    );
};

export default Sidebar;
