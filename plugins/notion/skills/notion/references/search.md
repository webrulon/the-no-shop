# Search API

## Search All Content

```bash
curl -s -X POST https://api.notion.com/v1/search \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "search terms",
    "page_size": 20
  }'
```

## Parameters

| Param | Type | Description |
|-------|------|-------------|
| query | string | Search text (optional — omit to list all) |
| filter | object | Filter by object type |
| sort | object | Sort results |
| page_size | integer | 1-100, default 100 |
| start_cursor | string | Pagination cursor |

## Filter by Object Type

```json
{"filter": {"value": "page", "property": "object"}}
{"filter": {"value": "database", "property": "object"}}
```

## Sort Options

```json
{"sort": {"direction": "ascending", "timestamp": "last_edited_time"}}
{"sort": {"direction": "descending", "timestamp": "last_edited_time"}}
```

Only `last_edited_time` is supported for sort.

## Response

```json
{
  "results": [
    {
      "object": "page",
      "id": "...",
      "parent": {"type": "data_source_id", "data_source_id": "..."},
      "properties": { ... },
      "url": "https://www.notion.so/..."
    }
  ],
  "has_more": false,
  "next_cursor": null
}
```

## Useful jq Patterns

### Extract titles from search results

```bash
jq '[.results[] | {
  type: .object,
  title: (if .object == "page" then
    (.properties | to_entries | map(select(.value.type == "title")) | .[0].value.title[0].plain_text // "untitled")
  else
    (.title[0].plain_text // "untitled")
  end),
  id: .id,
  url: .url
}]'
```

### Search only pages (not databases)

```bash
curl -s -X POST https://api.notion.com/v1/search \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "search terms",
    "filter": {"value": "page", "property": "object"},
    "page_size": 10
  }'
```

## Limitations

- Search indexes page titles and rich text content — not file attachments
- Results are ranked by relevance, not recency (unless sorted)
- Internal integration only searches content it has access to
- Search may take a few seconds to index newly created content
