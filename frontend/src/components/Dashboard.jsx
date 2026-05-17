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

  const [loading, setLoading] = useState(true);  // loading state for when players arent loaded in yet

  const fetchTeam = async () => {
    setLoading(true);

    const params = {
      num_of_gw: range
    };

    if (teamType === "differential") {
      params.differential = "True";
    }

    const response = await api.get("best_team", { params });
    setTeamData(response.data)

    setLoading(false);
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
      <div className="relative bg-emerald-950 rounded-lg p-4 h-[600px] flex flex-col justify-between mb-6">
      {loading ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            {/* loading spinner while fetching */}
            <svg className="animate-spin h-12 w-12 text-white-500 mb-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M 12 2 a 10 10 0 0 0 -10 10M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        ) : (
          <div className="flex flex-col justify-between h-full">
            <div className="flex justify-center">{getPos("GK").map((p, i) => <PlayerIcon key={i} p={p} />)}</div>
            <div className="flex justify-around px-4">{getPos("DEF").map((p, i) => <PlayerIcon key={i} p={p} />)}</div>
            <div className="flex justify-around px-2">{getPos("MID").map((p, i) => <PlayerIcon key={i} p={p} />)}</div>
            <div className="flex justify-around px-10">{getPos("FWD").map((p, i) => <PlayerIcon key={i} p={p} />)}</div>
          </div>
        )}
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