# custom
from config import Config
import helpers
from output_schemas import Plan, Router, ExecutorOutput
import tools

from typing import TypedDict, Annotated, Sequence
from functools import partial
import argparse

from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.prompts import PromptTemplate, BasePromptTemplate
from langchain_core.prompt_values import PromptValue
from langgraph.types import RetryPolicy
import pydantic_core
from pydantic import BaseModel, Field

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
    
    # executor-specific
    code: list
    execution_results: list
    files_generated: list
    assumptions: list
    wants: list
    misc: list
    
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
    data_dir = kwargs['data_dir']
    tree = helpers.get_data_paths_bash_tree(data_dir)
    df_heads = kwargs['df_heads']

    # create system prompt
    system_prompt_template: BasePromptTemplate = PromptTemplate.from_template(sys_prompt).partial(
        tree = tree,
        df_heads = df_heads
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
    return { 'plan': plan}
    

def executor_node(state: State, **kwargs):
    """
    Execute the plan
    """
    plan: Plan = state['plan']
    llm = kwargs['llm']
    prompt = kwargs['prompt']
    output_dir = kwargs['output_dir']
    data_dir = kwargs['data_dir']
    tree = helpers.get_data_paths_bash_tree(data_dir)
    df_heads = kwargs['df_heads']
    breakpoint()
    _tools = [
        tools.load_dataset,
        tools.get_sheet_names,
        tools.getpythonrepltool()
    ] + (tools.filesystemtools(working_dir=output_dir,
                                   selected_tools=['write_file', 'read_file', 'list_directory', 'file_search']))
    
    # TODO: Create prompt with previous code and messages
    system_prompt_template: BasePromptTemplate = PromptTemplate.from_template(prompt).partial(
        tree=tree,
        df_heads=df_heads,
    )
    system_prompt_str: str = system_prompt_template.invoke(input={}).to_string()
    system_prompt: SystemMessage = SystemMessage(content=system_prompt_str)
    
    # create the ReAct agent
    agent = create_react_agent(
        model=llm,
        tools=_tools,
        prompt=system_prompt,
        response_format=(prompt, ExecutorOutput)
    )
    breakpoint()
    for i, step in enumerate(plan.steps):
        print("-" * 50)
        print(f"Step {i+1}: {step.step_description}")
        print("-" * 50)
        
        # create input for the agent
        agent_input = {"messages": [{"role": "user", "content": step.step_description}]}
        response = agent.invoke(agent_input)
        structured_response = response["structured_response"]

        # add components of response to state
        state['code'].append(structured_response.code)
        state['execution_results'].append(structured_response.execution_results)
        state['files_generated'].append(structured_response.files_generated)
        state['assumptions'].append(structured_response.assumptions)
        state['wants'].append(structured_response.wants)
        state['misc'].append(structured_response.misc)

        # print the response
        print("Response:")
        print(response)

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
    data_dir = config.SELECTED_DATA_DIR
    df_heads = helpers.get_df_heads(data_dir)

    # complete node definitions
    router_node = partial(router_node, llm=llms['router_llm'], prompt=prompts['router_prompt'])
    planner_node = partial(planner_node, 
                           llm=llms['planner_llm'], 
                           sys_prompt=prompts['planner_prompt'], 
                           data_dir=data_dir,
                           df_heads=df_heads)
    executor_output_dir = config.EXECUTOR_OUTPUT_DIR
    executor_node = partial(executor_node, 
                            llm=llms['executor_llm'], 
                            prompt=prompts['executor_prompt'],
                            data_dir=data_dir,
                            df_heads=df_heads,
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
    print("=" * 50)
    print("Output:")
    print(result)

    print("="*50)
    print("Plan")
    print(result['plan'].pretty_print())