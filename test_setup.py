#!/usr/bin/env python3
"""
Main Orchestrator - Routes tasks to appropriate agents
"""
import sys
sys.path.insert(0, '.')

from agents.adb_agent import ADBAgent


# ANSI Colors
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
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
        
        # Future agents:
        # self.agents["confluence"] = ConfluenceAgent()
        # self.agents["sqlite"] = SQLiteAgent()
    
    def route_task(self, task: str) -> dict:
        """
        Route a task to the appropriate agent
        
        For now, routes everything to ADB agent.
        Future: add intelligent routing based on task content
        
        Args:
            task: Natural language task description
            
        Returns:
            Task execution results
        """
        # Simple routing: if task mentions confluence/wiki, route to confluence agent
        # Otherwise, route to ADB agent
        
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["confluence", "wiki", "document", "page"]):
            # Future: route to confluence agent
            print(f"{Colors.CYAN}ℹ️  Confluence agent not implemented yet{Colors.END}")
            return {"success": False, "error": "Confluence agent not available"}
        
        # Default: route to ADB agent
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
        print(f"  • {Colors.DIM}'quit' or 'exit' to stop{Colors.END}")
        print(f"{Colors.CYAN}{'─'*70}{Colors.END}\n")
        
        while True:
            try:
                user_input = input(f"{Colors.BOLD}{Colors.GREEN}You ▸{Colors.END} ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.END}\n")
                    break
                
                if not user_input:
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
