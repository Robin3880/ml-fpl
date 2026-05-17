import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import PlayerList from './components/PlayerList.jsx';
import Dashboard from "./components/Dashboard.jsx";
import Player from "./components/Player.jsx";
import { useState, useEffect } from 'react';
import api from './api';  

function App() {

  const [isDemoMode, setIsDemoMode] = useState(false);
  useEffect(() => {
    const fetchSystemStatus = async () => {
      const response = await api.get("status");
      setIsDemoMode(response.data.is_demo_mode);
    };
    fetchSystemStatus();
  }, []);
  
  return (
      <BrowserRouter>
        <div className="flex flex-col min-h-screen bg-black text-white font-sans">
          <Navbar />
          <div className="container mx-auto p-6 flex-grow">
            {/* GLOBAL OFFSEASON DEMO MODE BANNER */}
            {isDemoMode && (
              <div className="bg-amber-950/40 border border-amber-500/30 text-amber-200 rounded-lg p-3 mb-6 text-sm flex gap-2 shadow-md">
                <div>
                  <span className="font-bold">Offseason Demo Mode Active:</span> The Premier League is currently on summer break. All data is frozen at Gameweek 34 to maintain a prediction window of 5 fixtures for testing and demonstration purposes.
                </div>
              </div>
            )}
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/players" element={<PlayerList />} />
              <Route path="/players/:id" element={<Player />} /> 
            </Routes>
          </div>
          <footer className="w-full py-6 border-t border-gray-800 text-center text-white">
            <p>© {new Date().getFullYear()} Robin Konrad. All rights reserved.</p>
          </footer>
        </div>
      </BrowserRouter>
    );
}

export default App