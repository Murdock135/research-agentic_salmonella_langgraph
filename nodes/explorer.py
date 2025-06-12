from schemas.state import State
from schemas.output_schemas import Plan, ExecutorOutput
from tools import tools

from langchain_core.prompts import BasePromptTemplate, PromptTemplate
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

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
