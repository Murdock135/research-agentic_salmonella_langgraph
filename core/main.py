# custom
from config.config import Config
from utils import helpers
from schemas.output_schemas import Plan, Router, ExecutorOutput
from tools import tools

from typing import TypedDict, Annotated, Sequence
from functools import partial
import argparse
import os

from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.prompts import PromptTemplate, BasePromptTemplate
from langchain_core.prompt_values import PromptValue
from langgraph.types import RetryPolicy
import pydantic_core
from pydantic import BaseModel, Field
from rich import print

def get_llms(llm_config: dict):
    router_config = llm_config['router']
    explorer_config = llm_config['explorer']
    planner_config = llm_config['planner']
    analyzer_config = llm_config['analyzer']
    executor_config = llm_config['executor']
    aggregator_config = llm_config['aggregator']
    
    get_llm = helpers.get_llm
    
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
    route: bool | None
    answer: str | None
    plan: Plan | None
    
    # data-specific
    data_manifest: dict
    df_summaries: dict
    
    # executor-specific
    executor_results: dict
    
def router_func(router_output):
    """
    Function to determine the route of the query
    """
    return router_output['route']
    
def router_node(state: State, **kwargs):
    """
    Route the user query to the appropriate node based on the type of query
    """
    llm = kwargs['llm']
    prompt = kwargs['prompt']
    
    agent = create_react_agent(
        model=llm,
        tools=[],
        prompt=SystemMessage(content=prompt),
        response_format=(prompt, Router) # follow issue https://github.com/langchain-ai/langgraph/discussions/3794#discussioncomment-12578403
    )
    
    # invoke agent and stream the response
    agent_input = {"messages": [{"role": "user", "content": state['query']}]}
    for chunks in agent.stream(agent_input, stream_mode="updates"):
        print(chunks)
        
    response = agent.invoke(agent_input)
    output =  {
        'route': response["structured_response"].route,
        'answer': response["structured_response"].answer,
    }
    # if output['route'] is False:
    #     print(output['answer'])
    
    return output
    
def planner_node(state: State, **kwargs):
    """
    Create a plan to answer the user query
    """
    
    sys_prompt = kwargs['sys_prompt']
    llm = kwargs['llm']
    config: Config = kwargs['config']
    
    # load manifest
    manifest_path = os.path.join(config.BASE_DIR, "data_manifest.json")
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"No data manifest found in {manifest_path}.")
    
    manifest: dict = helpers.load_data_manifest(manifest_path)
    manifest_str = str(manifest)
    
    # load df summaries
    df_summaries = helpers.get_df_summaries_from_manifest(manifest)
    df_summaries_str = str(df_summaries)

    # create system prompt
    system_prompt_template: BasePromptTemplate = PromptTemplate.from_template(sys_prompt).partial(
        data_manifest=manifest_str,
        df_summaries=df_summaries_str
    )
    _system_prompt: str = system_prompt_template.invoke(input={}).to_string()
    system_prompt: SystemMessage = SystemMessage(content=_system_prompt)
    
    # create the ReAct agent
    agent = create_react_agent(
        model=llm,
        tools=[],
        prompt=system_prompt,
        response_format=Plan
    )
    
    # invoke agent and stream the response
    agent_input = {"messages": [{"role": "user", "content": state['query']}]}
    for chunks in agent.stream(agent_input, stream_mode="updates"):
        print(chunks)
        
    response = agent.invoke(agent_input)
            
    plan = response["structured_response"]
    return {'plan': plan, 'data_manifest': manifest, 'df_summaries': df_summaries}



def executor_node(state: State, **kwargs):
    """
    Execute the plan
    """
    plan: Plan = state['plan']
    llm = kwargs['llm']
    prompt = kwargs['prompt']
    output_dir = kwargs['output_dir']
    
    data_manifest = state['data_manifest']
    df_summaries = state['df_summaries']
    
    _tools = [
        tools.load_dataset,
        tools.get_sheet_names,
        tools.getpythonrepltool(),
        tools.find_csv_excel_files,
        tools.get_cached_dataset_path,
    ] + (tools.filesystemtools(working_dir=output_dir,
                                   selected_tools=['write_file', 'read_file', 'list_directory', 'file_search']))
    
    # TODO: Create prompt with previous code and messages
    system_prompt_template: BasePromptTemplate = PromptTemplate.from_template(prompt).partial(
        data_manifest=str(data_manifest),
        df_summaries=str(df_summaries),
    )
    system_prompt_str: str = system_prompt_template.invoke(input={}).to_string()
    system_prompt: SystemMessage = SystemMessage(content=system_prompt_str)
    
    # instantiate checkpointer to save results of each step
    from langgraph.checkpoint.memory import InMemorySaver
    checkpointer = InMemorySaver()
    config = {"configurable": {"thread_id" : "1"}}
    
    # create the ReAct agent
    agent = create_react_agent(
        model=llm,
        tools=_tools,
        prompt=system_prompt,
        response_format=(prompt, ExecutorOutput),
        checkpointer=checkpointer
    )
    
    def process_step(results: dict, step_description, step_index, config):
        agent_input = {"messages": [{"role": "user", "content": step_description}]}
        response = agent.invoke(agent_input, config)
        structured_response = response["structured_response"]

        # store response in results_dict
        outer_dict_key = f"Step {step_index}: {step_description}"
        results[outer_dict_key] = {} # make each key a dict
        inner_dict = results[outer_dict_key] # create reference to inner dict
        
        inner_dict['code'] = structured_response.code
        inner_dict['execution_results'] = structured_response.execution_results
        inner_dict['files_generated'] = structured_response.files_generated
        inner_dict['assumptions'] = structured_response.assumptions
        inner_dict['wants'] = structured_response.wants
        inner_dict['misc'] = structured_response.misc    
        
        return results 
    
    results = {}
    for i, step in enumerate(plan.steps):
        step_description = step.step_description
        results = process_step(results, step_description, i+1, config)
        state['executor_results'] = results

    return state
        

def aggregator(state: State, **kwargs):
    pass

def main():
    pass

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the LangGraph application.")
    parser.add_argument('-t', '--test', action='store_true', help="Run in test mode with a predefined query.")
    args = parser.parse_args()

    # Initialize the configuration
    config = Config()
    llm_config = config.load_llm_config()
    llms = get_llms(llm_config)
    prompts = config.load_prompts()
    

    # complete node definitions
    router_node = partial(router_node, llm=llms['router_llm'], prompt=prompts['router_prompt'])
    planner_node = partial(planner_node, 
                           llm=llms['planner_llm'], 
                           sys_prompt=prompts['planner_prompt'], 
                           config=config)
    executor_output_dir = config.EXECUTOR_OUTPUT_DIR
    executor_node = partial(executor_node, 
                            llm=llms['executor_llm'], 
                            prompt=prompts['executor_prompt'],
                            output_dir=executor_output_dir)
    
    # build graph
    graph_init = StateGraph(state_schema=State)
    graph_init.add_node("router", router_node)
    graph_init.add_node(
        "planner", 
        planner_node,
        retry=RetryPolicy(
            max_attempts=5,
            retry_on=pydantic_core._pydantic_core.ValidationError
            )
        )
    graph_init.add_node("executor", executor_node)
    
    graph_init.add_edge(START, "router")
    graph_init.add_conditional_edges("router", router_func, {True: "planner", False: END})
    graph_init.add_edge("planner", "executor")
    graph_init.add_edge("executor", END)
    
    graph = graph_init.compile()
    
    # get user query
    user_query = helpers.get_user_query(args=args, config=llm_config)
    input = {
        "query": user_query,
    }

    # invoke graph
    result = graph.invoke(input)
    # print("=" * 50)
    # print("Output:")
    # print(result)

    print("="*50)
    print("Plan")
    print(result['plan'].pretty_print())
    
    print("="*50)
    print("Executor results")
    print("-" * 50)
    
    # print executor results
    for step, results in result['executor_results'].items():
        print(step)
        print(results)
