const API_URL = "http://localhost:8000";

export async function searchPokemon(query){
    try{
        const response = await fetch(API_URL + "/pokemon/search?q=" + query);
        const data = await response.json();
        return data;
    } catch (e){
        console.log("Error: " + e)
    }
}

export async function getPokemon(name){
    try{
        const response = await fetch(API_URL + "/pokemon/" + name);
        const data = await response.json();
        return data;
    } catch (e){
        console.log("Error: " + e)
    }
}