python -c "
import sys
sys.path.insert(0, '.')
from mcp_servers import adb_mcp

# Check each function
funcs = ['list_devices', 'connect_device', 'get_device_info']
for name in funcs:
    func = getattr(adb_mcp, name)
    print(f'{name}: type={type(func)}, has_fn={hasattr(func, \"fn\")}, callable={callable(func)}')
    if hasattr(func, 'fn'):
        print(f'  -> fn type={type(func.fn)}, fn callable={callable(func.fn)}')
"
