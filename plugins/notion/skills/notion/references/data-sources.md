# Data Sources — Query, Filter, Sort

API Version: 2025-09-03

## Discovery

Every database has one or more data sources. Get the data_source_id before querying:

```bash
curl -s "https://api.notion.com/v1/databases/$DB_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" | jq '.data_sources[0].id'
```

## Query a Data Source

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/$DS_ID/query" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "filter": { ... },
    "sorts": [ ... ],
    "page_size": 100,
    "start_cursor": "optional-cursor-for-pagination"
  }'
```

Response:
```json
{
  "results": [ ... ],
  "has_more": false,
  "next_cursor": null,
  "type": "page_or_database",
  "page_or_database": {}
}
```

## Filter Syntax

### Single property filters

```json
{"property": "Status", "select": {"equals": "Active"}}
{"property": "Status", "select": {"does_not_equal": "Archived"}}
{"property": "Name", "rich_text": {"contains": "search term"}}
{"property": "Name", "rich_text": {"starts_with": "prefix"}}
{"property": "Priority", "select": {"equals": "P0"}}
{"property": "Tags", "multi_select": {"contains": "tag-name"}}
{"property": "Due Date", "date": {"before": "2026-04-01"}}
{"property": "Due Date", "date": {"after": "2026-03-01"}}
{"property": "Due Date", "date": {"is_not_empty": true}}
{"property": "Project", "relation": {"contains": "page-id"}}
{"property": "Project", "relation": {"is_not_empty": true}}
{"property": "URL", "url": {"is_not_empty": true}}
```

### Compound filters

```json
{
  "and": [
    {"property": "Status", "select": {"equals": "Active"}},
    {"property": "Priority", "select": {"equals": "P0"}}
  ]
}
```

```json
{
  "or": [
    {"property": "Status", "select": {"equals": "Todo"}},
    {"property": "Status", "select": {"equals": "In Progress"}}
  ]
}
```

Nesting: `and`/`or` can be nested one level deep.

### Title filter (uses rich_text operators)

```json
{"property": "Name", "rich_text": {"contains": "search"}}
```

Note: title properties use `rich_text` filter operators, not `title`.

## Sort Syntax

```json
[
  {"property": "Priority", "direction": "ascending"},
  {"property": "Name", "direction": "ascending"}
]
```

Sort by timestamps:
```json
[{"timestamp": "created_time", "direction": "descending"}]
[{"timestamp": "last_edited_time", "direction": "descending"}]
```

## Pagination

- Default page_size: 100 (max)
- If `has_more` is true, pass `start_cursor` from `next_cursor` in next request
- Loop until `has_more` is false for full results
