import aiohttp
import asyncio
import os
import json
from dataclasses import dataclass, field

base_url = "https://pokeapi.co/api/v2"

@dataclass
class Pokemon:
    id: int = 0
    species_name: str = ""
    types: dict = field(default_factory=dict)
    hp: int = 0
    attack: int = 0
    special_attack: int = 0
    defence: int = 0
    special_defence: int = 0
    moves: dict = field(default_factory=dict)

@dataclass
class Move:
    move_name: str = ""
    accuracy: int = 0
    damage_type: str = ""

##########################
# General Data Functions #
##########################

def find_json_file(file_name):
    return os.path.exists(file_name)

async def get_api_data(session, url):
    async with session.get(url) as r:
        return await r.json()

#########
# MOVES #
#########
async def import_all_moves():
    moves_url = f"{base_url}/move?limit=2000"
    print("Retrieving move data...")

    if find_json_file('moves.json'):
        with open('moves.json', 'r') as file:
            print("Moves loaded from file successfully")
            return moves_data_class(json.load(file))

    async with aiohttp.ClientSession() as session:

        moves_data = await get_api_data(session, moves_url)

        tasks = []
        for m in moves_data["results"]:
            tasks.append(get_api_data(session, m["url"]))
        details = await asyncio.gather(*tasks)

        for move, d in zip(moves_data["results"], details):
            move["accuracy"] = d["accuracy"]
            move["damage_type"] = d["damage_class"]["name"]

        with open('moves.json', 'w') as outfile:
            json.dump(moves_data, outfile, indent=4)

        print("moves.json created successfully")
        return moves_data_class(moves_data)

def moves_data_class(data):
    poke_moves = {}

    for m in data["results"]:
        move = Move()
        move.move_name = m["name"]
        move.accuracy = m["accuracy"]
        move.damage_type = m["damage_type"]
        poke_moves[move.move_name] = move

    return poke_moves


###########
# POKEMON #
###########

async def import_all_pokemon(moves):
    pokemon_url = f"{base_url}/pokemon?limit=2000"
    print("Retrieving pokemon data...")

    if find_json_file('pokemon.json'):
        with open('pokemon.json', 'r') as file:
            print("Pokemon loaded from file successfully")
            return pokemon_data_class(json.load(file), moves)

    async with aiohttp.ClientSession() as session:

        pokemon_data = await get_api_data(session, pokemon_url)

        tasks = []
        for p in pokemon_data["results"]:
            tasks.append(get_api_data(session, p["url"]))
        details = await asyncio.gather(*tasks)

        # Joins the data from https://pokeapi.co/api/v2/pokemon?limit=100000 and the individual pokemon (i.e. https://pokeapi.co/api/v2/pokemon/1/ (Bulbasaur)) together.
        for pkmn, api_data in zip(pokemon_data["results"], details):
            pkmn["id"] = api_data["id"]
            pkmn["name"] = api_data["name"]
            pkmn["height"] = api_data["height"]

            pkmn["types"] = []
            for t in api_data["types"]:
                pkmn["types"].append(t["type"]["name"])

            pkmn["stats"] = api_data["stats"]
            pkmn["abilities"] = api_data["abilities"]

            pkmn["move_names"] = []
            for m in api_data["moves"]:
                pkmn["move_names"].append(m["move"]["name"])

        with open('pokemon.json', 'w') as outfile:
            json.dump(pokemon_data, outfile, indent=4)

        print("pokemon.json created successfully")
        return pokemon_data_class(pokemon_data, moves)

def pokemon_data_class(data, moves):
    poke_list = {}

    for p in data["results"]:
        poke = Pokemon()
        poke.id = p["id"]
        poke.species_name = p["name"]
        # poke.types = p["types"]

        # Had to do stats this way because of how it's written in the api
        # i.e. {
        #       "base_stat": 45,
        #       "effort": 0,
        #       "stat": {
        #         "name": "hp",
        #         "url": "https://pokeapi.co/api/v2/stat/1/"
        #       }
        for poke_stat in p["stats"]:
            match poke_stat["stat"]["name"]:
                case "hp":
                    poke.hp = poke_stat["base_stat"]
                case "attack":
                    poke.attack = poke_stat["base_stat"]
                case "defense":
                    poke.defence = poke_stat["base_stat"]
                case "special-attack":
                    poke.special_attack = poke_stat["base_stat"]
                case "special-defense":
                    poke.special_defence = poke_stat["base_stat"]
                case _:
                    pass


        for move_name in p["move_names"]:
            if move_name in moves:
                poke.moves[move_name] = moves[move_name]

        poke_list[poke.species_name] = poke

    return poke_list


async def build_move_lookup(pokemon_db):
    moves_lookup = {}

    for pokemon in pokemon_db.values():
        for move in pokemon.moves:
            if move not in moves_lookup:
                moves_lookup[move] = []
            moves_lookup[move].append(pokemon)

    return moves_lookup

async def build_type_lookup(pokemon_db):
    types_lookup = {}

    for pokemon in pokemon_db.values():
        for t in pokemon.types:
            if t not in types_lookup:
                types_lookup[t] = []
            types_lookup[t].append(pokemon)

    return types_lookup

########
# MAIN #
########

async def main():
    moves_data = await import_all_moves()
    #abilities = await import_all_abilities()
    pokemon_data = await import_all_pokemon(moves_data)

    move_lookup = await build_move_lookup(pokemon_data)
    type_lookup = await build_type_lookup(pokemon_data)

    print(pokemon_data)

    while True:
        move_search = input("Search for a move: ")
        if move_search in move_lookup:
            print("The following pokemon can learn " + move_search + ":")
            for pokemon in move_lookup[move_search]:
                print(pokemon.species_name)
            print("\n")

    """

    for name, p in pokemon.items():
        print(f"\n{name.upper()}")
        print(f"ID: {p.id}")
        print(f"HP: {p.hp} | ATK: {p.attack} | DEF: {p.defence}")
        print(f"Special Attack: {p.special_attack} | Special Defence: {p.special_defence}")
        print(f"Moves: {', '.join(p.moves.keys())}")
    """

asyncio.run(main())
