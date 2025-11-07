#!/usr/bin/env python3
"""
Test ADB MCP Server - Verify it can communicate and execute commands
"""
import subprocess
import json
import sys

def test_adb_installed():
    """Check if ADB is installed and accessible"""
    print("🔍 Checking if ADB is installed...")
    try:
        result = subprocess.run(
            ["adb", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split("\n")[0]
            print(f"✅ ADB found: {version}")
            return True
        else:
            print("❌ ADB command failed")
            return False
    except FileNotFoundError:
        print("❌ ADB not found in PATH")
        print("   Please install Android SDK Platform Tools")
        return False
    except Exception as e:
        print(f"❌ Error checking ADB: {e}")
        return False


def test_devices_connected():
    """Check if any Android devices are connected"""
    print("\n🔍 Checking for connected devices...")
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        lines = result.stdout.strip().split("\n")[1:]  # Skip header
        devices = [line for line in lines if line.strip() and "\tdevice" in line]
        
        if devices:
            print(f"✅ Found {len(devices)} device(s):")
            for device in devices:
                device_id = device.split("\t")[0]
                print(f"   - {device_id}")
            return True
        else:
            print("⚠️  No devices connected")
            print("   Please connect an Android device with USB debugging enabled")
            return False
            
    except Exception as e:
        print(f"❌ Error checking devices: {e}")
        return False


def test_mcp_server_import():
    """Test if the MCP server can be imported"""
    print("\n🔍 Testing MCP server import...")
    try:
        # Try to import the module
        sys.path.insert(0, '.')
        import mcp_servers.adb_mcp as adb_mcp
        
        print("✅ ADB MCP server module imported successfully")
        
        # Check if tools are defined
        if hasattr(adb_mcp, 'mcp'):
            print("✅ FastMCP instance found")
            return True
        else:
            print("❌ FastMCP instance not found")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import MCP server: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_direct_tool_execution():
    """Test executing MCP tools directly (without stdio)"""
    print("\n🔍 Testing direct ADB execution...")
    try:
        sys.path.insert(0, '.')
        from mcp_servers.adb_mcp import execute_adb
        
        print("📤 Calling execute_adb(['devices', '-l'])...")
        result = execute_adb(["devices", "-l"])
        
        print(f"📥 Result: {json.dumps(result, indent=2)}")
        
        if result.get("success"):
            print(f"✅ ADB execution successful")
            
            # Try to parse devices from output
            stdout = result.get("stdout", "")
            lines = stdout.split("\n")[1:]  # Skip header
            device_count = sum(1 for line in lines if line.strip() and "\tdevice" in line)
            print(f"✅ Found {device_count} device(s) in output")
            return True
        else:
            print(f"⚠️  ADB execution failed: {result.get('stderr')}")
            return False
            
    except Exception as e:
        print(f"❌ Error executing ADB: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ADB MCP Server Test Suite")
    print("=" * 60)
    
    # Run tests
    test1 = test_adb_installed()
    test2 = test_devices_connected() if test1 else False
    test3 = test_mcp_server_import()
    test4 = test_direct_tool_execution() if test3 else False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"ADB Installed:          {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Devices Connected:      {'✅ PASS' if test2 else '⚠️  WARN'}")
    print(f"MCP Server Import:      {'✅ PASS' if test3 else '❌ FAIL'}")
    print(f"Tool Execution:         {'✅ PASS' if test4 else '❌ FAIL'}")
    print("=" * 60)
    
    if test1 and test3 and test4:
        print("\n🎉 ADB MCP Server is ready!")
        if not test2:
            print("⚠️  Note: No devices connected, but server is functional")
        print("\nYou can now:")
        print("  1. Connect an Android device with USB debugging")
        print("  2. Run the MCP server: python mcp_servers/adb_mcp.py")
        print("  3. Move to Phase 3: Create the ADB Agent")
    else:
        print("\n❌ Some tests failed. Please fix issues before proceeding.")
        if not test1:
            print("\n📝 To install ADB:")
            print("  Mac: brew install android-platform-tools")
            print("  Or download from: https://developer.android.com/tools/releases/platform-tools")
