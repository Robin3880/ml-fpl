import { useEffect, useState } from 'react'
import PlayerListComponent from './components/PlayerList.jsx';

function App() {

  return (
    <div>
      <header>
        <h1>Fpl Points Predictor</h1>
      </header>
      <main>
        <PlayerListComponent />
      </main>
    </div>
  );
}

export default App