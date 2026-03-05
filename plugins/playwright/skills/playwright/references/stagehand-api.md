# Stagehand v3 API Reference

Quick reference for agents using Stagehand v3 for browser automation and data extraction.

## extract(instruction, schema)

Natural language data extraction from the current page.

**Parameters:**
- `instruction` (string) — Natural language instruction describing what to extract
- `schema` (Zod schema) — Type definition for the returned object

**Returns:** Typed object matching the schema

**Token cost:** ~1K tokens (simple pages), ~11K tokens (complex pages like Hacker News)

**Best practices:**
- Be specific in instructions — say "full https URL" not "URL" or you'll get element references
- Use `.describe()` on schema fields to hint what the AI should look for
- Break complex extractions into multiple extract() calls if possible

**Example:**
```typescript
const data = await stagehand.extract(
  "Extract all article headlines with their full https URLs and publish dates",
  z.object({
    articles: z.array(z.object({
      title: z.string(),
      url: z.string().describe("Full https URL, not element reference"),
      date: z.string().optional(),
    })),
  }),
);
```

**Zod patterns:**
- `z.string()` — string field
- `z.number()` — numeric field
- `z.boolean()` — boolean field
- `z.array(z.string())` — array of strings
- `z.object({...})` — nested object
- `.optional()` — optional field (null if not found)
- `.describe("hint")` — hint for the AI about what to extract

---

## act(instruction)

Execute a single natural language action on the page.

**Parameters:**
- `instruction` (string) — Natural language description of the action

**Best practices:**
- One action per call for reliability
- Chain multiple `act()` calls for multi-step flows
- Avoid complex conditional logic — use `observe()` first if page structure is unknown

**Examples:**
```typescript
await stagehand.act("Click the Sign In button");
await stagehand.act("Type 'hello' into the search box");
await stagehand.act("Select 'United States' from the country dropdown");
await stagehand.act("Scroll down to the bottom of the page");
```

---

## observe(instruction)

Query what actions are available on the page.

**Parameters:**
- `instruction` (string) — Natural language question about available interactions

**Returns:** Array of possible interactions

**Use case:** Before calling `act()`, especially when page structure is unknown or dynamic

**Example:**
```typescript
const actions = await stagehand.observe("What can I click on this page?");
// Returns: ["Click the search button", "Click the filters dropdown", "Click on product cards", ...]
```

---

## agent({ mode, model })

Multi-step autonomous agent for complex workflows.

**Parameters:**
- `mode` (string) — Execution mode; "cua" (computed user actions) is standard
- `model` (string) — Model ID (see table below)

**Returns:** Agent instance with `.execute(instruction)` method

**Token cost:** Higher than `act()` — use for complex, multi-step workflows only

**Example:**
```typescript
const agent = stagehand.agent({
  mode: "cua",
  model: "anthropic/claude-sonnet-4-6",
});
const result = await agent.execute("Complete the checkout process");
```

---

## Page Access

Access the underlying Playwright Page object for raw operations.

**Correct (v3):**
```typescript
const page = stagehand.context.pages()[0];
await page.screenshot({ path: "screenshot.png" });
const pdf = await page.pdf();
```

**Incorrect (v2 syntax, won't work):**
```typescript
await stagehand.page.screenshot(); // Error: stagehand.page is undefined
```

---

## Model Options (Anthropic)

| Model ID | Use Case | Cost | Notes |
|---|---|---|---|
| `anthropic/claude-haiku-4-5-20251001` | Default — extraction, simple act, observe | Cheapest | Best for most tasks |
| `anthropic/claude-sonnet-4-6` | Complex pages, multi-step reasoning, agent workflows | Mid | Better accuracy on tricky layouts |
| `anthropic/claude-opus-4-6` | Research, high-reliability extraction | Expensive | Overkill for browser automation |

**Default:** Haiku is used if no model is specified. Override with `model` parameter on `extract()`, `act()`, `observe()`, or `agent()`.

---

## Common Patterns

### Multi-step workflow
```typescript
await stagehand.act("Click the search box");
await stagehand.act("Type 'nodejs tutorials'");
await stagehand.act("Press Enter");

const results = await stagehand.extract(
  "Extract all search result titles and links",
  z.object({
    results: z.array(z.object({
      title: z.string(),
      url: z.string().describe("Full https URL"),
    })),
  }),
);
```

### Conditional extraction
```typescript
const available = await stagehand.observe("What buttons are available?");

if (available.includes("Load more")) {
  await stagehand.act("Click the Load more button");
  // Wait for new content
  await stagehand.act("Scroll down");
}
```

### Taking screenshots and PDFs
```typescript
const page = stagehand.context.pages()[0];

// Screenshot
await page.screenshot({ path: "page.png" });

// PDF
const pdf = await page.pdf();
```

---

## Error Handling

Stagehand throws errors for:
- Invalid Zod schemas
- Page crashes or navigation errors
- Timeout on `act()` or `extract()` (default ~30s)
- Missing or malformed model IDs

Wrap in try-catch:
```typescript
try {
  await stagehand.act("Click non-existent button");
} catch (error) {
  console.error("Action failed:", error.message);
}
```

---

## Token Budgeting

- **extract() on simple pages:** ~1K tokens
- **extract() on complex pages:** ~11K tokens
- **act():** ~100-500 tokens
- **observe():** ~500-1K tokens
- **agent workflows:** 5K-50K+ tokens depending on complexity

For cost-sensitive tasks, use Haiku and break complex extractions into multiple smaller calls.
