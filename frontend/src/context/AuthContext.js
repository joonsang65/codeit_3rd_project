// src/context/AuthContext.js
import React, { createContext, useState, useEffect, useContext } from 'react';
import { initializeSession } from '../api/sessionAPI';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null); 
    const [loadingAuth, setLoadingAuth] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        const userInfo = localStorage.getItem('user_info');

        if (token && userInfo) {
            try {
                const parsedUser = JSON.parse(userInfo);
                setIsAuthenticated(true);
                setUser(parsedUser);
                console.log("AuthContext: User found in localStorage, setting authenticated state.");
            } catch (error) {
                console.error("AuthContext: Failed to parse user_info from localStorage", error);
                localStorage.removeItem('access_token');
                localStorage.removeItem('user_info');
                setIsAuthenticated(false);
                setUser(null);
            }
        } else {
            console.log("AuthContext: No valid token or user info found in localStorage. User is not authenticated.");
            setIsAuthenticated(false); 
            setUser(null);
        }
        setLoadingAuth(false); 

    }, []); 

    const login = async (accessToken, userInfo) => {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('user_info', JSON.stringify(userInfo));
        setIsAuthenticated(true);
        setUser(userInfo);
        console.log("AuthContext: User logged in, state updated.");

        const currentSessionId = localStorage.getItem('sessionId');
        if (currentSessionId && userInfo && userInfo.id) {
            try {
                await initializeSession(currentSessionId, userInfo.id);
                console.log(`AuthContext: Backend session ${currentSessionId} updated with user_id ${userInfo.id}.`);
            } catch (error) {
                console.error("AuthContext: Failed to link session with user ID:", error);
            }
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
        setIsAuthenticated(false);
        setUser(null);
        console.log("AuthContext: User logged out, state updated.");

        const currentSessionId = localStorage.getItem('sessionId');
        if (currentSessionId) {
            initializeSession(currentSessionId, null) 
                .then(() => console.log("AuthContext: Backend session reverted to anonymous."))
                .catch(error => console.error("AuthContext: Failed to revert session to anonymous:", error));
        }
    };

    const authContextValue = {
        isAuthenticated,
        user,
        loadingAuth,
        login,
        logout,
    };

    return (
        <AuthContext.Provider value={authContextValue}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    return useContext(AuthContext);
};