#!/usr/bin/env python3
"""
Workflow Engine - Executes YAML-based multi-step workflows
"""
import yaml
import json
import time
from typing import Dict, Any, List


class WorkflowEngine:
    """
    Executes workflows defined in YAML files
    """
    
    def __init__(self, orchestrator):
        """
        Initialize workflow engine
        
        Args:
            orchestrator: Reference to main orchestrator (for routing tasks)
        """
        self.orchestrator = orchestrator
        self.context = {}  # Shared context across workflow steps
    
    def load_workflow(self, workflow_path: str) -> Dict[str, Any]:
        """
        Load workflow from YAML file
        
        Args:
            workflow_path: Path to workflow YAML file
            
        Returns:
            Workflow definition dict
        """
        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Failed to load workflow: {e}")
            return None
    
    def execute_workflow(self, workflow_path: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a workflow from YAML file
        
        Args:
            workflow_path: Path to workflow YAML file
            variables: Optional variables to pass to workflow
            
        Returns:
            Workflow execution result
        """
        # Load workflow
        workflow = self.load_workflow(workflow_path)
        if not workflow:
            return {"success": False, "error": "Failed to load workflow"}
        
        print(f"\n🔄 Executing Workflow: {workflow.get('name', 'Unnamed')}")
        print(f"📝 Description: {workflow.get('description', 'No description')}\n")
        
        # Initialize context with variables
        self.context = variables or {}
        self.context['workflow_start_time'] = time.time()
        
        # Execute steps
        steps = workflow.get('steps', [])
        results = []
        
        for i, step in enumerate(steps, 1):
            print(f"\n{'='*70}")
            print(f"Step {i}/{len(steps)}: {step.get('name', 'Unnamed Step')}")
            print(f"{'='*70}")
            
            result = self._execute_step(step, i, len(steps))
            results.append(result)
            
            # Check if step failed and should stop
            if not result.get('success', False):
                if step.get('continue_on_error', False):
                    print(f"⚠️  Step failed but continuing due to continue_on_error flag")
                else:
                    print(f"❌ Workflow stopped due to step failure")
                    return {
                        "success": False,
                        "error": f"Step {i} failed: {result.get('error')}",
                        "completed_steps": i - 1,
                        "total_steps": len(steps),
                        "results": results
                    }
            
            # Optional delay between steps
            delay = step.get('delay', 0)
            if delay > 0:
                print(f"⏳ Waiting {delay} seconds before next step...")
                time.sleep(delay)
        
        # Workflow complete
        elapsed = time.time() - self.context['workflow_start_time']
        print(f"\n{'='*70}")
        print(f"✅ Workflow Complete!")
        print(f"⏱️  Total time: {elapsed:.2f} seconds")
        print(f"{'='*70}\n")
        
        return {
            "success": True,
            "workflow": workflow.get('name'),
            "completed_steps": len(steps),
            "total_steps": len(steps),
            "elapsed_time": elapsed,
            "results": results
        }
    
    def _execute_step(self, step: Dict[str, Any], step_num: int, total_steps: int) -> Dict[str, Any]:
        """
        Execute a single workflow step
        
        Args:
            step: Step definition
            step_num: Current step number
            total_steps: Total number of steps
            
        Returns:
            Step execution result
        """
        step_type = step.get('type', 'task')
        
        if step_type == 'task':
            return self._execute_task_step(step)
        elif step_type == 'condition':
            return self._execute_condition_step(step)
        elif step_type == 'set_variable':
            return self._execute_set_variable_step(step)
        elif step_type == 'loop':
            return self._execute_loop_step(step)
        else:
            return {"success": False, "error": f"Unknown step type: {step_type}"}
    
    def _execute_task_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task step (routes to agent)"""
        task = step.get('task', '')
        
        # Replace variables in task
        task = self._replace_variables(task)
        
        print(f"📋 Task: {task}")
        
        # Route task through orchestrator
        result = self.orchestrator.route_task(task)
        
        # Store result in context if specified
        store_as = step.get('store_as')
        if store_as and result.get('success'):
            self.context[store_as] = result
            print(f"💾 Stored result as: {store_as}")
        
        return result
    
    def _execute_condition_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a conditional step"""
        condition = step.get('condition', '')
        condition = self._replace_variables(condition)
        
        print(f"🔍 Checking condition: {condition}")
        
        try:
            # Simple condition evaluation
            result = eval(condition, {"context": self.context})
            
            if result:
                print(f"✅ Condition is TRUE")
                # Execute 'then' steps if provided
                then_steps = step.get('then', [])
                if then_steps:
                    for sub_step in then_steps:
                        self._execute_step(sub_step, 0, 0)
            else:
                print(f"❌ Condition is FALSE")
                # Execute 'else' steps if provided
                else_steps = step.get('else', [])
                if else_steps:
                    for sub_step in else_steps:
                        self._execute_step(sub_step, 0, 0)
            
            return {"success": True, "condition_result": result}
            
        except Exception as e:
            return {"success": False, "error": f"Condition evaluation failed: {e}"}
    
    def _execute_set_variable_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Set a variable in context"""
        var_name = step.get('variable')
        var_value = step.get('value')
        
        # Replace variables in value
        if isinstance(var_value, str):
            var_value = self._replace_variables(var_value)
        
        self.context[var_name] = var_value
        print(f"💾 Set {var_name} = {var_value}")
        
        return {"success": True, "variable": var_name, "value": var_value}
    
    def _execute_loop_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a loop step"""
        items = step.get('items', [])
        item_var = step.get('item_variable', 'item')
        loop_steps = step.get('steps', [])
        
        print(f"🔁 Looping over {len(items)} items")
        
        results = []
        for i, item in enumerate(items, 1):
            print(f"\n  --- Loop iteration {i}/{len(items)} ---")
            self.context[item_var] = item
            
            for loop_step in loop_steps:
                result = self._execute_step(loop_step, 0, 0)
                results.append(result)
                
                if not result.get('success') and not loop_step.get('continue_on_error'):
                    return {"success": False, "error": "Loop step failed", "results": results}
        
        return {"success": True, "iterations": len(items), "results": results}
    
    def _replace_variables(self, text: str) -> str:
        """
        Replace variables in text using context
        Format: {{variable_name}}
        """
        if not isinstance(text, str):
            return text
        
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            return str(self.context.get(var_name, match.group(0)))
        
        return re.sub(r'\{\{(\w+)\}\}', replace_var, text)
