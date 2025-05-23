# custom
from load_env import load_env_vars
from config import Config
import utils

# stdlib
from typing import TypedDict, Annotated

# langgraph imports
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages

def get_llms(llm_config: dict):
    explorer_config = llm_config['explorer']
    planner_config = llm_config['planner']
    analyzer_config = llm_config['analyzer']
    executor_config = llm_config['executor']
    aggregator_config = llm_config['aggregator']
    
    get_llm = utils.get_llm
    
    return {
        'explorer_llm': get_llm(model=explorer_config['model'], provider=explorer_config['provider']),
        'planner_llm': get_llm(model=planner_config['model'], provider=planner_config['provider']),
        'analyzer_llm': get_llm(model=analyzer_config['model'], provider=analyzer_config['provider']),
        'executor_llm': get_llm(model=executor_config['model'], provider=executor_config['provider']),
        'aggregator_llm': get_llm(model=aggregator_config['model'], provider=aggregator_config['provider'])
    }
    

if __name__ == "__main__":

    # Initialize the configuration
    config = Config()
    llm_config = config.load_llm_config()
    llms = get_llms(llm_config)
    
    print(llms)