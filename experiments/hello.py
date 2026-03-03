import asyncio
from pathlib import Path

from sparq.system import Agentic_system
from sparq.settings import Settings
from sparq.utils.get_package_dir import get_project_root

PROJECT_ROOT = get_project_root()
if PROJECT_ROOT is None:
    raise RuntimeError("Could not determine project root directory.")

CONFIG_PATH = PROJECT_ROOT / "config.toml"

QUERY = "What is salmonella?"

def main():
    settings = Settings(
        config_path=CONFIG_PATH
    )
    
    agentic_system = Agentic_system(settings)
    
    asyncio.run(agentic_system.run(QUERY))
    
if __name__ == "__main__":
    main()
