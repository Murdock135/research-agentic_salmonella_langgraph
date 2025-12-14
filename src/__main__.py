
from config.config import Config
from sparq.utils import helpers
from sparq.system import Agentic_system
import argparse
import asyncio

def main():
    config = Config()

    parser = argparse.ArgumentParser(description="Run the LangGraph application.")
    parser.add_argument('-t', '--test', action='store_true', help="Run in test mode with a predefined query.")
    args = parser.parse_args()

    user_query = helpers.get_user_query(args=args, config=config.load_llm_config())

    agentic_system_instance = Agentic_system(config=config)
    asyncio.run(agentic_system_instance.run(user_query=user_query))

if __name__ == "__main__":
    main()
