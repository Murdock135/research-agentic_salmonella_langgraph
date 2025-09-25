from schemas.state import State
from config.config import Config

from langchain_core.messages import SystemMessage
from langchain_core.prompts import BasePromptTemplate, PromptTemplate
from langgraph.prebuilt import create_react_agent

from tools import tools


def _find_genetiology_sheet_path(config: Config):
    """
    Search cached datasets referenced in the manifest to find an Excel file
    that contains a sheet named "GenEtiology". Return the first match path.
    """
    import pandas as pd
    from utils.helpers import load_data_manifest
    from pathlib import Path

    manifest = load_data_manifest(config.DATA_MANIFEST_PATH)

    for dataset, info in manifest.items():
        repo_id = info.get('repo_id')
        if repo_id is None:
            continue
        try:
            dataset_path: Path = tools.get_cached_dataset_path.invoke(repo_id)
        except Exception:
            continue
        try:
            files = tools.find_csv_excel_files.invoke({'root_dir': dataset_path})
        except Exception:
            files = []
        for file in files:
            if getattr(file, 'suffix', None) == '.xlsx':
                try:
                    xls = pd.ExcelFile(file)
                    if 'GenEtiology' in xls.sheet_names:
                        return str(file)
                except Exception:
                    continue
    return None


def serotype_node(state: State, **kwargs):
    """
    Answer serotype-specific questions using ONLY the GenEtiology sheet.
    """
    print("Answering with GenEtiology serotype sheet.")

    llm = kwargs['llm']
    prompt_template_str = kwargs['prompt']
    config: Config = kwargs['config']

    from utils import helpers
    import pandas as pd

    excel_path = _find_genetiology_sheet_path(config)
    if excel_path is None:
        state['answer'] = "Could not locate an Excel file containing the GenEtiology sheet."
        return state

    try:
        df = pd.read_excel(excel_path, sheet_name='GenEtiology')
    except Exception as e:
        state['answer'] = f"Failed to load GenEtiology sheet: {e}"
        return state

    # Build lightweight context from the sheet
    preview = df.head(10).to_markdown(index=False)
    columns = list(df.columns)

    system_prompt_template: BasePromptTemplate = PromptTemplate.from_template(prompt_template_str).partial(
        sheet_path=str(excel_path),
        columns=", ".join(columns),
        preview_markdown=preview,
    )
    system_prompt_str: str = system_prompt_template.invoke(input={}).to_string()
    system_prompt: SystemMessage = SystemMessage(content=system_prompt_str)

    # Restrict tools to minimal python/data loading to ensure we only use the single sheet
    _tools = [
        tools.getpythonrepltool(),
    ]

    agent = create_react_agent(
        model=llm,
        tools=_tools,
        prompt=system_prompt,
    )

    agent_input = {"messages": [{"role": "user", "content": state['query']}]} 
    for chunks in agent.stream(agent_input, stream_mode="updates"):
        print(chunks)

    response = agent.invoke(agent_input)

    # Prefer the final text output
    try:
        final_text = response["messages"][ -1 ].content  # langgraph returns the message list
    except Exception:
        try:
            final_text = response.get('output_text')
        except Exception:
            final_text = None

    state['answer'] = final_text or "No answer produced."
    return state
