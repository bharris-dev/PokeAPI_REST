import { useState, useEffect } from "react";
import { searchPokemon, getPokemon } from "../scripts/api";

function SearchBar({addPokemon}){

    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);

    useEffect(() => {
        async function runSearch() {
            if (query.length < 2){
                setResults([]);
                return
            }
            const pokemon = await searchPokemon(query);
            setResults(pokemon)
        }
        
        runSearch();
    }, [query]);

    async function selectPokemon(name){
        try{
            const pokemon = await getPokemon(name);
            addPokemon(pokemon);

            setQuery("");
            setResults([]);
        } catch (e){
            console.log("Error:" + e)
        }
    }

    return(
        <div className = "searchBar">
            <input placeholder="Search Pokemon..." value={query} onChange={(event) => setQuery(event.target.value)}></input>

            <ul>
                {results.map((pokemon) => (
                    <li key={pokemon.id} onClick={() => selectPokemon(pokemon.name)}>
                        <img src={pokemon.sprite} alt={pokemon.name}/>
                        {pokemon.name}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default SearchBar;