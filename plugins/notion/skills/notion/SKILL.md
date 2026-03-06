---
name: notion
description: "Notion API for PKM: create/query/update pages, databases, blocks, and search.
  Covers Projects, Tasks, Notes, Research, and Journal databases. API version 2025-09-03
  with data source support. Requires NOTION_API_KEY."
user-invokable: true
argument-hint: "notion add task 'Fix login bug' --project zeroclaw --priority P1,
  notion search 'webhook payload', notion add note --type Decision 'Use Bun over Node',
  notion journal 'Productive day, shipped the notion skill', notion query research --project yntk,
  notion query tasks --status 'In Progress', notion projects"
allowed-tools: "Bash(curl *)"
license: MIT
metadata:
  version: "1.0.0"
  author: "Brian Morin"
  homepage: "https://github.com/bdmorin/the-no-shop"
  category: pkm
  api_version: "2025-09-03"
  requires:
    env:
      - NOTION_API_KEY
---

# Notion API — PKM Skill

Base URL: `https://api.notion.com/v1`

## Authentication

Every request requires these headers:

```
Authorization: Bearer $NOTION_API_KEY
Notion-Version: 2025-09-03
Content-Type: application/json
```

Load the token: `NOTION_API_KEY=$(grep NOTION_API_KEY /path/to/plugins/notion/.env | cut -d= -f2-)`

If the .env path is unknown, check common locations:
- `plugins/notion/.env` (relative to project)
- `~/.claude/plugins/notion/.env`

## Data Source Model (2025-09-03)

Databases contain **data sources** with independent schemas. All query/create operations use `data_source_id`, not `database_id`.

See [references/brian-pkm-schema.md](references/brian-pkm-schema.md) for Brian's real IDs.

## Quick Reference — Common Operations

### Add a Task

```bash
curl -s -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "data_source_id", "data_source_id": "TASKS_DS_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "Task title here"}}]},
      "Status": {"select": {"name": "Todo"}},
      "Priority": {"select": {"name": "P1"}},
      "Project": {"relation": [{"id": "PROJECT_PAGE_ID"}]}
    }
  }'
```

### Quick Capture a Note

```bash
curl -s -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "data_source_id", "data_source_id": "NOTES_DS_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "Note title"}}]},
      "Type": {"select": {"name": "Note"}}
    }
  }'
```

Note types: Note, Meeting, Idea, Decision, Bookmark, Contact

### Log Research

```bash
curl -s -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "data_source_id", "data_source_id": "RESEARCH_DS_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "Research title"}}]},
      "Source": {"url": "https://example.com"},
      "Summary": {"rich_text": [{"text": {"content": "Summary text"}}]},
      "Agent": {"select": {"name": "Claude"}},
      "Date": {"date": {"start": "2026-03-05"}}
    }
  }'
```

### Journal Entry

```bash
curl -s -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "data_source_id", "data_source_id": "JOURNAL_DS_ID"},
    "properties": {
      "Date": {"title": [{"text": {"content": "2026-03-05"}}]},
      "Mood": {"select": {"name": "Good"}},
      "Energy": {"select": {"name": "High"}},
      "Body": {"rich_text": [{"text": {"content": "Journal body text"}}]},
      "Tags": {"multi_select": [{"name": "productive"}, {"name": "shipped"}]}
    }
  }'
```

### Query Tasks by Status

```bash
curl -s -X POST https://api.notion.com/v1/data_sources/TASKS_DS_ID/query \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"equals": "In Progress"}},
    "sorts": [{"property": "Priority", "direction": "ascending"}]
  }'
```

### Query Tasks by Project

```bash
curl -s -X POST https://api.notion.com/v1/data_sources/TASKS_DS_ID/query \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Project", "relation": {"contains": "PROJECT_PAGE_ID"}}
  }'
```

### Search Across Everything

```bash
curl -s -X POST https://api.notion.com/v1/search \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "search terms", "page_size": 10}'
```

### List All Projects

```bash
curl -s -X POST https://api.notion.com/v1/data_sources/PROJECTS_DS_ID/query \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"property": "Status", "select": {"does_not_equal": "Archived"}},
    "sorts": [{"property": "Name", "direction": "ascending"}]
  }'
```

### Create a Project

```bash
curl -s -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "data_source_id", "data_source_id": "PROJECTS_DS_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "Project name"}}]},
      "Status": {"select": {"name": "Active"}},
      "Area": {"select": {"name": "Side Project"}},
      "Tags": {"multi_select": [{"name": "tag1"}]},
      "Start Date": {"date": {"start": "2026-03-05"}},
      "URL": {"url": "https://github.com/org/repo"}
    }
  }'
```

### Update a Page

```bash
curl -s -X PATCH https://api.notion.com/v1/pages/PAGE_ID \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Status": {"select": {"name": "Done"}}
    }
  }'
```

### Add Body Content (blocks) to a Page

```bash
curl -s -X PATCH https://api.notion.com/v1/blocks/PAGE_ID/children \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Body text"}}]}},
      {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "Section"}}]}}
    ]
  }'
```

## Key Gotchas

- **data_source_id, not database_id** — page creation and queries use data_source_id in 2025-09-03
- **Parent format** — `{"type": "data_source_id", "data_source_id": "..."}` for new pages
- **Relations** — pass an array of `{"id": "page_id"}` objects
- **Multi-select** — pass an array of `{"name": "tag"}` objects (Notion auto-creates new options)
- **Rich text** — always an array: `[{"text": {"content": "..."}}]`
- **Title property** — uses `{"title": [...]}` not `{"rich_text": [...]}`
- **Date format** — ISO 8601: `{"start": "2026-03-05"}` or `{"start": "2026-03-05", "end": "2026-03-10"}`
- **Internal integration** — cannot create workspace-level pages; all pages need a parent page or database
- **Page access is per-page, not workspace-wide** — moving a page to a new parent does NOT inherit the old parent's integration access. If you move or reorganize pages in Notion, you must re-grant access via the integration's Content Access settings or the API returns 404.
- **Pagination** — responses may have `has_more: true` and `next_cursor` for large result sets

## Reference Files

- [references/brian-pkm-schema.md](references/brian-pkm-schema.md) — Real IDs, property schemas, pre-built recipes
- [references/data-sources.md](references/data-sources.md) — Query, filter, sort (2025-09-03 data source API)
- [references/pages.md](references/pages.md) — Create, update, retrieve, archive pages
- [references/blocks.md](references/blocks.md) — Read/append block content
- [references/search.md](references/search.md) — Search API
- [references/property-types.md](references/property-types.md) — Property value JSON formats
