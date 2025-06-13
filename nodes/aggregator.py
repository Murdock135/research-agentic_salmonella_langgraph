from schemas.state import State

from langchain_core.prompts import BasePromptTemplate, PromptTemplate
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.language_models import BaseChatModel

def aggregator_node(state: State, **kwargs):
    execution_results: dict = State['execution_results']
    prompt = kwargs['prompt']
    llm: BaseChatModel = kwargs['llm']
    
    system_prompt_template: BasePromptTemplate = PromptTemplate.from_template(prompt).partial(
        user_query=state['query'],
        plan=str(state['plan']),
        execution_results=str(execution_results)
    )
    
    system_prompt_str: str = system_prompt_template.invoke(input={}).to_string()
    
    response: BaseMessage = llm.invoke(system_prompt_str)
    
    return {'answer': response.content}
    