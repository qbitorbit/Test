# atlas_test.py - Simple test for MCP + Agent + LLM integration (LangChain 1.0+)

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool

# Your local LLM connection
llm = ChatOpenAI(
    base_url="http://10.202.1.3:8000/v1",
    api_key="dummy-key",
    model="/models/openai/gpt-oss-120b",
    temperature=0.1
)

# Simple MCP-like tools
@tool
def get_device_info(device_id: str) -> str:
    """Get information about an Android device.
    
    Args:
        device_id: The device serial number
    """
    return f"Device {device_id}: Samsung Galaxy S24+, Android 14, Battery: 85%"

@tool
def execute_command(command: str) -> str:
    """Execute a shell command.
    
    Args:
        command: The command to execute
    """
    return f"Executed: {command} - Success"

# Create tools list
tools = [get_device_info, execute_command]

# Create agent
agent = create_agent(
    model=llm,
    tools=tools
)

# Test
print("🧪 Testing Atlas - Basic Agent + Tools + LLM\n")
print("=" * 60)

result = agent.invoke({
    "messages": [{"role": "user", "content": "What is the battery level of device ABC123?"}]
})

print("\n" + "=" * 60)
print("📋 Full conversation:")
for msg in result['messages']:
    if hasattr(msg, 'content') and msg.content:
        print(f"\n{msg.type}: {msg.content}")
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        print(f"\n🔧 Tool calls: {msg.tool_calls}")

print("\n" + "=" * 60)
print(f"✅ Final Answer: {result['messages'][-1].content}")
print("\n✅ Atlas basic infrastructure works!")
