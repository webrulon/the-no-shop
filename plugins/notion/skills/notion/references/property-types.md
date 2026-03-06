# Property Value JSON Formats

Reference for how to set each property type when creating or updating pages.

## Title

```json
{"title": [{"text": {"content": "Page title"}}]}
```

## Rich Text

```json
{"rich_text": [{"text": {"content": "Text content"}}]}
```

With formatting:
```json
{"rich_text": [
  {"text": {"content": "Bold"}, "annotations": {"bold": true}},
  {"text": {"content": " and "}},
  {"text": {"content": "linked", "link": {"url": "https://example.com"}}}
]}
```

## Select

```json
{"select": {"name": "Option Name"}}
```

Set to null to clear: `{"select": null}`

## Multi-Select

```json
{"multi_select": [{"name": "Tag1"}, {"name": "Tag2"}]}
```

New option names are auto-created. Clear all: `{"multi_select": []}`

## Date

```json
{"date": {"start": "2026-03-05"}}
{"date": {"start": "2026-03-05", "end": "2026-03-10"}}
{"date": {"start": "2026-03-05T14:30:00.000-07:00"}}
```

Clear: `{"date": null}`

## URL

```json
{"url": "https://example.com"}
```

Clear: `{"url": null}`

## Number

```json
{"number": 42}
```

## Checkbox

```json
{"checkbox": true}
```

## Email

```json
{"email": "user@example.com"}
```

## Phone Number

```json
{"phone_number": "+1-555-0100"}
```

## Relation

```json
{"relation": [{"id": "page-id-1"}, {"id": "page-id-2"}]}
```

Clear: `{"relation": []}`

## People

```json
{"people": [{"object": "user", "id": "user-id"}]}
```

## Files (external URL only via API)

```json
{"files": [{"name": "file.pdf", "type": "external", "external": {"url": "https://example.com/file.pdf"}}]}
```

## Created Time (read-only)

Cannot be set — auto-populated by Notion.

## Last Edited Time (read-only)

Cannot be set — auto-populated by Notion.

## Formula (read-only)

Computed property — cannot be set directly.

## Rollup (read-only)

Computed from relations — cannot be set directly.

## Reading Property Values

When reading pages, property values come wrapped differently:

| Type | Read Path |
|------|-----------|
| title | `.title[0].plain_text` |
| rich_text | `.rich_text[0].plain_text` |
| select | `.select.name` |
| multi_select | `.multi_select[].name` |
| date | `.date.start` |
| url | `.url` |
| number | `.number` |
| checkbox | `.checkbox` |
| relation | `.relation[].id` |
| created_time | `.created_time` |

## jq Helper — Extract All Properties

```bash
jq '.properties | to_entries | map({key: .key, type: .value.type, value: (
  if .value.type == "title" then .value.title[0].plain_text // null
  elif .value.type == "rich_text" then .value.rich_text[0].plain_text // null
  elif .value.type == "select" then .value.select.name // null
  elif .value.type == "multi_select" then [.value.multi_select[].name]
  elif .value.type == "date" then .value.date.start // null
  elif .value.type == "url" then .value.url
  elif .value.type == "number" then .value.number
  elif .value.type == "checkbox" then .value.checkbox
  elif .value.type == "relation" then [.value.relation[].id]
  elif .value.type == "created_time" then .value.created_time
  else "unsupported"
  end
)})'
```
