python -c "
import sys
sys.path.insert(0, '.')
from utils.mcp_client import MCPClient
from mcp_servers import adb_mcp

client = MCPClient(adb_mcp)
print('Available tools:', client.list_tools())

# Test calling list_devices
print('\nTesting list_devices:')
result = client.call_tool('list_devices')
print(result)
"
