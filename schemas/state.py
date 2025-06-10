from typing import TypedDict
from .output_schemas import Plan

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