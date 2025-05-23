from pydantic import BaseModel, Field
from typing import List, Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages

# Define desired output structure
class Step(BaseModel):
    """Information about a step"""
    step_description: str = Field(..., description="Description of the analytical step")
    datasets: List[str] = Field(..., description="List of dataset names used")
    rationale: str = Field(..., description="Why this step is necessary")
    task_type: List[str] = Field(..., description="The type of computation required e.g. data_retrieval, correlation, visualization")
    
class Plan(BaseModel):
    """Information about the the steps in a plan to answer the user query"""
    steps: List[Step]
    wants: str = Field(..., description="Further information you need to make a better plan")
    misc: str = Field(..., description="Anything else you want the user to know or just a general scratchpad")

    def pretty_print(self):
        for i, step in enumerate(self.steps):
            print(f"Step {i}")
            print(f"Description: {step.step_description}")
            print(f"Datasets: {step.datasets}")
            print(f"Rationale: {step.rationale}")
            print(f"Tast Type: {step.task_type}")
            print()
        
        print("Wants:")
        print(self.wants)
        print("Misc:")
        print(self.misc)