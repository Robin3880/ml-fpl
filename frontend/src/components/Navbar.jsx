import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="border-b border-gray-800 p-4">
      <div className="container mx-auto flex justify-between items-center">

        <Link to="/" className="text-xl font-bold text-white hover:text-purple-400 transition">
          FPL Best Team
        </Link>
        <div className="space-x-6 text-white-400 font-medium">
          <a 
            href="https://github.com/Robin3880/ml-fpl" 
            target="_blank" 
            rel="noopener noreferrer"
            className="hover:text-purple-400 transition"
          >
            GitHub
          </a>
          <Link to="/" className="hover:text-purple-400 transition">Dashboard</Link>
          <Link to="/players" className="hover:text-purple-400 transition">Players</Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;