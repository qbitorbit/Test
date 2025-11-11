# Step 3: Add Workflows System - Installation Guide

## 📋 What We're Adding
YAML-based workflow system for multi-step automated tasks

## 📁 Files to Download & Create

### 3A: Create workflow engine
**File:** `AI-PROJECT/utils/workflow_engine.py`
**Download:** workflow_engine.py

### 3B: Create workflows directory and examples
```bash
cd AI-PROJECT
mkdir -p workflows
```

**Copy these 3 workflow examples:**
1. `install_app.yaml` → `AI-PROJECT/workflows/install_app.yaml`
2. `device_setup.yaml` → `AI-PROJECT/workflows/device_setup.yaml`  
3. `confluence_report.yaml` → `AI-PROJECT/workflows/confluence_report.yaml`

### 3C: Install PyYAML
```bash
source venv/bin/activate
pip install pyyaml
```

### 3D: Update main.py

**Add import** at top (after other imports):
```python
from utils.workflow_engine import WorkflowEngine
import os
```

**In Orchestrator.__init__** (after `self._initialize_agents()`):
```python
def __init__(self):
    self.agents = {}
    self._initialize_agents()
    self.workflow_engine = WorkflowEngine(self)  # ← ADD THIS LINE
```

**In interactive_mode**, add workflow commands. Find the section with special commands and add:
```python
if user_input.lower().startswith('workflow '):
    # Extract workflow name
    workflow_name = user_input[9:].strip()
    workflow_path = f"workflows/{workflow_name}.yaml"
    
    if os.path.exists(workflow_path):
        print(f"\n🔄 Executing workflow: {workflow_name}")
        result = self.workflow_engine.execute_workflow(workflow_path)
        print(f"\n{Colors.BOLD}Workflow Result:{Colors.END}")
        print(f"Success: {result.get('success')}")
        print(f"Steps: {result.get('completed_steps')}/{result.get('total_steps')}")
    else:
        print(f"❌ Workflow not found: {workflow_path}")
    print()
    continue
    
if user_input.lower() == 'workflows':
    print(f"\n{Colors.BOLD}Available Workflows:{Colors.END}")
    if os.path.exists('workflows'):
        workflows = [f[:-5] for f in os.listdir('workflows') if f.endswith('.yaml')]
        for wf in workflows:
            print(f"  • {wf}")
        print(f"\nRun with: workflow <name>")
    else:
        print("  No workflows found")
    print()
    continue
```

**Update help text** - Find where it says "Type 'examples'" and add:
```python
print(f"  • Type {Colors.GREEN}'workflows'{Colors.END} to see available workflows")
print(f"  • Type {Colors.GREEN}'workflow <name>'{Colors.END} to run a workflow")
```

## ✅ Testing

```bash
python main.py

# List workflows
You ▸ workflows

# Run a workflow
You ▸ workflow device_setup

# Or pass variables (advanced)
You ▸ workflow install_app
```

## 📊 Expected Structure
```
AI-PROJECT/
├── utils/
│   ├── workflow_engine.py  ← NEW!
│   └── skills_loader.py
├── workflows/              ← NEW!
│   ├── install_app.yaml
│   ├── device_setup.yaml
│   └── confluence_report.yaml
└── (rest of structure)
```

## 🎯 What Workflows Can Do
- ✅ Multi-step automation
- ✅ Variable substitution {{var}}
- ✅ Conditional logic
- ✅ Error handling
- ✅ Context sharing between steps
- ✅ Delays between steps
- ✅ Loop over items

Tell me "Step 3 done" when complete!
