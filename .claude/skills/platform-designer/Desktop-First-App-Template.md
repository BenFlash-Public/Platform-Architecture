---
name: Desktop-First App Template
description: For pro tools, developer utilities, power user apps. Ship native macOS or Windows first, then web, then mobile.
---

# Desktop-First App Architecture Template

**Best for:** Developer tools (IDEs, terminals, build tools), creative software (design, video, audio), power user applications, system utilities, desktop-centric workflows where native performance and OS integration matter more than mobile reach.

**Platform sequence:** Desktop native (macOS or Windows, Tier 1) → Web Dashboard (Tier 2) → Mobile Web PWA (Tier 3) → Mobile native (Tier 4+)

**Last verified:** 2026-09-27 (Electron version support, code signing requirements, macOS/Windows deployment options)

**Timeline assumption:** Week ranges assume ~2 full-time engineers ("Parallel" rows need at least 2). Scale per SKILL.md Step 4.

---

## Platform Status Table

| Tier | Platform | Timeline | Tech Stack | Status | Notes |
|------|----------|----------|-----------|--------|-------|
| **1** | macOS (native) | Weeks 1–12 | Swift/SwiftUI or Electron | Critical path | Direct distribution via App Store or DMG |
| **1** | Windows (native) | Weeks 1–12 | C#/.NET MAUI or Electron | Critical path | Direct distribution via Microsoft Store or exe |
| **2** | Web Dashboard | Weeks 13–18 | Next.js, React, Tailwind | Post-launch | Cloud sync, admin, settings, cross-platform access |
| **3** | Mobile Web PWA | Weeks 19–24 | React, Service Worker | Post-launch | Responsive design; offline support |
| **4** | iOS / Android | Weeks 25+ | Swift / Kotlin | Optional | Secondary; sync with desktop via cloud |

---

## Key Architectural Decisions

### 1. Native vs. Electron Trade-off

**Native (macOS/Windows):**
- **Pros:** Fastest performance; full OS access; native UX polish; code signing trusted by OS
- **Cons:** Separate codebases; hiring cost (Swift for Mac, C# for Windows); longer dev time
- **Use when:** Performance critical (video editing, large file processing), direct hardware access needed, or premium brand positioning

**Electron (cross-platform):**
- **Pros:** Single codebase (JavaScript/TypeScript); fast iteration; Chromium engine
- **Cons:** Heavier memory footprint (300–500MB per app); slower than native; harder to distribute via app stores
- **Use when:** Speed to market critical; small team; don't need App Store distribution

**Recommendation:** If budget allows → native for each platform. If not → Electron for both macOS + Windows in Tier 1.

### 2. Desktop-to-Cloud Sync Architecture

**Most desktop apps need cloud sync (settings, files, collab).**

```
macOS Client ──┐
               ├──> Sync Engine ──> Cloud API ──> PostgreSQL / S3
Windows Client ┤
               └──> Local file system (Documents, AppData)
```

**Sync strategy:**
- **Local-first:** Keep working copy on disk; sync to cloud async
- **Offline:** Full app functionality offline; sync queued changes on reconnect
- **File watching:** Monitor local directories; upload changes within 5 seconds
- **Conflict resolution:** Show user conflict dialog; keep both versions + server version
- **Cloud storage:** S3, Google Drive, Dropbox API for file sync

### 3. Auto-Update & Distribution

**Desktop apps must update safely and automatically.**

- **macOS:** Sparkle framework (signed .dmg releases) or notarization via Apple
- **Windows:** MSIX package format (Microsoft Store) or signed exe installer
- **Electron:** electron-updater (check GitHub releases for updates)
- **Update strategy:** Delta updates (only changed files); background install; restart prompt
- **Code signing:** Sign all binaries; attach certificates; revoke if compromised

### 4. Monetization Gating

**For desktop pro tools:**

| Model | Tier 1 Strategy | Implementation |
|-------|---|---|
| **One-time purchase** | $99 lifetime license (perpetual) | License key in app; server validation |
| **Subscription** | $10/mo or $99/year | Subscription via Stripe; license renewed yearly |
| **Freemium** | Free tier (basic features); Pro ($99/year) | License check at startup; gate features |
| **Team licensing** | $499/year for up to 5 users | Bulk license keys; seat validation |

**Key difference from mobile:** Desktop users expect offline licensing. Validate license on first run; cache result locally.

---

## Tier 1 Release Gates

**Must pass before public release (desktop Tier 1 MVP):**

### Code Quality
- [ ] Unit test coverage ≥ 70% on core logic (file processing, sync, auth)
- [ ] Integration tests for offline → online → sync flow
- [ ] No crashes on file operations, large files, network toggle
- [ ] Linting passing (swiftlint for Mac, dotnet format for Windows, ESLint for Electron)

### Performance
- [ ] App launch < 1 second (measured on mid-range machine)
- [ ] File open < 2 seconds for typical files (< 1GB)
- [ ] Sync latency < 10 seconds for small file changes
- [ ] Memory usage < 500MB (for feature-rich apps; < 200MB for simple tools)
- [ ] CPU idle < 2% when backgrounded

### Security
- [ ] All cloud API calls over HTTPS; certificate pinning
- **For native apps:** Code signed with valid developer certificate
- **For Electron:** ASAR archives signed; auto-update source verified
- [ ] License keys cryptographically signed (cannot forge)
- [ ] Credentials stored in OS keychain (Keychain on Mac, Credential Manager on Windows)
- [ ] No secrets in app bundles or config files
- [ ] Update mechanism secured (signed manifests, hash verification)

### User Experience
- [ ] Onboarding < 2 minutes (license entry, cloud sync setup, first project)
- [ ] Core workflow (open file, make change, save) without errors
- [ ] Error messages clear (not "Error 42", but "Couldn't upload. Network unavailable.")
- [ ] Offline mode clearly indicated (banner or status bar)
- [ ] Sync status visible (spinning indicator, completion message)
- [ ] Undo/redo working; undo/redo stash survives app restart

### System Integration
- [ ] **macOS:** App appears in Applications folder; menu bar icons work; keyboard shortcuts responsive
- [ ] **Windows:** Installer creates Start Menu entry; uninstall cleans up (no leftover files)
- [ ] **Both:** Right-click context menu integration (if applicable)
- [ ] File associations (*.myformat → open with app)

### Licensing & Distribution
- [ ] License key entry/validation tested end-to-end
- [ ] License server responds correctly (valid, expired, revoked keys)
- [ ] Offline license check working (cached license valid for 30 days offline)
- [ ] App Store (Mac or Windows) submission passing review
- [ ] Or: DMG/exe installer signed, notarized, ready for direct distribution

---

## Tech Stack Rationale

### macOS Native (Swift + SwiftUI)
- **Swift:** Type-safe, memory-safe; Xcode integration; best macOS ecosystem
- **SwiftUI:** Modern declarative UI; automatic Dark Mode, accessibility
- **Cocoa frameworks:**
  - **AppKit:** Low-level window management, menus, responder chain
  - **Foundation:** Core data types, file I/O, networking
  - **CloudKit:** iCloud sync for documents and settings
- **Sparkle:** Trusted auto-update framework; Delta updates; user-friendly
- **Performance:** Native compiled; instant launch; minimal memory

**Alternative:** Electron (slower, larger footprint)

### Windows Native (C# + .NET MAUI)
- **.NET MAUI:** Cross-platform UI framework; compiles to native Windows
- **C#:** Modern, type-safe; LINQ for data processing; large library ecosystem
- **Windows APIs:**
  - **WinUI 3:** Modern UI framework; Fluent Design
  - **Windows.Storage:** File access, OneDrive sync
  - **Windows.ApplicationModel:** App lifecycle, notifications
- **MSIX:** Modern package format; Microsoft Store distribution
- **Performance:** Native compiled; responsive; solid memory footprint

**Alternative:** Electron (simpler for multi-platform)

### Electron (Cross-Platform)
- **Electron:** Single codebase (TypeScript/JavaScript); Chromium engine
- **TypeScript:** Catch bugs at compile time
- **electron-builder:** Packaging for macOS + Windows; automatic signing, code signing
- **electron-updater:** Delta updates; background install
- **Native modules (C++):** Performance-critical operations (file I/O, compression)
- **IPC:** Electron main process ↔ renderer process communication

**Pros:** Reuse web skills, one codebase
**Cons:** ~300MB app size, higher memory, slower than native

### Backend (Cloud Sync)
- **API:** Node.js/Express, Python/FastAPI, or Go/Gin
- **Database:** PostgreSQL (ACID, transactions); Firebase (managed)
- **Storage:** S3 or Google Cloud Storage (files)
- **Sync:** Custom REST API + polling, or Firestore Realtime (if using Firebase)

---

## Sample Feature Roadmap (24 weeks to Tier 3)

### Tier 1 (Weeks 1–12): Native Desktop + Backend Infrastructure
- macOS app (Swift + SwiftUI) OR Windows app (C# + .NET MAUI)
- License key system (one-time or subscription)
- Local file management
- Settings/preferences
- Auto-update framework
- Direct distribution (DMG or exe) or App Store submission
- (Parallel, Weeks 8–12) Backend API (Node/Python/Go)
- (Parallel, Weeks 8–12) Cloud storage (S3 or GCS), Document sync, Settings sync

### Tier 2 (Weeks 13–18): Web Dashboard
- Web app (Next.js + React) for cloud access
- Settings management
- Team management (if team features)
- Billing dashboard

### Tier 3 (Weeks 19–24): Mobile PWA
- Mobile web PWA (responsive, offline)
- Sync with desktop data

### Tier 4 (Weeks 25+): Mobile Native (optional)
- iOS/Android native apps (optional; sync with desktop)

---

## Known Pitfalls & How to Avoid

| Pitfall | Why It Hurts | Mitigation |
|---------|---|---|
| **Shipping unsigned code** | macOS blocks on first run; user friction | Code sign from day 1; test unsigned app behavior |
| **File sync conflicts** | Data loss or user confusion | Show conflict dialog; keep all versions; last-write-wins default |
| **License server down** | Users can't use offline-invalid app | Cache license locally (valid 30 days offline); graceful degradation |
| **Large app bundle** | Users hesitant to download; update failures | Minimize dependencies; delta updates; lazy load features |
| **Auto-update crashes** | App becomes unusable after update | Staged rollout (10%, 50%, 100%); keep previous version; rollback option |
| **No offline support** | App unusable on bad network | All features work offline; sync queued changes on reconnect |
| **Neglecting Windows/macOS parity** | Windows version feels second-class; loses users | Test both equally; feature parity within 1 release |
| **Heavy on RAM/CPU** | Fans spin; battery drain (laptops); complaints | Profile regularly (Activity Monitor / Task Manager); optimize hot paths |

---

## Checklist for Tier 1 MVP Launch

### macOS (if shipping native)
- [ ] App built and tested on Intel and Apple Silicon (M1+)
- [ ] Code signed with Apple Developer certificate
- [ ] App notarized by Apple (required for Monterey+)
- [ ] DMG installer created; code signed
- [ ] Sparkle auto-update configured and tested
- [ ] License key system working (entry, validation, offline cache)
- [ ] Settings persist across app restart (UserDefaults or plist)
- [ ] File open/save dialogs working; file associations set
- [ ] macOS App Store submission passing review (or direct distribution)

### Windows (if shipping native)
- [ ] App built and tested on Windows 10 + Windows 11
- [ ] Code signed with Windows certificate
- [ ] MSIX package created; signed
- [ ] Installer (.exe) created; signed
- [ ] Auto-update mechanism tested (WinUI auto-update or custom)
- [ ] License key system working
- [ ] Settings persist across app restart (AppData)
- [ ] File open/save dialogs working; file associations set
- [ ] Microsoft Store submission passing review (or direct distribution)

### Both (macOS + Windows)
- [ ] Core feature (open, edit, save) works end-to-end
- [ ] Offline sync tested (queue changes offline, sync on reconnect)
- [ ] Error handling: no crashes on network toggle, file errors, large files
- [ ] Performance: launch < 1s, file ops < 2s, memory < 500MB
- [ ] Security: all API calls HTTPS; no plaintext secrets
- [ ] Analytics firing: launch, feature usage, errors
- [ ] Crash reporting (Sentry or custom) integrated
- [ ] Help/documentation ready (in-app + website)
- [ ] Support email live and monitored
- [ ] Privacy policy and ToS published

### Cloud Sync (if included)
- [ ] Backend API deployed and monitored
- [ ] Database backups automated (daily)
- [ ] Cloud storage (S3/GCS) configured and tested
- [ ] File sync tested (upload, download, conflict resolution)
- [ ] Settings sync tested across devices
- [ ] Authentication tested (login, token refresh, logout)

---

## Post-Launch Operations

| Area | Plan |
|---|---|
| **Release cadence** | Auto-update channel (stable + beta); signed and notarized builds only |
| **Minimum supported versions** | Support current and previous macOS/Windows versions; state the policy on the download page |
| **License & sync API** | Version the license-check and sync APIs; offline-cached licenses must keep working after server changes |
| **Rollback** | Keep the previous build downloadable; auto-updater must be able to roll back a bad release |
| **Tier gate** | Start the web dashboard when active paid users ask for cross-device access, not on a date |
