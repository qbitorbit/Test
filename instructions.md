# Step 2: Update Agents to Read Skills

## Files to Create/Update

### 2A: Create skills_loader.py
**File:** `AI-PROJECT/utils/skills_loader.py`
**Content:** Download from outputs

### 2B: Update ADB Agent
**File:** `AI-PROJECT/agents/adb_agent.py`

**Add this import at the top** (around line 13):
```python
from utils.skills_loader import load_multiple_skills
```

**Update the execute_task method** - Find this line (around line 235):
```python
# Create prompt for LLM
prompt = f"""You are an Android Device Controller. Your task is to {task_description}.
```

**Replace with:**
```python
# Load skills
skills_content = load_multiple_skills(['adb_skills', 'general_skills'])

# Create prompt for LLM
prompt = f"""You are an Android Device Controller. Your task is to {task_description}.

{skills_content}

Available tools:
```

### 2C: Update Confluence Agent  
**File:** `AI-PROJECT/agents/confluence_agent.py`

**Add same import** at top (around line 12):
```python
from utils.skills_loader import load_multiple_skills
```

**Update execute_task method** - Find this line (around line 295):
```python
# Create prompt for LLM
prompt = f"""You are a Confluence Documentation Manager. Your task is to {task_description}.
```

**Replace with:**
```python
# Load skills
skills_content = load_multiple_skills(['confluence_skills', 'general_skills'])

# Create prompt for LLM
prompt = f"""You are a Confluence Documentation Manager. Your task is to {task_description}.

{skills_content}

Available tools:
```

## Testing

After updates, test:
```bash
python main.py
You ▸ list all connected devices
```

The agent should now use skills for better decisions!

## What Changed?
- Agents load relevant skill files before execution
- Skills are included in LLM prompt
- LLM makes better decisions with examples/patterns

Tell me "Step 2 done" when complete!
