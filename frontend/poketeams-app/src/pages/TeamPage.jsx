import SearchBar from "../components/SearchBar";

function TeamPage({ teamId, teams, setTeams, setSelectedTeamId}) {
    const team = teams.find(team => team.id === teamId);
    
    if(!team){
        return <p>Team not found</p>;
    }

    function renameTeam(name){
        setTeams(currentTeams =>
            currentTeams.map(t => {
                if(t.id !== teamId){
                    return t;
                }

                return {...t, name: name};
            })
        );

    }

    function addPokemon(pokemon){
        if(team.pokemon.length >= 6){
            return;
        }

        const teamPokemon = {...pokemon, teamId: crypto.randomUUID()};

        setTeams(currentTeams =>
            currentTeams.map(t => {
                if(t.id !== teamId){
                    return t;
                }

                return {...t, pokemon: [...t.pokemon, teamPokemon]};
            })
        );
    }

    function removePokemon(pokemonId){
        setTeams(currentTeams =>
            currentTeams.map(t => {
                if(t.id !== teamId){
                    return t;
                }

                return {...t, pokemon: t.pokemon.filter(pokemon => pokemon.teamId !== pokemonId)};
            })
        );
    }

    return (
        <>
            <button onClick={() => setSelectedTeamId(null)}>Back</button>
            <h2><input value={team.name} onChange={(event) => renameTeam(event.target.value)}/></h2>

            <SearchBar addPokemon={addPokemon}/>{team.pokemon.map((pokemon) => (
                <div className="pokeCard" key={pokemon.teamId}>
                    <div classname="pokeCardNamePlate"></div>
                    <img src={pokemon.sprite} alt={pokemon.name}/>
                    <h3>{pokemon.name}</h3>

                    <p>Types: {pokemon.types.join(", ")}</p>
                    <p>HP: {pokemon.hp}</p>
                    <p>Attack: {pokemon.attack}</p>
                    <p>Defence: {pokemon.defence}</p>
                    <button onClick={() => removePokemon(pokemon.teamId)}>Remove</button>
                </div>
            ))}
        </>
    );
}

export default TeamPage;