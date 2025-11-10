# General Orchestration Skills

## Best Practices for AI Agent Orchestration

### Task Analysis
Before executing any task:
1. Identify the domain (Android/Confluence/Files/etc)
2. Break into steps
3. Determine dependencies
4. Plan error handling

### Agent Selection
- **ADB Agent**: Device operations, apps, screenshots, input
- **Confluence Agent**: Documentation, search, create/update pages
- **Future agents**: SQLite, Files, Logs, etc.

### Multi-Step Execution
When tasks require multiple steps:
1. Execute sequentially by default
2. Verify each step before proceeding
3. Store intermediate results in context
4. Handle failures gracefully

### Context Management
- Store important values (device_id, page_id, etc.)
- Pass context between steps
- Don't ask for same info twice
- Clear context when task complete

### Error Recovery
When a step fails:
1. Check if can retry (connection issues)
2. Try alternative approach
3. Provide helpful error message
4. Don't continue if prerequisite fails

### Output Formatting
- Use colors for readability
- Group related information
- Show progress clearly
- Provide links when available

### Common Patterns

#### Pattern: Verify Before Action
```
1. Check current state
2. Perform action
3. Verify result
```

#### Pattern: Iterative Refinement
```
1. Try action
2. If fails, adjust parameters
3. Retry with new parameters
```

#### Pattern: Information Gathering
```
1. Collect from source 1
2. Collect from source 2
3. Combine and present
```

### Tool Usage Guidelines

#### When to Use Which Tool
- **Search**: Finding information
- **Get**: Retrieving specific item
- **List**: Discovering options
- **Create**: Making something new
- **Update**: Modifying existing
- **Execute**: Running commands

#### Tool Sequencing
Some operations require specific order:
1. Connect before operating (ADB)
2. Search before retrieve (Confluence)
3. Get version before update (Confluence)
4. Verify before commit

### Prompt Engineering

#### Good Prompts for LLM
- Specific and clear
- Include constraints
- Specify format needed
- Provide examples when helpful

#### Bad Prompts
- Too vague
- Contradictory requirements
- Missing key information
- Unrealistic expectations

### Performance Optimization
- Cache frequently used data
- Avoid redundant operations
- Batch when possible
- Use specific queries (not broad searches)

### Security Considerations
- Never expose credentials
- Respect permissions
- Don't delete without confirmation
- Validate user input

### User Experience

#### Good UX Patterns
- Show progress
- Confirm destructive actions
- Provide clear success/failure messages
- Offer helpful suggestions
- Give links to results

#### Bad UX Patterns
- Silent failures
- Cryptic error messages
- No progress indication
- Assuming user knowledge

### Workflow Design

#### Simple Workflow
```
Input → Action → Output
```

#### Complex Workflow
```
Input → Validation → Action 1 → Verify → Action 2 → Output
```

#### Conditional Workflow
```
Input → Check State → If A: Path 1, If B: Path 2 → Output
```

### Debugging Tips
- Enable verbose mode for details
- Check tool availability
- Verify parameters
- Test each step individually
- Review LLM reasoning

### Common Mistakes to Avoid
- Skipping validation steps
- Ignoring error messages
- Not handling edge cases
- Assuming success without verification
- Over-complicating simple tasks

### Best Practices Summary
1. ✅ Validate inputs
2. ✅ Check prerequisites
3. ✅ Handle errors gracefully
4. ✅ Verify results
5. ✅ Provide clear feedback
6. ✅ Use appropriate tools
7. ✅ Keep context clean
8. ✅ Format output well

### Language and Tone
- Be clear and concise
- Use technical terms appropriately
- Explain when necessary
- Stay professional
- Be helpful, not condescending

### Extensibility
When adding new capabilities:
- Follow existing patterns
- Keep modules small
- Document thoroughly
- Test independently
- Integrate gradually

### Maintenance
- Review and update skills regularly
- Remove outdated information
- Add new patterns as discovered
- Keep examples current
- Document breaking changes
