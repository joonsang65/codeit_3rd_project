// react_app/src/App.jsx
// 실행: npm start

import React, { useEffect, useState }from 'react';
import axios from 'axios';

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Gallery from './pages/Gallery';
import Editor from './pages/Editor/Editor';
import Sidebar from './components/Sidebar';
import './App.css';

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    axios.get("http://localhost:8000/api/hello")
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        console.error("There was an error fetching the message!", error);
      });
  }, []);

  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/gallery" element={<Gallery />} />
            <Route path="/editor" element={<Editor />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;