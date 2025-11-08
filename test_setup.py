#!/usr/bin/env python3
"""
MCP Client - Wrapper to communicate with MCP servers and use their tools
Simplified to directly call tool functions from the server module
"""
import json
from typing import Callable, Any


class MCPClient:
    """
    Client for interacting with MCP servers
    Directly calls tool functions from the server module
    """
    
    def __init__(self, server_module):
        """
        Initialize MCP client with a server module
        
        Args:
            server_module: The imported MCP server module
        """
        self.server_module = server_module
        self.tools = {}
        self._load_tools()
    
    def _load_tools(self):
        """Load tool functions directly from the server module"""
        # List of known tool function names from adb_mcp.py
        tool_functions = [
            'list_devices',
            'connect_device', 
            'disconnect_device',
            'get_device_info',
            'execute_shell_command',
            'get_active_device'
        ]
        
        for func_name in tool_functions:
            if hasattr(self.server_module, func_name):
                func = getattr(self.server_module, func_name)
                
                # If it's wrapped by FastMCP, unwrap it
                if hasattr(func, 'fn'):
                    # It's a FunctionTool, get the actual function
                    self.tools[func_name] = func.fn
                elif callable(func):
                    # It's already a callable function
                    self.tools[func_name] = func
    
    def call_tool(self, tool_name: str, **kwargs) -> dict:
        """
        Call an MCP tool by name
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Tool result as dictionary
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found. Available: {list(self.tools.keys())}"
            }
        
        try:
            func = self.tools[tool_name]
            
            # Call the function directly
            result = func(**kwargs)
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return {"success": True, "result": result}
            
            return result
            
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": f"Error calling tool '{tool_name}': {str(e)}",
                "traceback": traceback.format_exc()
            }
    
    def get_tool_descriptions(self) -> dict:
        """Get descriptions of all available tools"""
        descriptions = {}
        for tool_name, func in self.tools.items():
            descriptions[tool_name] = {
                "name": tool_name,
                "description": func.__doc__ or "No description available",
            }
        return descriptions
    
    def list_tools(self) -> list:
        """List all available tool names"""
        return list(self.tools.keys())


def test_mcp_client():
    """Test the MCP client with ADB server"""
    print("Testing MCP Client...")
    
    # Import ADB MCP server
    import sys
    sys.path.insert(0, '.')
    from mcp_servers import adb_mcp
    
    # Create client
    client = MCPClient(adb_mcp)
    
    print(f"Available tools: {client.list_tools()}")
    
    # Test list_devices
    print("\nTesting list_devices:")
    result = client.call_tool("list_devices")
    print(json.dumps(result, indent=2))
    
    return client


if __name__ == "__main__":
    test_mcp_client()
