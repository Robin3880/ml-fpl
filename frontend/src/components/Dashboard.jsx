import { useEffect, useState } from 'react'
import api from '../api';
import PlayerIcon from './PlayerIcon.jsx';

const Dashboard = () => {

  const [teamData, setTeamData] = useState({         // data variable and its setter function, useState saves data between functions runs
    starters: [],
    bench: [],
    total_cost: 0,
    total_xpts: 0
  });

  const [teamType, setTeamType] = useState("best"); // "best" or "differential"
  const [range, setRange] = useState(1);        // 1-5  gameweeks taken into account

  const fetchTeam = async () => {
    const params = {
      num_of_gw: range
    };

    if (teamType === "differential") {
      params.differential = "True";
    }

    const response = await api.get("best_team", { params });
    setTeamData(response.data)
  };

  useEffect(() => {                 // runs once initally
    fetchTeam();
  }, [teamType, range]);          // re-run whenever teamtype or range changes             

  // sort by position for formation layout
  const getPos = (pos) => teamData.starters.filter(p => p.position === pos);
  const posMap = { "GK": 1, "DEF": 2, "MID": 3, "FWD": 4 };
  const sortedBench = [...teamData.bench].sort((a, b) => posMap[a.position] - posMap[b.position]);

  return (
    <div className="max-w-xl mx-auto text-gray-300">

      {/* parameters / controls */}
      <div className="bg-gray-800 rounded-lg p-3 mb-6 flex flex-col sm:flex-row justify-between items-center gap-4 shadow-lg border border-gray-700">

        {/* best xi / differential toggle */}
        <div className="flex bg-gray-900 rounded p-1">
          <button
            onClick={() => setTeamType("best")}
            className={`px-4 py-1.5 rounded text-sm font-bold transition ${teamType === "best" ? "bg-purple-600 text-white shadow-md" : "text-gray-400 hover:text-white cursor-pointer"
              }`}
          >
            Best XI
          </button>
          <button
            onClick={() => setTeamType("differential")}
            className={`px-4 py-1.5 rounded text-sm font-bold transition ${teamType === "differential" ? "bg-purple-600 text-white shadow-md" : "text-gray-400 hover:text-white cursor-pointer"
              }`}
          >
            Differential
          </button>
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

      {/* header */}
      <div className="flex justify-between items-end mb-4">
        <h1 className="text-2xl font-bold text-white">Best XI</h1>
        <div className="text-right text-sm">
          <span className="font-bold text-purple-400">{Number(teamData.total_xpts).toFixed(1)} xp</span>
          <span className="mx-2 text-gray-600">|</span>
          <span>€{(teamData.total_cost / 10).toFixed(1)}m</span>
        </div>
      </div>

      {/* pitch */}
      <div className="bg-emerald-950 rounded-lg p-4 h-[600px] flex flex-col justify-between mb-6">
        {/* position rows */}
        <div className="flex justify-center">{getPos("GK").map((p, i) => <PlayerIcon key={i} p={p} />)}</div>
        <div className="flex justify-around px-4">{getPos("DEF").map((p, i) => <PlayerIcon key={i} p={p} />)}</div>
        <div className="flex justify-around px-2">{getPos("MID").map((p, i) => <PlayerIcon key={i} p={p} />)}</div>
        <div className="flex justify-around px-10">{getPos("FWD").map((p, i) => <PlayerIcon key={i} p={p} />)}</div>
      </div>

      {/* bench */}
      <div className="bg-gray-900 rounded p-4">
        <p className="text-xs font-bold text-gray-500 uppercase mb-3">Bench</p>
        <div className="flex justify-between">
          {sortedBench.map((p, i) => <PlayerIcon key={i} p={p} isBench={true} />)}
        </div>
      </div>

    </div>
  )
};

export default Dashboard;