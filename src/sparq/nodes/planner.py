from sparq.schemas.state import State
from sparq.schemas.output_schemas import Plan
from sparq.settings import Settings
from sparq.utils import helpers

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from langchain_core.prompts import BasePromptTemplate, PromptTemplate

def planner_node(state: State, **kwargs):
    """
    Create a plan to answer the user query

    Args:
        state (State): The current state containing the user query.
        **kwargs: Additional keyword arguments including:
            - sys_prompt (str): The system prompt template for the planner.
            - llm: The language model to use for planning.
            - settings (Settings): The settings object containing configuration.

    Returns:
        dict: A dictionary containing the generated plan, data manifest, and dataframe summaries.
    """
    print("Making a plan to answer your query")
    
    sys_prompt = kwargs['sys_prompt']
    llm = kwargs['llm']
    settings: Settings = kwargs['settings']
    
    # load manifest
    manifest_path = settings.DATA_MANIFEST_PATH    
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
    
    print("Created plan")
    return {'plan': plan, 'data_manifest': manifest, 'df_summaries': df_summaries}

def test_planner():
    print("Running test code for planner.py")
    
    config = Config()
    llm = helpers.get_llm()
    system_prompt = "Create a plan to answer the user query"
    user_query = "What is the relation between time of day and traffic in Kuala Lumpur, Malaysia?"
    input = {"query": user_query}
    
    response = planner_node(state=input, sys_prompt=system_prompt, llm=llm, config=config)
    print(response['plan'].pretty_print())
    
if __name__ == "__main__":
    test_planner()