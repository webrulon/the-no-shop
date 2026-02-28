# Foldspace Console — Changelog

A narrative history of how this thing came to be. Commits are here if you want specifics, but this is the story.

---

## The Spike (before the repo existed)

Foldspace started as a question: *what if Claude could see itself?* The spike lived in `/Users/bdmorin/cowork/sidecar` — three commits, no polish, just enough to prove the idea worked. The core mechanic was discovered here: Claude Code's `UserPromptSubmit` hook pushes plain text to stdout and it gets injected into the next prompt, no JSON ceremony needed. The `Stop` hook hands you `last_assistant_message` directly — no transcript parsing required. That was the unlock.

The spike ran quietly in the background for weeks, accumulating session registrations from the old daemon, entirely unnoticed until the shakedown.

---

## February 27, 2026

### Initial Release (`6dbed30`)

The spike got promoted to a proper Claude Code plugin marketplace. The No-Shop repo was created — a marketplace manifest at the root, with Foldspace Console as its first and only plugin. The initial release had the daemon, the SPA, and all four hooks wired up. Multi-session support was in from day one: a `Map<sessionId, SessionMeta>` for sessions, another for responses, another for annotations. Bun HTTP + WebSocket on port 3377, a self-contained HTML file served by `Bun.file()`, no build step.

The design at this point was functional but raw — readable, but not yet what it wanted to be.

### The Retheme (`7b26d90`, `3554ce4`)

The aesthetic needed a name before it could be executed. The direction settled on: *Subterranean Precision*. Herbert's Ix as the reference point — not the brutalism of the Harkonnens, but the thing that looks deceptively simple until you realize it just replaced a Guild Navigator. Instrument Sans for body text. IBM Plex Mono for data. Teal as the signal color, amber as the brand accent used sparingly. Borders at rgba(255,255,255,0.04) — barely there. An SVG noise overlay at 0.012 opacity for depth.

A contrast pass followed immediately — fonts were too small, colors too dim for actual use. Fixed.

### The Five Feature Branches

Five parallel feature agents were dispatched into git worktrees. Each worked in isolation; all five touched `web/index.html`. The integration required manual conflict resolution on every merge.

**Git Status** (`1804c1e`) — The session header got real-time git context. The daemon polls every 10 seconds with a 5-second timeout, diffs against the last result, and only pushes an update when something changed. Branch name, dirty state, remote sync status — all visible at a glance without leaving the browser.

**Animated Numbers** (`7f946fa`) — Every numeric metric in the UI — token counts, session counts, response numbers — animates on change. Ease-out cubic tweening with `requestAnimationFrame`. The tabular-nums CSS property keeps counters from jumping in layout. It's a small thing that makes the data feel alive.

**Tab Management** (`fb54c1c`) — Sessions sort by most recent activity. Tabs expire after 6 hours of inactivity. When there are more sessions than fit, the overflow is counted and shown. Three visual states: active, recent, idle. The tab strip became something you could actually navigate rather than a flat list that grew forever.

**Rich Components** (`605c70e`) — Five sidecar component types, each rendered from specially-prefixed code blocks in Claude's output: `sidecar-mermaid` for diagrams, `sidecar-table` for structured data with sortable columns, `sidecar-diff` for before/after comparisons, `sidecar-json` for collapsible JSON trees, `sidecar-progress` for progress bars. The Foldspace Console started being able to render things Claude couldn't show in the terminal.

**Mise Component** (`f0ce423`) — The System panel gained visibility into the local dev environment. Installed tools, active versions, environment variables (with secret masking for anything matching KEY, SECRET, TOKEN, PASSWORD, CREDENTIAL, API), and mise config files with a modal viewer. A `15-minute TTL cache` keeps it from hammering mise on every request.

### Annotation Visibility (`9f7d2b1`)

The annotation injection mechanism — where browser annotations get prepended to the next user prompt — was working but silent. There was nothing to tell the user their annotations were being included. Two safeguards were added: a stderr line printed to the terminal (`Foldspace: N annotation(s) injected`) and a mandatory acknowledgment injected into the LLM context instructing Claude to confirm it received the annotations before proceeding. The README got a proper "Feedback Loop" section explaining how the whole circuit works.

---

## February 28, 2026

### Round Two Features

Four more agents, four more worktrees.

**System Introspection** (`e5aa9fe`) — The System panel became genuinely useful. Every skill, plugin, hook, and MCP server Claude Code knows about can be browsed from the browser. Accordion UI with ARIA keyboard accessibility. The config introspection reads directly from `~/.claude/settings.json` and the skills/plugins directories, giving you a live view of what's loaded in your Claude environment.

**Rich Output Mode** (`0213b7d`) — A second view mode for responses: append-only, cross-session, showing every response in chronological order across all active sessions. Persistent via `localStorage`. The session view shows one session's conversation; the stream view shows everything. Auto-scroll with manual override — scroll up to pause, scroll back to the bottom to resume.

**Layout Modes + Themes** (`dc222f0`) — Three themes (void, slate, parchment) and three layouts (default, focus, split). A status bar at the bottom showing connection state, active session, and response count. Everything stored in `localStorage`. The parchment theme is light mode for daylight use.

**System Stats** (`b3ca8ef`) — CPU and memory bars in the System panel with real-time updates. CPU usage calculated as a delta between heartbeat snapshots so it reflects current load rather than lifetime average. Memory shows used/total with a visual bar. The bars animate on change, consistent with the rest of the UI's approach to live data.

**Context Document Enumeration** (`c73bfb1`) — A Context tab that shows every file Claude has touched in the current session: reads, writes, edits, globs, greps. Grouped by directory. Sorted by access frequency. The daemon parses the session's JSONL transcript to extract tool_use blocks with file paths. A text-length cache prevents re-parsing unchanged transcripts, and a file-size quick-check in the heartbeat loop skips unchanged transcripts entirely.

### Security Hardening (`76257ac`)

A code review found the things you'd expect from code assembled across a dozen feature branches by parallel agents: XSS, open CORS, missing input validation, dead code accumulation.

The XSS was the serious one — all `marked.parse()` output was going directly into `innerHTML`. DOMPurify was added. All five HTML entities got proper encoding symmetry (the copy button was only encoding four of them). CORS was opened to `*`; it's now restricted to `http://localhost:PORT`. The SPA wildcard route was serving the HTML file for any unmatched path; it's now gated to `/` and `/index.html` only. The transcript cache had a race condition using async `Bun.file().size` as a freshness check; it now reads the file once and uses `text.length`. The `runWithTimeout` function got replaced with a clean `Promise.race` pattern.

Dead code: `formatNum` was a duplicate of `formatTokens` — removed. `mermaidIdCounter` was renamed to `sidecarIdCounter` to reflect that it IDs all sidecar components, not just mermaid ones. The `updateStatus()` wrapper function that did nothing but call `updateStatusSessionLabel()` was removed at all call sites.

One bug introduced during the fix pass: the agent replaced `updateStatus()` with `updateStatusSessionLabel()` without noticing the next line already called it, resulting in a double invocation. Caught on review.

---

## What's Left

P2 items that aren't wrong, just incomplete: a dead `marked.setOptions` call that configures nothing, some hardcoded widths that should be variables, no favicon, and some shell script style issues (`||` used after `set -e` where `if` is required for safety).

The daemon needs a re-register mechanism for mid-session restarts. Right now if you kill and restart the daemon, active sessions go dark until the SessionStart hook fires again on the next session open.

The installed plugin at `~/.claude/plugins/foldspace-console/` has never been audited against the spike — it may still be pointing at old code.
