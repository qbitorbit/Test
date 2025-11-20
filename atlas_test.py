# atlas_test.py - Simple test for MCP + Agent + LLM integration

from langchain_openai import OpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain.prompts import PromptTemplate

# Your local LLM connection
llm = OpenAI(
    base_url="http://10.202.1.3:8000/v1",
    api_key="dummy-key",
    model="/models/openai/gpt-oss-120b",
    temperature=0.1
)

# Simple MCP-like tool
@tool
def get_device_info(device_id: str) -> str:
    """Get information about an Android device.
    
    Args:
        device_id: The device serial number
    """
    # Simulated response
    return f"Device {device_id}: Samsung Galaxy S24+, Android 14, Battery: 85%"

@tool
def execute_command(command: str) -> str:
    """Execute a shell command.
    
    Args:
        command: The command to execute
    """
    # Simulated response
    return f"Executed: {command} - Success"

# Create tools list
tools = [get_device_info, execute_command]

# Agent prompt
prompt = PromptTemplate.from_template("""Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
Thought:{agent_scratchpad}""")

# Create agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# Test
print("🧪 Testing Atlas - Basic Agent + Tools + LLM\n")
print("=" * 60)

result = agent_executor.invoke({"input": "What is the battery level of device ABC123?"})

print("\n" + "=" * 60)
print(f"✅ Result: {result['output']}")
print("\n✅ Atlas basic infrastructure works!")
