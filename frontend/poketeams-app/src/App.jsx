import {useState, useEffect} from 'react';

import TeamCard from './components/TeamCard';
import TeamPage from './pages/TeamPage';

function App() {
  const [teams, setTeams] = useState(() => {
      try {
          const savedTeams = localStorage.getItem("teams");
          if(savedTeams){
              return JSON.parse(savedTeams);
          }

          return [
              {
                  id: crypto.randomUUID(),
                  name: "My First Team",
                  pokemon: []
              }
          ];

      } catch {
          return [];
      }
  });

  const [selectedTeamId, setSelectedTeamId] = useState(null);

  useEffect(() => {
    localStorage.setItem("teams", JSON.stringify(teams));
  }, [teams]);

  function createTeam(){
    const newTeam = {
        id: crypto.randomUUID(),
        name: "New Team",
        pokemon: []
    };

    setTeams([...teams, newTeam]);
  }

  function deleteTeam(id){
    setTeams(currentTeams =>
        currentTeams.filter(team => team.id !== id)
    );

    if(selectedTeamId === id){
        setSelectedTeamId(null);
    }
  }

  function openTeam(id){
    setSelectedTeamId(id);
  }

  if(selectedTeamId){
      return (
          <TeamPage teamId={selectedTeamId} teams={teams} setTeams={setTeams} setSelectedTeamId={setSelectedTeamId}/>
      );
  }
  
  return (
    <>
      <button onClick={createTeam}>Create Team</button>

      <div className="teamsGrid">
        {teams.map((team) => (
          <div key={team.id} onClick={() => openTeam(team.id)} className="teamCard">
              <h2>{team.name}</h2>
              
              <div className="teamSprites">
                {team.pokemon.map((pokemon) => (<img className="pokeSprite" key={pokemon.teamId} src={pokemon.sprite} alt={pokemon.name}/>))}
              </div>

              <p>{team.pokemon.length}/6 Pokémon</p>
              <button onClick={(event) => {event.stopPropagation(); deleteTeam(team.id);}}>Delete</button>
          </div>
        ))}
      </div>
    </>);
}

export default App;
