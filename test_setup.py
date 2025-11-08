# First, let's see what tools are actually available
python -c "
import sys
sys.path.insert(0, '.')
from utils.mcp_client import MCPClient
from mcp_servers import adb_mcp
client = MCPClient(adb_mcp)
print('Available tools:', client.list_tools())
"
