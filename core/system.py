from config.config import Config
from functools import partial

from nodes.planner import planner_node
from nodes.executor import executor_node
from nodes.router import router_func, router_node
from nodes.aggregator import aggregator_node
from nodes.saver import saver_node
from schemas.state import State

from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
import pydantic_core
from rich import print

class Agentic_system:
    def __init__(self, config: Config):
        self.config = config
        self.llm_config = config.load_llm_config()
        self.llms = self._get_llms()
        self.prompts = config.load_prompts()

    def _get_llms(self):
        from utils.helpers import get_llm
        
        router_config = self.llm_config['router']
        explorer_config = self.llm_config['explorer']
        planner_config = self.llm_config['planner']
        analyzer_config = self.llm_config['analyzer']
        executor_config = self.llm_config['executor']
        aggregator_config = self.llm_config['aggregator']
        
        return {
            'router_llm': get_llm(model=router_config['model'], provider=router_config['provider']),
            'explorer_llm': get_llm(model=explorer_config['model'], provider=explorer_config['provider']),
            'planner_llm': get_llm(model=planner_config['model'], provider=planner_config['provider']),
            'analyzer_llm': get_llm(model=analyzer_config['model'], provider=analyzer_config['provider']),
            'executor_llm': get_llm(model=executor_config['model'], provider=executor_config['provider']),
            'aggregator_llm': get_llm(model=aggregator_config['model'], provider=aggregator_config['provider'])
        }
    
    def _get_node_definitions(self):
        self.router_node_partial = partial(router_node, llm=self.llms['router_llm'], prompt=self.prompts['router_prompt'])
        self.planner_node_partial = partial(planner_node, llm=self.llms['planner_llm'], sys_prompt=self.prompts['planner_prompt'], config=self.config)
        self.executor_node_partial = partial(executor_node, llm=self.llms['executor_llm'], prompt=self.prompts['executor_prompt'], output_dir=self.config.EXECUTOR_OUTPUT_DIR)
        self.aggregator_node_partial = partial(aggregator_node, llm=self.llms['aggregator_llm'], prompt=self.prompts['aggregator_prompt'])
    
    def _build_graph(self):
        graph_init = StateGraph(state_schema=State)
        graph_init.add_node("router", self.router_node_partial)
        graph_init.add_node(
            "planner", 
            self.planner_node_partial,
            retry=RetryPolicy(
                max_attempts=5,
                retry_on=pydantic_core._pydantic_core.ValidationError
                )
            )
        graph_init.add_node("executor", self.executor_node_partial)
        graph_init.add_node("aggregator", self.aggregator_node_partial)
        
        graph_init.add_edge(START, "router")
        graph_init.add_conditional_edges("router", router_func, {True: "planner", False: END})
        graph_init.add_edge("planner", "executor")
        graph_init.add_edge("executor", "aggregator")
        graph_init.add_edge("aggregator", END)
        
        self.graph = graph_init.compile()

    async def run(self, user_query: str):
        self._get_node_definitions()
        self._build_graph()

        input_data = {"query": user_query}
        async for chunk in self.graph.astream(input=input_data, stream_mode="updates"):
            print(chunk)

    def save_results(self):
        pass
