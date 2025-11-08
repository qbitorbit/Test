import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://10.202.1.3:8000/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "/models/openai/gpt-oss-120b")

# MCP Server Ports
ADB_MCP_PORT = int(os.getenv("ADB_MCP_PORT", "5001"))
CONFLUENCE_MCP_PORT = int(os.getenv("CONFLUENCE_MCP_PORT", "5002"))
SQLITE_MCP_PORT = int(os.getenv("SQLITE_MCP_PORT", "5003"))

# Orchestrator API
ORCHESTRATOR_PORT = int(os.getenv("ORCHESTRATOR_PORT", "8080"))

# Device Configuration
DEFAULT_DEVICE_UNLOCK_PIN = os.getenv("DEFAULT_DEVICE_UNLOCK_PIN", "1234")

# Confluence Configuration
CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL", "https://10.20.15.19:8444/rest/api/content")
CONFLUENCE_API_KEY = os.getenv("CONFLUENCE_API_KEY", "")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Telemetry
OTEL_SDK_DISABLE = os.getenv("OTEL_SDK_DISABLE", "true")
