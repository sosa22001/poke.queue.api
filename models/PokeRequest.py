from pydantic import BaseModel, Field
from typing import Optional

class PokeRequest(BaseModel):
    id : Optional[int] = Field(None, ge=1,description="ID of the request pokemon")

    pokemon_type: Optional[str] = Field(None, 
                                        description="Type of pokemon",
                                        pattern="^[a-zA-Z0-9_]+$")
    
    url: Optional[str] = Field(None,
                            description="URL of the request pokemon",
                            pattern="^https?://[a-zA-Z0-9._-]+(:[0-9]+)?(/.*)?$")
    
    status: Optional[str] = Field(None,
                            description="Status of the request pokemon",
                            pattern="^(sent|completed|failed|inprogress)$")
    
    