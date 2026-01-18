import { useEffect, useState } from 'react'
import api from '../api';
import { Link } from 'react-router-dom';

const PlayerList = () => {

  const [players, setPlayers] = useState([]);          // players variable and its setter funciton, useState saves data between functions runs
  const [sortBy, setSortBy] = useState('xpts');          // sort by xpts by defualt
  const [range, setRange] = useState(1);                   // 1-5  gameweeks taken into account

  const fetchPlayers = async () => {
    const response = await api.get(`players?num_of_gw=${range}&sort_by=${sortBy}`);
    setPlayers(response.data)
  };

  useEffect(() => {         // runs once initally
    fetchPlayers();
  }, [sortBy, range]);      // re-run whenver sort-by or gw range changes                  
  return (
    <div className="max-w-4xl mx-auto text-gray-300">
      <h2 className="text-2xl font-bold mb-4 text-purple-400">Leaderboard</h2>

      {/* parameters / controls */}
      <div className="bg-gray-800 rounded-lg p-3 mb-6 flex flex-col sm:flex-row justify-between items-center gap-4 shadow-lg border border-gray-700">

        {/* sort by toggle */}
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold text-gray-500">SORT BY:</span>
          <div className="flex bg-gray-900 rounded p-1">
            <button
              onClick={() => setSortBy("xpts")}
              className={`px-4 py-1.5 rounded text-sm font-bold transition ${sortBy === "xpts" ? "bg-purple-600 text-white shadow-md" : "text-gray-400 hover:text-white cursor-pointer"
                }`}
            >
              xpts
            </button>
            <button
              onClick={() => setSortBy("xpts_per_cost")}
              className={`px-4 py-1.5 rounded text-sm font-bold transition ${sortBy === "xpts_per_cost" ? "bg-purple-600 text-white shadow-md" : "text-gray-400 hover:text-white cursor-pointer"
                }`}
            >
              xpts per cost
            </button>
          </div>
        </div>

        {/* Range of GW's buttons */}
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold text-gray-500">NUM OF GW"S:</span>
          <div className="flex bg-gray-900 rounded p-1">
            {[1, 2, 3, 4, 5].map((gw) => (
              <button
                key={gw}
                onClick={() => setRange(gw)}
                className={`w-8 h-8 rounded text-sm font-bold transition ${range === gw ? "bg-emerald-600 text-white shadow-md" : "text-gray-400 hover:bg-gray-700 hover:text-white cursor-pointer"
                  }`}
              >
                {gw}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="border border-gray-800 rounded">
        <table className="w-full text-left">
          <thead className="bg-gray-900 text-gray-500 border-b border-gray-800">
            <tr>
              <th className="p-4">Rank</th>
              <th className="p-4">Player</th>
              <th className="p-4">Position</th>
              <th className="p-4">Cost</th>
              <th className="p-4 text-right">xPts</th>
              <th className="p-4 text-right">xPts/cost</th>
            </tr>
          </thead>
          <tbody>
            {players.map((p, i) => (
              <tr key={i} className="border-b border-gray-800 hover:bg-gray-900/50">
                {/* rank */}
                <td className="p-4 text-gray-600">{i + 1}</td>

                {/* name */}
                <td className="p-4 font-bold text-white">
                  <Link to={`/players/${p.id}`} className="hover:underline hover:text-purple-400">
                    {p.name}
                  </Link>
                </td>

                {/* Position */}
                <td className="p-4 text-sm">{p.position}</td>

                {/* Cost */}
                <td className="p-4">{(p.cost / 10).toFixed(1)}m</td>

                {/* xPoints */}
                <td className="p-4 text-right font-bold text-purple-400">
                  {Number(p.xpts).toFixed(2)}
                </td>

                <td className="p-4 text-right">{Number(p.xpts_per_cost).toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default PlayerList;