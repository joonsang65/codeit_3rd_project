// src/context/AuthContext.js
import React, { createContext, useState, useEffect, useContext } from 'react';
import { initializeSession } from '../api/sessionAPI';

// 1. Create the AuthContext
export const AuthContext = createContext(null);

// 2. Create the AuthProvider component
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
        setLoadingAuth(false); // Authentication check is complete

    }, []); // Run only once on mount

    // Function to handle login (called from LoginPage)
    const login = async (accessToken, userInfo) => {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('user_info', JSON.stringify(userInfo));
        setIsAuthenticated(true);
        setUser(userInfo);
        console.log("AuthContext: User logged in, state updated.");

        // IMPORTANT: Update backend session with user_id after successful login
        // Assuming userInfo contains an 'id' field for the user's ID
        const currentSessionId = localStorage.getItem('sessionId');
        if (currentSessionId && userInfo && userInfo.id) {
            try {
                await initializeSession(currentSessionId, userInfo.id);
                console.log(`AuthContext: Backend session ${currentSessionId} updated with user_id ${userInfo.id}.`);
            } catch (error) {
                console.error("AuthContext: Failed to link session with user ID:", error);
                // Decide if you want to show an error to the user or just log
            }
        }
    };

    // Function to handle logout (called from Sidebar or other components)
    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
        setIsAuthenticated(false);
        setUser(null);
        console.log("AuthContext: User logged out, state updated.");

        // OPTIONAL: You might want to also hit a backend logout endpoint if you have one
        // and/or re-initialize the session without a user_id
        const currentSessionId = localStorage.getItem('sessionId');
        if (currentSessionId) {
            // Re-initialize session to clear user_id linkage if needed
            // This would create a new "anonymous" session or update the existing one without a user_id
            initializeSession(currentSessionId, null) // Pass null for userId
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

// 3. Custom hook for easy consumption
export const useAuth = () => {
    return useContext(AuthContext);
};