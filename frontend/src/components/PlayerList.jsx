import { useEffect, useState } from 'react'
import api from '../api';

const PlayerList = () => {

    const [players, setPlayers] = useState([]);          // players variabe and its setter funciton, useState saves data between functions runs

    const fetchPlayers = async () => {
        const response = await api.get("players");
        setPlayers(response.data)
    };

    useEffect(() => {         
        fetchPlayers();
    }, []);                        // runs once initally

    return (
        <ul>
            {players.map((player, index) => (
                <li key={index}>{player.name} {Math.round(player.xpts * 100) / 100}</li>
            ))}
      </ul>
    )
}

export default PlayerList;