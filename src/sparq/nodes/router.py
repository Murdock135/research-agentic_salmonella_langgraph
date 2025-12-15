from sparq.schemas.state import State
from sparq.schemas.output_schemas import Router

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage

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
    
    return output
