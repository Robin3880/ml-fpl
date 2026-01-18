import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import PlayerList from './components/PlayerList.jsx';
import Dashboard from "./components/Dashboard.jsx";
import Player from "./components/Player.jsx";

function App() {
return (
    <BrowserRouter>
      <div className="min-h-screen bg-black text-white font-sans">
        <Navbar />
        <div className="container mx-auto p-6">
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