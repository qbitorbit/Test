#!/usr/bin/env python3
"""
ADB MCP Server - Android Device Control via Model Context Protocol
Provides tools for controlling Android devices through ADB
"""
import subprocess
import json
from typing import Optional
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("ADB Controller")

# Global state for active connection
active_device_id: Optional[str] = None


def execute_adb(command: list[str], device_id: Optional[str] = None) -> dict:
    """
    Execute an ADB command and return results
    
    Args:
        command: List of command arguments (e.g., ['devices', '-l'])
        device_id: Optional specific device ID to target
        
    Returns:
        dict with success, stdout, stderr, return_code
    """
    try:
        # Build ADB command
        adb_cmd = ["adb"]
        
        # Add device specifier if provided
        if device_id:
            adb_cmd.extend(["-s", device_id])
        
        # Add the actual command
        adb_cmd.extend(command)
        
        print(f"[ADB] Executing: {' '.join(adb_cmd)}")
        
        # Execute command
        result = subprocess.run(
            adb_cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "return_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out after 30 seconds",
            "return_code": -1
        }
    except FileNotFoundError:
        return {
            "success": False,
            "stdout": "",
            "stderr": "ADB not found. Please install Android SDK Platform Tools",
            "return_code": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "return_code": -1
        }


@mcp.tool()
def list_devices() -> str:
    """
    List all connected Android devices
    
    Returns a list of connected devices with their IDs and states
    """
    result = execute_adb(["devices", "-l"])
    
    if not result["success"]:
        return json.dumps({
            "error": result["stderr"],
            "devices": []
        })
    
    # Parse devices output
    lines = result["stdout"].split("\n")[1:]  # Skip header line
    devices = []
    
    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                device_info = {
                    "device_id": parts[0],
                    "state": parts[1]
                }
                
                # Parse additional info if available
                for part in parts[2:]:
                    if ":" in part:
                        key, value = part.split(":", 1)
                        device_info[key] = value
                
                devices.append(device_info)
    
    return json.dumps({
        "success": True,
        "count": len(devices),
        "devices": devices
    }, indent=2)


@mcp.tool()
def connect_device(device_id: Optional[str] = None) -> str:
    """
    Connect to a specific Android device or the only available device
    
    Args:
        device_id: Device ID to connect to. If None, connects to the only device if only one is available
        
    Returns:
        Connection status and device information
    """
    global active_device_id
    
    # If no device_id provided, try to auto-select
    if not device_id:
        devices_result = json.loads(list_devices())
        
        if not devices_result.get("success"):
            return json.dumps({
                "success": False,
                "error": "Failed to list devices"
            })
        
        devices = devices_result.get("devices", [])
        
        if len(devices) == 0:
            return json.dumps({
                "success": False,
                "error": "No devices connected"
            })
        elif len(devices) == 1:
            device_id = devices[0]["device_id"]
        else:
            return json.dumps({
                "success": False,
                "error": f"Multiple devices found ({len(devices)}). Please specify device_id",
                "available_devices": [d["device_id"] for d in devices]
            })
    
    # Test connection by getting device state
    result = execute_adb(["get-state"], device_id)
    
    if result["success"] and "device" in result["stdout"]:
        active_device_id = device_id
        
        return json.dumps({
            "success": True,
            "device_id": device_id,
            "state": result["stdout"],
            "message": f"Connected to device {device_id}"
        }, indent=2)
    else:
        return json.dumps({
            "success": False,
            "error": f"Cannot connect to device {device_id}",
            "details": result["stderr"]
        })


@mcp.tool()
def disconnect_device() -> str:
    """
    Disconnect from the currently active device
    
    Returns:
        Disconnection status
    """
    global active_device_id
    
    if not active_device_id:
        return json.dumps({
            "success": False,
            "error": "No device currently connected"
        })
    
    disconnected_id = active_device_id
    active_device_id = None
    
    return json.dumps({
        "success": True,
        "message": f"Disconnected from device {disconnected_id}"
    })


@mcp.tool()
def get_device_info() -> str:
    """
    Get comprehensive information about the currently connected device
    
    Returns detailed device information including model, Android version, battery, etc.
    """
    if not active_device_id:
        return json.dumps({
            "success": False,
            "error": "No device connected. Use connect_device() first"
        })
    
    # Collect device properties
    properties = {
        "device_id": active_device_id,
        "model": "",
        "manufacturer": "",
        "android_version": "",
        "sdk_version": "",
        "serial": "",
        "battery_level": "",
        "battery_status": ""
    }
    
    # Get device properties
    prop_mapping = {
        "model": "ro.product.model",
        "manufacturer": "ro.product.manufacturer",
        "android_version": "ro.build.version.release",
        "sdk_version": "ro.build.version.sdk",
        "serial": "ro.serialno"
    }
    
    for key, prop in prop_mapping.items():
        result = execute_adb(["shell", "getprop", prop], active_device_id)
        if result["success"]:
            properties[key] = result["stdout"]
    
    # Get battery info
    battery_result = execute_adb(
        ["shell", "dumpsys", "battery", "|", "grep", "level"],
        active_device_id
    )
    if battery_result["success"]:
        try:
            level_line = battery_result["stdout"]
            if "level:" in level_line:
                properties["battery_level"] = level_line.split("level:")[1].strip()
        except:
            properties["battery_level"] = "unknown"
    
    # Get screen state
    screen_result = execute_adb(
        ["shell", "dumpsys", "power", "|", "grep", "'Display Power'"],
        active_device_id
    )
    if screen_result["success"]:
        properties["screen_state"] = screen_result["stdout"]
    
    return json.dumps({
        "success": True,
        "device_info": properties
    }, indent=2)


@mcp.tool()
def execute_shell_command(command: str) -> str:
    """
    Execute a shell command on the connected Android device
    
    Args:
        command: Shell command to execute (e.g., "ls /sdcard")
        
    Returns:
        Command output
    """
    if not active_device_id:
        return json.dumps({
            "success": False,
            "error": "No device connected. Use connect_device() first"
        })
    
    result = execute_adb(["shell", command], active_device_id)
    
    return json.dumps({
        "success": result["success"],
        "command": command,
        "output": result["stdout"],
        "error": result["stderr"] if not result["success"] else None
    }, indent=2)


@mcp.tool()
def get_active_device() -> str:
    """
    Get the currently active/connected device ID
    
    Returns:
        Active device information
    """
    if active_device_id:
        return json.dumps({
            "success": True,
            "active_device_id": active_device_id
        })
    else:
        return json.dumps({
            "success": False,
            "message": "No device currently connected"
        })


if __name__ == "__main__":
    # Run the MCP server
    print("Starting ADB MCP Server...")
    print("Available tools:")
    print("  - list_devices()")
    print("  - connect_device(device_id)")
    print("  - disconnect_device()")
    print("  - get_device_info()")
    print("  - execute_shell_command(command)")
    print("  - get_active_device()")
    print("\nServer running via stdio...")
    
    mcp.run()
