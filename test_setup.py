import os
from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://10.202.1.3:8000/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "/models/Qwen/Qwen3-Coder-40B-A3B-Instruct-FP8")

ADB_MCP_PORT = int(os.getenv("ADB_MCP_PORT", 5001))
CONFLUENCE_MCP_PORT = int(os.getenv("CONFLUENCE_MCP_PORT", 5002))
SQLITE_MCP_PORT = int(os.getenv("SQLITE_MCP_PORT", 5003))

ORCHESTRATOR_PORT = int(os.getenv("ORCHESTRATOR_PORT", 8080))
DEFAULT_DEVICE_UNLOCK_PIN = os.getenv("DEFAULT_DEVICE_UNLOCK_PIN", "1234")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
