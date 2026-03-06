# Pages — Create, Update, Retrieve, Archive

## Create a Page (row in a database)

```bash
curl -s -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"type": "data_source_id", "data_source_id": "DS_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "Page title"}}]}
    },
    "children": [
      {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Body text"}}]}}
    ]
  }'
```

- `parent` — use `data_source_id` for database rows (2025-09-03), `page_id` for sub-pages
- `properties` — must match the database schema
- `children` — optional, adds block content to the page body

## Create a Sub-page (under another page)

```bash
curl -s -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "PARENT_PAGE_ID"},
    "properties": {
      "title": {"title": [{"text": {"content": "Sub-page title"}}]}
    }
  }'
```

Note: standalone pages use `"title"` as the property name (lowercase).

## Retrieve a Page

```bash
curl -s "https://api.notion.com/v1/pages/$PAGE_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

Returns properties but NOT block content. Use blocks API for body.

## Retrieve Page Properties

For large property values (relations, rollups):

```bash
curl -s "https://api.notion.com/v1/pages/$PAGE_ID/properties/$PROPERTY_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

## Update Page Properties

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/$PAGE_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Status": {"select": {"name": "Done"}},
      "Priority": {"select": {"name": "P0"}}
    }
  }'
```

Only include properties you want to change. Omitted properties stay unchanged.

## Archive (Soft Delete)

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/$PAGE_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"archived": true}'
```

Restore: `{"archived": false}`

## Permanently Delete

```bash
curl -s -X DELETE "https://api.notion.com/v1/blocks/$PAGE_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

Warning: permanent, not recoverable.

## Icon and Cover

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/$PAGE_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "icon": {"type": "emoji", "emoji": "🎯"},
    "cover": {"type": "external", "external": {"url": "https://example.com/image.jpg"}}
  }'
```
