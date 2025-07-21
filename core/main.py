# custom
from config.config import Config
from utils import helpers

import argparse
import asyncio

from .system import agentic_system



if __name__ == "__main__":
    config = Config()

    parser = argparse.ArgumentParser(description="Run the LangGraph application.")
    parser.add_argument('-t', '--test', action='store_true', help="Run in test mode with a predefined query.")
    args = parser.parse_args()

    user_query = helpers.get_user_query(args=args, config=config.load_llm_config())

    agentic_system_instance = agentic_system(config=config)
    asyncio.run(agentic_system_instance.run(user_query=user_query))