import { useEffect, useState } from 'react'
import api from '../api';

const PlayerList = () => {

  const [players, setPlayers] = useState([]);          // players variable and its setter funciton, useState saves data between functions runs

  const fetchPlayers = async () => {
    const response = await api.get("players");
    setPlayers(response.data)
  };

  useEffect(() => {
    fetchPlayers();
  }, []);                        // runs once initally

  return (
    <div className="max-w-4xl mx-auto text-gray-300">
      <h2 className="text-2xl font-bold mb-4 text-purple-400">Leaderboard</h2>

      <div className="border border-gray-800 rounded">
        <table className="w-full text-left">
          <thead className="bg-gray-900 text-gray-500 border-b border-gray-800">
            <tr>
              <th className="p-4">Rank</th>
              <th className="p-4">Player</th>
              <th className="p-4">Position</th>
              <th className="p-4">Cost</th>
              <th className="p-4 text-right">xPts</th>
            </tr>
          </thead>
          <tbody>
            {players.map((p, i) => (
              <tr key={i} className="border-b border-gray-800 hover:bg-gray-900/50">
                {/* rank */}
                <td className="p-4 text-gray-600">{i + 1}</td>

                {/* name */}
                <td className="p-4 font-bold text-white">{p.name}</td>

                {/* Position */}
                <td className="p-4 text-sm">{p.position}</td>

                {/* Cost */}
                <td className="p-4">{(p.cost / 100).toFixed(1)}m</td>

                {/* xPoints */}
                <td className="p-4 text-right font-bold text-purple-400">
                  {Number(p.xpts).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default PlayerList;