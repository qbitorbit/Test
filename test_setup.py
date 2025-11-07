python -c "
import sys
sys.path.insert(0, '.')
from mcp_servers.adb_mcp import list_devices
result = list_devices()
print(result)
"
