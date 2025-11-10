# Confluence Agent Skills

## Best Practices for Confluence Documentation Management

### CQL (Confluence Query Language)

#### Basic Syntax
- Space filter: `space = DEV`
- Label filter: `label = api`
- Title search: `title ~ "documentation"`
- Text search: `text ~ "authentication"`
- Combine with AND: `space = DEV and label = api`
- Combine with OR: `space = DEV or space = DOCS`

#### Common CQL Patterns
```
# Pages in specific space
space = DEV

# Pages with specific label
space = DEV and label = api

# Pages modified recently
lastmodified >= "2024-01-01"

# Pages by creator
creator = currentUser()

# Pages with specific text
space = DOCS and text ~ "deployment"

# Combining multiple conditions
space = DEV and (label = api or label = documentation)
```

### Search Best Practices
- Always specify space when possible for faster results
- Use labels for categorization
- Limit results appropriately (default: 10)
- Use text search (~) for partial matches
- Use exact match (=) for titles

### Content Creation

#### Page Structure
Good page structure:
```
Title: Clear, descriptive (e.g., "API Authentication Guide")
Content: 
- Brief introduction
- Clear sections with headers
- Code examples
- Links to related pages
```

#### Content Formatting
- Keep paragraphs short (2-4 sentences)
- Use headers for sections
- Use lists for steps or items
- Add code blocks with proper syntax

#### HTML Storage Format
For create/update operations:
- Simple text: `<p>Your text here</p>`
- Headers: `<h2>Section Title</h2>`
- Lists: `<ul><li>Item 1</li><li>Item 2</li></ul>`
- Code: `<ac:structured-macro ac:name="code">...</ac:structured-macro>`

### Space Organization

#### Space Keys
- Usually 2-5 uppercase letters
- Common patterns: DEV, DOCS, TEAM, PROJ
- Use `list_spaces` to discover available spaces

#### Space Types
- Personal: Individual user spaces
- Global: Team/company-wide spaces
- Choose appropriate space based on audience

### Page Hierarchy
- Use parent pages for organization
- Create child pages for sub-topics
- Good hierarchy example:
  ```
  API Documentation (parent)
  ├── Authentication (child)
  ├── Endpoints (child)
  └── Examples (child)
  ```

### Version Management
- Always get current version before updating
- Use `get_page_version` helper
- Increment version number in update
- Version conflicts = someone else edited

### Comments
- Use for feedback/questions
- Thread replies with `parent_id`
- Keep comments constructive
- Use `get_page_comments` before adding

### Common Patterns

#### Pattern: Search and Summarize
```
1. search_confluence(query="space = DEV and label = api")
2. For each result: get_page_content(page_id)
3. Summarize key points
```

#### Pattern: Create Structured Page
```
1. Prepare content with proper HTML
2. create_page(space_key, title, content)
3. Verify creation with returned URL
```

#### Pattern: Safe Update
```
1. get_page_content(page_id) - get current version
2. Modify content
3. update_page(page_id, new_title, new_content, version)
```

#### Pattern: Navigate Hierarchy
```
1. get_page_by_title(space_key, "Parent Page")
2. get_page_children(page_id)
3. Process child pages
```

### Content Guidelines

#### Good Documentation
- Clear title
- Purpose stated upfront
- Step-by-step instructions
- Examples included
- Links to related pages
- Updated regularly

#### Page Naming
- Descriptive: "REST API Authentication" not "API Stuff"
- Consistent: Follow team conventions
- Searchable: Use common terms

#### Labels
- Use consistent labeling scheme
- Common labels: api, documentation, guide, tutorial, internal, public
- Don't over-label (3-5 labels per page)

### Search Optimization

#### Making Pages Discoverable
- Use keywords in title
- Add relevant labels
- Include common search terms in content
- Link from other pages
- Update regularly to boost relevance

#### Search Tips for Users
- Start with space filter
- Add labels for refinement
- Use text search for specific terms
- Check recent modifications

### Error Handling

#### Common Issues

**Page Not Found:**
- Verify space key is correct
- Check page title spelling
- Use search_confluence instead

**Update Fails:**
- Get latest version number
- Check permissions
- Verify page hasn't been deleted

**Create Fails:**
- Verify space key exists
- Check permissions
- Ensure title is unique in space

**Search Returns Nothing:**
- Broaden search criteria
- Check CQL syntax
- Verify space access

### Performance Tips
- Cache frequently accessed pages
- Use specific searches (space + label)
- Limit result count appropriately
- Avoid full-text search when possible

### Security & Permissions
- Respect space permissions
- Don't expose sensitive data
- Use appropriate spaces (Personal vs Global)
- Check user has access before operations

### Documentation Standards

#### When to Create New Page
- New feature/component
- Significant process change
- Team decision/agreement
- Tutorial or guide

#### When to Update Existing
- Corrections or clarifications
- Additional examples
- Process improvements
- Outdated information

#### When to Comment
- Questions about content
- Suggestions for improvement
- Temporary notes
- Feedback on drafts

### Workflow Integration

#### Common Workflows
1. **Meeting Notes → Confluence**
   - Create page with date in title
   - Add attendees, decisions, action items
   - Link to related pages

2. **Code Changes → Documentation**
   - Search for relevant docs
   - Update with new information
   - Add examples

3. **Question → Documentation**
   - Search existing docs
   - If not found, create FAQ entry
   - Link in comments

### Advanced CQL

#### Date Queries
```
# Modified in last 7 days
lastmodified >= now("-7d")

# Created this year
created >= startOfYear()

# Modified between dates
lastmodified >= "2024-01-01" and lastmodified <= "2024-12-31"
```

#### User Queries
```
# My pages
creator = currentUser()

# Pages I contributed to
contributor = currentUser()

# Pages I'm watching
watcher = currentUser()
```

#### Content Queries
```
# Pages with attachments
type = page and attachment is not null

# Pages without labels
type = page and label is null

# Pages with specific macro
macro = "code"
```

### Troubleshooting

**Slow Searches:**
- Add space filter
- Limit results
- Use specific labels
- Avoid wildcards

**Can't Find Page:**
- Use search instead of get_by_title
- Check space permissions
- Verify page exists
- Try partial title match

**Update Conflicts:**
- Get fresh version number
- Merge changes manually
- Consider using comments instead

**Content Not Formatted:**
- Check HTML syntax
- Use proper Confluence macros
- Test with simple content first
