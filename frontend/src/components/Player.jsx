import { useEffect, useState } from 'react'
import api from '../api';
import { useParams } from 'react-router-dom';
import jerseyImg from '../assets/jersey.svg';

const teamMap = {    // 2025-2026 season
    1: "Arsenal", 2: "Aston Villa", 3: "Bournemouth", 4: "Brentford",
    5: "Brighton", 6: "Chelsea", 7: "Crystal Palace", 8: "Everton",
    9: "Fulham", 10: "Ipswich", 11: "Leicester", 12: "Liverpool",
    13: "Man City", 14: "Man Utd", 15: "Newcastle", 16: "Nott'm Forest",
    17: "Southampton", 18: "Spurs", 19: "West Ham", 20: "Wolves"
};

const Player = () => {
    const { id } = useParams();
    const [Player, setPlayer] = useState([]);          // player variable and its setter funciton, useState saves data between functions runs

    const fetchPlayer = async () => {
        const response = await api.get(`players/${id}`);
        setPlayer(response.data)
    };

    useEffect(() => {
        fetchPlayer();
    }, []);                        // runs once initally

    return (
        <div className="max-w-2xl mx-auto text-gray-300 p-6">

            {/* header */}
            <div className="flex items-center gap-6 mb-8 bg-gray-900 border border-gray-800 p-6 rounded">
                <div className="w-24 flex-shrink-0">
                    <img src={jerseyImg} alt="jersey" className="w-24 h-24 drop-shadow-md" />
                </div>

                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <h1 className="text-4xl font-bold text-white">{Player.name}</h1>
                        <span className="bg-gray-800 text-purple-400 font-bold px-2 py-1 rounded text-sm border border-gray-700">
                            {Player.position}
                        </span>
                    </div>
                    <p className="text-xl text-gray-400">{teamMap[Player.team]}</p>
                </div>
            </div>

            {/* stats */}
            <div className="grid grid-cols-3 gap-4 mb-8">
                <div className="bg-gray-900 border border-gray-800 p-4 rounded text-center">
                    <p className="text-xs text-gray-500 uppercase font-bold">Price</p>
                    <p className="text-2xl font-bold text-white">€{(Player.cost / 10).toFixed(1)}m</p>
                </div>

                <div className="bg-gray-900 border border-gray-800 p-4 rounded text-center">
                    <p className="text-xs text-gray-500 uppercase font-bold">Ownership</p>
                    <p className="text-2xl font-bold text-white">{Player.selected_by_percent}%</p>
                </div>

                <div className="bg-gray-900 border border-gray-800 p-4 rounded text-center">
                    <p className="text-xs text-gray-500 uppercase font-bold">Chance of Playing</p>
                    <p className="text-2xl font-bold text-white">{Player.chance_of_playing_this_round}%</p>
                </div>

            </div>

            {/* gw expected points predictions */}
            <div className="border border-gray-800 rounded-lg overflow-hidden">
                <div className="bg-gray-900 px-4 py-3 border-b border-gray-800 font-bold text-white">
                    Expected Points (Next 5 GWs)
                </div>

                <div className="divide-y divide-gray-800">
                    {Player.xpts_predictions && Object.entries(Player.xpts_predictions).map(([gw, points]) => (
                        <div key={gw} className="flex justify-between items-center px-4 py-3 bg-black hover:bg-gray-900/50 transition">

                            <span className="text-gray-400 font-medium uppercase">
                                {gw.replace('_', ' ')}
                            </span>

                            <span className="text-purple-400 font-bold text-lg">
                                {Number(points).toFixed(2)} xp
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}


export default Player;