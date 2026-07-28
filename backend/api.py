from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from main import build_database, pokemon_to_dict

pokemon_db = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pokemon_db

    print("Loading database...")
    try:
        database = await build_database()
        pokemon_db = database["pokemon"]
        print("Database loaded")
    except Exception:
        raise
    yield

app = FastAPI(lifespan=lifespan)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/pokemon")
def get_all_pokemon():
    return [
        pokemon_to_dict(p)
        for p in pokemon_db.values()
    ]

@app.get("/pokemon/search")
@limiter.limit("30/minute")
def search_pokemon(request: Request, q: str = Query("", min_length=1, max_length=30)):
    q = q.lower()

    results = [
        {
            "id": p.id,
            "name": p.species_name,
            "sprite": p.sprite
        }
        for p in pokemon_db.values()
        if p.species_name.lower().startswith(q)
    ]
    return results[:10]

@app.get("/pokemon/{name}")
def get_pokemon(name: str):
    pokemon = pokemon_db.get(name.lower())
    if pokemon is None:
        return {
            "error": "not found"
        }
    return pokemon_to_dict(pokemon)

@app.get("/health")
def health():
    return {
        "status": "ok"
    }