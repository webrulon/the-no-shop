# Deep Introspection Reference

Power-user debugging guide: HAR capture, tracing, CDP profiling, flamegraphs, heap snapshots, code coverage, accessibility introspection.

---

## HAR Recording (Network Traffic Capture)

HAR (HTTP Archive) captures all network traffic as structured JSON. Viewable in Chrome DevTools, har.tech, or any HAR viewer.

### Method 1: Automatic (All Traffic)

```typescript
const context = await browser.newContext({
  recordHar: { path: "./tmp/capture.har" },
});
const page = await context.newPage();
await page.goto("https://example.com");

// ... interact with page ...

await context.close(); // MUST close context to flush HAR to disk
```

### Method 2: Filtered (API Calls Only)

```typescript
const context = await browser.newContext({
  recordHar: {
    path: "./tmp/api.har",
    urlFilter: "**/api/**"  // only capture API endpoints
  },
});
const page = await context.newPage();

// ... interact ...

await context.close();
```

### Method 3: CLI

```bash
npx playwright open \
  --save-har=capture.har \
  --save-har-glob="**/api/**" \
  https://example.com
```

### Viewing HAR Files

- **Chrome DevTools**: Open DevTools, Network tab → drag `.har` file
- **har.tech**: Online viewer at https://www.softwareishard.com/har/viewer/
- **Command-line**: `jq '.log.entries[] | {method, url, status}' capture.har`

---

## Tracing (Timeline + DOM Snapshots + Screenshots)

Playwright tracing captures a complete execution timeline with:
- Screenshots at each action
- DOM snapshots enabling retroactive element inspection
- Source file references
- Network waterfall context

### Basic Tracing

```typescript
const context = await browser.newContext();

await context.tracing.start({
  screenshots: true,  // include timeline screenshots
  snapshots: true,    // include DOM snapshots at every action
  sources: true,      // include source files for debugging
  title: "my-debug-session",
});

const page = await context.newPage();
await page.goto("https://example.com");

// ... test actions ...

await context.tracing.stop({ path: "./tmp/trace.zip" });
```

### View Trace

```bash
npx playwright show-trace ./tmp/trace.zip
```

This opens a local Playwright trace viewer with:
- Timeline showing all actions, navigation, and network events
- Snapshots panel (DOM tree at each snapshot point)
- Network waterfall
- Console logs and errors
- Source code context

### Chunked Tracing (Multi-Phase)

For long test runs, split tracing into phases to reduce memory pressure:

```typescript
const context = await browser.newContext();
await context.tracing.start({ screenshots: true, snapshots: true });

// Phase 1: Login
await context.tracing.startChunk({ title: "login-phase" });
await page.goto("https://example.com/login");
await page.fill('[name="email"]', "user@example.com");
await page.fill('[name="password"]', "secret");
await page.click("button[type=submit]");
await page.waitForNavigation();
await context.tracing.stopChunk({ path: "./tmp/trace-login.zip" });

// Phase 2: Checkout
await context.tracing.startChunk({ title: "checkout-phase" });
await page.click(".add-to-cart");
await page.click(".checkout");
// ... checkout flow ...
await context.tracing.stopChunk({ path: "./tmp/trace-checkout.zip" });

await context.tracing.stop();
```

---

## Chrome DevTools Protocol (CDP) Direct Access

Access raw CDP for low-level profiling and metrics impossible via Playwright API.

### Get CDP Session

```typescript
const cdp = await page.context().newCDPSession(page);
```

---

## CPU Profiling (Flamegraph-Ready)

Capture JavaScript execution profile for performance analysis.

```typescript
const cdp = await page.context().newCDPSession(page);

await cdp.send("Profiler.enable");
await cdp.send("Profiler.start");

// ... actions to profile ...
await page.click("button");
await page.waitForNavigation();

const { profile } = await cdp.send("Profiler.stop");

// Save as .cpuprofile
const fs = require("fs");
fs.writeFileSync("./tmp/profile.cpuprofile", JSON.stringify(profile));
```

### View Profile

- **Chrome DevTools**: Open Performance tab → drag `.cpuprofile` file
- **Speedscope**: https://www.speedscope.app → upload `.cpuprofile` → view flamegraph

Profile structure:
- `nodes[]`: function info (name, scriptId, line, column)
- `samples[]`: array of node IDs visited during sampling
- `timeDeltas[]`: milliseconds between samples

---

## Performance Metrics (FCP, LCP, Layout Count)

Retrieve low-level performance metrics from CDP.

```typescript
const cdp = await page.context().newCDPSession(page);

await cdp.send("Performance.enable");

// ... page load or user actions ...
await page.goto("https://example.com");
await page.waitForLoadState("networkidle");

const { metrics } = await cdp.send("Performance.getMetrics");

metrics.forEach(({ name, value }) => {
  console.log(`${name}: ${value}`);
});
```

### Common Metrics

| Metric | Meaning | Unit |
|--------|---------|------|
| `FirstContentfulPaint` | First paint with content | ms |
| `LargestContentfulPaint` | Largest visible element painted | ms |
| `LayoutCount` | Total layout recalculations | count |
| `RecalcStyleCount` | Total style recalculations | count |
| `TaskDuration` | Total JS task time | ms |
| `ScriptDuration` | Total JavaScript execution | ms |

---

## Heap Snapshots (Memory Analysis)

Capture JavaScript heap state for memory leak detection.

```typescript
const cdp = await page.context().newCDPSession(page);

const chunks: string[] = [];
cdp.on("HeapProfiler.addHeapSnapshotChunk", ({ chunk }) => {
  chunks.push(chunk);
});

await cdp.send("HeapProfiler.takeHeapSnapshot");
// Wait for completion:
await new Promise((resolve) => {
  const check = setInterval(() => {
    // Monitor HeapProfiler.addHeapSnapshotChunk events
    if (chunks.length > 0) {
      clearInterval(check);
      resolve(null);
    }
  }, 100);
});

const fs = require("fs");
fs.writeFileSync("./tmp/heap.heapsnapshot", chunks.join(""));
```

### View Heap Snapshot

- **Chrome DevTools**: Memory tab → drag `.heapsnapshot` file
- **Analysis**: Sort by size or count, expand prototypes to find retained objects

---

## Code Coverage (Line-Level)

Measure JavaScript and CSS code coverage during test execution.

### JavaScript Coverage

```typescript
const cdp = await page.context().newCDPSession(page);

await cdp.send("Profiler.enable");
await cdp.send("Profiler.startPreciseCoverage", {
  callCount: true,
  detailed: true,
});

// ... interact with page ...
await page.goto("https://example.com");
await page.click(".button");

const { result } = await cdp.send("Profiler.takePreciseCoverage");

// result: array of { scriptId, url, functions: [{ranges, functionName}] }
const fs = require("fs");
fs.writeFileSync("./tmp/coverage.json", JSON.stringify(result, null, 2));

await cdp.send("Profiler.stopPreciseCoverage");
```

### Parse Coverage Output

```typescript
const coverage = JSON.parse(fs.readFileSync("./tmp/coverage.json", "utf-8"));

coverage.forEach(({ url, functions }) => {
  console.log(`\n${url}:`);
  functions.forEach(({ functionName, ranges }) => {
    const covered = ranges.filter((r) => r.count > 0).length;
    console.log(`  ${functionName}: ${covered}/${ranges.length} ranges`);
  });
});
```

---

## Network Throttling (3G/4G Simulation)

Emulate slow network conditions via CDP.

```typescript
const cdp = await page.context().newCDPSession(page);

// 3G slow (100ms latency, 400KB/s down)
await cdp.send("Network.emulateNetworkConditions", {
  offline: false,
  latency: 100,                    // milliseconds
  downloadThroughput: 400000,      // bytes/s
  uploadThroughput: 400000,
});

// ... page load / interactions ...
await page.goto("https://example.com");

// Reset to normal
await cdp.send("Network.emulateNetworkConditions", {
  offline: false,
  latency: 0,
  downloadThroughput: -1,  // unlimited
  uploadThroughput: -1,
});
```

### Common Profiles

| Profile | Latency | Down | Up |
|---------|---------|------|-----|
| Fast 4G | 20ms | 4MB/s | 3MB/s |
| 4G | 50ms | 4MB/s | 3MB/s |
| 3G | 100ms | 400KB/s | 400KB/s |
| Slow 3G | 400ms | 50KB/s | 50KB/s |

---

## Accessibility Snapshot (a11y Tree)

Extract full accessibility tree for structure analysis without visual rendering.

```typescript
const snapshot = await page.accessibility.snapshot();

// snapshot: {
//   role: "document",
//   name: "Page Title",
//   children: [
//     { role: "heading", level: 1, name: "Main Header" },
//     { role: "button", name: "Click Me", disabled: false },
//     ...
//   ]
// }

const fs = require("fs");
fs.writeFileSync(
  "./tmp/a11y.json",
  JSON.stringify(snapshot, null, 2)
);
```

### Use Cases

- Verify heading hierarchy without CSS
- Confirm button labels are exposed
- Check for missing landmarks (main, nav, contentinfo)
- Validate ARIA roles and labels

---

## Console & Error Capture

Forward browser console output to test logs.

```typescript
page.on("console", (msg) => {
  console.log(`[browser:${msg.type()}] ${msg.text()}`);
});

page.on("pageerror", (err) => {
  console.error(`[browser:error] ${err.message}`);
  console.error(err.stack);
});

page.on("response", (response) => {
  if (!response.ok()) {
    console.warn(
      `[${response.status()}] ${response.url()}`
    );
  }
});
```

---

## Output Files & Viewers

| File Type | Created By | How to View |
|-----------|-----------|------------|
| `.har` | `recordHar` | Chrome DevTools Network tab, har.tech |
| `trace.zip` | `context.tracing` | `npx playwright show-trace trace.zip` |
| `.cpuprofile` | CDP Profiler | Chrome DevTools Performance tab, speedscope.app |
| `.heapsnapshot` | CDP HeapProfiler | Chrome DevTools Memory tab |
| `coverage.json` | CDP coverage | Custom script, or upload to coverage tools |

---

## Integration Pattern

Combine multiple tools for comprehensive debugging:

```typescript
async function debugSession(url: string) {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    recordHar: { path: "./tmp/capture.har" },
  });

  await context.tracing.start({
    screenshots: true,
    snapshots: true,
    sources: true,
  });

  const cdp = await context.newCDPSession(page);
  await cdp.send("Profiler.enable");
  await cdp.send("Profiler.start");

  const page = await context.newPage();
  await page.goto(url);

  // ... user interactions ...
  await page.click("button");

  const { profile } = await cdp.send("Profiler.stop");
  const { metrics } = await cdp.send("Performance.getMetrics");

  const fs = require("fs");
  fs.writeFileSync("./tmp/profile.cpuprofile", JSON.stringify(profile));
  fs.writeFileSync("./tmp/metrics.json", JSON.stringify(metrics, null, 2));

  await context.tracing.stop({ path: "./tmp/trace.zip" });
  await context.close();
  await browser.close();

  console.log("Debug artifacts:");
  console.log("  - HAR: ./tmp/capture.har");
  console.log("  - Trace: ./tmp/trace.zip (npx playwright show-trace)");
  console.log("  - Profile: ./tmp/profile.cpuprofile");
  console.log("  - Metrics: ./tmp/metrics.json");
}
```
