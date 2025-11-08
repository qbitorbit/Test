#!/usr/bin/env python3
"""
MCP Client - Wrapper to communicate with MCP servers and use their tools
Simplified to directly call tool functions from the server module
"""
import json
import importlib
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
        # Don't reload - it breaks function unwrapping
        self.server_module = server_module
        self.tools = {}
        self._load_tools()
    
    def _load_tools(self):
        """Load tool function names from the server module"""
        # List of known tool function names from adb_mcp.py
        tool_functions = [
            'list_devices',
            'connect_device', 
            'disconnect_device',
            'get_device_info',
            'execute_shell_command',
            'get_active_device'
        ]
        
        # Just store the names, we'll get functions fresh on each call
        for func_name in tool_functions:
            if hasattr(self.server_module, func_name):
                self.tools[func_name] = True  # Just mark as available
    
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
            # Get the function fresh from the module each time
            func = getattr(self.server_module, tool_name)
            
            # Unwrap if needed
            if hasattr(func, 'fn') and callable(func.fn):
                actual_func = func.fn
            elif callable(func):
                actual_func = func
            else:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' is not callable"
                }
            
            # Call the function
            result = actual_func(**kwargs)
            
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
