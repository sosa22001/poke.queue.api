import json
import logging

from fastapi import HTTPException
from models.PokeRequest import PokeRequest
from utils.database import execute_query_json
from utils.AQueue import AQueue
from utils.ABlob import ABlob


#Configurar el logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def select_pokemon_request( id: int ):
    try:
        query = "select * from pokequeue.requests where id = ?"
        params = (id,)
        result = await execute_query_json( query , params )
        result_dict = json.loads(result)
        return result_dict
    except Exception as e:
        logger.error( f"Error selecting report request {e}" )
        raise HTTPException( status_code=500 , detail="Internal Server Error" )

async def insert_pokemon_request(pokemon_request: PokeRequest) -> dict:
    try:
        # Simulate inserting the pokemon request into the database
        logger.info(f"Inserting pokemon request: {pokemon_request}")
        query = "execute pokequeue.CREATE_POKE_REQUEST ?, ?"

        params = (pokemon_request.pokemon_type,pokemon_request.sample_size,)

        result = await execute_query_json(query, params, True)
        logger.info(f"Result from database: {result}")
        result_dict = json.loads(result)
        logger.info(f"Pokemon request inserted successfully: {result_dict}")
        
        await AQueue().insert_message_on_queue(result)
        return result_dict

    except Exception as e:
        logger.error(f"Error inserting pokemon request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
async def update_pokemon_request( pokemon_request: PokeRequest) -> dict:
    try:
        query = " exec pokequeue.update_poke_request ?, ?, ? "
        if not pokemon_request.url:
            pokemon_request.url = "";

        params = ( pokemon_request.id, pokemon_request.status, pokemon_request.url  )
        result = await execute_query_json( query , params, True )
        result_dict = json.loads(result)
        return result_dict
    except Exception as e:
        logger.error( f"Error updating report request {e}" )
        raise HTTPException( status_code=500 , detail="Internal Server Error" )
    
async def get_all_request() -> dict:
    query = """
        select 
            r.id as ReportId
            , s.description as Status
            , r.type as PokemonType
            , r.url 
            , r.created 
            , r.updated
        from pokequeue.requests r 
        inner join pokequeue.status s 
        on r.id_status = s.id 
    """
    result = await execute_query_json( query  )
    result_dict = json.loads(result)
    blob = ABlob()
    for record in result_dict:
        id = record['ReportId']
        record['url'] = f"{record['url']}?{blob.generate_sas(id)}"
    return result_dict

#Funciones nuevas para la tarea:
async def delete_pokemon_request(report_id: int):
    try:
        # 1. Verificar si el reporte existe
        check_query = "SELECT * FROM pokequeue.requests WHERE id = ?"
        result = await execute_query_json(check_query, (report_id,))
        logger.info(f"Resultado de la verificación: {result}")
        if not result or result == "[]":
            raise HTTPException(status_code=404, detail="Reporte no encontrado")

        # 2. Eliminar el blob
        blob_name = f"poke_report_{report_id}.csv"
        blob = ABlob()
        blob.container_client.delete_blob(blob_name)
        logger.info(f"Blob {blob_name} eliminado exitosamente.")

        # 3. Eliminar el registro de la BD
        delete_query = "DELETE FROM pokequeue.requests WHERE id = ?"
        await execute_query_json(delete_query, (report_id,), needs_commit=True)
        logger.info(f"Reporte con ID {report_id} eliminado de la base de datos.")

        return {"detail": "Reporte eliminado correctamente"}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error al eliminar el reporte {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al eliminar reporte")
