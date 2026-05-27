import requests
import os
import json
from dataclasses import dataclass

base_url = "https://pokeapi.co/api/v2"

@dataclass
class Pokemon:
    id: int = 0
    name: str = ""
    types: list[str] = None
    hp: int = 0
    attack: int = 0
    special_attack = 0
    defence: int = 0
    special_defence = 0
    moves = {}

@dataclass
class Move:
    name: str = ""
    accuracy: int = 0
    damage_type: str = ""

##########################
# General Data Functions #
##########################

def get_api_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error code: {response.status_code}")
        return None

def find_json_file(file_name):
    return os.path.exists(file_name)



#########
# MOVES #
#########
def import_all_moves():
    moves_url = f"{base_url}/move?limit=10000"
    if find_json_file('moves.json'):
        # TO-DO -> Read moves from 'moves.json'
        print("Moves imported successfully")
        pass
    else:
        moves_data = get_api_data(moves_url)
        with open('moves.json', 'w') as outfile:
            json.dump(moves_data, outfile, indent=4)
        print("moves.json created successfully")

###########
# POKEMON #
###########

def get_pokemon_info(name):
    pokemon_url = f"{base_url}/pokemon/{name}"
    pokemon_data = get_api_data(pokemon_url)
    return pokemon_data

def assign_pokemon(poke_info):
    current_pokemon: Pokemon = Pokemon()

    current_pokemon.id = pokemon_info['id']
    current_pokemon.name = pokemon_info['name']
    current_pokemon.types = pokemon_info['types']

    types: list = []

    for t in pokemon_info["types"]:
        type_name = t["type"]["name"]
        types.append(type_name)

    current_pokemon.types = types

    stats = {}

    # Dict Key
    for stat in pokemon_info["stats"]:
        stat_name = stat["stat"]["name"]
        stat_value = stat["base_stat"]

        stats[stat_name] = stat_value

    # Dict value
    current_pokemon.hp = stats["hp"]
    current_pokemon.attack = stats["attack"]
    current_pokemon.special_attack = stats["special-attack"]
    current_pokemon.defence = stats["defense"]
    current_pokemon.special_defence = stats["special-defense"]

    moves = {}
    for move in pokemon_info["moves"]:
        move_name = move["move"]["name"]
        print(move_name)

    print(current_pokemon)


########
# MAIN #
########

import_all_moves()

pokemon_name = input("Input pokemon name: ").lower()
pokemon_info = get_pokemon_info(pokemon_name)

if pokemon_info:
    print(pokemon_info.keys())
    print("Stats:", pokemon_info["stats"])
    print("Moves", pokemon_info['moves'])

    assign_pokemon(pokemon_info)
else:
    print("Pokémon not found or API error.")
