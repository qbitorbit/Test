#!/usr/bin/env python3
"""
Confluence Agent - Handles Confluence documentation tasks
"""
import json
import re
import sys
sys.path.insert(0, '.')

from utils.mcp_client import MCPClient
from mcp_servers import confluence_simple
import requests
from config.settings import LLM_BASE_URL, LLM_MODEL, CONFLUENCE_BASE_URL, CONFLUENCE_API_KEY


# ANSI Color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    DIM = '\033[2m'


class OutputFormatter:
    """Handles beautiful output formatting for Confluence"""
    
    @staticmethod
    def print_success(text: str):
        print(f"{Colors.GREEN}✅ {text}{Colors.END}")
    
    @staticmethod
    def print_error(text: str):
        print(f"{Colors.RED}❌ {text}{Colors.END}")
    
    @staticmethod
    def print_warning(text: str):
        print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")
    
    @staticmethod
    def print_info(text: str):
        print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")
    
    @staticmethod
    def print_step(step_num: int, total: int, text: str):
        print(f"\n{Colors.BOLD}{Colors.YELLOW}⚙️  Step {step_num}/{total}:{Colors.END} {text}")
    
    @staticmethod
    def format_search_results(results: dict) -> str:
        """Format search results beautifully"""
        if not results.get("success"):
            return f"{Colors.RED}Search failed: {results.get('error')}{Colors.END}"
        
        pages = results.get("pages", [])
        count = results.get("count", 0)
        query = results.get("query", "")
        
        if count == 0:
            return f"{Colors.YELLOW}No pages found matching: {query}{Colors.END}"
        
        lines = [
            f"{Colors.BOLD}📚 Found {count} pages matching \"{query}\":{Colors.END}\n"
        ]
        
        for i, page in enumerate(pages, 1):
            lines.append(f"{i}. {Colors.BOLD}📄 {page.get('title')}{Colors.END} ({Colors.CYAN}{page.get('space_key')}{Colors.END})")
            lines.append(f"   🔗 {Colors.DIM}{page.get('url')}{Colors.END}")
            if i < len(pages):
                lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_page_content(content: dict) -> str:
        """Format page content beautifully"""
        if not content.get("success"):
            return f"{Colors.RED}Failed to get page: {content.get('error')}{Colors.END}"
        
        lines = [
            f"{Colors.BOLD}📄 {content.get('title')}{Colors.END}",
            f"🔗 {Colors.DIM}{content.get('url')}{Colors.END}",
            f"👤 Author: {Colors.GREEN}{content.get('author', 'Unknown')}{Colors.END}",
            f"📅 Updated: {Colors.GREEN}{content.get('updated', 'Unknown')}{Colors.END}",
            f"📦 Space: {Colors.CYAN}{content.get('space_name')} ({content.get('space_key')}){Colors.END}",
            f"🔢 Version: {Colors.GREEN}{content.get('version')}{Colors.END}",
            "",
            f"{Colors.DIM}{'━' * 70}{Colors.END}",
            content.get('content', ''),
            f"{Colors.DIM}{'━' * 70}{Colors.END}"
        ]
        
        return "\n".join(lines)
    
    @staticmethod
    def format_spaces_list(spaces: dict) -> str:
        """Format spaces list"""
        if not spaces.get("success"):
            return f"{Colors.RED}Failed to list spaces: {spaces.get('error')}{Colors.END}"
        
        space_list = spaces.get("spaces", [])
        count = spaces.get("count", 0)
        
        lines = [f"{Colors.BOLD}📚 Available Spaces ({count}):{Colors.END}\n"]
        
        for space in space_list:
            lines.append(
                f"  • {Colors.BOLD}{Colors.CYAN}{space.get('key')}{Colors.END} - "
                f"{space.get('name')} {Colors.DIM}({space.get('type')}){Colors.END}"
            )
        
        return "\n".join(lines)
    
    @staticmethod
    def format_page_list(pages: dict) -> str:
        """Format page list"""
        if not pages.get("success"):
            return f"{Colors.RED}Failed to list pages: {pages.get('error')}{Colors.END}"
        
        page_list = pages.get("pages", [])
        count = pages.get("count", 0)
        space_key = pages.get("space_key", "")
        
        lines = [f"{Colors.BOLD}📄 Pages in {space_key} ({count}):{Colors.END}\n"]
        
        for page in page_list:
            lines.append(
                f"  • {Colors.GREEN}{page.get('title')}{Colors.END} "
                f"{Colors.DIM}(v{page.get('version')}){Colors.END}"
            )
            lines.append(f"    🔗 {Colors.DIM}{page.get('url')}{Colors.END}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_comments(comments: dict) -> str:
        """Format comments"""
        if not comments.get("success"):
            return f"{Colors.RED}Failed to get comments: {comments.get('error')}{Colors.END}"
        
        comment_list = comments.get("comments", [])
        count = comments.get("count", 0)
        
        if count == 0:
            return f"{Colors.YELLOW}No comments on this page{Colors.END}"
        
        lines = [f"{Colors.BOLD}💬 Comments ({count}):{Colors.END}\n"]
        
        for comment in comment_list:
            lines.append(f"  {Colors.BOLD}{comment.get('author')}{Colors.END} - {Colors.DIM}{comment.get('created')}{Colors.END}")
            content = comment.get('content', '')
            lines.append(f"  {content[:200]}..." if len(content) > 200 else f"  {content}")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_result(result: dict) -> str:
        """Smart formatting based on result content"""
        if not result.get("success"):
            error = result.get("error", "Unknown error")
            return f"{Colors.RED}Error: {error}{Colors.END}"
        
        # Search results
        if "pages" in result and "query" in result:
            return OutputFormatter.format_search_results(result)
        
        # Page content
        elif "content" in result and "title" in result:
            return OutputFormatter.format_page_content(result)
        
        # Spaces list
        elif "spaces" in result:
            return OutputFormatter.format_spaces_list(result)
        
        # Page list
        elif "pages" in result and "space_key" in result:
            return OutputFormatter.format_page_list(result)
        
        # Comments
        elif "comments" in result:
            return OutputFormatter.format_comments(result)
        
        # Page creation/update
        elif "page_id" in result and "message" in result:
            return (
                f"{Colors.GREEN}✅ {result.get('message')}{Colors.END}\n"
                f"📄 Title: {result.get('title')}\n"
                f"🔗 URL: {result.get('url')}"
            )
        
        # Generic success
        elif "message" in result:
            return f"{Colors.GREEN}{result.get('message')}{Colors.END}"
        
        # Default
        return f"{Colors.GREEN}Operation completed successfully{Colors.END}"


class ConfluenceAgent:
    """
    Confluence Agent - Handles Confluence documentation tasks
    """
    
    def __init__(self):
        self.name = "Confluence Agent"
        self.role = "Documentation Manager - Expert in Confluence search, content management, and documentation"
        
        # Initialize Confluence credentials
        confluence_simple.set_confluence_credentials(CONFLUENCE_BASE_URL, CONFLUENCE_API_KEY)
        
        self.mcp_client = MCPClient(confluence_simple)
        self.formatter = OutputFormatter()
    
    def _call_llm(self, prompt: str) -> str:
        """Call the local LLM with a prompt"""
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": f"You are {self.role}"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 1500
        }
        
        try:
            response = requests.post(
                f"{LLM_BASE_URL}/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
            
            return None
            
        except Exception as e:
            self.formatter.print_error(f"LLM Error: {e}")
            return None
    
    def _extract_tool_calls(self, llm_response: str) -> list:
        """Extract tool calls from LLM response"""
        try:
            cleaned = llm_response.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(cleaned)
            
            if "actions" in parsed:
                return parsed["actions"]
            elif "tool" in parsed:
                return [parsed]
            
            return []
            
        except json.JSONDecodeError:
            self.formatter.print_warning("Could not parse JSON, attempting pattern matching...")
            return []
    
    def execute_task(self, task_description: str) -> dict:
        """
        Execute a Confluence task using available tools
        
        Args:
            task_description: Natural language task description
            
        Returns:
            dict with success status and results
        """
        self.formatter.print_info(f"Task: {task_description}")
        
        # Get available tools
        available_tools = self.mcp_client.list_tools()
        tool_descriptions = self.mcp_client.get_tool_descriptions()
        
        # Format tools for LLM
        tools_info = []
        for tool_name in available_tools:
            if tool_name in tool_descriptions:
                desc = tool_descriptions[tool_name]
                tools_info.append(f"- {tool_name}: {desc['description']}")
        
        tools_text = "\n".join(tools_info)
        
        # Create prompt for LLM
        prompt = f"""You are a Confluence Documentation Manager. Your task is to {task_description}.

Available tools:
{tools_text}

IMPORTANT NOTES:
- Use search_confluence for searching pages (CQL syntax: "space = KEY and label = tag")
- Use get_page_content to retrieve full page content by ID
- Use get_page_by_title to find pages by title in a specific space
- Use create_page to create new documentation
- Use update_page to modify existing pages (requires version number)
- Always provide specific parameters (space keys, page IDs, etc.)

Analyze the task and respond with a JSON object containing:
1. "reasoning": Brief explanation of your approach
2. "actions": Array of tool calls needed to complete the task

Format:
{{
    "reasoning": "I will search for API documentation pages in the DEV space",
    "actions": [
        {{"tool": "search_confluence", "params": {{"query": "space = DEV and label = api", "limit": 10}}}}
    ]
}}

Important:
- Only use tools from the available list
- Provide exact tool names and required parameters
- For search, use proper CQL syntax
- Respond ONLY with valid JSON, no other text

Task: {task_description}
"""
        
        self.formatter.print_info("Asking LLM for action plan...")
        llm_response = self._call_llm(prompt)
        
        if not llm_response:
            return {"success": False, "error": "LLM did not respond"}
        
        # Show LLM reasoning
        try:
            cleaned = llm_response.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(cleaned)
            if "reasoning" in parsed:
                print(f"\n{Colors.DIM}💭 Reasoning: {parsed['reasoning']}{Colors.END}")
        except:
            pass
        
        # Extract actions
        actions = self._extract_tool_calls(llm_response)
        
        if not actions:
            actions = self._pattern_match_task(task_description)
        
        if not actions:
            return {"success": False, "error": "Could not determine actions"}
        
        # Execute actions
        results = []
        context = {}
        
        for i, action in enumerate(actions, 1):
            tool_name = action.get("tool")
            params = action.get("params", {})
            
            self.formatter.print_step(i, len(actions), f"{tool_name}()")
            
            result = self.mcp_client.call_tool(tool_name, **params)
            
            results.append({
                "tool": tool_name,
                "params": params,
                "result": result
            })
            
            # Print formatted result
            print(f"\n{self.formatter.format_result(result)}\n")
            
            # Update context with important values
            if result.get("success"):
                if tool_name == "search_confluence" and result.get("pages"):
                    pages = result.get("pages", [])
                    if pages:
                        context["page_id"] = pages[0]["id"]
                elif tool_name == "get_page_by_title" and result.get("page_id"):
                    context["page_id"] = result.get("page_id")
                    context["version"] = result.get("version")
                elif tool_name == "create_page" and result.get("page_id"):
                    context["page_id"] = result.get("page_id")
        
        return {
            "success": True,
            "task": task_description,
            "actions_taken": len(actions),
            "results": results
        }
    
    def _pattern_match_task(self, task: str) -> list:
        """Fallback pattern matching for common tasks"""
        task_lower = task.lower()
        
        # Search
        if any(word in task_lower for word in ["search", "find", "look for"]):
            return [{"tool": "search_confluence", "params": {"query": task, "limit": 10}}]
        
        # List spaces
        if "list spaces" in task_lower or "show spaces" in task_lower:
            return [{"tool": "list_spaces", "params": {}}]
        
        # Get page content
        if "get page" in task_lower or "show page" in task_lower:
            match = re.search(r'page[_\s]?id[:\s]+(\d+)', task_lower)
            if match:
                page_id = match.group(1)
                return [{"tool": "get_page_content", "params": {"page_id": page_id}}]
        
        return []
