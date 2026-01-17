import jerseyImg from '../assets/jersey.svg';

const PlayerIcon = ({p}) => (
    <div className="flex flex-col items-center w-20 group cursor-pointer">
        <div className="relative">
        {/* jersey */}
            <img 
              src={jerseyImg} 
              alt="jersey" 
              className="w-12 h-12 mx-auto drop-shadow-md"
            />
        </div>
        
        {/* info box */}
        <div className="bg-gray-900 text-center w-full mt-1 border border-gray-700 rounded-sm">
            <div className="text-white text-xs font-bold truncate px-1">{p.name}</div>
            <div className="bg-gray-800 text-xs text-gray-400 flex justify-between p-0.5">
                <span>€{(p.cost / 10).toFixed(1)}m</span>
                <span className="text-purple-400 font-bold">{Number(p.xpts).toFixed(1)}xp</span>
            </div>
        </div>
    </div>
);

export default PlayerIcon;