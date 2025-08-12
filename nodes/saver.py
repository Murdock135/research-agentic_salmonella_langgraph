from schemas.state import State

import json
from pathlib import Path

def saver_node(state: State, save_dir: Path):
    save_path = save_dir / 'trace.json'
    with open(save_path, 'w') as file:
        json.dump(state, file, indent=4)
