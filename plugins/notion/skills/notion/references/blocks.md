# Blocks — Read and Append Content

Blocks are the content inside pages: paragraphs, headings, lists, code, etc.

## Get Block Children (read page body)

```bash
curl -s "https://api.notion.com/v1/blocks/$PAGE_ID/children?page_size=100" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

Paginated — check `has_more` and `next_cursor`.

## Append Blocks (add content to page)

```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/$PAGE_ID/children" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
          "rich_text": [{"text": {"content": "New paragraph text"}}]
        }
      }
    ]
  }'
```

## Common Block Types

### Paragraph
```json
{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Text"}}]}}
```

### Headings
```json
{"object": "block", "type": "heading_1", "heading_1": {"rich_text": [{"text": {"content": "H1"}}]}}
{"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"text": {"content": "H2"}}]}}
{"object": "block", "type": "heading_3", "heading_3": {"rich_text": [{"text": {"content": "H3"}}]}}
```

### Bulleted List
```json
{"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"text": {"content": "Item"}}]}}
```

### Numbered List
```json
{"object": "block", "type": "numbered_list_item", "numbered_list_item": {"rich_text": [{"text": {"content": "Item"}}]}}
```

### To-do
```json
{"object": "block", "type": "to_do", "to_do": {"rich_text": [{"text": {"content": "Task"}}], "checked": false}}
```

### Code
```json
{"object": "block", "type": "code", "code": {"rich_text": [{"text": {"content": "const x = 1;"}}], "language": "javascript"}}
```

Languages: javascript, typescript, python, bash, json, markdown, rust, go, etc.

### Quote
```json
{"object": "block", "type": "quote", "quote": {"rich_text": [{"text": {"content": "Quoted text"}}]}}
```

### Callout
```json
{"object": "block", "type": "callout", "callout": {"icon": {"type": "emoji", "emoji": "💡"}, "rich_text": [{"text": {"content": "Callout text"}}]}}
```

### Divider
```json
{"object": "block", "type": "divider", "divider": {}}
```

### Toggle
```json
{"object": "block", "type": "toggle", "toggle": {"rich_text": [{"text": {"content": "Toggle title"}}]}}
```

### Bookmark
```json
{"object": "block", "type": "bookmark", "bookmark": {"url": "https://example.com", "caption": [{"text": {"content": "Description"}}]}}
```

## Rich Text Formatting

```json
[
  {"text": {"content": "Normal text"}},
  {"text": {"content": "Bold text"}, "annotations": {"bold": true}},
  {"text": {"content": "Italic"}, "annotations": {"italic": true}},
  {"text": {"content": "Code"}, "annotations": {"code": true}},
  {"text": {"content": "Link text", "link": {"url": "https://example.com"}}}
]
```

Annotation options: `bold`, `italic`, `strikethrough`, `underline`, `code`, `color`.

## Update a Block

```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/$BLOCK_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "paragraph": {
      "rich_text": [{"text": {"content": "Updated text"}}]
    }
  }'
```

## Delete a Block

```bash
curl -s -X DELETE "https://api.notion.com/v1/blocks/$BLOCK_ID" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2025-09-03"
```

## Max Blocks per Request

Append: up to 100 blocks per request.
