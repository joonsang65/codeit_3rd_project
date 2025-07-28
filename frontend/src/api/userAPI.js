// src/api/userAPI.js
import axios from 'axios';

const API_BASE_URL = "http://34.135.93.123:8000";
//const API_BASE_URL = "http://localhost:8000"; 

export const registerUser = async (userData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/users/`, userData);
        return response.data; // Return the user data from the backend
    } catch (error) {
        // Re-throw the error so the calling component can handle it
        throw error; 
    }
};

// You might add loginUser, getUser, etc., here later