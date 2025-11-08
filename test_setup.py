#!/usr/bin/env python3
"""
Enhanced ADB Server - More Android control functions
Based on phone-mcp capabilities
"""
import subprocess
import json
import time
from typing import Optional


# Global state
active_device_id: Optional[str] = None


def execute_adb(command: list[str], device_id: Optional[str] = None) -> dict:
    """Execute an ADB command"""
    try:
        adb_cmd = ["adb"]
        if device_id:
            adb_cmd.extend(["-s", device_id])
        adb_cmd.extend(command)
        
        result = subprocess.run(adb_cmd, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e)}


# ========== Basic Device Management ==========

def list_devices() -> str:
    """List all connected Android devices"""
    result = execute_adb(["devices", "-l"])
    if not result["success"]:
        return json.dumps({"success": False, "error": result["stderr"]})
    
    lines = result["stdout"].split("\n")[1:]
    devices = []
    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) >= 2:
                devices.append({"device_id": parts[0], "state": parts[1]})
    
    return json.dumps({"success": True, "count": len(devices), "devices": devices})


def connect_device(device_id: Optional[str] = None) -> str:
    """Connect to an Android device"""
    global active_device_id
    
    if not device_id:
        devices_result = json.loads(list_devices())
        devices = devices_result.get("devices", [])
        if len(devices) == 1:
            device_id = devices[0]["device_id"]
        else:
            return json.dumps({"success": False, "error": "Specify device_id or connect only one device"})
    
    result = execute_adb(["get-state"], device_id)
    if result["success"] and "device" in result["stdout"]:
        active_device_id = device_id
        return json.dumps({"success": True, "device_id": device_id})
    return json.dumps({"success": False, "error": "Cannot connect"})


def get_device_info() -> str:
    """Get device information"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    props = {}
    for key, prop in {"model": "ro.product.model", "manufacturer": "ro.product.manufacturer", 
                      "android_version": "ro.build.version.release", "sdk_version": "ro.build.version.sdk"}.items():
        result = execute_adb(["shell", "getprop", prop], active_device_id)
        props[key] = result["stdout"] if result["success"] else "Unknown"
    
    battery = execute_adb(["shell", "dumpsys", "battery"], active_device_id)
    if battery["success"]:
        for line in battery["stdout"].split("\n"):
            if "level:" in line:
                props["battery_level"] = line.split("level:")[1].strip()
    
    return json.dumps({"success": True, "device_info": props})


# ========== App Management ==========

def list_packages() -> str:
    """List installed packages"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    result = execute_adb(["shell", "pm", "list", "packages"], active_device_id)
    if result["success"]:
        packages = [line.replace("package:", "") for line in result["stdout"].split("\n") if line.strip()]
        return json.dumps({"success": True, "count": len(packages), "packages": packages[:50]})  # Limit to 50
    return json.dumps({"success": False, "error": result["stderr"]})


def launch_app(package_name: str) -> str:
    """Launch an app by package name"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    result = execute_adb(["shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"], active_device_id)
    if result["success"]:
        return json.dumps({"success": True, "message": f"Launched {package_name}"})
    return json.dumps({"success": False, "error": result["stderr"]})


def stop_app(package_name: str) -> str:
    """Force stop an app"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    result = execute_adb(["shell", "am", "force-stop", package_name], active_device_id)
    if result["success"]:
        return json.dumps({"success": True, "message": f"Stopped {package_name}"})
    return json.dumps({"success": False, "error": result["stderr"]})


def install_apk(apk_path: str) -> str:
    """Install an APK file"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    result = execute_adb(["install", apk_path], active_device_id)
    if result["success"]:
        return json.dumps({"success": True, "message": f"Installed {apk_path}"})
    return json.dumps({"success": False, "error": result["stderr"]})


def uninstall_app(package_name: str) -> str:
    """Uninstall an app"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    result = execute_adb(["uninstall", package_name], active_device_id)
    if result["success"]:
        return json.dumps({"success": True, "message": f"Uninstalled {package_name}"})
    return json.dumps({"success": False, "error": result["stderr"]})


# ========== Screen & Input ==========

def take_screenshot(filename: Optional[str] = None) -> str:
    """Take a screenshot"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    if not filename:
        filename = f"screenshot_{int(time.time())}.png"
    
    device_path = f"/sdcard/{filename}"
    
    # Take screenshot on device
    result = execute_adb(["shell", "screencap", "-p", device_path], active_device_id)
    if not result["success"]:
        return json.dumps({"success": False, "error": result["stderr"]})
    
    # Pull to local
    pull_result = execute_adb(["pull", device_path, filename], active_device_id)
    if pull_result["success"]:
        return json.dumps({"success": True, "message": f"Screenshot saved to {filename}"})
    return json.dumps({"success": False, "error": pull_result["stderr"]})


def tap_screen(x: int, y: int) -> str:
    """Tap at coordinates"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    result = execute_adb(["shell", "input", "tap", str(x), str(y)], active_device_id)
    if result["success"]:
        return json.dumps({"success": True, "message": f"Tapped at ({x}, {y})"})
    return json.dumps({"success": False, "error": result["stderr"]})


def swipe_screen(x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> str:
    """Swipe from (x1,y1) to (x2,y2)"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    result = execute_adb(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)], active_device_id)
    if result["success"]:
        return json.dumps({"success": True, "message": f"Swiped from ({x1},{y1}) to ({x2},{y2})"})
    return json.dumps({"success": False, "error": result["stderr"]})


def input_text(text: str) -> str:
    """Input text"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    # Escape special characters
    text = text.replace(" ", "%s")
    result = execute_adb(["shell", "input", "text", text], active_device_id)
    if result["success"]:
        return json.dumps({"success": True, "message": f"Typed: {text}"})
    return json.dumps({"success": False, "error": result["stderr"]})


def press_key(keycode: str) -> str:
    """Press a key (BACK, HOME, MENU, etc)"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    keycode_map = {
        "back": "KEYCODE_BACK",
        "home": "KEYCODE_HOME",
        "menu": "KEYCODE_MENU",
        "enter": "KEYCODE_ENTER",
        "power": "KEYCODE_POWER"
    }
    
    key = keycode_map.get(keycode.lower(), keycode)
    result = execute_adb(["shell", "input", "keyevent", key], active_device_id)
    if result["success"]:
        return json.dumps({"success": True, "message": f"Pressed {key}"})
    return json.dumps({"success": False, "error": result["stderr"]})


# ========== File Operations ==========

def push_file(local_path: str, device_path: str) -> str:
    """Push file to device"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    result = execute_adb(["push", local_path, device_path], active_device_id)
    if result["success"]:
        return json.dumps({"success": True, "message": f"Pushed {local_path} to {device_path}"})
    return json.dumps({"success": False, "error": result["stderr"]})


def pull_file(device_path: str, local_path: str) -> str:
    """Pull file from device"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    result = execute_adb(["pull", device_path, local_path], active_device_id)
    if result["success"]:
        return json.dumps({"success": True, "message": f"Pulled {device_path} to {local_path}"})
    return json.dumps({"success": False, "error": result["stderr"]})


# ========== System Commands ==========

def execute_shell_command(command: str) -> str:
    """Execute shell command"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    result = execute_adb(["shell", command], active_device_id)
    return json.dumps({"success": result["success"], "output": result["stdout"], "error": result["stderr"]})


def reboot_device(mode: str = "normal") -> str:
    """Reboot device (normal, recovery, bootloader)"""
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    
    if mode == "recovery":
        result = execute_adb(["reboot", "recovery"], active_device_id)
    elif mode == "bootloader":
        result = execute_adb(["reboot", "bootloader"], active_device_id)
    else:
        result = execute_adb(["reboot"], active_device_id)
    
    if result["success"]:
        return json.dumps({"success": True, "message": f"Rebooting to {mode}"})
    return json.dumps({"success": False, "error": result["stderr"]})


# ========== Helper Functions ==========

def disconnect_device() -> str:
    """Disconnect from device"""
    global active_device_id
    if not active_device_id:
        return json.dumps({"success": False, "error": "No device connected"})
    active_device_id = None
    return json.dumps({"success": True, "message": "Disconnected"})


def get_active_device() -> str:
    """Get active device ID"""
    if active_device_id:
        return json.dumps({"success": True, "active_device_id": active_device_id})
    return json.dumps({"success": False, "message": "No device connected"})
