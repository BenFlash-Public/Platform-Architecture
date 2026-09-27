---
name: iOS-First App Template
description: For premium consumer apps requiring deep OS integration (HealthKit, notifications, camera). Ship native iOS first, then web, then Android.
---

# iOS-First App Architecture Template

**Best for:** Premium fitness/health apps (HealthKit integration), location-based services, camera-intensive apps, games with OS-level features, VoIP apps, notification-driven experiences where iOS polish and App Store positioning matter more than cross-platform speed.

**Platform sequence:** iOS native (Tier 1) → Mobile Web PWA (Tier 2) → Web Dashboard (Tier 3) → Android native (Tier 4) → watchOS (Tier 5)

**Last verified:** 2026-09-27 (HealthKit SDK, App Store commission rates, StoreKit 2, iOS minimum version support)

---

## Platform Status Table

| Tier | Platform | Timeline | Tech Stack | Status | Notes |
|------|----------|----------|-----------|--------|-------|
| **1** | iOS (native) | Weeks 1–10 | Swift, SwiftUI, Core Data / Realm | Critical path | HealthKit, notifications, cameras; App Store launch |
| **2** | Mobile Web PWA | Weeks 8–12 | React, TypeScript, IndexedDB | Parallel | Web fallback; user acquisition; zero-install trial |
| **3** | Web Dashboard | Weeks 13–18 | Next.js, React, Tailwind | Post-launch | Analytics, insights, admin; desktop users |
| **4** | Android native | Weeks 19–30 | Kotlin, Jetpack Compose, Room | Post-launch | Leverage iOS learnings; Play Store positioning |
| **5** | watchOS / Apple TV | Weeks 31+ | SwiftUI, HealthKit Watch | Optional | Companion app; fitness tracking on wrist |

---

## Key Architectural Decisions

### 1. iOS OS Integration Points

**Question:** Which system frameworks do you need?

**HealthKit (fitness/health apps):**
- Request user permission to read/write HealthKit data (workouts, steps, sleep)
- Write app data back to HealthKit for system health dashboard
- Use HKHealthStoreDelegate for background updates
- Cross-device sync via iCloud HealthKit (Apple handles encryption)
- **Warning:** HealthKit is iOS-only; no Android equivalent

**NotificationCenter (reminders, engagement):**
- Local notifications (in-app reminders) via UNUserNotificationCenter
- Remote push notifications (APNs) for engagement
- Silent push for background sync (max 30s runtime)
- Critical alerts for health/safety apps (bypass Do Not Disturb)

**CoreLocation (maps, geofencing):**
- Background location updates (always-on, high battery cost)
- Geofencing with <100m precision
- Region monitoring (enter/exit triggers)

**Camera/PhotoKit:**
- AVFoundation for real-time camera capture
- Photos framework for library access
- CameraX alternative doesn't exist on iOS; ship native

**Bluetooth (wearables, accessories):**
- Core Bluetooth for wearable connectivity
- HIDKit for Bluetooth accessories
- Network framework for persistent connections

### 2. Backend Architecture

**Recommended:** Lightweight API + Realm Sync (if real-time needed) OR managed CloudKit alternative

```
iOS App ──────┐
              ├──> API Gateway ──> Auth ──> PostgreSQL / Firestore
Web (PWA) ────┤                 ├──> Sync Service (WebSocket)
Web (Dashboard)┤                 └──> Push Notification Service (APNs)
              │
         Optional: Realm Sync or CloudKit for native sync
```

**Tech choices:**
- **API:** Node.js/Express, Python/FastAPI, or Go/Gin
- **Database:** PostgreSQL or Firebase (Firestore has good iOS SDK)
- **Sync:** Realm Sync (built for iOS), CloudKit (Apple-native), or custom WebSocket
- **Push:** APNs (Apple Push Notification service); requires .p8 certificate
- **Storage:** iCloud Documents + CloudKit for app-specific data, S3 for media

### 3. Offline-First Data Model

**iOS is inherently offline-friendly. Use it.**

- **Local store:** Realm (Realm Mobile Database) or Core Data
- **Sync strategy:** 
  - Write changes to Realm immediately (optimistic updates)
  - Queue sync operations asynchronously
  - On reconnect, replay pending changes
  - Conflict resolution: last-write-wins by default, but flag conflicts for user review
- **Background sync:** Use BackgroundTasks framework to sync while app is suspended
- **HealthKit:** Automatically syncs across user's devices via iCloud

### 4. Monetization Gating

**For premium iOS apps:**

| Model | Tier 1 Strategy | Implementation |
|-------|---|---|
| **Freemium** | Free tier (limited workouts); Pro ($4.99/mo) | StoreKit 2; feature gate on subscription flag |
| **One-time purchase** | $9.99 lifetime unlock | Non-consumable IAP; cached on device |
| **Subscription + Trial** | 7-day free, then $9.99/mo | StoreKit 2 auto-renew; server validates receipt |
| **Premium features** | Base app free; Pro features $2.99 each | Consumable IAPs for one-time features |

**Critical rule:** Web pricing must match iOS. If iOS is $4.99/mo, web is $4.99/mo (not $5.99).

---

## Tier 1 Release Gates

**Must pass before App Store submission (Tier 1 MVP):**

### Code Quality
- [ ] Unit test coverage ≥ 70% on sync logic, data models, HealthKit integration
- [ ] Integration tests for auth → offline → sync → online flow
- [ ] No crashes on network toggle, background/foreground, memory pressure
- [ ] SwiftLint passing (zero warnings in main targets)
- [ ] No retain cycles (Instruments > Allocations + Address Sanitizer)

### Performance
- [ ] iOS app cold launch < 2 seconds (measured on iPhone 12 mini)
- [ ] Scroll performance ≥ 60 FPS (no jank in lists/tables)
- [ ] Memory usage < 100MB under normal load
- [ ] Battery drain < 5% per hour of active use
- [ ] Sync latency < 5 seconds for offline changes post-reconnect

### Security
- [ ] All API calls over HTTPS; certificate pinning (optional but recommended)
- [ ] Credentials stored in Keychain, never in UserDefaults or files
- [ ] JWT token refresh automatic; expired tokens rejected
- [ ] HealthKit permissions requested with clear privacy explanation
- [ ] Location data (if used) only accessed when user grants permission
- [ ] No hardcoded API keys or secrets in source code
- [ ] Biometric auth (Face ID/Touch ID) optional but secure

### User Experience
- [ ] Onboarding completes in < 2 minutes (auth, permission requests, first action)
- [ ] Core feature (e.g., log workout, view dashboard) works without tutorial
- [ ] Error messages are clear: not "Sync failed", but "Couldn't upload workout. Check your internet."
- [ ] Loading states visible (spinners, progress bars)
- [ ] Offline mode clearly indicated (banner at top)
- [ ] Form validation clear (red borders, inline hints)

### App Store Compliance
- [ ] Privacy policy and terms of service in app + on website
- [ ] App privacy label completed (location, health, etc.)
- [ ] No hardcoded links to external payment (App Store rules)
- [ ] Screenshots ready (5 per locale; highlight key features)
- [ ] App description clear; keywords relevant
- [ ] Support email live
- [ ] Screenshots, description, metadata in 2+ languages (if targeting multiple)

### Analytics & Monitoring
- [ ] Analytics firing: signup, first workout logged, purchase, churn
- [ ] Crash reporting (Firebase Crashlytics or Sentry) integrated
- [ ] Error logging for sync failures, API errors
- [ ] Beta testing via TestFlight (at least 50 testers)

---

## Tech Stack Rationale

### iOS (Swift + SwiftUI)
- **Swift:** Industry standard; fastest compile times; memory-safe by design
- **SwiftUI:** Modern declarative UI; automatic Dark Mode + accessibility; fastest to iterate
- **Combine:** Reactive state management; pairs naturally with SwiftUI
- **Core Data:** Built-in, no dependencies; sufficient for < 100MB apps
- **Realm:** Better for large datasets (> 50MB), complex queries, offline sync; 1.5 MB framework
- **StoreKit 2:** Apple's latest In-App Purchase framework; handles receipts, entitlements, subscriptions
- **HealthKit:** Native health data integration; automatic iCloud sync

**Alternatives:** Objective-C (deprecated), React Native (slower, harder debugging)

### Web (React + TypeScript)
- **React:** Largest ecosystem; easy to hire; 100+ UI libraries
- **TypeScript:** Catches bugs at compile time; improves IDE support
- **Vite:** Fast dev server, instant HMR, < 1s rebuilds
- **Service Worker + IndexedDB:** Offline-first PWA; zero-install trial
- **TanStack Query:** Sync data between devices without duplicating backend logic

### Backend
- **Firestore:** Managed by Google; SDKs for iOS, web, admin; real-time sync built-in
- **Node.js + PostgreSQL:** Full control; custom sync logic; smaller ops overhead
- **Parse Server:** Open-source backend-as-a-service; iOS, web, Android SDKs included

---

## Sample Feature Roadmap (20 weeks to Tier 4)

### Tier 1 (Weeks 1–10): iOS MVP
- Auth (email/password, Apple Sign-In)
- Core feature (log data: workouts, symptoms, meals)
- HealthKit integration (write to Health app)
- Offline support (Realm + background sync)
- In-app purchase (freemium paywall)
- iOS app to App Store

### Tier 2 (Weeks 8–12): Mobile Web PWA
- Mobile web PWA (responsive, offline)
- Email invite system
- Basic sharing (view-only)

### Tier 3 (Weeks 13–18): Web Dashboard + Retention
- Web dashboard (analytics, insights)
- Push notifications (workouts, milestones)
- Social features (friends, leaderboards)
- Advanced analytics dashboard (charting)
- Premium tier features (custom workouts, coaching)

### Tier 4 (Weeks 19–30): Android
- Native Android app (Kotlin + Jetpack Compose)
- Sync data across iOS + Android + web
- watchOS companion app (quick log, wrist display)

---

## Known Pitfalls & How to Avoid

| Pitfall | Why It Hurts | Mitigation |
|---------|---|---|
| **Shipping with sync bugs** | Data loss; user health data is sensitive | Extensive offline/online testing; conflict resolution tests |
| **HealthKit permission denied** | User can't use core feature | Request permissions at right moment (after onboarding, clear why needed) |
| **Background task crashes** | Silent failures; user doesn't know | Test background sync extensively; error logging mandatory |
| **Memory leaks in notifications** | App crashes after 100 notifications | Use Instruments (Allocations + Address Sanitizer); review retain cycles |
| **Battery drain from location** | Users uninstall; 1-star reviews | Use significant location updates, not continuous; add battery warning |
| **Building web too late** | Growth plateau without web option | Start web in parallel (Tier 2); PWA ready by week 12 |
| **Ignoring Android until Tier 4** | Data sync issues between iOS/Android | Design sync protocol now; test with both platforms early |
| **App Store rejection** | Delays launch 1–2 weeks | Review guidelines early (privacy labels, no external payments) |

---

## Checklist for Tier 1 MVP Launch (App Store)

- [ ] iOS app built and tested on physical devices (iPhone 12 mini minimum)
- [ ] Realm or Core Data configured for offline sync
- [ ] HealthKit permissions requested and working
- [ ] StoreKit 2 integration complete; sandbox purchase tested
- [ ] Auth flow tested (email/password, Apple Sign-In, password reset)
- [ ] Offline → online sync tested (toggle airplane mode, verify sync works)
- [ ] Crash reporting (Crashlytics or Sentry) integrated and tested
- [ ] Analytics firing (signup, core action, purchase)
- [ ] Background task sync working (app backgrounded, resume with new data)
- [ ] APNs certificate configured; test push received
- [ ] Privacy policy and ToS published on website
- [ ] App privacy label completed (health, location, etc.)
- [ ] Screenshots (5 per locale) ready; appealing and clear
- [ ] App name, description, keywords optimized
- [ ] TestFlight beta (50+ testers) for 2 weeks minimum
- [ ] Address TestFlight feedback; fix crashes/major bugs
- [ ] Archive build signed with correct provisioning profile
- [ ] App Store submission complete; metadata reviewed for compliance
- [ ] Monitoring dashboard live (Crashlytics, analytics)
- [ ] Support email live and monitored
