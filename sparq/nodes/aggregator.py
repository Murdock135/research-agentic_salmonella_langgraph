from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.prompts import BasePromptTemplate, PromptTemplate
from schemas.state import State


def aggregator_node(state: State, **kwargs):
    executor_results: dict = state['executor_results']
    prompt = kwargs['prompt']
    llm: BaseChatModel = kwargs['llm']
    
    system_prompt_template: BasePromptTemplate = PromptTemplate.from_template(prompt).partial(
        user_query=state['query'],
        # plan=str(state['plan']),
        execution_results=str(executor_results)
    )
    
    system_prompt_str: str = system_prompt_template.invoke(input={}).to_string()
    
    response: BaseMessage = llm.invoke(system_prompt_str)
    
    return {'answer': response.content}
    