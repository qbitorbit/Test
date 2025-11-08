#!/usr/bin/env python3
"""
Diagnostic script to test Confluence tool loading
"""
import sys
sys.path.insert(0, '.')

# Test 1: Can we import confluence_simple?
print("Test 1: Importing confluence_simple...")
try:
    from mcp_servers import confluence_simple
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: What functions are in the module?
print("\nTest 2: Functions in confluence_simple:")
funcs = [name for name in dir(confluence_simple) if not name.startswith('_') and callable(getattr(confluence_simple, name))]
print(f"Found {len(funcs)} functions:")
for func in funcs:
    print(f"  - {func}")

# Test 3: Can we call set_confluence_credentials?
print("\nTest 3: Setting credentials...")
try:
    confluence_simple.set_confluence_credentials(
        "https://10.20.15.19:8444/rest/api/content",
        "test_key"
    )
    print("✅ Credentials set")
except Exception as e:
    print(f"❌ Failed: {e}")

# Test 4: Try to create MCPClient
print("\nTest 4: Creating MCPClient...")
try:
    from utils.mcp_client import MCPClient
    client = MCPClient(confluence_simple)
    print("✅ MCPClient created")
    
    # Test 5: What tools does it see?
    print("\nTest 5: Available tools:")
    tools = client.list_tools()
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool}")
    
    if len(tools) == 0:
        print("\n❌ NO TOOLS FOUND - This is the problem!")
        print("\nDebugging MCPClient...")
        print(f"MCPClient.tools attribute: {getattr(client, 'tools', 'NOT FOUND')}")
        
except Exception as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Diagnostic complete")
