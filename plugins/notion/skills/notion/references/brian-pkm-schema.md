# Brian's PKM Schema — Real IDs and Recipes

## Workspace

- **Workspace**: bdmspace
- **Bot**: n8n (internal integration)
- **PKM Hub Page**: `31bc075c-f4fe-81d7-986a-e5aedc8d0f7b`

## Database IDs

| Database | database_id | data_source_id |
|----------|------------|----------------|
| Projects | `31bc075c-f4fe-81ab-8916-edbf69e9886d` | `31bc075c-f4fe-81e4-bc05-000bb4770a59` |
| Tasks | `31bc075c-f4fe-8194-8587-e2ad8c8e25c9` | `31bc075c-f4fe-8139-a555-000b4b6b48c7` |
| Notes | `31bc075c-f4fe-81a4-b101-d8699b3b6672` | `31bc075c-f4fe-81e2-8405-000be2f6c4d6` |
| Research | `31bc075c-f4fe-814e-9896-c464f89ef5a0` | `31bc075c-f4fe-81a1-a948-000bd41019a7` |
| Journal | `31bc075c-f4fe-81bf-9d16-ff204efaf2f9` | `31bc075c-f4fe-818c-9318-000b6beed256` |

## Property Schemas

### Projects
| Property | Type | Options |
|----------|------|---------|
| Name | title | — |
| Status | select | Active, Paused, Done, Archived |
| Area | select | Personal, Work, Side Project, Learning |
| Tags | multi_select | (dynamic) |
| Start Date | date | — |
| URL | url | — |

### Tasks
| Property | Type | Options |
|----------|------|---------|
| Name | title | — |
| Status | select | Todo, In Progress, Done, Blocked |
| Priority | select | P0, P1, P2, P3 |
| Project | relation | → Projects database |
| Due Date | date | — |
| Assignee | rich_text | — |

### Notes
| Property | Type | Options |
|----------|------|---------|
| Name | title | — |
| Type | select | Note, Meeting, Idea, Decision, Bookmark, Contact |
| Project | relation | → Projects database |
| Tags | multi_select | (dynamic) |
| URL | url | — |
| Created | created_time | (auto) |

### Research
| Property | Type | Options |
|----------|------|---------|
| Name | title | — |
| Source | url | — |
| Summary | rich_text | — |
| Project | relation | → Projects database |
| Agent | select | Claude, Gemini, Manual |
| Tags | multi_select | (dynamic) |
| Date | date | — |

### Journal
| Property | Type | Options |
|----------|------|---------|
| Date | title | — |
| Mood | select | Great, Good, Okay, Rough, Bad |
| Energy | select | High, Medium, Low |
| Body | rich_text | — |
| Tags | multi_select | (dynamic) |

## Relations Map

```
Tasks.Project ──→ Projects
Notes.Project ──→ Projects
Research.Project ──→ Projects
```

## Pre-Built Recipes

### Add task with project relation

```bash
NOTION_API_KEY=$(grep NOTION_API_KEY plugins/notion/.env | cut -d= -f2-)
TASKS_DS="31bc075c-f4fe-8139-a555-000b4b6b48c7"

# First find the project by name
PROJECT_ID=$(curl -s -X POST "https://api.notion.com/v1/data_sources/31bc075c-f4fe-81e4-bc05-000bb4770a59/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"filter": {"property": "Name", "rich_text": {"contains": "PROJECT_NAME"}}}' \
  | jq -r '.results[0].id')

# Then create the task
curl -s -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "data_source_id", "data_source_id": "'$TASKS_DS'"},
    "properties": {
      "Name": {"title": [{"text": {"content": "TASK_TITLE"}}]},
      "Status": {"select": {"name": "Todo"}},
      "Priority": {"select": {"name": "P1"}},
      "Project": {"relation": [{"id": "'$PROJECT_ID'"}]}
    }
  }' | jq '{id: .id, title: .properties.Name.title[0].plain_text}'
```

### Quick capture note

```bash
NOTION_API_KEY=$(grep NOTION_API_KEY plugins/notion/.env | cut -d= -f2-)
NOTES_DS="31bc075c-f4fe-81e2-8405-000be2f6c4d6"

curl -s -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "data_source_id", "data_source_id": "'$NOTES_DS'"},
    "properties": {
      "Name": {"title": [{"text": {"content": "NOTE_TITLE"}}]},
      "Type": {"select": {"name": "Note"}},
      "Tags": {"multi_select": [{"name": "TAG1"}]}
    }
  }' | jq '{id: .id, title: .properties.Name.title[0].plain_text}'
```

### Log research from agent pipeline

```bash
NOTION_API_KEY=$(grep NOTION_API_KEY plugins/notion/.env | cut -d= -f2-)
RESEARCH_DS="31bc075c-f4fe-81a1-a948-000bd41019a7"

curl -s -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "data_source_id", "data_source_id": "'$RESEARCH_DS'"},
    "properties": {
      "Name": {"title": [{"text": {"content": "RESEARCH_TITLE"}}]},
      "Source": {"url": "SOURCE_URL"},
      "Summary": {"rich_text": [{"text": {"content": "SUMMARY_TEXT"}}]},
      "Project": {"relation": [{"id": "PROJECT_PAGE_ID"}]},
      "Agent": {"select": {"name": "Claude"}},
      "Tags": {"multi_select": [{"name": "TAG1"}]},
      "Date": {"date": {"start": "YYYY-MM-DD"}}
    }
  }' | jq '{id: .id, title: .properties.Name.title[0].plain_text}'
```

### Journal entry

```bash
NOTION_API_KEY=$(grep NOTION_API_KEY plugins/notion/.env | cut -d= -f2-)
JOURNAL_DS="31bc075c-f4fe-818c-9318-000b6beed256"

curl -s -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "data_source_id", "data_source_id": "'$JOURNAL_DS'"},
    "properties": {
      "Date": {"title": [{"text": {"content": "'$(date +%Y-%m-%d)'"}}]},
      "Mood": {"select": {"name": "MOOD"}},
      "Energy": {"select": {"name": "ENERGY"}},
      "Body": {"rich_text": [{"text": {"content": "BODY_TEXT"}}]},
      "Tags": {"multi_select": [{"name": "TAG1"}]}
    }
  }' | jq '{id: .id, date: .properties.Date.title[0].plain_text}'
```

### Search across all databases

```bash
NOTION_API_KEY=$(grep NOTION_API_KEY plugins/notion/.env | cut -d= -f2-)

curl -s -X POST https://api.notion.com/v1/search \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "SEARCH_TERMS", "page_size": 20}' \
  | jq '[.results[] | {
    type: .object,
    title: (if .object == "page" then (.properties | to_entries | map(select(.value.type == "title")) | .[0].value.title[0].plain_text // "untitled") else (.title[0].plain_text // "untitled") end),
    id: .id,
    url: .url
  }]'
```

### Query tasks by project and status

```bash
NOTION_API_KEY=$(grep NOTION_API_KEY plugins/notion/.env | cut -d= -f2-)
TASKS_DS="31bc075c-f4fe-8139-a555-000b4b6b48c7"

curl -s -X POST "https://api.notion.com/v1/data_sources/$TASKS_DS/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "and": [
        {"property": "Project", "relation": {"contains": "PROJECT_PAGE_ID"}},
        {"property": "Status", "select": {"does_not_equal": "Done"}}
      ]
    },
    "sorts": [{"property": "Priority", "direction": "ascending"}]
  }' | jq '[.results[] | {
    title: .properties.Name.title[0].plain_text,
    status: .properties.Status.select.name,
    priority: .properties.Priority.select.name
  }]'
```
