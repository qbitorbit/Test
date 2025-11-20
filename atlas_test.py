# atlas_test.py - Fixed with middleware for system prompt

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.tools import tool

# Your local LLM connection
llm = ChatOpenAI(
    base_url="http://10.202.1.3:8000/v1",
    api_key="dummy-key",
    model="/models/openai/gpt-oss-120b",
    temperature=0.1
)

# Simple MCP-like tool
@tool
def get_device_info(device_id: str) -> str:
    """Get information about an Android device including battery level.
    
    Args:
        device_id: The device serial number
    
    Returns:
        Device information including battery percentage
    """
    return f"Device {device_id}: Samsung Galaxy S24+, Android 14, Battery: 85%"

# System prompt middleware
@dynamic_prompt
def system_prompt(request: ModelRequest) -> str:
    """System prompt for the agent."""
    return "You are a helpful assistant. Use the available tools to answer questions completely."

# Create agent with middleware
agent = create_agent(
    model=llm,
    tools=[get_device_info],
    middleware=[system_prompt]
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

print("\n" + "=" * 60)
print(f"✅ Final Answer: {result['messages'][-1].content}")
print("\n✅ Atlas basic infrastructure works!")
