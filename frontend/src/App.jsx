// react_app/src/App.jsx
// 실행: npm start

import React, { useEffect, useState }from 'react';
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

  useEffect(() => {
    const id = uuidv4();
    setSessionId(id);

    axios.post('http://localhost:8000/image/init-session', null, {
      headers: {'session-id': id}
    })
      .then(response => setMessage(response.data.message))
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
            {/* sessionId가 생성되기 전엔 로딩 표시하거나 null 처리 */}
            <Route 
              path="/editor"
              element={sessionId ? <Editor sessionId={sessionId} /> : <div>Loading...</div>} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;