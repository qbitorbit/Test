#!/usr/bin/env python3
"""
Main Orchestrator - Routes tasks to appropriate agents
"""
import sys
sys.path.insert(0, '.')

from agents.adb_agent import ADBAgent
from agents.confluence_agent import ConfluenceAgent


# ANSI Colors
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    END = '\033[0m'
    DIM = '\033[2m'


class Orchestrator:
    """
    Main orchestrator that manages agents and routes tasks
    """
    
    def __init__(self):
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents"""
        # ADB Agent for Android device control
        self.agents["adb"] = ADBAgent()
        
        # Confluence Agent for documentation management
        self.agents["confluence"] = ConfluenceAgent()
        
        # Future agents:
        # self.agents["sqlite"] = SQLiteAgent()
        # self.agents["jira"] = JiraAgent()
    
    def route_task(self, task: str) -> dict:
        """
        Route a task to the appropriate agent based on content
        
        Args:
            task: Natural language task description
            
        Returns:
            Task execution results
        """
        task_lower = task.lower()
        
        # Confluence keywords
        confluence_keywords = [
            "confluence", "document", "documentation", "page", "wiki",
            "search", "article", "space", "content", "write", "create page",
            "update page", "edit page", "find page", "summarize"
        ]
        
        # ADB keywords
        adb_keywords = [
            "device", "phone", "android", "adb", "app", "install",
            "screenshot", "tap", "swipe", "shell", "command", "package"
        ]
        
        # Check for Confluence keywords
        confluence_score = sum(1 for keyword in confluence_keywords if keyword in task_lower)
        
        # Check for ADB keywords
        adb_score = sum(1 for keyword in adb_keywords if keyword in task_lower)
        
        # Route based on scores
        if confluence_score > adb_score:
            print(f"{Colors.CYAN}📚 Routing to: Confluence Agent{Colors.END}\n")
            agent = self.agents["confluence"]
            return agent.execute_task(task)
        
        elif adb_score > confluence_score:
            print(f"{Colors.CYAN}📱 Routing to: ADB Agent{Colors.END}\n")
            agent = self.agents["adb"]
            return agent.execute_task(task)
        
        else:
            # Default to ADB if unclear
            print(f"{Colors.YELLOW}⚠️  Task unclear, defaulting to: ADB Agent{Colors.END}\n")
            agent = self.agents["adb"]
            return agent.execute_task(task)
    
    def interactive_mode(self):
        """Run orchestrator in interactive mode"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'🤖 AI Agent Orchestrator - Interactive Mode'.center(70)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")
        
        print(f"{Colors.BOLD}Available Agents:{Colors.END}")
        for name, agent in self.agents.items():
            print(f"  • {Colors.CYAN}{agent.name}{Colors.END}")
            print(f"    {Colors.DIM}{agent.role}{Colors.END}")
        
        print(f"\n{Colors.BOLD}Commands:{Colors.END}")
        print(f"  • Type your task in natural language")
        print(f"  • Type {Colors.GREEN}'agents'{Colors.END} to see available agents")
        print(f"  • Type {Colors.GREEN}'examples'{Colors.END} to see example tasks")
        print(f"  • Type {Colors.DIM}'quit' or 'exit'{Colors.END} to stop")
        print(f"{Colors.CYAN}{'─'*70}{Colors.END}\n")
        
        while True:
            try:
                user_input = input(f"{Colors.BOLD}{Colors.GREEN}You ▸{Colors.END} ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.END}\n")
                    break
                
                if not user_input:
                    continue
                
                # Special commands
                if user_input.lower() == 'agents':
                    print(f"\n{Colors.BOLD}Available Agents:{Colors.END}")
                    for name, agent in self.agents.items():
                        print(f"  • {Colors.CYAN}{agent.name}{Colors.END} - {agent.role}")
                    print()
                    continue
                
                if user_input.lower() == 'examples':
                    print(f"\n{Colors.BOLD}Example Tasks:{Colors.END}\n")
                    print(f"{Colors.CYAN}📱 Android (ADB):{Colors.END}")
                    print(f"  • list all connected devices")
                    print(f"  • get device info")
                    print(f"  • list installed packages")
                    print(f"  • take a screenshot")
                    print(f"  • launch chrome app\n")
                    print(f"{Colors.CYAN}📚 Confluence:{Colors.END}")
                    print(f"  • search for API documentation")
                    print(f"  • list all spaces")
                    print(f"  • get pages in DEV space")
                    print(f"  • show me page ID 123456")
                    print(f"  • create a new page called 'Test' in DEV space")
                    print()
                    continue
                
                # Route and execute task
                result = self.route_task(user_input)
                
                # Print summary
                print(f"\n{Colors.CYAN}{'─'*70}{Colors.END}")
                print(f"{Colors.BOLD}Summary:{Colors.END}")
                if result.get("success"):
                    print(f"{Colors.GREEN}✅ Task completed - {result.get('actions_taken', 0)} actions executed{Colors.END}")
                else:
                    print(f"❌ Task failed: {result.get('error')}")
                print(f"{Colors.CYAN}{'─'*70}{Colors.END}\n")
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.CYAN}👋 Goodbye!{Colors.END}\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                import traceback
                traceback.print_exc()


def main():
    """Main entry point"""
    orchestrator = Orchestrator()
    
    if len(sys.argv) > 1:
        # Command line mode: python main.py "your task here"
        task = " ".join(sys.argv[1:])
        result = orchestrator.route_task(task)
        
        print(f"\n{Colors.BOLD}Final Result:{Colors.END}")
        print(f"Success: {result.get('success')}")
        print(f"Actions: {result.get('actions_taken', 0)}")
    else:
        # Interactive mode
        orchestrator.interactive_mode()


if __name__ == "__main__":
    main()
