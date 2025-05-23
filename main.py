# custom
from config import Config
import utils
from planner import Plan

from typing import TypedDict
from functools import partial

from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import SystemMessage

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
    
class State(TypedDict):
    query: str
    plan: Plan | None
    results: MessagesState | None
    
def get_user_query_node(state: State):
    """
    Get the user query from the state
    """
    
def planner_node(state: State, **kwargs):
    sys_prompt = kwargs['sys_prompt']
    llm = kwargs['llm']
    data_dir = kwargs['data_dir']
    tree = utils.get_data_paths_bash_tree(data_dir)
    
    system_prompt = SystemMessage(
        content=sys_prompt,
        tree=tree,
        data_dir=data_dir,
    )
    
    # create the ReAct agent
    agent = create_react_agent(
        model=llm,
        tools=[],
        prompt=system_prompt,
        response_format=Plan
    )
    
    response = agent.invoke(state['query'])
    plan = response["structured_response"]
    state['plan'] = plan
    
    

if __name__ == "__main__":

    # Initialize the configuration
    config = Config()
    llm_config = config.load_llm_config()
    llms = get_llms(llm_config)
    prompts = config.load_prompts()

    # complete node definitions
    planner_node = partial(planner_node, llm=llms['planner_llm'], sys_prompt=prompts['planner_prompt'])
    graph_init = StateGraph(state_schema=State)
    graph_init.add_node("planner", planner_node)
    
    # get user query
    user_query = "What is langchain?"
    input = {
        "query": user_query,
        "plan": None,
        "results": None
    }
    print(0)