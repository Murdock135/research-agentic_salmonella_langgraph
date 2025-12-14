from pathlib import Path
from dotenv import load_dotenv
import os

DEFAULT_PATH = Path.home() / ".secrets/.llm_apis"

def load_env_vars(path=DEFAULT_PATH):
    # load ~/.secrets/.llm_apis
    load_dotenv(dotenv_path=path)

    # load project .env
    load_dotenv()

if __name__=="__main__":
    load_env_vars()
    print("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    print("LANGSMITH_API_KEY", os.getenv("LANGSMITH_API_KEY"))
    print("LANGSMITH PROJECT NAME", os.getenv("LANGSMITH_PROJECT"))
    print("GOOGLE_GENAI_API_KEY", os.getenv("GOOGLE_GENAI_API_KEY"))
