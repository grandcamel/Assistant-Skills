# Confluence Assistant Skills Patterns

Patterns extracted from the Confluence-Assistant-Skills project (14 skills, 60+ scripts, 200+ tests).

## Project Structure

```
Confluence-Assistant-Skills/
├── .claude/
│   ├── settings.json
│   ├── commands/
│   └── skills/
│       ├── shared/
│       ├── confluence-assistant/   # Hub skill
│       ├── confluence-page/        # Page CRUD
│       ├── confluence-space/       # Space management
│       ├── confluence-search/      # CQL queries
│       ├── confluence-content/     # Content operations
│       ├── confluence-template/    # Templates
│       ├── confluence-export/      # Export formats
│       ├── confluence-labels/      # Label management
│       ├── confluence-attachments/ # File handling
│       ├── confluence-comments/    # Comments
│       ├── confluence-permissions/ # Access control
│       ├── confluence-macros/      # Macro handling
│       ├── confluence-hierarchy/   # Page trees
│       └── confluence-admin/       # Admin ops
├── docs/
└── README.md
```

## Content-Specific Patterns

### Atlassian Document Format (ADF)

Confluence uses ADF for rich content. Key patterns:

```python
from adf_helper import (
    create_paragraph,
    create_heading,
    create_code_block,
    create_table,
    adf_to_markdown,
    markdown_to_adf
)

# Creating content
content = {
    'type': 'doc',
    'content': [
        create_heading('Title', level=1),
        create_paragraph('Body text'),
        create_code_block('python', 'print("hello")')
    ]
}
```

### Template System

```python
# Template with placeholders
template = {
    'name': 'Meeting Notes',
    'body': {
        'storage': {
            'value': '<h1>Meeting: {{title}}</h1><p>Date: {{date}}</p>',
            'representation': 'storage'
        }
    }
}

# Apply template
page = apply_template(template, {
    'title': 'Sprint Planning',
    'date': '2024-01-15'
})
```

## Hierarchical Content Pattern

Confluence has parent-child page relationships:

```python
# Get page tree
tree = client.get_page_tree(space_key='PROJ', root_page_id='123')

# Move page
client.move_page(page_id='456', new_parent_id='789')

# Bulk operations on tree
for page in tree.descendants():
    update_page_labels(page.id, ['archived'])
```

## Export Pattern

```python
# Export to different formats
export_to_pdf(page_id, output_path)
export_to_word(page_id, output_path)
export_space_to_html(space_key, output_dir)
```

## Configuration Pattern

```json
{
  "confluence": {
    "default_profile": "production",
    "profiles": {
      "production": {
        "url": "https://company.atlassian.net/wiki",
        "default_space": "DOCS"
      }
    },
    "content": {
      "default_format": "storage",
      "enable_markdown": true
    }
  }
}
```

## Key Differences from Jira

| Aspect | Jira | Confluence |
|--------|------|------------|
| Primary resource | Issues | Pages |
| Query language | JQL | CQL |
| Content format | Plain/ADF | Storage/ADF |
| Hierarchy | Epics > Stories | Spaces > Pages > Children |
| Attachments | On issues | On pages |

## Key Metrics

| Metric | Value |
|--------|-------|
| Skills | 14 |
| Scripts | 60+ |
| Tests | 200+ |
| Focus | Content management |
