---
name: playwright
description: "Stagehand + Playwright browser automation — scraping, screenshots, HAR recording, tracing, CDP profiling, and AI-powered data extraction via script generation. Triggers on any request for browser automation, web scraping, page screenshots, network capture, performance profiling, or interaction with JS-rendered pages. No MCP needed. Requires ANTHROPIC_API_KEY (standard, not OAuth)."
user-invokable: true
argument-hint: "scrape https://reuters.com for headlines, screenshot https://example.com fullpage, profile https://example.com performance, har https://example.com/api capture traffic, trace https://example.com interaction trace"
allowed-tools: "Bash(bun *), Bash(bunx *), Bash(npx *), Bash(mkdir *), Write, Read, Glob"
license: MIT
metadata:
  version: "1.0.0"
  author: "Brian Morin"
  homepage: "https://github.com/bdmorin/the-no-shop"
  category: browser-automation
  requires:
    env:
      - ANTHROPIC_API_KEY
    packages:
      - "@browserbasehq/stagehand"
      - zod
---

# Playwright Skill

Browser automation via Stagehand (AI-powered) and Playwright (direct). Generate and execute self-contained scripts. No MCP server required.

## Setup

One-time per project:

```bash
# Per-project (recommended)
bun add @browserbasehq/stagehand zod
# Install Chromium browser
npx playwright install chromium
```

## Execution Model

Follow these steps in order for every automation request:

1. `mkdir -p ai/browser-scripts tmp`
2. Generate ISO timestamp slug: `YYYY-MM-DDTHH-MM-SS`
3. Write script to `ai/browser-scripts/<timestamp>-<slug>.ts`
4. Run: `ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY bunx tsx <script-path>`
5. Capture stdout (JSON data) + stderr (logs/errors) + exit code
6. Append manifest entry to `ai/browser-scripts/manifest.jsonl`
7. If `BROWSER_ARTIFACT_ENDPOINT` is set, POST the manifest entry

## Script Boilerplate — Stagehand (primary)

Use this when the page structure is unknown or you need AI-powered extraction/interaction.

```typescript
import { Stagehand } from "@browserbasehq/stagehand";
import { z } from "zod";

async function main() {
  const stagehand = new Stagehand({
    env: "LOCAL",
    model: "anthropic/claude-haiku-4-5-20251001",
    localBrowserLaunchOptions: { headless: true },
  });
  await stagehand.init();
  const page = stagehand.context.pages()[0];

  // --- YOUR TASK LOGIC HERE ---

  // Output results as JSON to stdout
  console.log(JSON.stringify(result, null, 2));

  await stagehand.close();
}

main().catch((err) => {
  console.error("FATAL:", err);
  process.exit(1);
});
```

## Script Boilerplate — Playwright Direct (for introspection tasks)

Use this for screenshots, HAR recording, traces, CDP profiling, PDF generation, and known-selector interactions.

```typescript
import { chromium } from "playwright";

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    recordHar: { path: "./tmp/capture.har" },
  });
  const page = await context.newPage();

  await context.tracing.start({ screenshots: true, snapshots: true });

  // --- YOUR TASK LOGIC HERE ---

  await context.tracing.stop({ path: "./tmp/trace.zip" });
  await context.close();
  await browser.close();
}

main().catch((err) => {
  console.error("FATAL:", err);
  process.exit(1);
});
```

## Decision Table — When to Use What

| Scenario | Use | Why |
|---|---|---|
| Extract data from unknown page | Stagehand `extract()` | AI understands page structure |
| Click/fill on unknown forms | Stagehand `act()` | No selector knowledge needed |
| Take screenshots | Playwright direct | No AI needed, faster |
| Record HAR / traces | Playwright direct | Built-in, no AI cost |
| CDP profiling (flamegraphs, metrics) | Playwright CDP session | Direct Chrome DevTools access |
| PDF generation | Playwright direct | Built-in capability |
| Known selector interactions | Playwright direct | Faster, deterministic |

## Manifest Format

Each execution appends one line to `ai/browser-scripts/manifest.jsonl`:

```json
{"timestamp":"2026-03-04T14:30:00Z","script":"ai/browser-scripts/2026-03-04T14-30-00-scrape-reuters.ts","intent":"scrape reuters headlines","result":"success","duration_ms":4200,"exit_code":0,"output_files":["tmp/reuters.json"],"tokens_used":1015}
```

## Key Gotchas

- ANTHROPIC_API_KEY must be standard `sk-ant-api03-...`, NOT an OAuth token (`sk-ant-oat01-...`)
- Stagehand `extract()` schemas: be explicit about URL format in the instruction — say "full https URL" or Stagehand returns element refs
- Each script is self-contained: launches browser, does work, closes browser
- Output data via `console.log(JSON.stringify(...))` to stdout
- Output files (screenshots, HAR, traces) to `./tmp/`
- Default timeout 60s — override with `setTimeout` if needed
- Stagehand v3 page access: `stagehand.context.pages()[0]`, NOT `stagehand.page`

## Reference Links

- [references/stagehand-api.md](references/stagehand-api.md) — extract, act, observe, agent, model options
- [references/playwright-api.md](references/playwright-api.md) — screenshots, PDF, navigation, selectors
- [references/deep-introspection.md](references/deep-introspection.md) — HAR, tracing, CDP profiling, flamegraphs
- [references/patterns.md](references/patterns.md) — Copy-paste script templates for common tasks
