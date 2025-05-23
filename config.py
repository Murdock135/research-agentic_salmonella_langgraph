import os
import datetime

from utils import load_text
from load_env import load_env_vars

class Config:
    def __init__(self):
        # Load environment variables
        load_env_vars()
        
        # Set the base directory to the directory of this file
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # Path to llm config toml
        self.LLM_CONFIG_PATH = os.path.join(self.BASE_DIR, 'config.toml')
        
        # Path to system messages
        self.PROMPT_DIR = os.path.join(self.BASE_DIR, 'sys_messages')
        self.PLANNER_PROMPT_PATH = os.path.join(self.PROMPT_DIR, 'planner_message.txt')
        self.EXPLORER_PROMPT_PATH = os.path.join(self.PROMPT_DIR, 'explorer_message.txt')
        self.ANALYZER_PROMPT_PATH = os.path.join(self.PROMPT_DIR, 'analyzer_message.txt')
        self.EXECUTOR_PROMPT_PATH = os.path.join(self.PROMPT_DIR, 'executor_message.txt')
        self.AGGREGATOR_PROMPT_PATH = os.path.join(self.PROMPT_DIR, 'aggregator_message.txt')
        
        # Path to user messages
        self.EXPLORER_MESSAGE_PATH = os.path.join(self.PROMPT_DIR, 'explorer_user_message.txt')

        # Data directories
        self.DATA_DIR = os.path.join(self.BASE_DIR, 'data')
        self.RAW_DATA_DIR = os.path.join(self.DATA_DIR, 'raw')
        self.PROCESSED_DATA_DIR = os.path.join(self.DATA_DIR, 'processed')
        self.SQL_DATA_DIR = os.path.join(self.DATA_DIR, 'SQL version')

        # Specific Data directories
        self.MMG_DATA_DIR = os.path.join(self.RAW_DATA_DIR, 'mmg')
        self.PN_DATA_DIR = os.path.join(self.RAW_DATA_DIR, 'pulsenet')
        self.SVI_DATA_DIR = os.path.join(self.RAW_DATA_DIR, 'social_vulnerability_index')
        self.RAW_POULTRY_DATA_DIR = os.path.join(self.RAW_DATA_DIR, 'raw_poultry')
        self.CENSUS_DATA_DIR = os.path.join(self.RAW_DATA_DIR, 'census')
        self.NORS_DATA_DIR = os.path.join(self.RAW_DATA_DIR, 'nors')
        self.FOODNET_DATA_DIR = os.path.join(self.RAW_DATA_DIR, 'foodnet')
        self.SOCIOECONO_SALMONELLA_DIR = os.path.join(self.PROCESSED_DATA_DIR, 'salmonella_population')

        # Selected data directories
        self.SELECTED_DATA_DIR = os.path.join(self.BASE_DIR, 'selected_data')
        self.SELECTED_MMG_DIR = os.path.join(self.SELECTED_DATA_DIR, 'mmg')
        self.SELECTED_NORS_DIR = os.path.join(self.SELECTED_DATA_DIR, 'nors')
        self.SELECTED_SVI_DIR = os.path.join(self.SELECTED_DATA_DIR, 'svi')
        self.SELECTED_SOCIOECONO_SALMONELLA = os.path.join(self.SELECTED_DATA_DIR, 'sense-d_socioecono_salmonella_MO_2020.csv')

        # Set the output directories relative to the base directory
        self.OUTPUT_DIR = os.path.join(self.BASE_DIR, 'output')
        os.makedirs(self.OUTPUT_DIR, exist_ok=True) # Create output directory if it doesn't exist

        # Create output directory for a specific run
        self.RUN_OUTPUT_DIR = self.create_output_directory_for_run()
        
        # Create output directories for all llms
        self.PLANNER_OUTPUT_DIR = os.path.join(self.RUN_OUTPUT_DIR, 'planner')
        self.EXPLORER_OUTPUT_DIR = os.path.join(self.RUN_OUTPUT_DIR, 'explorer')
        self.ANALYZER_OUTPUT_DIR = os.path.join(self.RUN_OUTPUT_DIR, 'analyzer')
        self.EXECUTOR_OUTPUT_DIR = os.path.join(self.RUN_OUTPUT_DIR, 'executor')
        self.AGGREGATOR_OUTPUT_DIR = os.path.join(self.RUN_OUTPUT_DIR, 'aggregator')
        
        llm_output_dirs = [
            self.PLANNER_OUTPUT_DIR,
            self.EXPLORER_OUTPUT_DIR,
            self.ANALYZER_OUTPUT_DIR,
            self.EXECUTOR_OUTPUT_DIR,
            self.AGGREGATOR_OUTPUT_DIR
        ]
        
        for dir in llm_output_dirs:
            os.makedirs(dir, exist_ok=True)
    
    def get_selected_data_paths(self):
        return {
            'mmg': self.SELECTED_MMG_DIR,
            'nors': self.SELECTED_NORS_DIR,
            'svi': self.SELECTED_SVI_DIR,
            'socioecono_salmonella': self.SELECTED_SOCIOECONO_SALMONELLA
        }
    
    def load_prompts(self):
        return {
            'planner_prompt': load_text(self.PLANNER_PROMPT_PATH),
            'explorer_prompt': load_text(self.EXPLORER_PROMPT_PATH),
            'analyzer_prompt': load_text(self.ANALYZER_PROMPT_PATH),
            'executor_prompt': load_text(self.EXECUTOR_PROMPT_PATH),
            'aggregator_prompt': load_text(self.AGGREGATOR_PROMPT_PATH)
        }
        
    def load_user_messages(self):
        return {
            'explorer_user_message': load_text(self.EXPLORER_MESSAGE_PATH)
        }
        
    def load_llm_config(self, path_to_toml_file=None):
        """
        Takes in a toml file and returns a dictionary
        with llm models and providers
        """
        import tomllib
        
        path_to_toml_file = self.LLM_CONFIG_PATH if path_to_toml_file is None else path_to_toml_file
        with open(path_to_toml_file, mode="rb") as f:
            llm_config = tomllib.load(f)
        
        return llm_config
        
    def create_output_directory_for_run(self):
        format = "%d-%m-%Y_%H-%M-%S"
        now = datetime.datetime.now()
        now_str = now.strftime(format)
        RUN_OUTPUT_DIR = os.path.join(self.OUTPUT_DIR, f"output_{now_str}")
        os.makedirs(RUN_OUTPUT_DIR, exist_ok=True)
        
        return RUN_OUTPUT_DIR
    
# Create main guard to test the Config class
if __name__ == "__main__":
    config = Config()
    print("Base Directory: ", config.BASE_DIR)
    print("Data Directory: ", config.DATA_DIR)
    print("Raw Data Directory: ", config.RAW_DATA_DIR)
    print("Processed Data Directory: ", config.PROCESSED_DATA_DIR)
    print("SQL Data Directory: ", config.SQL_DATA_DIR)
    print("MMG Data Directory: ", config.MMG_DATA_DIR)
    print("PN Data Directory: ", config.PN_DATA_DIR)
    print("SVI Data Directory: ", config.SVI_DATA_DIR)
    print("Raw Poultry Data Directory: ", config.RAW_POULTRY_DATA_DIR)
    print("Census Data Directory: ", config.CENSUS_DATA_DIR)
    print("NORS Data Directory: ", config.NORS_DATA_DIR)
    print("FoodNet Data Directory: ", config.FOODNET_DATA_DIR)
    print("Socioeconomic Salmonella Data Directory: ", config.SOCIOECONO_SALMONELLA_DIR)
    print("Selected Data Directory: ", config.SELECTED_DATA_DIR)
    print("Selected MMG Directory: ", config.SELECTED_MMG_DIR)
    print("Selected NORS Directory: ", config.SELECTED_NORS_DIR)
    print("Selected SVI Directory: ", config.SELECTED_SVI_DIR)
    print("Selected Socioeconomic Salmonella Directory: ", config.SELECTED_SOCIOECONO_SALMONELLA)
    print("Output Directory: ", config.OUTPUT_DIR)
    print("Run Output Directory: ", config.RUN_OUTPUT_DIR)
    print("Planner Output Directory: ", config.PLANNER_OUTPUT_DIR)
    print("Explorer Output Directory: ", config.EXPLORER_OUTPUT_DIR)
    print("Analyzer Output Directory: ", config.ANALYZER_OUTPUT_DIR)
    print("Executor Output Directory: ", config.EXECUTOR_OUTPUT_DIR)
    print("Aggregator Output Directory: ", config.AGGREGATOR_OUTPUT_DIR)
    print("Selected Data Paths: ", config.get_selected_data_paths())
    print("Prompts: ", config.load_prompts())







