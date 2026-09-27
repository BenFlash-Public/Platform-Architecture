---
name: Mobile-First App Template
description: For consumer/prosumer apps where users access primarily via mobile (iOS + Android). Ships iOS + web PWA together in Tier 1, then desktop, then Android.
---

# Mobile-First App Architecture Template

**Best for:** Consumer apps, social platforms, creator tools, fitness apps, productivity apps where mobile is the primary interface.

**Platform sequence:** iOS + Mobile Web (Tier 1) → Desktop Web (Tier 2) → Android (Tier 3) → Watch/TV (Tier 4+)

---

## Platform Status Table

| Tier | Platform | Timeline | Tech Stack | Status | Notes |
|------|----------|----------|-----------|--------|-------|
| **1** | iOS (native) | Weeks 1–6 | Swift, SwiftUI, Core Data / Realm | Critical path | Launch cohort; App Store positioning |
| **1** | Mobile Web (PWA) | Weeks 4–7 | React, TypeScript, IndexedDB | Parallel | Zero-install trial; instant updates |
| **2** | Desktop Web | Weeks 8–14 | React, Electron (optional) | After MVP | Dashboard view; bulk operations |
| **3** | Android (native) | Weeks 15–24 | Kotlin, Jetpack Compose | Post-launch | Leverage iOS codebase learnings |
| **4** | watchOS / TV | TBD | SwiftUI | Optional | Native OS integrations if relevant |

---

## Key Architectural Decisions

### 1. Cross-Platform Sync Strategy

**Question:** Do users create/edit content on one device and view/continue on another?

**If YES (multi-device sync needed):**
- Architecture: Cloud-backed sync with versioned JSON events
- Implementation:
  - All platforms write events to backend queue
  - Offline queue (iOS: Realm, web: IndexedDB) holds pending changes
  - Sync layer reconciles conflicts (last-write-wins or custom resolution)
  - Backend broadcasts changes to all connected clients

**If NO (single-device primary):**
- Architecture: Simpler session-based sync
- Implementation:
  - Each device maintains local state
  - Optional cloud backup for recovery
  - No cross-device reconciliation needed

### 2. Backend Architecture

**Recommended:** Headless API (REST or GraphQL) + database + message queue

```
iOS Client ──┐
             ├──> API Gateway ──> Auth ──> Database (PostgreSQL)
Web Client ──┤                 ├──> Sync Service
Android ─────┘                 ├──> Message Queue (for offline sync)
                                └──> File Storage (S3)
```

**Tech choices:**
- **API:** Node.js/Express, Python/FastAPI, Go/Gin (choose based on team expertise)
- **Database:** PostgreSQL (relational) or Firebase (managed backend)
- **Sync:** Custom implementation or Firestore Realtime Database
- **Storage:** S3, Cloud Storage, or Cloudinary (if user-generated media)

### 3. Offline-First Capability

**Question:** Must users work offline and sync when reconnected?

**If YES:**
- iOS: Realm for local persistence
- Web: IndexedDB + Service Worker for offline PWA
- Android: Room database
- Sync strategy: Event-based (queue changes, replay on reconnect)

**If NO:**
- Simpler: Cache recent data locally, sync optional
- No complex conflict resolution needed

### 4. Monetization Gating

**Common patterns for mobile-first apps:**

| Model | Tier 1 Strategy | Platform Approach |
|-------|---|---|
| **Freemium** | Free tier with limited features; Pro unlocks | iOS: StoreKit 2 IAP. Web: Stripe Billing. |
| **Subscription** | Trial period (7-30 days free) then recurring | iOS: StoreKit 2 auto-renew. Web: Stripe subscriptions. |
| **Ads** | Free with ads; Pro removes ads | iOS: Ad networks (Google Mobile Ads). Web: AdSense/Mediavine. |
| **One-time purchase** | $X to unlock app permanently | iOS: Non-consumable IAP. Web: One-time payment via Stripe. |

**Critical rule:** iOS revenue must align with Web. Examples:
- If iOS charges $4.99/mo, web should be $4.99/mo (not $5.99)
- If iOS offers free trial, web should offer same trial length
- Apple takes 30% on IAP; Stripe takes 2.9% + $0.30. Factor into pricing.

---

## Tier 1 Release Gates

**Must pass before launching Tier 1 MVP:**

### Code Quality
- [ ] Unit test coverage ≥ 70% on core features (sync, auth, offline)
- [ ] No crashes on iOS/web when offline
- [ ] No unhandled promise rejections in web; no uncaught exceptions in iOS
- [ ] Lint passing (ESLint, SwiftLint)

### Performance
- [ ] iOS app cold launch < 2 seconds
- [ ] Web app loads in < 3 seconds (mobile 4G)
- [ ] Sync latency < 1 second for online changes
- [ ] Offline queue syncs within 30 seconds after reconnect

### Security
- [ ] All API calls over HTTPS
- [ ] JWT tokens refreshed every 60 minutes
- [ ] User credentials never logged or cached in plaintext
- [ ] Third-party APIs (Stripe, etc.) use server-side keys, not client-side

### User Experience
- [ ] Onboarding flow completes in < 2 minutes
- [ ] Core feature (e.g., create, save, view) works without tutorial
- [ ] Error messages are clear (not "Error: 500")
- [ ] Loading states visible on slow networks

### Business
- [ ] Revenue flow tested (purchase succeeds, receipt validated, Pro flag set)
- [ ] Analytics tracking core events (signup, first action, purchase, churn)
- [ ] Support process defined (email, chat, or in-app)

---

## Tech Stack Rationale

### iOS
- **Swift + SwiftUI:** Industry standard; fastest development; best iOS UX
- **Core Data:** Built-in, no dependencies; lightweight for <100MB apps
- **Realm:** Better for large datasets, complex queries, offline sync (1.5 MB framework)
- **Combine:** For reactive state management
- **StoreKit 2:** Apple's latest IAP framework; handles revenue complexities

**Alternatives:** React Native (faster cross-platform but slower performance, harder debugging)

### Web (PWA)
- **React:** Largest ecosystem, easiest to hire; 100+ UI component libraries
- **TypeScript:** Catches bugs at compile time; improves IDE support
- **IndexedDB + Service Worker:** No dependencies; enables true offline-first
- **Vite + esbuild:** Fast dev server, instant HMR, < 1s rebuilds

**Alternatives:** Vue (smaller community), Next.js (adds server-side complexity if not needed)

### Backend
- **Node.js/Express:** JavaScript full-stack; rapid iteration; npm ecosystem
- **PostgreSQL:** Relational; scales to millions of users; strong consistency
- **Redis:** Caching + session store; <1ms read latency
- **Bull (job queue):** Background sync processing, email delivery, analytics

**Alternatives:** Go (faster, lower memory; smaller ecosystem), Python (great for ML if needed)

---

## Sample Feature Roadmap (16 weeks to Tier 3)

### Tier 1 (Weeks 1–7): MVP Launch
- Auth (email/password, OAuth)
- Core feature (user creates/saves something)
- View library (list/search existing content)
- iOS app release
- Web PWA launch
- Freemium paywall (Pro subscription $4.99/mo)

### Tier 2 (Weeks 8–14): Growth & Retention
- Desktop web dashboard (if applicable)
- Notifications (reminders, social engagement)
- Basic analytics (user cohorts, feature usage)
- Android native app (leverage iOS learnings)

### Tier 3 (Weeks 15–24): Scale & Monetization
- Advanced features (depending on app type)
- Community/social features
- Creator tools (if applicable)
- Monetization optimization (pricing experiments, upsells)

---

## Known Pitfalls & How to Avoid

| Pitfall | Why It Hurts | Mitigation |
|---------|---|---|
| **Trying iOS + Android in parallel** | 2x the work; delays launch; iOS and Android SDKs diverge | Ship iOS Tier 1, Android Tier 3. Learn from iOS. |
| **Neglecting web in Tier 1** | Limits audience (web = desktop users); slows growth | Ship PWA alongside iOS; zero-install = higher conversion. |
| **Syncing without versioning** | Last-write-wins loses data; conflicts silently | Use event sourcing; version all changes (timestamps + user ID). |
| **Ignoring offline** | Users churn when switching networks | Offline queue mandatory; test on device with network toggle. |
| **Monetization added late** | Free users expect to stay free; harder to convert | Paywall in Tier 1; experiment early. |
| **No analytics** | Can't measure growth or churn; flying blind | Track: signup, first action, purchase, retention; set targets. |

---

## Checklist for Tier 1 MVP Launch

- [ ] iOS app built, tested, ready for App Store submission
- [ ] Web PWA served over HTTPS with Service Worker
- [ ] Backend API deployed and monitored
- [ ] Database backed up (daily snapshots)
- [ ] Auth flow (login, logout, password reset) tested end-to-end
- [ ] Monetization (Stripe, StoreKit 2) tested with real payments
- [ ] Error tracking setup (Sentry or equivalent)
- [ ] Analytics firing (Mixpanel, Segment, or custom)
- [ ] Support process defined (how do users reach you?)
- [ ] Privacy policy and ToS in place
- [ ] App Store submission complete; build approved
- [ ] Initial users (friends, beta testers) can install and use
