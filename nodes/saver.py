from pydantic import BaseModel
from schemas.output_schemas import Plan
from schemas.state import State

import json
from pathlib import Path

def pydantic_encoder(obj):
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode='json')
    
    raise TypeError(f"Object of type {__obj.__class__.__name__} is not JSON serializable")

def saver_node(state: State, save_dir: Path):
    # convert state into a json-serializable 
    # breakpoint()
    
    save_path = save_dir / 'trace.json'
    with open(save_path, 'w') as file:
        json.dump(state, file, indent=4, default=pydantic_encoder)
