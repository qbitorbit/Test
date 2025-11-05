# Create directories
mkdir -p mcp_servers
mkdir -p agents
mkdir -p workflows
mkdir -p config
mkdir -p utils
mkdir -p tests

# Create main files
touch main.py
touch config/settings.py
touch requirements.txt
touch .env
touch .gitignore
touch README.md

# Open requirements.txt in VS Code and add:
txt

crewai>=0.1.0
crewai-tools>=0.1.0
fastmcp>=0.1.0
langchain>=0.1.0
langchain-community>=0.1.0
uiautomator2>=3.0.0
requests>=2.31.0
flask>=3.0.0
python-dotenv>=1.0.0

# Save the file.

# Open .gitignore and add:
# Virtual Environment
venv/
env/
ENV/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temporary files
temp/
tmp/
*.tmp

# SQLite databases
*.db
*.sqlite3

# Save the file.

# Open .env and add your settings:

# LLM Server Configuration
LLM_BASE_URL=http://ip:port/v1
LLM_MODEL=/models/Qwen/Qwen3-Coder-40B-A3B-Instruct-FP8

# MCP Server Ports
ADB_MCP_PORT=5001
CONFLUENCE_MCP_PORT=5002
SQLITE_MCP_PORT=5003

# Orchestrator API
ORCHESTRATOR_PORT=8080

# Device Configuration
DEFAULT_DEVICE_UNLOCK_PIN=1234

# Logging
LOG_LEVEL=INFO

# Verify Your Project Structure

tree -L 2 -I 'venv'

# or this:

ls -la
```

should see:
```
android-ai-orchestrator/
├── agents/
├── config/
│   └── settings.py
├── mcp_servers/
├── utils/
├── workflows/
├── tests/
├── venv/
├── main.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md

# Open config/settings.py and add:

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LLM Configuration
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://ip:port/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "/models/Qwen/Qwen3-Coder-40B-A3B-Instruct-FP8")

# MCP Ports
ADB_MCP_PORT = int(os.getenv("ADB_MCP_PORT", 5001))
CONFLUENCE_MCP_PORT = int(os.getenv("CONFLUENCE_MCP_PORT", 5002))
SQLITE_MCP_PORT = int(os.getenv("SQLITE_MCP_PORT", 5003))

# Orchestrator
ORCHESTRATOR_PORT = int(os.getenv("ORCHESTRATOR_PORT", 8080))

# Device Settings
DEFAULT_DEVICE_UNLOCK_PIN = os.getenv("DEFAULT_DEVICE_UNLOCK_PIN", "1234")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Save the file.

# Create a simple test file test_setup.py:

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

# Run it:
python test_setup.py

# You should see all green checkmarks! ✅









