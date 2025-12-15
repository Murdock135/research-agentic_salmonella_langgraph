from pathlib import Path
from typing import Dict

class Settings:
    """Default settings for SPARQ with sensible defaults."""
    
    def __init__(self, prompts_dir: Path = None):
        # Get package directory
        self.PACKAGE_DIR = Path(__file__).parent
        
        # Allow override of prompts directory
        self.PROMPTS_DIR = prompts_dir or (self.PACKAGE_DIR / "prompts")
        
        # Define prompt paths
        self.ROUTER_PROMPT_PATH = self.PROMPTS_DIR / "router_message.txt"
        self.PLANNER_PROMPT_PATH = self.PROMPTS_DIR / "planner_message.txt"
        self.EXPLORER_PROMPT_PATH = self.PROMPTS_DIR / "explorer_message.txt"
        self.ANALYZER_PROMPT_PATH = self.PROMPTS_DIR / "analyzer_message.txt"
        self.EXECUTOR_PROMPT_PATH = self.PROMPTS_DIR / "executor_message.txt"
        self.AGGREGATOR_PROMPT_PATH = self.PROMPTS_DIR / "aggregator_message.txt"
    
    def load_prompts(self) -> Dict[str, str]:
        """Load all prompts from the prompts directory."""
        from sparq.utils.helpers import load_text
        
        return {
            'router_prompt': load_text(self.ROUTER_PROMPT_PATH),
            'planner_prompt': load_text(self.PLANNER_PROMPT_PATH),
            'explorer_prompt': load_text(self.EXPLORER_PROMPT_PATH),
            'analyzer_prompt': load_text(self.ANALYZER_PROMPT_PATH),
            'executor_prompt': load_text(self.EXECUTOR_PROMPT_PATH),
            'aggregator_prompt': load_text(self.AGGREGATOR_PROMPT_PATH)
        }

if __name__ == "__main__":
    # Test loading prompts
    settings = Settings()
    prompts = settings.load_prompts()
    print(prompts.keys())