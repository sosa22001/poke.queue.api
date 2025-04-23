import uvicorn
import json
from fastapi import FastAPI
from utils.database import execute_query_json
from controllers.PokeRequestController import insert_pokemon_request, update_pokemon_request, select_pokemon_request, get_all_request, delete_pokemon_request
from models.PokeRequest import PokeRequest
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los encabezados
)

@app.get("/")
async def root():
    query = "select * from pokequeue.MESSAGES"
    result = await execute_query_json(query)
    result_dict = json.loads(result)
    return result_dict

@app.get("/api/version")
async def version():
    return { "version":  "0.2.0" }

@app.get("/api/request")
async def select_all_request():
    return await get_all_request()

@app.post("/api/request")
async def create_request(pokemon_request: PokeRequest):
    return await insert_pokemon_request(pokemon_request)

@app.put("/api/request")
async def update_request(pokemon_request: PokeRequest):
    return await update_pokemon_request( pokemon_request )

@app.get("/api/request/{id}")
async def select_request(id: int):
    return await select_pokemon_request(id)

@app.get("/project")
def project():
    return {"project": "poke queue"}

#Endpoints Nuevos para la tarea:
@app.delete("/api/request/{report_id}")
async def delete_report(report_id: int):
    from controllers.PokeRequestController import delete_pokemon_request
    return await delete_pokemon_request(report_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)