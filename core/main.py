# custom
from config.config import Config
from utils import helpers

from functools import partial
import argparse
import asyncio

from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
import pydantic_core
from rich import print

from nodes.planner import planner_node
from nodes.executor import executor_node
from nodes.router import router_func, router_node
from nodes.aggregator import aggregator_node
from schemas.state import State

# for type hints
from langchain_core.messages import AIMessage

def get_llms(llm_config: dict):
    from utils.helpers import get_llm
    
    router_config = llm_config['router']
    explorer_config = llm_config['explorer']
    planner_config = llm_config['planner']
    analyzer_config = llm_config['analyzer']
    executor_config = llm_config['executor']
    aggregator_config = llm_config['aggregator']
    
    return {
        'router_llm': get_llm(model=router_config['model'], provider=router_config['provider']),
        'explorer_llm': get_llm(model=explorer_config['model'], provider=explorer_config['provider']),
        'planner_llm': get_llm(model=planner_config['model'], provider=planner_config['provider']),
        'analyzer_llm': get_llm(model=analyzer_config['model'], provider=analyzer_config['provider']),
        'executor_llm': get_llm(model=executor_config['model'], provider=executor_config['provider']),
        'aggregator_llm': get_llm(model=aggregator_config['model'], provider=aggregator_config['provider'])
    }

async def main():
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
    router_node_partial  = partial(router_node, llm=llms['router_llm'], prompt=prompts['router_prompt'])
    planner_node_partial = partial(planner_node, 
                           llm=llms['planner_llm'], 
                           sys_prompt=prompts['planner_prompt'], 
                           config=config)
    executor_output_dir = config.EXECUTOR_OUTPUT_DIR
    executor_node_partial = partial(executor_node, 
                            llm=llms['executor_llm'], 
                            prompt=prompts['executor_prompt'],
                            output_dir=executor_output_dir)
    aggregator_node_partial = partial(aggregator_node,
                                      llm=llms['aggregator_llm'],
                                      prompt=prompts['aggregator_prompt']
                                      )
    
    # build graph
    graph_init = StateGraph(state_schema=State)
    graph_init.add_node("router", router_node_partial)
    graph_init.add_node(
        "planner", 
        planner_node_partial,
        retry=RetryPolicy(
            max_attempts=5,
            retry_on=pydantic_core._pydantic_core.ValidationError
            )
        )
    graph_init.add_node("executor", executor_node_partial)
    graph_init.add_node("aggregator", aggregator_node_partial)
    
    graph_init.add_edge(START, "router")
    graph_init.add_conditional_edges("router", router_func, {True: "planner", False: END})
    graph_init.add_edge("planner", "executor")
    graph_init.add_edge("executor", "aggregator")
    graph_init.add_edge("aggregator", END)
    
    graph = graph_init.compile()
    
    # get user query
    user_query = helpers.get_user_query(args=args, config=llm_config)
    input = {
        "query": user_query,
    }

    # invoke graph
    # result = graph.invoke(input)
    
    # get results and stream them
    async for chunk in graph.astream(input=input, stream_mode="updates"):
        print(chunk)
    
    # # print("=" * 50)
    # # print("Output:")
    # # print(result)

    # print("="*50)
    # print("Plan")
    # print(result['plan'].pretty_print())
    
    # print("="*50)
    # print("Executor results")
    # print("-" * 50)
    
    # # print executor results
    # for step, results in result['executor_results'].items():
    #     print(step)
    #     print(results)
        
    # # print final response
    # print(result['answer'])


if __name__ == "__main__":
    asyncio.run(main())

