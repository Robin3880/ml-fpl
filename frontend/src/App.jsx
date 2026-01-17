import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import PlayerList from './components/PlayerList.jsx';
import Dashboard from "./components/Dashboard.jsx";

function App() {
return (
    <BrowserRouter>
      <div className="min-h-screen bg-black text-white font-sans">
        <Navbar />
        <div className="container mx-auto p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/players" element={<PlayerList />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App