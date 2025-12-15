from pathlib import Path
from typing import Dict
import os
import sys

class Settings:
    """Default settings for SPARQ with sensible defaults.
    
    To override, create a subclass and provide your own values or
    pass in different paths during initialization.

    Values that can be overridden:
    - config_path: Path to the LLM configuration TOML file.
    - prompts_dir: Directory containing prompt text files.
    """
    def __init__(self, prompts_dir: Path = None, config_path: Path = None):
        # Set package and project root directories
        self.PACKAGE_DIR = Path(__file__).parent
        self.PROJECT_ROOT = Path(__file__).parent.parent.parent

        if os.isatty(0):
            self._verify_project_root()

        # Load environment variables from .env file if it exists
        self._load_env_variables()
        self._verify_env_variables()

        # Create .config/sparq directory
        self._create_dot_config_dir()

        # Load configuration
        self.CONFIG_PATH = config_path or (self.PACKAGE_DIR / "default_config.toml")
        self.CONFIG = self.load_config(self.CONFIG_PATH)

        self.LLM_CONFIG = self.CONFIG['llm_config']
        self.OUTPUT_DIR = Path(os.path.expanduser(self.CONFIG['paths']['OUTPUT_DIR']))
        self.DATA_MANIFEST_PATH = Path(os.path.expanduser(self.CONFIG['paths']['DATA_MANIFEST_PATH']))
        self.DATA_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Set output directories for different agents
        self.ROUTER_OUTPUT_DIR = self.OUTPUT_DIR / "router"
        self.PLANNER_OUTPUT_DIR = self.OUTPUT_DIR / "planner"
        self.EXECUTOR_OUTPUT_DIR = self.OUTPUT_DIR / "executor"
        self.AGGREGATOR_OUTPUT_DIR = self.OUTPUT_DIR / "aggregator"

        # Create output directories
        self._create_output_dirs()
        
        # Allow override of prompts directory
        self.PROMPTS_DIR = prompts_dir or self.PACKAGE_DIR / self.CONFIG['paths']['PROMPTS_DIR']
        self.PROMPTS_DIR = Path(self.PROMPTS_DIR)
    
    def load_prompts(self) -> Dict[str, str]:
        """Load all prompts from the prompts directory."""
        from sparq.utils.helpers import load_text

        self.ROUTER_PROMPT_PATH = self.PROMPTS_DIR / "router_message.txt"
        self.PLANNER_PROMPT_PATH = self.PROMPTS_DIR / "planner_message.txt"
        self.EXPLORER_PROMPT_PATH = self.PROMPTS_DIR / "explorer_message.txt"
        self.ANALYZER_PROMPT_PATH = self.PROMPTS_DIR / "analyzer_message.txt"
        self.EXECUTOR_PROMPT_PATH = self.PROMPTS_DIR / "executor_message.txt"
        self.AGGREGATOR_PROMPT_PATH = self.PROMPTS_DIR / "aggregator_message.txt"
        
        return {
            'router_prompt': load_text(self.ROUTER_PROMPT_PATH),
            'planner_prompt': load_text(self.PLANNER_PROMPT_PATH),
            'explorer_prompt': load_text(self.EXPLORER_PROMPT_PATH),
            'analyzer_prompt': load_text(self.ANALYZER_PROMPT_PATH),
            'executor_prompt': load_text(self.EXECUTOR_PROMPT_PATH),
            'aggregator_prompt': load_text(self.AGGREGATOR_PROMPT_PATH)
        }

    def load_config(self, path_to_toml_file=None):
        """
        Takes in a toml file and returns a dictionary
        with llm models and providers
        """
        import tomllib
        
        path_to_toml_file = self.CONFIG_PATH if path_to_toml_file is None else path_to_toml_file
        with open(path_to_toml_file, mode="rb") as f:
            config = tomllib.load(f)
        
        return config
    
    def _create_dot_config_dir(self):
        """Create a ~/.config/sparq directory if it doesn't exist."""
        sparq_config_dir = Path.home() / ".config" / "sparq"
        sparq_config_dir.mkdir(parents=True, exist_ok=True)
    
    def _create_output_dirs(self):
        """Create output directories if they don't exist."""
        dirs = [
            self.OUTPUT_DIR,
            self.ROUTER_OUTPUT_DIR,
            self.PLANNER_OUTPUT_DIR,
            self.EXECUTOR_OUTPUT_DIR,
            self.AGGREGATOR_OUTPUT_DIR
        ]
        for dir in dirs:
            os.makedirs(dir, exist_ok=True)

    def _verify_project_root(self):
        """Ask user to confirm the project root directory."""
        user_input = input(f"Is '{self.PROJECT_ROOT}' the correct project root? (y/n): ")
        if user_input.lower() != 'y':
            new_path = input("Please enter the correct project root path: ")

            try:
                self.PROJECT_ROOT = Path(os.path.expanduser(new_path)).resolve()
            except Exception as e:
                raise ValueError(f"Invalid path provided: {new_path}") from e
    
    def _load_env_variables(self):
        """Load environment variables from a .env file if it exists."""
        from dotenv import load_dotenv

        env_path = self.PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)

    def _verify_env_variables(self):
        """List all loaded environment variables."""
        print("Loaded Environment Variables:\n")
        for key, value in os.environ.items():
            print(f"{key}: {value}")

        user_input = input("Do you want to continue? (y/n): ")
        if user_input.lower() != 'y':
            print("Exiting program.")
            sys.exit(0)
    

if __name__ == "__main__":
    # Test loading prompts
    settings = Settings()
    prompts = settings.load_prompts()
    print(prompts.keys())