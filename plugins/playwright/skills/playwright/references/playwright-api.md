# Playwright API Reference

Quick reference for agents using Playwright directly (without Stagehand). Code-heavy, minimal prose.

---

## Screenshots

```typescript
// Full page — no height limit
await page.screenshot({ path: "full.png", fullPage: true });

// Clip to region
await page.screenshot({ clip: { x: 0, y: 0, width: 1280, height: 2000 } });

// Element only
await page.locator("#hero").screenshot({ path: "hero.png" });

// Mask sensitive areas
await page.screenshot({ mask: [page.locator(".credit-card")], maskColor: "#000" });

// JPEG with quality
await page.screenshot({ path: "page.jpg", type: "jpeg", quality: 80 });
```

**Options:**
- `fullPage` (bool) — screenshot entire scrollable page
- `clip` (object) — `{ x, y, width, height }` region only
- `mask` (Locator[]) — areas to redact
- `maskColor` (string) — redaction color, default `#000`
- `path` (string) — file path (optional, returns buffer if omitted)
- `type` (string) — `"png"` or `"jpeg"`, default `"png"`
- `quality` (number) — JPEG quality 1–100, default 92
- `scale` (string) — `"device"` or `"css"`, default `"css"`
- `omitBackground` (bool) — transparent background
- `animations` (string) — `"allow"` or `"disabled"`, default `"allow"`
- `caret` (string) — `"hide"` or `"initial"`, default `"hide"`
- `timeout` (number) — milliseconds, default 30000

---

## PDF Generation (Chromium only)

```typescript
await page.pdf({
  path: "page.pdf",
  format: "A4",
  printBackground: true,
  margin: { top: "1cm", right: "1cm", bottom: "1cm", left: "1cm" },
});
```

**Common formats:** `"Letter"`, `"A4"`, `"A3"`, `"Tabloid"`, `"Ledger"`, `"Legal"`, `"Statement"`, `"Executive"`, `"Folio"`, `"A5"`, `"A6"`

**Options:**
- `path` (string) — output file
- `format` (string) — page size, default `"Letter"`
- `width` / `height` (string) — custom dimensions (overrides `format`)
- `margin` (object) — `{ top, right, bottom, left }` (CSS units: cm, mm, in, px)
- `printBackground` (bool) — include background colors/images
- `landscape` (bool) — landscape orientation
- `scale` (number) — scale factor 0.1–2, default 1
- `pageRanges` (string) — `"1-5"` or `"1, 3, 5-7"`
- `displayHeaderFooter` (bool) — show header/footer
- `headerTemplate` / `footerTemplate` (string) — HTML with `<span class='pageNumber'>`, `<span class='totalPages'>`
- `preferCSSPageSize` (bool) — use CSS `@page` rules for dimensions

---

## Navigation

```typescript
// Wait for network idle (no requests for 500ms)
await page.goto(url, { waitUntil: "networkidle" });

// Faster: DOM ready, don't wait for images/css
await page.goto(url, { waitUntil: "domcontentloaded" });

// All resources loaded (slowest)
await page.goto(url, { waitUntil: "load" });

// Wait for navigation to complete
await page.waitForURL("**/dashboard");

// Back/forward
await page.goBack();
await page.goForward();
```

**goto() options:**
- `waitUntil` (string) — `"domcontentloaded"`, `"load"`, `"networkidle"`, `"commit"`, default `"load"`
- `referer` (string) — HTTP Referer header
- `timeout` (number) — milliseconds, default 30000

---

## Selectors (Priority Order)

```typescript
// 1. BEST — getByRole (accessible)
page.getByRole("button", { name: "Submit" });
page.getByRole("link", { name: "Dashboard" });
page.getByRole("heading", { name: "Welcome" });

// 2. BEST — getByLabel (forms)
page.getByLabel("Email");
page.getByLabel("Password");

// 3. OK — getByText (static content)
page.getByText("Welcome back");
page.getByText(/exact|regex/);

// 4. LAST RESORT — getByTestId
page.getByTestId("date-picker");

// 5. AVOID — CSS/XPath (brittle)
page.locator(".btn-primary");      // fragile to class changes
page.locator("xpath=//button[1]"); // fragile to DOM reordering
```

**Locator chains:**
```typescript
// Compose selectors
page.locator("form").locator("input").first();
page.getByRole("dialog").getByRole("button", { name: "Close" });

// Filtering
page.locator("a").filter({ hasText: "Sign Up" });
page.locator("li").filter({ has: page.locator("span.active") });
```

---

## Interaction

```typescript
// Text input
await page.locator("#email").fill("user@example.com");
await page.locator("#search").pressSequentially("query", { delay: 50 });

// Click
await page.locator("#submit").click();
await page.locator(".dropdown").dblclick();
await page.locator("button").click({ button: "right", modifiers: ["Shift"] });

// Select option
await page.selectOption("select#country", "US");
await page.selectOption("select#country", { value: "US" }); // explicit value
await page.selectOption("select#country", { label: "United States" }); // by label

// Checkbox / radio
await page.locator("#terms").check();
await page.locator("#agree").uncheck();
await page.locator('input[type="radio"]').click();

// Keyboard
await page.keyboard.press("Enter");
await page.keyboard.press("Tab");
await page.keyboard.type("Hello World", { delay: 100 });
await page.keyboard.down("Control");
await page.keyboard.press("A");
await page.keyboard.up("Control");

// Hover
await page.locator("#dropdown").hover();

// Drag & drop
await page.locator("#source").dragTo(page.locator("#target"));

// Upload
await page.locator("input[type='file']").setInputFiles("path/to/file.pdf");
await page.locator("input[type='file']").setInputFiles(["file1.pdf", "file2.pdf"]);
```

---

## Wait Conditions

```typescript
// Wait for element visible
await page.waitForSelector("#loaded", { state: "visible" });

// Wait for element hidden
await page.waitForSelector(".spinner", { state: "hidden" });

// Wait for function
await page.waitForFunction(() => document.readyState === "complete");

// Wait for navigation
await page.waitForNavigation();
await page.waitForURL("**/dashboard");

// Wait for specific response
const responsePromise = page.waitForResponse("**/api/data");
await page.locator("#load-data").click();
const response = await responsePromise;
const data = await response.json();
```

---

## Content Extraction

```typescript
// HTML
const html = await page.content();

// Text content
const text = await page.locator("#main").textContent();
const text = await page.getByText("Search").textContent();

// Attribute
const src = await page.locator("img").first().getAttribute("src");
const href = await page.getByRole("link", { name: "Home" }).getAttribute("href");

// Arbitrary JS in browser context
const title = await page.evaluate(() => document.title);

// Parse structured data
const data = await page.evaluate(() => {
  return JSON.parse(document.querySelector("#data").textContent);
});

// Multiple values
const hrefs = await page.locator("a").evaluateAll((nodes) =>
  nodes.map((n) => n.href)
);

// Input/select values
const email = await page.locator("#email").inputValue();
const country = await page.locator("select#country").inputValue();

// Check if element exists
const exists = await page.locator("#maybe").isVisible();
const disabled = await page.locator("#submit").isDisabled();
const checked = await page.locator("#terms").isChecked();
```

---

## Network

```typescript
// Intercept & log all requests
await page.route("**/*", (route) => {
  console.log(route.request().url(), route.request().method());
  route.continue();
});

// Block requests (speed up page load)
await page.route("**/*.{png,jpg,gif,svg,webp}", (route) => route.abort());

// Mock API responses
await page.route("**/api/users", (route) => {
  route.abort("blockedbyclient");
});

await page.route("**/api/config", (route) => {
  route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({ theme: "dark" }),
  });
});

// Monitor responses
page.on("response", (response) => {
  if (response.status() >= 400) {
    console.log("Error:", response.status(), response.url());
  }
});

// Get response body
const response = await page.goto(url);
const body = await response.body();      // Buffer
const text = await response.text();      // string
const json = await response.json();      // parsed object
```

---

## Browser Context & Pages

```typescript
// Multiple pages in same context (shared cookies/storage)
const page1 = await context.newPage();
const page2 = await context.newPage();

// Switch context (new cookies, storage, etc.)
const newContext = await browser.newContext();
const page = await newContext.newPage();

// Close
await page.close();
await context.close();
await browser.close();

// Local storage / session storage
await page.evaluate(() => {
  localStorage.setItem("key", "value");
  sessionStorage.setItem("key", "value");
});

const value = await page.evaluate(() => localStorage.getItem("key"));
```

---

## Debugging

```typescript
// Log all console messages
page.on("console", (msg) => console.log("[PAGE]", msg.text()));

// Log all errors
page.on("pageerror", (error) => console.error("[PAGE ERROR]", error));

// Pause browser (interactive debugging)
await page.pause();

// Slow down execution
page.setDefaultTimeout(10000);
page.setDefaultNavigationTimeout(30000);

// Trace for debugging
await context.tracing.start({ screenshots: true, snapshots: true });
// ... run test ...
await context.tracing.stop({ path: "trace.zip" });
```

---

## Common Patterns

```typescript
// Wait for element + click
await page.waitForSelector("#ready");
await page.locator("#action").click();

// Fill form + submit
await page.locator("#email").fill("user@example.com");
await page.locator("#password").fill("secret");
await page.locator("button[type='submit']").click();
await page.waitForURL("**/dashboard");

// Extract table data
const rows = await page.locator("tbody tr").all();
const data = [];
for (const row of rows) {
  const cells = await row.locator("td").allTextContents();
  data.push(cells);
}

// Infinite scroll
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await page.waitForSelector(".loading", { state: "hidden" });
```
