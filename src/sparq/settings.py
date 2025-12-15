from pathlib import Path
from typing import Dict

class Settings:
    """Default settings for SPARQ with sensible defaults.
    
    To override, create a subclass and provide your own values or
    pass in different paths during initialization.

    Values that can be overridden:
    - config_path: Path to the LLM configuration TOML file.
    - prompts_dir: Directory containing prompt text files.
    """
    
    def __init__(self, prompts_dir: Path = None, config_path: Path = None):
        # Get package directory
        self.PACKAGE_DIR = Path(__file__).parent

        # Load configuration
        self.CONFIG_PATH = config_path or (self.PACKAGE_DIR / "default_config.toml")
        self.CONFIG = self.load_config(self.CONFIG_PATH)

        self.LLM_CONFIG = self.CONFIG['llm_config']
        self.RUN_OUTPUT_DIR = self.CONFIG['output_paths']['RUN_OUTPUT_DIR']
        
        # Allow override of prompts directory
        self.PROMPTS_DIR = prompts_dir or (self.CONFIG["prompts_dir"])
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


if __name__ == "__main__":
    # Test loading prompts
    settings = Settings()
    prompts = settings.load_prompts()
    print(prompts.keys())