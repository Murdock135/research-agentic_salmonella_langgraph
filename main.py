# custom
from config import Config
import utils
from output_schemas import Plan, Router

from typing import TypedDict
from functools import partial

from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import SystemMessage
from langgraph.types import RetryPolicy
import pydantic_core

def get_llms(llm_config: dict):
    router_config = llm_config['router']
    explorer_config = llm_config['explorer']
    planner_config = llm_config['planner']
    analyzer_config = llm_config['analyzer']
    executor_config = llm_config['executor']
    aggregator_config = llm_config['aggregator']
    
    get_llm = utils.get_llm
    
    return {
        'router_llm': get_llm(model=router_config['model'], provider=router_config['provider']),
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
    
def router_node(state: State, **kwargs):
    """
    Route the user query to the appropriate node based on the type of query
    """
    llm = kwargs['llm']
    prompt = """"You are a 'router'. You will receive the user's message and decide whether it requires further planning to answer, in which case you will say 'True'
    "or if it can be answered directly, in which case you will say 'False'. If you say 'False', you will also provide the answer to the user's question.
    
    Your output should simply be either 'True' or 'False'. And if it's 'False', then 'answer': <answer>
    
    Examples
    (1) User: What is langchain?
    Router: False
    answer: <your answer here>
    
    (2) User: What is the average age of the people in the dataset?
    Router: True
    """
    
    agent = create_react_agent(
        model=llm,
        tools=[],
        prompt=SystemMessage(content=prompt),
        response_format=Router
    )
    
    agent_input = {"messages": [{"role": "user", "content": state['query']}]}
    response = agent.invoke(agent_input)
    
    return response["structured_response"]
    
def planner_node(state: State, **kwargs):
    """
    Create a plan to answer the user query
    """
    
    sys_prompt = kwargs['sys_prompt']
    llm = kwargs['llm']
    data_dir = kwargs['data_dir']
    tree = utils.get_data_paths_bash_tree(data_dir)
    df_heads = kwargs['df_heads']
    
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
    
    agent_input = {"messages": [{"role": "user", "content": state['query']}]}
    response = agent.invoke(agent_input)
            
    plan = response["structured_response"]
    state['plan'] = plan
    
    plan.pretty_print()
    
    # May need to return a State-like dict

def executor_node(state: State, **kwargs):
    """
    Execute the plan
    """
    pass

if __name__ == "__main__":

    # Initialize the configuration
    config = Config()
    llm_config = config.load_llm_config()
    llms = get_llms(llm_config)
    prompts = config.load_prompts()
    data_dir = config.SELECTED_DATA_DIR
    df_heads = utils.get_df_heads(data_dir)

    # complete node definitions
    router_node = partial(router_node, llm=llms['router_llm'])
    planner_node = partial(planner_node, 
                           llm=llms['planner_llm'], 
                           sys_prompt=prompts['planner_prompt'], 
                           data_dir=data_dir,
                           df_heads=df_heads)
    
    # build graph
    graph_init = StateGraph(state_schema=State)
    graph_init.add_node(
        "planner", 
        planner_node,
        retry=RetryPolicy(
            max_attempts=5,
            retry_on=pydantic_core._pydantic_core.ValidationError
            )
        )
    graph_init.add_edge(START, "planner")
    
    graph = graph_init.compile()
    
    # get user query
    user_query = "What is langchain?"
    input = {
        "query": user_query,
        "plan": None,
        "results": None
    }
    
    # invoke graph
    graph.invoke(input)
    print(0)