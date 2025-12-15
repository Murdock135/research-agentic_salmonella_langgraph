
from sparq.settings import Settings
from sparq.utils import helpers
from sparq.system import Agentic_system
import argparse
import asyncio

def main():
    settings = Settings()

    parser = argparse.ArgumentParser(description="Run the LangGraph application.")
    parser.add_argument('-t', '--test', action='store_true', help="Run in test mode with a predefined query.")
    args = parser.parse_args()

    user_query = helpers.get_user_query(args=args, config=settings.LLM_CONFIG)

    agentic_system_instance = Agentic_system(settings=settings)
    asyncio.run(agentic_system_instance.run(user_query=user_query))

if __name__ == "__main__":
    main()
