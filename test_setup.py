#!/usr/bin/env python3
import sys
print(f"✅ Python version: {sys.version}")

try:
    import crewai
    print(f"✅ CrewAI installed: {crewai.__version__}")
except ImportError as e:
    print(f"❌ CrewAI not found: {e}")

try:
    import fastmcp
    print(f"✅ FastMCP installed")
except ImportError as e:
    print(f"❌ FastMCP not found: {e}")

try:
    import uiautomator2
    print(f"✅ UIAutomator2 installed")
except ImportError as e:
    print(f"❌ UIAutomator2 not found: {e}")

try:
    from config.settings import LLM_BASE_URL, LLM_MODEL
    print(f"✅ Settings loaded:")
    print(f"   LLM URL: {LLM_BASE_URL}")
    print(f"   LLM Model: {LLM_MODEL}")
except ImportError as e:
    print(f"❌ Settings error: {e}")

print("\n🎉 Setup complete!")
