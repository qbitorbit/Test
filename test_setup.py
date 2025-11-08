#!/usr/bin/env python3
"""
ADB Agent - Handles Android device control tasks
"""
import json
import re
import sys
sys.path.insert(0, '.')

from utils.mcp_client import MCPClient
from mcp_servers import adb_simple
import requests
from config.settings import LLM_BASE_URL, LLM_MODEL


# ANSI Color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    DIM = '\033[2m'


class OutputFormatter:
    """Handles beautiful output formatting"""
    
    @staticmethod
    def print_success(text: str):
        print(f"{Colors.GREEN}✅ {text}{Colors.END}")
    
    @staticmethod
    def print_error(text: str):
        print(f"{Colors.RED}❌ {text}{Colors.END}")
    
    @staticmethod
    def print_warning(text: str):
        print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")
    
    @staticmethod
    def print_info(text: str):
        print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")
    
    @staticmethod
    def print_step(step_num: int, total: int, text: str):
        print(f"\n{Colors.BOLD}{Colors.YELLOW}⚙️  Step {step_num}/{total}:{Colors.END} {text}")
    
    @staticmethod
    def format_device_info(info: dict) -> str:
        """Format device information beautifully"""
        lines = [
            f"{Colors.BOLD}Device Information:{Colors.END}",
            f"  📱 Model: {Colors.GREEN}{info.get('model', 'Unknown')}{Colors.END}",
            f"  🏭 Manufacturer: {Colors.GREEN}{info.get('manufacturer', 'Unknown')}{Colors.END}",
            f"  🤖 Android: {Colors.GREEN}{info.get('android_version', 'Unknown')}{Colors.END}",
            f"  📊 SDK: {Colors.GREEN}{info.get('sdk_version', 'Unknown')}{Colors.END}",
            f"  🔋 Battery: {Colors.GREEN}{info.get('battery_level', 'Unknown')}{Colors.END}",
        ]
        return "\n".join(lines)
    
    @staticmethod
    def format_devices_list(devices: list) -> str:
        """Format device list"""
        if not devices:
            return f"{Colors.YELLOW}No devices connected{Colors.END}"
        
        lines = [f"{Colors.BOLD}Connected Devices ({len(devices)}):{Colors.END}"]
        for i, device in enumerate(devices, 1):
            status_color = Colors.GREEN if device.get('state') == 'device' else Colors.YELLOW
            lines.append(
                f"  {i}. {Colors.CYAN}{device.get('device_id', 'Unknown')}{Colors.END} "
                f"[{status_color}{device.get('state', 'Unknown')}{Colors.END}]"
            )
        return "\n".join(lines)
    
    @staticmethod
    def format_packages_list(packages: list) -> str:
        """Format package list - show ALL packages"""
        if not packages:
            return f"{Colors.YELLOW}No packages found{Colors.END}"
        
        total = len(packages)
        
        lines = [f"{Colors.BOLD}Installed Packages (Total: {total}):{Colors.END}\n"]
        
        # Group packages by category
        categories = {
            'System': [],
            'Google': [],
            'Samsung': [],
            'Other': []
        }
        
        for pkg in packages:
            if 'android' in pkg.lower() or 'system' in pkg.lower():
                categories['System'].append(pkg)
            elif 'google' in pkg.lower() or 'gms' in pkg.lower():
                categories['Google'].append(pkg)
            elif 'samsung' in pkg.lower() or 'sec.' in pkg.lower():
                categories['Samsung'].append(pkg)
            else:
                categories['Other'].append(pkg)
        
        for category, pkgs in categories.items():
            if pkgs:
                lines.append(f"\n  {Colors.BOLD}{Colors.BLUE}{category} Apps ({len(pkgs)}):{Colors.END}")
                for pkg in pkgs:  # Show ALL packages
                    short_name = pkg.split('.')[-1] if '.' in pkg else pkg
                    lines.append(f"    • {Colors.GREEN}{short_name}{Colors.END} {Colors.DIM}({pkg}){Colors.END}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_shell_output(output: str) -> str:
        """Format shell command output - show complete output"""
        if not output:
            return f"{Colors.DIM}(no output){Colors.END}"
        return output
    
    @staticmethod
    def format_result(result: dict) -> str:
        """Smart formatting based on result content"""
        if not result.get("success"):
            error = result.get("error", "Unknown error")
            return f"{Colors.RED}Error: {error}{Colors.END}"
        
        output_lines = []
        
        if "device_info" in result:
            output_lines.append(OutputFormatter.format_device_info(result["device_info"]))
        elif "devices" in result:
            output_lines.append(OutputFormatter.format_devices_list(result["devices"]))
        elif "packages" in result:
            output_lines.append(OutputFormatter.format_packages_list(result["packages"]))
        elif "output" in result:
            output = result["output"]
            output_lines.append(f"{Colors.BOLD}Command Output:{Colors.END}")
            output_lines.append(OutputFormatter.format_shell_output(output))
        elif "message" in result:
            output_lines.append(f"{Colors.GREEN}{result['message']}{Colors.END}")
        elif "device_id" in result:
            output_lines.append(f"{Colors.GREEN}Connected to: {result['device_id']}{Colors.END}")
        elif "active_device_id" in result:
            output_lines.append(f"{Colors.GREEN}Active device: {result['active_device_id']}{Colors.END}")
        else:
            output_lines.append(f"{Colors.GREEN}Operation completed successfully{Colors.END}")
        
        return "\n".join(output_lines) if output_lines else f"{Colors.GREEN}Success{Colors.END}"


class ADBAgent:
    """
    ADB Agent - Handles Android device control tasks
    """
    
    def __init__(self):
        self.name = "ADB Agent"
        self.role = "Android Device Controller - Expert in ADB commands and device management"
        self.mcp_client = MCPClient(adb_simple)
        self.formatter = OutputFormatter()
    
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
            self.formatter.print_error(f"LLM Error: {e}")
            return None
    
    def _extract_tool_calls(self, llm_response: str) -> list:
        """Extract tool calls from LLM response"""
        try:
            cleaned = llm_response.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(cleaned)
            
            if "actions" in parsed:
                return parsed["actions"]
            elif "tool" in parsed:
                return [parsed]
            
            return []
            
        except json.JSONDecodeError:
            self.formatter.print_warning("Could not parse JSON, attempting pattern matching...")
            return []
    
    def execute_task(self, task_description: str) -> dict:
        """
        Execute a task using available ADB tools
        
        Args:
            task_description: Natural language task description
            
        Returns:
            dict with success status and results
        """
        self.formatter.print_info(f"Task: {task_description}")
        
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
        
        self.formatter.print_info("Asking LLM for action plan...")
        llm_response = self._call_llm(prompt)
        
        if not llm_response:
            return {"success": False, "error": "LLM did not respond"}
        
        # Show LLM reasoning
        try:
            cleaned = llm_response.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(cleaned)
            if "reasoning" in parsed:
                print(f"\n{Colors.DIM}💭 Reasoning: {parsed['reasoning']}{Colors.END}")
        except:
            pass
        
        # Extract actions
        actions = self._extract_tool_calls(llm_response)
        
        if not actions:
            actions = self._pattern_match_task(task_description)
        
        if not actions:
            return {"success": False, "error": "Could not determine actions"}
        
        # Execute actions
        results = []
        context = {}
        
        for i, action in enumerate(actions, 1):
            tool_name = action.get("tool")
            params = action.get("params", {})
            
            # Clean parameters
            for key, value in params.items():
                if isinstance(value, str):
                    if value == "<active_device_id>" and "device_id" in context:
                        params[key] = context["device_id"]
                    elif value in ["null", "None", "none"]:
                        params[key] = None
            
            self.formatter.print_step(i, len(actions), f"{tool_name}()")
            
            result = self.mcp_client.call_tool(tool_name, **params)
            
            # Auto-connect if needed
            if not result.get("success") and "No device connected" in result.get("error", ""):
                self.formatter.print_warning("Device not connected, auto-connecting...")
                
                connect_result = self.mcp_client.call_tool("connect_device")
                if connect_result.get("success"):
                    self.formatter.print_success("Auto-connected to device")
                    
                    if connect_result.get("device_id"):
                        context["device_id"] = connect_result.get("device_id")
                    
                    result = self.mcp_client.call_tool(tool_name, **params)
                else:
                    self.formatter.print_error(f"Auto-connect failed: {connect_result.get('error')}")
            
            results.append({
                "tool": tool_name,
                "params": params,
                "result": result
            })
            
            # Print formatted result
            print(f"\n{self.formatter.format_result(result)}\n")
            
            # Update context
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
        """Fallback pattern matching"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["list", "show", "devices"]):
            return [{"tool": "list_devices", "params": {}}]
        
        if any(word in task_lower for word in ["device info", "phone info", "device details"]):
            return [{"tool": "get_device_info", "params": {}}]
        
        if "connect" in task_lower:
            return [{"tool": "connect_device", "params": {}}]
        
        if "shell" in task_lower or "command" in task_lower:
            match = re.search(r"command[:\s]+['\"](.+?)['\"]", task_lower)
            if match:
                cmd = match.group(1)
                return [{"tool": "execute_shell_command", "params": {"command": cmd}}]
        
        return []
