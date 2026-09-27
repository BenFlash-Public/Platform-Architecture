---
name: Browser Extension Template
description: For browser extensions, web plugins, and cross-browser tools. Ship Chrome first, then Firefox/Safari/Edge extensions in parallel. Requires Manifest V3 and cross-browser compatibility planning.
---

# Browser Extension Architecture Template

**Best for:** Productivity tools, developer utilities, security/privacy tools, content enhancers, form fillers, note-takers, password managers, ad blockers—anything that extends browser functionality and reaches users where they spend time: in the browser.

**Platform sequence:** Chrome Web Store (Tier 1) → Firefox Add-ons + Safari Extensions + Edge Add-ons (Tier 2, parallel) → Web dashboard (Tier 3, optional) → Electron wrapper (Tier 4, optional)

**Last verified:** 2026-09-27 (Manifest V3 requirements, Chrome Web Store policies, Firefox/Safari/Edge extension APIs)

---

## Platform Status Table

| Tier | Platform | Timeline | Tech Stack | Status | Notes |
|------|----------|----------|-----------|--------|-------|
| **1** | Chrome Extension | Weeks 1–8 | Manifest V3, TypeScript, React/Vue | Critical path | Largest user base; Web Store review 1–3 days |
| **2** | Firefox Add-on | Weeks 7–10 | Same codebase; Manifest V2/V3 compat | Parallel | Second-largest; review 1–5 days |
| **2** | Safari App Extension | Weeks 7–10 | Same codebase; Safari Web Extension API | Parallel | Growing user base; notarization required |
| **2** | Edge Add-on | Weeks 7–10 | Same codebase; Chromium-compatible | Parallel | Chromium-based; reuses Chrome build |
| **3** | Web Dashboard | Weeks 11–16 | Next.js, React, TypeScript | Post-launch | User settings, sync, license management, analytics |
| **4** | Electron Wrapper | Weeks 17+ | Electron, same React UI | Optional | Standalone app; not typical for extensions |

---

## Key Architectural Decisions

### 1. Manifest Version & Browser Compatibility

**Manifest V3 (MV3) is the new standard; Manifest V2 (MV2) is deprecated.**

**Strategy:**
- **Chrome:** MV3 required (as of Jan 2025)
- **Firefox:** Supporting both MV2 and MV3; use build-time flag to switch
- **Safari:** Web Extension API (Safari-specific; similar to MV3)
- **Edge:** Chromium-based; MV3 compatible (same as Chrome)

**Build approach:**
- Single source, MV2/MV3 builds:
  - `src/manifest.v2.json` and `src/manifest.v3.json`
  - Webpack/Vite conditional bundling
  - Shared `src/` code (background script, content scripts, popup)
- Content Security Policy (CSP) per browser (varies slightly)
- Test on all 4 browsers before release

### 2. Extension Architecture Pattern

**Typical structure:**

```
├── manifest.json (V3)
├── src/
│   ├── background/
│   │   └── service-worker.ts (replaces background.html in MV3)
│   ├── content-scripts/
│   │   └── content.ts (injected into page; DOM access)
│   ├── popup/
│   │   ├── popup.tsx (UI for extension icon click)
│   │   └── popup.css
│   ├── options/
│   │   ├── options.tsx (settings page)
│   │   └── options.css
│   ├── shared/
│   │   ├── types.ts (shared types)
│   │   ├── storage.ts (chrome.storage API)
│   │   └── messaging.ts (content ↔ background communication)
│   └── assets/
│       ├── icon-16.png
│       ├── icon-48.png
│       ├── icon-128.png
│       └── logo.png
└── build/ (dist/)
    ├── manifest.json
    ├── service-worker.js
    ├── content.js
    ├── popup.html / popup.js
    └── assets/
```

**Key patterns:**
- **Service Worker (MV3):** Background script; no DOM access; handles alarms, API calls, storage
- **Content Script:** Injected into pages; can access DOM; communicates with service worker via `chrome.runtime.sendMessage()`
- **Popup:** Small UI (320×600px typical); appears when user clicks extension icon
- **Options Page:** Full settings UI (can be larger)

### 3. Cross-Browser Data Sync

**Question:** Do users need settings synced across devices?

**If YES (multi-device sync):**
- Architecture: Cloud backend + `chrome.storage.sync` (Chrome) or custom API
- Implementation:
  - Cloud service stores user settings (PostgreSQL)
  - Extension syncs via `chrome.storage.sync` (free, limited to 100KB per item)
  - OR custom HTTP API (full control; requires backend)
  - On browser sync-in, settings merged (user's last-modified version wins)
  - Conflicts rare if sync is atomic

**If NO (single device):**
- Architecture: Local `chrome.storage.local` only
- Implementation:
  - Simpler; no backend needed
  - Settings never sync across devices
  - Users re-configure on new device

### 4. Monetization Model

**Extension-specific options:**

| Model | Tier 1 Strategy | Store Compliance |
|-------|---|---|
| **Free + optional donation** | Completely free; donation link in options page | Allowed by all stores |
| **Premium features** | Free tier (core features); Pro ($2.99/mo or $19.99/yr) | Stripe payment in options page (store allows) |
| **One-time purchase** | $4.99 lifetime unlock | Stripe (most stores allow); receipt stored locally |
| **Freemium with cloud sync** | Free extension; cloud sync costs $1.99/mo | Pro tier: backend costs justify pricing |
| **Ad-supported** | Free with ads in popup/dashboard; ad-free for Pro | Ads allowed if clearly labeled |

**Critical rule:** Store policies are stricter than app stores.
- No darkpatterns (confusing upgrade prompts)
- Pricing must be clear before charge
- Refund policy transparent
- Cannot use notifications to advertise premium tier

### 5. Permissions & User Trust

**MV3 permissions model is stricter (user must explicitly grant):**

**Permissions to minimize:**
- `<all_urls>` — Broadest; users trust least. Narrow to `*://example.com/*` if possible.
- `tabs` — Can read tab URLs (privacy concern)
- `storage` — Can persist data (usually safe)
- `scripting` — Can inject scripts; user must grant per-site

**Best practice:**
- Request fewest permissions on install
- Request additional permissions at runtime (when user needs them)
- Explain *why* you need each permission (tooltip or onboarding)

---

## Tier 1 Release Gates

**Must pass before Chrome Web Store submission:**

### Code Quality
- [ ] Unit test coverage ≥ 70% on core logic (storage, messaging, sync)
- [ ] Integration tests for popup ↔ service worker communication
- [ ] No console errors in Chrome DevTools Console
- [ ] TypeScript strict mode enabled; no `any` types
- [ ] ESLint + Prettier passing

### Performance
- [ ] Service worker startup < 500ms
- [ ] Popup UI renders in < 300ms
- [ ] Memory footprint < 50MB (measured via DevTools)
- [ ] No memory leaks (Chrome DevTools > Memory > Detached DOM nodes)
- [ ] Content script injection overhead < 100ms

### Security
- [ ] Content Security Policy (CSP) configured; no `unsafe-inline` or `unsafe-eval`
- [ ] No hardcoded API keys or secrets (use `chrome.storage` or environment variables)
- [ ] HTTPS only for all API calls
- [ ] User data never sent to third parties without opt-in
- [ ] Extension ID pinned (prevent sideloading of rogue version)
- [ ] Permissions justified and minimal (each permission documented)

### Browser Compatibility
- [ ] Extension tested and functional on:
  - Chrome (latest 2 versions)
  - Firefox (latest 2 versions)
  - Safari (latest 2 versions)
  - Edge (latest 2 versions)
- [ ] Manifest.json valid for all browsers (use validator tools)
- [ ] Icons render correctly (16×16, 48×48, 128×128 PNG)
- [ ] Popup/options page responsive (no horizontal scroll at any zoom level)

### User Experience
- [ ] Onboarding in < 30 seconds (1–2 screens max)
- [ ] Core feature works without tutorial
- [ ] Error messages clear (not "Error 500", but "Couldn't fetch data. Try again.")
- [ ] Permissions request explains why (e.g., "We need site access to enhance this page")
- [ ] Dark mode support (follows system preference)
- [ ] Tooltip hover text on unclear UI elements

### Store Compliance
- [ ] Privacy policy published (URL required by all stores)
- [ ] Extension icon (128×128 PNG) attractive and clear
- [ ] Description (short: < 140 chars; full: < 4000 chars) compelling and accurate
- [ ] Screenshots (2–5) showing core features
- [ ] No external links in popup (policy violation in some stores)
- [ ] No requests for unnecessary permissions (red flag to reviewers)
- [ ] No background activity when extension not in use (battery drain concern)

### Analytics & Support
- [ ] Analytics configured (track: install, key features used, errors)
- [ ] Error logging (Sentry or custom) to catch user-facing bugs
- [ ] Support email or form ready
- [ ] FAQ or documentation for common issues

---

## Tech Stack Rationale

### Manifest V3 + TypeScript
- **Manifest V3:** Required for Chrome (2025+); Firefox moving there; Safari Web Extension API similar
- **TypeScript:** Catches bugs at compile; easier refactoring across 4 browser builds
- **Service Worker (MV3):** Replaces persistent background page; more memory efficient

### Frontend Framework (choose one)
- **React:** Largest ecosystem; 1000+ component libraries; easiest to hire
  - Bundle: ~40KB gzipped (acceptable for extensions)
  - Use `react-dom/client` for popup/options rendering
- **Vue:** Lightweight; ~35KB gzipped; excellent TypeScript support
  - Simpler mental model than React; good for small extensions
- **Preact:** Ultra-light (~10KB); good for minimal extensions
  - Trade: smaller ecosystem; fewer components

**Recommendation:** React for complex extensions (password manager, form filler); Vue or Preact for simpler tools.

### Build Tooling
- **Vite:** Fast dev server, instant HMR, native ESM support
  - Config: `vite.config.ts` with `rollupOptions` for multiple entry points (background, popup, options)
- **Webpack:** More mature; better for complex setups
- **esbuild:** Fastest; good for simple extensions

### Storage & Sync
- **chrome.storage.sync:** Free; 100KB limit per item; handled by browser
  - **Pros:** Works across Chrome, Firefox, Edge; no backend needed
  - **Cons:** Limited size; limited to structured data
- **chrome.storage.local:** Unlimited; local device only
- **IndexedDB:** More complex; useful for large datasets (SQLite-like)

### API Communication
- **Fetch API:** Standard; works in service workers and content scripts
- **axios:** Popular; slightly larger bundle
- **Got (Node) or ofetch:** Not available in browser context; don't use

---

## Sample Feature Roadmap (16 weeks to multi-browser)

### Tier 1 (Weeks 1–8): Chrome MVP
- Core feature (e.g., content enhancement, data entry)
- Popup UI for settings/quick access
- Options page for advanced settings
- Local storage (chrome.storage.local)
- Basic analytics
- Chrome Web Store submission + approval

### Tier 2 (Weeks 7–10): Multi-Browser Launch (parallel)
- Firefox Add-on (same codebase, Manifest V2 compat layer)
- Safari App Extension (Web Extension API)
- Edge Add-on (reuse Chrome build; Chromium-compatible)
- Cross-browser testing framework
- Store submissions for all platforms

### Tier 3 (Weeks 11–16): Cloud Sync & Premium
- Backend API (Node/Python) for user settings sync
- `chrome.storage.sync` integration
- Premium tier (subscription or one-time)
- Web dashboard (view/manage settings, billing)
- Analytics dashboard (usage trends, feature popularity)

---

## Known Pitfalls & How to Avoid

| Pitfall | Why It Hurts | Mitigation |
|---------|---|---|
| **Broadest permissions on install** | Users distrust and uninstall; store reviewers reject | Request minimal permissions on install; request additional permissions at runtime |
| **Content script DOM conflicts** | Extension breaks page functionality; user reports bug to website not extension | Scope CSS with `.ext-*` prefix; use shadow DOM for isolated UI; test on major sites |
| **Service worker crashes** | User loses extension silently; no error reporting | Add uncaught error handler; log errors to analytics; test with background tasks |
| **No MV3 migration plan** | MV2 deadline passed; extension stops working | Support both MV2 and MV3 from day 1 with feature flags |
| **Large bundle size** | Slow download, install, startup; users with slow internet uninstall | Target < 500KB uncompressed; tree-shake dependencies; lazy-load features |
| **Sync conflicts** | User has conflicting settings across devices; confusing behavior | Last-write-wins (simplest); or show conflict dialog asking user to merge |
| **Store review rejection** | 1–2 week delay; unclear why rejected | Read store guidelines thoroughly; test on actual store environment; ask reviewer for specifics |
| **No testing for all 4 browsers** | Works on Chrome, breaks on Firefox; bad reviews | Multi-browser test matrix from Tier 1; use BrowserStack or similar |
| **Hardcoded API key in popup** | Key leaked publicly; bad actors spam your API | Use chrome.storage or environment variables; never hardcode |

---

## Checklist for Tier 1 MVP Launch (Chrome Web Store)

- [ ] Extension built and tested locally on Chrome (latest)
- [ ] Core feature working end-to-end (no errors in console)
- [ ] Popup UI functional; options page working
- [ ] Service worker starts successfully; no uncaught errors
- [ ] Memory footprint checked (< 50MB)
- [ ] Content Security Policy configured and tested
- [ ] No hardcoded secrets or API keys
- [ ] TypeScript strict mode enabled; no `any` types
- [ ] Unit tests passing (≥ 70% coverage on core)
- [ ] Integration tests for popup ↔ background communication
- [ ] Manifest.json validates (use Chrome extension checker)
- [ ] Icons created (16×16, 48×48, 128×128 PNG)
- [ ] Screenshots ready (2–5 images showing feature)
- [ ] Privacy policy written and published online
- [ ] Description written (short + long versions)
- [ ] Permissions justified and minimal
- [ ] Keyboard shortcuts configured (if applicable)
- [ ] Dark mode support (if using UI library that supports it)
- [ ] Tested on Chrome, Firefox, Safari, Edge (at least visually)
- [ ] Error logging setup (Sentry or custom)
- [ ] Analytics configured (track installs, key features)
- [ ] Support email/form live
- [ ] Zip file created with `src/` and `manifest.json`
- [ ] Chrome Web Store account created
- [ ] Store listing filled out completely
- [ ] Payment method added (if monetizing)
- [ ] Submit for review; target approval in 1–3 days

### Post-Launch (Tier 1)
- [ ] Monitor store reviews for bugs/feedback
- [ ] Fix critical bugs within 24 hours
- [ ] Plan Firefox/Safari/Edge launches

