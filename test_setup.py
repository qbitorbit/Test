#!/usr/bin/env python3
"""
Simple Agent Orchestrator - Direct LLM integration without CrewAI
"""
import json
import re
import sys
sys.path.insert(0, '.')

from config.settings import LLM_BASE_URL, LLM_MODEL
from utils.mcp_client import MCPClient
from mcp_servers import adb_simple  # Use the simple version
import requests


class SimpleAgent:
    """
    Simple agent that uses LLM + MCP tools without CrewAI overhead
    """
    
    def __init__(self, name: str, role: str, mcp_client: MCPClient):
        self.name = name
        self.role = role
        self.mcp_client = mcp_client
        self.conversation_history = []
    
    def _call_llm(self, prompt: str) -> str:
        """Call the local LLM with a prompt"""
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": f"You are {self.role}"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 1500
        }
        
        try:
            response = requests.post(
                f"{LLM_BASE_URL}/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
            
            return None
            
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return None
    
    def _extract_tool_calls(self, llm_response: str) -> list:
        """
        Extract tool calls from LLM response
        Expects JSON format like:
        {
            "reasoning": "...",
            "actions": [
                {"tool": "list_devices", "params": {}},
                {"tool": "connect_device", "params": {"device_id": "ABC123"}}
            ]
        }
        """
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            cleaned = llm_response.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            parsed = json.loads(cleaned)
            
            # Extract actions
            if "actions" in parsed:
                return parsed["actions"]
            elif "tool" in parsed:
                # Single action format
                return [parsed]
            
            return []
            
        except json.JSONDecodeError:
            # Fallback: try to find tool names in text
            print(f"⚠️  Could not parse JSON, attempting text extraction...")
            return []
    
    def execute_task(self, task_description: str) -> dict:
        """
        Execute a task using available tools
        
        Args:
            task_description: Natural language task description
            
        Returns:
            dict with success status and results
        """
        print(f"\n{'='*60}")
        print(f"🤖 Agent: {self.name}")
        print(f"📋 Task: {task_description}")
        print(f"{'='*60}\n")
        
        # Get available tools
        available_tools = self.mcp_client.list_tools()
        tool_descriptions = self.mcp_client.get_tool_descriptions()
        
        # Format tools for LLM
        tools_info = []
        for tool_name in available_tools:
            if tool_name in tool_descriptions:
                desc = tool_descriptions[tool_name]
                tools_info.append(f"- {tool_name}: {desc['description']}")
        
        tools_text = "\n".join(tools_info)
        
        # Create prompt for LLM
        prompt = f"""You are an Android Device Controller. Your task is to {task_description}.

Available tools:
{tools_text}

IMPORTANT NOTES:
- If only one device is connected, you do NOT need to call connect_device explicitly
- Most tools work without needing device_id parameter
- Only use connect_device if you need to switch devices or if explicitly asked

Analyze the task and respond with a JSON object containing:
1. "reasoning": Brief explanation of your approach
2. "actions": Array of tool calls needed to complete the task

Format:
{{
    "reasoning": "I will get device info to find the model and Android version",
    "actions": [
        {{"tool": "connect_device", "params": {{}}}},
        {{"tool": "get_device_info", "params": {{}}}}
    ]
}}

Important:
- Only use tools from the available list
- Provide exact tool names
- Most tools don't need any parameters
- Respond ONLY with valid JSON, no other text

Task: {task_description}
"""
        
        print("🤔 Asking LLM for action plan...")
        llm_response = self._call_llm(prompt)
        
        if not llm_response:
            return {
                "success": False,
                "error": "LLM did not respond"
            }
        
        print(f"💬 LLM Response:\n{llm_response}\n")
        
        # Extract tool calls
        actions = self._extract_tool_calls(llm_response)
        
        if not actions:
            # Fallback: try direct pattern matching
            print("⚠️  No structured actions found, trying pattern matching...")
            actions = self._pattern_match_task(task_description)
        
        if not actions:
            return {
                "success": False,
                "error": "Could not determine actions to take",
                "llm_response": llm_response
            }
        
        # Execute actions sequentially
        results = []
        context = {}  # Store results for later steps
        
        for i, action in enumerate(actions, 1):
            tool_name = action.get("tool")
            params = action.get("params", {})
            
            # Replace placeholders with actual values from context
            for key, value in params.items():
                if isinstance(value, str):
                    if value == "<active_device_id>" and "device_id" in context:
                        params[key] = context["device_id"]
                    elif value in ["null", "None", "none"]:
                        params[key] = None
            
            print(f"⚙️  Step {i}/{len(actions)}: {tool_name}({params})")
            
            result = self.mcp_client.call_tool(tool_name, **params)
            
            # If tool failed because no device connected, auto-connect and retry
            if not result.get("success") and "No device connected" in result.get("error", ""):
                print(f"⚠️  Device not connected, auto-connecting...")
                
                # Try to connect
                connect_result = self.mcp_client.call_tool("connect_device")
                if connect_result.get("success"):
                    print(f"✅ Auto-connected to device")
                    
                    # Update context
                    if connect_result.get("device_id"):
                        context["device_id"] = connect_result.get("device_id")
                    
                    # Retry the original action
                    print(f"🔄 Retrying: {tool_name}({params})")
                    result = self.mcp_client.call_tool(tool_name, **params)
                else:
                    print(f"❌ Auto-connect failed: {connect_result.get('error')}")
            
            results.append({
                "tool": tool_name,
                "params": params,
                "result": result
            })
            
            print(f"✅ Result: {json.dumps(result, indent=2)}\n")
            
            # Update context with important values from this result
            if result.get("success"):
                if tool_name == "list_devices" and result.get("devices"):
                    devices = result.get("devices", [])
                    if devices:
                        context["device_id"] = devices[0]["device_id"]
                elif tool_name == "connect_device" and result.get("device_id"):
                    context["device_id"] = result.get("device_id")
                elif tool_name == "get_active_device" and result.get("active_device_id"):
                    context["device_id"] = result.get("active_device_id")
        
        return {
            "success": True,
            "task": task_description,
            "actions_taken": len(actions),
            "results": results
        }
    
    def _pattern_match_task(self, task: str) -> list:
        """
        Fallback: Simple pattern matching for common tasks
        """
        task_lower = task.lower()
        
        # List devices
        if any(word in task_lower for word in ["list", "show", "devices"]):
            return [{"tool": "list_devices", "params": {}}]
        
        # Get device info
        if any(word in task_lower for word in ["device info", "phone info", "device details"]):
            return [
                {"tool": "connect_device", "params": {}},
                {"tool": "get_device_info", "params": {}}
            ]
        
        # Connect to device
        if "connect" in task_lower:
            return [{"tool": "connect_device", "params": {}}]
        
        # Execute shell command
        if "shell" in task_lower or "command" in task_lower:
            # Try to extract command
            match = re.search(r"command[:\s]+['\"](.+?)['\"]", task_lower)
            if match:
                cmd = match.group(1)
                return [{"tool": "execute_shell_command", "params": {"command": cmd}}]
        
        return []


class SimpleOrchestrator:
    """
    Orchestrator that manages multiple agents and routes tasks
    """
    
    def __init__(self):
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize available agents"""
        # ADB Agent
        adb_client = MCPClient(adb_simple)
        self.agents["adb"] = SimpleAgent(
            name="ADB Agent",
            role="an expert in Android device management and ADB commands",
            mcp_client=adb_client
        )
    
    def route_task(self, task: str) -> dict:
        """
        Route a task to the appropriate agent
        
        Args:
            task: Natural language task description
            
        Returns:
            Task execution results
        """
        # For now, route everything to ADB agent
        # Later: add logic to route to different agents based on task
        agent = self.agents["adb"]
        return agent.execute_task(task)
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("\n" + "="*60)
        print("🤖 Simple AI Orchestrator - Interactive Mode")
        print("="*60)
        print("\nAvailable agents:")
        for name, agent in self.agents.items():
            print(f"  - {agent.name}: {agent.role}")
        print("\nCommands:")
        print("  - Type your task in natural language")
        print("  - 'quit' or 'exit' to stop")
        print("="*60)
        
        while True:
            try:
                user_input = input("\n🧠 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                result = self.route_task(user_input)
                
                print(f"\n{'='*60}")
                print("📊 Summary")
                print(f"{'='*60}")
                if result.get("success"):
                    print(f"✅ Task completed successfully")
                    print(f"📝 Actions taken: {result.get('actions_taken', 0)}")
                else:
                    print(f"❌ Task failed: {result.get('error')}")
                print(f"{'='*60}\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()


def main():
    """Main entry point"""
    orchestrator = SimpleOrchestrator()
    
    if len(sys.argv) > 1:
        # Command line mode
        task = " ".join(sys.argv[1:])
        result = orchestrator.route_task(task)
        print(f"\nFinal Result: {json.dumps(result, indent=2)}")
    else:
        # Interactive mode
        orchestrator.interactive_mode()


if __name__ == "__main__":
    main()
