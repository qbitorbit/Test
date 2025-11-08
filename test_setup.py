#!/usr/bin/env python3
"""
MCP Client - Wrapper to communicate with MCP servers and use their tools
"""
import json
from typing import Callable, Any


class MCPClient:
    """
    Client for interacting with MCP servers
    For now, uses direct function calls (same process)
    Later can be extended to stdio/HTTP communication
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
        """Load available tools from the MCP server"""
        # Get the FastMCP instance
        if hasattr(self.server_module, 'mcp'):
            mcp_instance = self.server_module.mcp
            
            # Try different ways to access tools from FastMCP
            if hasattr(mcp_instance, 'list_tools'):
                # Use list_tools method if available
                try:
                    tools_list = mcp_instance.list_tools()
                    for tool in tools_list:
                        self.tools[tool.name] = tool
                except:
                    pass
            
            # Try accessing _tools attribute
            if hasattr(mcp_instance, '_tools'):
                for tool_name, tool_obj in mcp_instance._tools.items():
                    self.tools[tool_name] = tool_obj
            
            # Fallback: scan module for @mcp.tool decorated functions
            if not self.tools:
                for attr_name in dir(self.server_module):
                    attr = getattr(self.server_module, attr_name)
                    # Check if it's a decorated tool function
                    if callable(attr) and not attr_name.startswith('_'):
                        # Skip common module functions
                        if attr_name not in ['execute_adb']:
                            self.tools[attr_name] = attr
    
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
            tool = self.tools[tool_name]
            
            # Call the tool's function
            if hasattr(tool, 'fn'):
                result = tool.fn(**kwargs)
            else:
                # Fallback: try calling directly
                result = tool(**kwargs)
            
            # Parse JSON result if it's a string
            if isinstance(result, str):
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return {"success": True, "result": result}
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error calling tool '{tool_name}': {str(e)}"
            }
    
    def get_tool_descriptions(self) -> dict:
        """Get descriptions of all available tools"""
        descriptions = {}
        for tool_name, tool_obj in self.tools.items():
            if hasattr(tool_obj, 'fn'):
                fn = tool_obj.fn
                descriptions[tool_name] = {
                    "name": tool_name,
                    "description": fn.__doc__ or "No description available",
                    "parameters": fn.__annotations__ if hasattr(fn, '__annotations__') else {}
                }
        return descriptions
    
    def list_tools(self) -> list:
        """List all available tool names"""
        return list(self.tools.keys())


def create_crewai_tool(mcp_client: MCPClient, tool_name: str) -> Callable:
    """
    Create a CrewAI-compatible tool function from an MCP tool
    
    Args:
        mcp_client: MCP client instance
        tool_name: Name of the MCP tool
        
    Returns:
        Function that can be used as a CrewAI tool
    """
    def tool_wrapper(**kwargs) -> str:
        """Wrapper function for CrewAI"""
        result = mcp_client.call_tool(tool_name, **kwargs)
        return json.dumps(result, indent=2)
    
    # Get the original tool for documentation
    if tool_name in mcp_client.tools:
        tool_obj = mcp_client.tools[tool_name]
        if hasattr(tool_obj, 'fn'):
            original_fn = tool_obj.fn
            tool_wrapper.__name__ = tool_name
            tool_wrapper.__doc__ = original_fn.__doc__ or f"MCP tool: {tool_name}"
    
    return tool_wrapper


# Example usage functions
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
