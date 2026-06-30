import aiohttp
import asyncio
import os
import json
from dataclasses import dataclass, field

base_url = "https://pokeapi.co/api/v2"

@dataclass
class Type:
    id: int
    type_name: str

    strengths: dict = field(default_factory = dict)
    weaknesses: dict = field(default_factory = dict)
    resistant_to: dict = field(default_factory = dict)
    resisted_by: dict = field(default_factory=dict)
    immunities: dict = field(default_factory = dict)
    no_effect: dict = field(default_factory=dict)

@dataclass
class Pokemon:
    id: int = 0
    species_name: str = ""
    types: dict = field(default_factory = dict)
    hp: int = 0
    attack: int = 0
    special_attack: int = 0
    defence: int = 0
    special_defence: int = 0
    moves: dict = field(default_factory = dict)

    def __str__(self):
        return (
            f"{self.species_name.title()} (#{self.id})\n"
            f"Types: {', '.join(self.types.keys())}\n"
            f"HP: {self.hp}\n"
            f"ATK: {self.attack}\n"
            f"DEF: {self.defence}\n"
            f"SP. ATK: {self.special_attack}\n"
            f"SP. DEF: {self.special_defence}\n"
            f"Moves ({len(self.moves)}): {', '.join(self.moves)}"
        )

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
# TYPES #
#########

async def import_all_types():
    types_url = f"{base_url}/type?limit=2000"
    print("Retrieving typing data...")

    if find_json_file('types.json'):
        with open('types.json', 'r') as file:
            print("Types loaded from file successfully")
            return types_data_class(json.load(file))

    async with aiohttp.ClientSession() as session:

        type_data = await get_api_data(session, types_url)

        tasks = []
        for t in type_data["results"]:
            tasks.append(get_api_data(session, t["url"]))
        details = await asyncio.gather(*tasks)

        processed_data = []

        # Goes through the unprocessed API data and only processes the type data that is relevant and saves it to local json.
        for api_data in details:
            poke_type = {
                "id": api_data["id"],
                "name": api_data["name"],
                "strengths": [],
                "weaknesses": [],
                "resisted_by": [],
                "resistant_to": [],
                "immunities": [],
                "no_effect": []
            }

            for t in api_data["damage_relations"]["double_damage_to"]:
                poke_type["strengths"].append(t["name"])

            poke_type["weaknesses"] = []
            for t in api_data["damage_relations"]["double_damage_from"]:
                poke_type["weaknesses"].append(t["name"])

            poke_type["resisted_by"] = []
            for t in api_data["damage_relations"]["half_damage_to"]:
                poke_type["resisted_by"].append(t["name"])

            poke_type["resistant_to"] = []
            for t in api_data["damage_relations"]["half_damage_from"]:
                poke_type["resistant_to"].append(t["name"])

            poke_type["immunities"] = []
            for t in api_data["damage_relations"]["no_damage_from"]:
                poke_type["immunities"].append(t["name"])

            poke_type["no_effect"] = []
            for t in api_data["damage_relations"]["no_damage_to"]:
                poke_type["no_effect"].append(t["name"])

            processed_data.append(poke_type)

        with open('types.json', 'w') as outfile:
            json.dump(processed_data, outfile, indent=4)

        print("types.json created successfully")
        return types_data_class(processed_data)

def types_data_class(types_json):
    types_by_name = {}

    for data in types_json:
        types_by_name[data["name"]] = Type(
            id = data["id"],
            type_name = data["name"]
        )

    for poke_type in types_json:
        current = types_by_name[poke_type["name"]]

        current.strengths = {
            type_name: types_by_name[type_name]
            for type_name in poke_type["strengths"]
            if type_name in types_by_name
        }

        current.weaknesses = {
            type_name: types_by_name[type_name]
            for type_name in poke_type["weaknesses"]
            if type_name in types_by_name
        }

        current.resisted_by = {
            type_name: types_by_name[type_name]
            for type_name in poke_type["resisted_by"]
            if type_name in types_by_name
        }

        current.resistant_to = {
            type_name: types_by_name[type_name]
            for type_name in poke_type["resistant_to"]
            if type_name in types_by_name
        }

        current.immunities = {
            type_name: types_by_name[type_name]
            for type_name in poke_type["immunities"]
            if type_name in types_by_name
        }

        current.no_effect = {
            type_name: types_by_name[type_name]
            for type_name in poke_type["no_effect"]
            if type_name in types_by_name
        }

    return types_by_name

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

        processed_data = []

        # Goes through the unprocessed API data and only processes the moves data that is relevant and saves it to local json.
        for api_data in details:
            move = {"id": api_data["id"],
                    "name": api_data["name"],
                    "accuracy": api_data["accuracy"],
                    "damage_type": api_data["damage_class"]["name"]
                    }

            processed_data.append(move)

        with open('moves.json', 'w') as outfile:
            json.dump(processed_data, outfile, indent=4)

        print("moves.json created successfully")
        return moves_data_class(processed_data)

def moves_data_class(data):
    poke_moves = {}

    for m in data:
        move = Move()
        move.move_name = m["name"]
        move.accuracy = m["accuracy"]
        move.damage_type = m["damage_type"]
        poke_moves[move.move_name] = move

    return poke_moves

###########
# POKEMON #
###########

async def import_all_pokemon(move_data, type_data):
    pokemon_url = f"{base_url}/pokemon?limit=2000"
    print("Retrieving pokemon data...")

    if find_json_file('pokemon.json'):
        with open('pokemon.json', 'r') as file:
            print("Pokemon loaded from file successfully")
            return pokemon_data_class(json.load(file), move_data, type_data)

    async with aiohttp.ClientSession() as session:

        pokemon_data = await get_api_data(session, pokemon_url)

        tasks = []
        for p in pokemon_data["results"]:
            tasks.append(get_api_data(session, p["url"]))
        details = await asyncio.gather(*tasks)

        processed_data = []

        # Goes through the unprocessed API data and only processes the Pokemon data that is relevant and saves it to local json.
        for api_data in details:

            pkmn = { "id": api_data["id"],
                     "name": api_data["name"],
                     "height": api_data["height"],
                     "types": [],
                     "stats": api_data["stats"],
                     "abilities": api_data["abilities"],
                     "moves": []
            }

            for t in api_data["types"]:
                pkmn["types"].append(t["type"]["name"])

            for m in api_data["moves"]:
                pkmn["moves"].append(m["move"]["name"])

            processed_data.append(pkmn)

        with open('pokemon.json', 'w') as outfile:
            json.dump(processed_data, outfile, indent=4)

        print("pokemon.json created successfully")
        return pokemon_data_class(processed_data, move_data, type_data)

def pokemon_data_class(data, move_data, type_data):
    poke_list = {}

    for p in data:
        poke = Pokemon()
        poke.id = p["id"]
        poke.species_name = p["name"]

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


        for move_name in p["moves"]:
            if move_name in move_data:
                poke.moves[move_name] = move_data[move_name]

        for type_name in p["types"]:
            if type_name in type_data:
                poke.types[type_name] = type_data[type_name]

        poke_list[poke.species_name] = poke

    return poke_list


def build_move_lookup(pokemon_db):
    moves_lookup = {}

    for pokemon in pokemon_db.values():
        for move in pokemon.moves:
            if move not in moves_lookup:
                moves_lookup[move] = []
            moves_lookup[move].append(pokemon)

    return moves_lookup

def build_type_lookup(pokemon_db):
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
    type_data = await import_all_types()
    moves_data = await import_all_moves()
    #ability_data = await import_all_abilities()
    pokemon_data = await import_all_pokemon(moves_data, type_data)

    move_lookup = build_move_lookup(pokemon_data)
    type_lookup = build_type_lookup(pokemon_data)

    main_menu(pokemon_data, move_lookup, type_lookup)

def main_menu(pokemon_data, move_lookup, type_lookup):
    while True:
        choice = input("choice: ")
        match choice:
            case "moves":
                moves_menu(move_lookup)
            case "types":
                pass
            case "pokemon":
                poke_menu(pokemon_data)
                #moves_menu(move_lookup)
            case "exit":
                break
            case _:
                pass

def moves_menu(move_lookup):
    while True:
        move_search = input("Search for a move: ")
        if move_search == "back":
            return
        if move_search in move_lookup:
            print("The following pokemon can learn " + move_search + ":")
            for pokemon in move_lookup[move_search]:
                print(pokemon.species_name)
            print("\n")

def poke_menu(pokemon_list):
    while True:
        poke_search = input("Search for a pokemon: ")
        if poke_search == "back":
            return
        if poke_search in pokemon_list:
            print(pokemon_list[poke_search])
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
