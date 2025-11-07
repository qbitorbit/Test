#!/usr/bin/env python3
"""
ADB Agent - CrewAI agent for controlling Android devices
Using CrewAI's LLM class for custom OpenAI-compatible endpoints
"""
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import json
import sys
sys.path.insert(0, '.')

from config.settings import LLM_BASE_URL, LLM_MODEL
from utils.mcp_client import MCPClient
from mcp_servers import adb_mcp


# Initialize MCP Client
mcp_client = MCPClient(adb_mcp)

# Create CrewAI tools from MCP tools
@tool("list_devices")
def list_devices_tool() -> str:
    """List all connected Android devices with their IDs and states"""
    result = mcp_client.call_tool("list_devices")
    return json.dumps(result, indent=2)


@tool("connect_device")
def connect_device_tool(device_id: str = None) -> str:
    """
    Connect to a specific Android device
    
    Args:
        device_id: Device ID to connect to (optional, auto-selects if only one device)
    """
    kwargs = {}
    if device_id:
        kwargs["device_id"] = device_id
    
    result = mcp_client.call_tool("connect_device", **kwargs)
    return json.dumps(result, indent=2)


@tool("get_device_info")
def get_device_info_tool() -> str:
    """Get comprehensive information about the currently connected device"""
    result = mcp_client.call_tool("get_device_info")
    return json.dumps(result, indent=2)


@tool("execute_shell_command")
def execute_shell_command_tool(command: str) -> str:
    """
    Execute a shell command on the connected Android device
    
    Args:
        command: Shell command to execute (e.g., 'ls /sdcard')
    """
    result = mcp_client.call_tool("execute_shell_command", command=command)
    return json.dumps(result, indent=2)


@tool("disconnect_device")
def disconnect_device_tool() -> str:
    """Disconnect from the currently connected device"""
    result = mcp_client.call_tool("disconnect_device")
    return json.dumps(result, indent=2)


@tool("get_active_device")
def get_active_device_tool() -> str:
    """Get the currently active/connected device ID"""
    result = mcp_client.call_tool("get_active_device")
    return json.dumps(result, indent=2)


def create_adb_agent(verbose: bool = True) -> Agent:
    """
    Create and configure the ADB Agent using CrewAI's LLM class
    
    Args:
        verbose: Enable verbose output
        
    Returns:
        Configured CrewAI Agent
    """
    # Configure local LLM using CrewAI's LLM class
    # This works with any OpenAI-compatible endpoint
    local_llm = LLM(
        model="openai/custom",  # Provider/model format
        base_url=LLM_BASE_URL,
        api_key="not-needed",   # Dummy key for local server
        temperature=0.1,
        max_tokens=2000
    )
    
    # Create agent
    agent = Agent(
        role="Android Device Controller",
        goal="Control and manage Android devices efficiently using ADB commands",
        backstory="""You are an expert in Android device management and ADB (Android Debug Bridge).
        You have deep knowledge of Android internals, shell commands, and device automation.
        You help users interact with their Android devices through natural language commands.
        You always provide clear, accurate information and execute commands safely.""",
        llm=local_llm,
        tools=[
            list_devices_tool,
            connect_device_tool,
            get_device_info_tool,
            execute_shell_command_tool,
            disconnect_device_tool,
            get_active_device_tool
        ],
        verbose=verbose,
        allow_delegation=False
    )
    
    return agent


def run_adb_task(task_description: str, verbose: bool = True) -> str:
    """
    Execute a task using the ADB agent
    
    Args:
        task_description: Natural language description of what to do
        verbose: Enable verbose output
        
    Returns:
        Task result
    """
    # Create agent
    agent = create_adb_agent(verbose=verbose)
    
    # Create task
    task = Task(
        description=task_description,
        agent=agent,
        expected_output="A clear summary of the action taken and results"
    )
    
    # Create crew and execute
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=verbose
    )
    
    result = crew.kickoff()
    return result


# Interactive mode
def interactive_mode():
    """Run agent in interactive mode"""
    print("=" * 60)
    print("ADB Agent - Interactive Mode (CrewAI)")
    print("=" * 60)
    print("\nCommands:")
    print("  - Ask anything about Android devices")
    print("  - 'quit' or 'exit' to stop")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n🤖 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤔 Agent is thinking...\n")
            result = run_adb_task(user_input, verbose=True)
            print(f"\n✅ Result:\n{result}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # Test mode - can be run directly
    import sys
    
    if len(sys.argv) > 1:
        # Run with command line argument
        task = " ".join(sys.argv[1:])
        print(f"Running task: {task}\n")
        result = run_adb_task(task, verbose=True)
        print(f"\nResult: {result}")
    else:
        # Interactive mode
        interactive_mode()
