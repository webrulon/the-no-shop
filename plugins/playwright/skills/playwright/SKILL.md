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
4. Run: `cd <project-root> && ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY bun <script-path>` (Bun resolves imports from cwd, so run from the directory containing `node_modules`)
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

## Script Boilerplate — Playwright Direct (raw content & introspection)

Use this for **raw content extraction** (articles, pages, text), screenshots, HAR recording, traces, CDP profiling, PDF generation, and known-selector interactions.

**IMPORTANT**: For "extract the article" or "get the page content" requests, ALWAYS use Playwright direct — NOT Stagehand. Stagehand's `extract()` interprets content through an AI middleman, which summarizes and paraphrases instead of returning the actual text. You cannot write a Zod schema for content you haven't seen yet.

```typescript
import { chromium } from "playwright";

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto("https://TARGET_URL", { waitUntil: "domcontentloaded" });
  await new Promise((r) => setTimeout(r, 3000)); // let JS render

  // Raw text extraction — tries article > main > .post-content > body
  const content = await page.evaluate(() => {
    const el = document.querySelector("article")
      || document.querySelector("main")
      || document.querySelector(".post-content")
      || document.body;
    return el?.innerText || "";
  });

  // Extract all outgoing links
  const links = await page.evaluate(() => {
    return Array.from(document.querySelectorAll("a[href]"))
      .map((a) => ({
        text: (a as HTMLAnchorElement).innerText.trim(),
        url: (a as HTMLAnchorElement).href,
      }))
      .filter((l) => l.text && l.url.startsWith("http"));
  });

  console.log(JSON.stringify({ content, links }, null, 2));
  await browser.close();
}

main().catch((err) => {
  console.error("FATAL:", err);
  process.exit(1);
});
```

### Playwright Direct — Introspection (HAR/Tracing)

For HAR recording, tracing, and CDP profiling, use context-level instrumentation:

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
| **Get article/page text** | **Playwright direct** | **Raw text via `innerText` — no AI interpretation** |
| **Get page content + links** | **Playwright direct** | **`evaluate()` returns actual content, not a summary** |
| Extract structured data (prices, specs, tables) | Stagehand `extract()` | AI maps messy HTML to clean schema |
| Click/fill on unknown forms | Stagehand `act()` | No selector knowledge needed |
| Take screenshots | Playwright direct | No AI needed, faster |
| Record HAR / traces | Playwright direct | Built-in, no AI cost |
| CDP profiling (flamegraphs, metrics) | Playwright CDP session | Direct Chrome DevTools access |
| PDF generation | Playwright direct | Built-in capability |
| Known selector interactions | Playwright direct | Faster, deterministic |

### When NOT to Use Stagehand extract()

Stagehand `extract()` passes page content through an LLM to fill a Zod schema. This means:
- It **summarizes and paraphrases** — you don't get the actual text
- You must define a schema **before seeing the content** — impossible for generic "get the article" requests
- It costs tokens and adds latency for no benefit when you just want raw text

**Rule of thumb**: If the user says "extract the article" or "get the page content," use Playwright direct. If they say "extract all product prices into a table," use Stagehand.

## Manifest Format

Each execution appends one line to `ai/browser-scripts/manifest.jsonl`:

```json
{"timestamp":"2026-03-04T14:30:00Z","script":"ai/browser-scripts/2026-03-04T14-30-00-scrape-reuters.ts","intent":"scrape reuters headlines","result":"success","duration_ms":4200,"exit_code":0,"output_files":["tmp/reuters.json"],"tokens_used":1015}
```

## Key Gotchas

- **Stagehand extract() is NOT for raw content** — it interprets through AI. For "get the article," use Playwright direct with `page.evaluate(() => article.innerText)`
- ANTHROPIC_API_KEY must be standard `sk-ant-api03-...`, NOT an OAuth token (`sk-ant-oat01-...`)
- Stagehand `extract()` schemas: be explicit about URL format in the instruction — say "full https URL" or Stagehand returns element refs
- Each script is self-contained: launches browser, does work, closes browser
- Output data via `console.log(JSON.stringify(...))` to stdout
- Output files (screenshots, HAR, traces) to `./tmp/`
- Default timeout 60s — override with `setTimeout` if needed
- Stagehand v3 page access: `stagehand.context.pages()[0]`, NOT `stagehand.page`
- **Module resolution**: scripts import from `node_modules` relative to the script location. Ensure `@browserbasehq/stagehand`, `zod`, and `playwright` are installed in the project root (run `bun add` there)
- **`networkidle` timeout**: Ad-heavy sites never reach networkidle. Use `waitUntil: "domcontentloaded"` + manual `setTimeout` delay instead
- **Cloudflare Turnstile**: Headless Chromium is blocked by CF's bot detection. No workaround in headless mode — use WebFetch for CF-protected sites, or a cloud browser service (Browserbase) for Turnstile-protected pages

## Reference Links

- [references/stagehand-api.md](references/stagehand-api.md) — extract, act, observe, agent, model options
- [references/playwright-api.md](references/playwright-api.md) — screenshots, PDF, navigation, selectors
- [references/deep-introspection.md](references/deep-introspection.md) — HAR, tracing, CDP profiling, flamegraphs
- [references/patterns.md](references/patterns.md) — Copy-paste script templates for common tasks
