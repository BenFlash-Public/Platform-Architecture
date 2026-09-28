---
name: Android-First App Template
description: For apps targeting Android-dominant markets (India, SE Asia) or teams with deep Kotlin expertise. Ship Android native first, then web, then iOS.
---

# Android-First App Architecture Template

**Best for:** Apps targeting Android-dominant markets (India, Southeast Asia, Brazil), teams with strong Kotlin expertise, products that benefit from Android-specific sensors (NFC, broader hardware support), or when iOS reach is secondary to market expansion.

**Platform sequence:** Android native (Tier 1) → Mobile Web PWA (Tier 2) → Web Dashboard (Tier 3) → iOS native (Tier 4) → Wear OS (Tier 5)

**Last verified:** 2026-09-27 (Play Store target API 36+ requirement, Google Play Billing commission rates, Kotlin/Jetpack support)

**Timeline assumption:** Week ranges assume ~2 full-time engineers ("Parallel" rows need at least 2). Scale per SKILL.md Step 4.

---

## Platform Status Table

| Tier | Platform | Timeline | Tech Stack | Status | Notes |
|------|----------|----------|-----------|--------|-------|
| **1** | Android (native) | Weeks 1–12 | Kotlin, Jetpack Compose, Room | Critical path | Play Store launch; diverse device support |
| **2** | Mobile Web PWA | Weeks 10–14 | React, TypeScript, IndexedDB | Parallel | Web fallback; user acquisition; zero-install |
| **3** | Web Dashboard | Weeks 15–20 | Next.js, React, Tailwind | Post-launch | Analytics, admin, insights; desktop users |
| **4** | iOS native | Weeks 21–32 | Swift, SwiftUI, Core Data | Post-launch | Premium tier; App Store presence |
| **5** | Wear OS (smartwatch) | Weeks 33+ | Kotlin, Jetpack Compose for Wear | Optional | Companion app; offline functionality |

---

## Key Architectural Decisions

### 1. Android Device & OS Fragmentation

**Challenge:** Android runs on devices from $50 (low memory) to $2000 (flagship).

**Strategy:**
- **Target API:** Minimum SDK 24 (current AndroidX default; many libraries no longer support 21); target API 36+ (required for new apps and updates from Aug 31, 2026 — [Play target API policy](https://developer.android.com/google/play/requirements/target-sdk))
- **Memory:** Design for low-end devices (1GB RAM). If it works on Moto G (2GB RAM), it works everywhere.
- **Network:** Assume 3G/4G with variable latency; batch requests, implement retry logic
- **Screen sizes:** Test on phones (5.5–6.5"), tablets (7–10"), foldables (emerging)
- **Permissions:** Request at runtime; graceful fallback if permission denied

**Dependency reduction:** Every library adds APK size. Target max 50MB (uncompressed) for 4G connectivity.

### 2. Backend Architecture

**Recommended:** Lightweight API + managed sync (Firestore or custom WebSocket)

```
Android App ───┐
               ├──> API Gateway ──> Auth ──> PostgreSQL / Firestore
Web (PWA) ─────┤                 ├──> Sync Service
Web (Dashboard)┤                 └──> FCM (Firebase Cloud Messaging)
               │
        Optional: Firestore for native sync
```

**Tech choices:**
- **API:** Node.js/Express, Python/FastAPI, or Kotlin/Ktor (backend in same language)
- **Database:** Firestore (native Android SDK) or PostgreSQL
- **Sync:** Firestore Realtime Database (built for Android), or custom REST + polling
- **Push:** FCM (Firebase Cloud Messaging); free tier includes push
- **Storage:** Firebase Storage or S3
- **Analytics:** Firebase Analytics (built-in) or Mixpanel

### 3. Offline-First with Room Database

**Android's local database: Room (built on SQLite)**

- **Room:** Type-safe ORM; compile-time schema checking; excellent coroutine support
- **Sync strategy:**
  - Write changes to Room immediately (optimistic updates)
  - Queue sync operations on background thread (WorkManager)
  - On reconnect, replay pending changes
  - Conflict resolution: timestamp-based (last-write-wins)
- **WorkManager:** Background task execution; survives app restart, device reboot
- **DataStore:** Lightweight key-value store for user preferences

### 4. Monetization Gating

**For Android apps (Play Store):**

| Model | Tier 1 Strategy | Implementation |
|-------|---|---|
| **Freemium** | Free tier (3 workouts); Pro ($3.99/mo) | Google Play Billing; feature gate on license |
| **One-time purchase** | $4.99 lifetime | Google Play Billing (non-subscription product) |
| **Subscription + Trial** | 7-day free trial, then $4.99/mo | Google Play subscriptions with trial |
| **Ads** | Free with ads; Pro removes ads | Google AdMob or other ad networks |

**Critical rule:** Price parity with other platforms. If iOS is $4.99/mo, Android must be $4.99/mo.

---

## Tier 1 Release Gates

**Must pass before Google Play Store launch:**

### Code Quality
- [ ] Unit test coverage ≥ 70% on sync, auth, database models
- [ ] Integration tests for auth → offline → online → sync flow
- [ ] No crashes on devices: Moto G (low-end), Pixel 6 (mid-range), Samsung Galaxy (high-end)
- [ ] Lint passing (Android Lint, Detekt); no warnings in main targets
- [ ] Memory leaks tested (Android Profiler, LeakCanary)

### Performance
- [ ] App launch < 3 seconds (on Moto G / 2GB RAM)
- [ ] Scroll performance ≥ 60 FPS on recycler views (Pixel 6 or equivalent)
- [ ] Memory usage < 100MB under normal load
- [ ] Battery drain < 5% per hour of active use
- [ ] APK size < 50MB (uncompressed)
- [ ] Sync latency < 5 seconds for offline changes post-reconnect

### Security
- [ ] All API calls over HTTPS; certificate pinning (Network Security Config)
- [ ] Credentials stored in EncryptedSharedPreferences, never plaintext
- [ ] JWT token refresh automatic; expired tokens rejected
- [ ] Biometric auth (fingerprint/face) optional but secure (BiometricPrompt)
- [ ] No hardcoded API keys or secrets in source code
- [ ] Runtime permissions requested with clear explanation
- [ ] Database encrypted with SQLCipher (if handling sensitive data)

### User Experience
- [ ] Onboarding completes in < 2 minutes (auth, permissions, first action)
- [ ] Core feature (e.g., create item, view list) works without tutorial
- [ ] Error messages clear: not "Sync failed", but "Couldn't upload. Check your internet."
- [ ] Loading states visible (progress bars, skeleton screens)
- [ ] Offline mode clearly indicated (banner or status)
- [ ] Material Design 3 compliance (color, typography, spacing)
- [ ] Dark mode support (follows system preference)

### Play Store Compliance
- [ ] Privacy policy and terms of service accessible in app + website
- [ ] Privacy label completed (location, contacts, etc.)
- [ ] Target SDK 34+ (required by Play Store)
- [ ] Payment flows follow current Play payments policy for each country you ship in (external-link and alternative-billing rules vary by region; verify before launch)
- [ ] Screenshots (4–8 per language) ready; show key features
- [ ] App description clear; keywords relevant
- [ ] Support email live
- [ ] App signing configured (Google Play App Signing)

### Analytics & Monitoring
- [ ] Analytics firing: signup, first action, purchase, churn
- [ ] Crash reporting (Firebase Crashlytics) integrated
- [ ] Error logging for sync failures, API errors
- [ ] Beta testing via Google Play Console (Open Testing track)

---

## Tech Stack Rationale

### Android (Kotlin + Jetpack Compose)
- **Kotlin:** Official Android language; null-safe; concise; coroutines for async
- **Jetpack Compose:** Modern declarative UI; automatic Dark Mode + accessibility
- **Jetpack libraries:**
  - **Room:** Type-safe database ORM; plays well with coroutines
  - **DataStore:** Lightweight preferences (replacement for SharedPreferences)
  - **WorkManager:** Background tasks; survives app restart + device reboot
  - **Lifecycle:** Manage fragments, activities, app state lifecycle
  - **Navigation:** Fragment routing + backstack management
- **Firebase:** Analytics, Crashlytics, Cloud Messaging, Authentication all free tier
- **Hilt:** Dependency injection; reduces boilerplate

**Alternatives:** Java (more boilerplate), React Native/Expo or Flutter (one codebase for Android + iOS; native modules needed for some OS features), Kotlin Multiplatform (share business logic, keep native UI)

### Web (React + TypeScript)
- **React:** Largest ecosystem; easy to hire; 100+ UI libraries
- **TypeScript:** Catches bugs at compile time; improves IDE support
- **Vite:** Fast dev server, instant HMR, < 1s rebuilds
- **Service Worker + IndexedDB:** Offline-first PWA; zero-install trial
- **TanStack Query:** Sync data without duplicating backend logic

### Backend
- **Firebase:** Managed by Google; SDKs for Android, web, admin; free Tier 1 hosting
- **Node.js + PostgreSQL:** Full control; custom sync; lower cost at scale
- **Kotlin/Ktor:** Backend in same language as Android; share data models

---

## Sample Feature Roadmap (32 weeks to Tier 4)

### Tier 1 (Weeks 1–12): Android MVP
- Auth (email/password, Google Sign-In)
- Core feature (create/edit/delete content)
- Room database + offline sync
- Google Play Billing (freemium paywall)
- Push notifications via FCM
- Play Store launch

### Tier 2 (Weeks 10–14): Mobile Web PWA
- Mobile web PWA (responsive, offline)
- Email invite system
- Basic sharing (view/edit permissions)

### Tier 3 (Weeks 15–20): Web Dashboard + Retention
- Web dashboard (analytics, user management)
- Advanced notifications (campaigns, reminders)
- Analytics dashboard (charts, user cohorts)
- Social features (comments, likes)
- Premium tier features

### Tier 4 (Weeks 21–32): iOS
- Native iOS app (Swift + SwiftUI)
- Cross-platform sync (Android + iOS + web)
- Wear OS companion app (smartwatch)

---

## Known Pitfalls & How to Avoid

| Pitfall | Why It Hurts | Mitigation |
|---------|---|---|
| **Testing on one device** | Crashes on low-end phones; Play Store refunds | Test on physical devices: low-end (Moto G), mid-range (Pixel), flagship |
| **Memory leaks** | App crashes after 2–3 hours; 1-star reviews | Use LeakCanary in dev; Instruments (Memory Profiler) in staging |
| **Blocking main thread** | Janky UI, ANR (Application Not Responding) crashes | Use coroutines/WorkManager; never fetch network on main |
| **Sync race conditions** | Data loss or duplicate entries | Use timestamps + last-write-wins; extensive offline/online testing |
| **Large APK size** | Users on 4G hesitant to download | Target < 50MB; use ProGuard/R8 for obfuscation; lazy load features |
| **Shipping without Play Store compliance** | Rejection; wasted 1–2 weeks | Review Target SDK, privacy label, external payments early |
| **No background sync** | Offline data never syncs; users think app is broken | Implement WorkManager; test with airplane mode |
| **Building iOS in parallel** | Slow MVP; duplicated logic | Finish Android Tier 1, learn lessons, then iOS |

---

## Checklist for Tier 1 MVP Launch (Play Store)

- [ ] Android app built and tested on low-end (Moto G), mid-range (Pixel), high-end devices
- [ ] Room database configured and tested for offline persistence
- [ ] WorkManager integration for background sync
- [ ] Google Play Billing SDK integrated; sandbox purchase tested
- [ ] Auth flow tested (email/password, Google Sign-In, password reset)
- [ ] Offline → online sync tested (toggle airplane mode, verify sync)
- [ ] Firebase Crashlytics integrated and tested
- [ ] Firebase Analytics firing (signup, first action, purchase)
- [ ] FCM push notifications working on test devices
- [ ] Permissions tested (runtime requests, graceful fallback)
- [ ] Battery and memory profiling passed (< 5% drain/hour, < 100MB RAM)
- [ ] Privacy policy and ToS accessible in app
- [ ] Privacy label completed and uploaded
- [ ] APK size < 50MB (check with bundletool)
- [ ] Material Design 3 compliance verified
- [ ] Dark mode support working
- [ ] Screenshots (4–8) ready; attractive and clear
- [ ] App description, keywords, and metadata optimized
- [ ] Support email configured and monitored
- [ ] Open Testing beta (20+ testers) for 2 weeks
- [ ] Address beta feedback; fix crashes/major bugs
- [ ] Generate signed APK; upload to Play Store Console
- [ ] Play Store submission complete; compliance reviewed
- [ ] Monitor Crashlytics, analytics, user reviews post-launch

---

## Post-Launch Operations

| Area | Plan |
|---|---|
| **Release cadence** | Staged rollouts (e.g., 10% → 50% → 100%) through Play Console; halt on crash spikes |
| **Minimum supported versions** | Raise minSdk deliberately and announce it; re-check the Play target API deadline every August |
| **API versioning** | `/v1` from day 1; old APKs stay installed for months, so never break a shipped contract |
| **Device coverage** | Keep a low-end, mid-range, and flagship device in the test matrix every release |
| **Tier gate** | Start Tier 2 when retention and ANR/crash targets are met, not on a date |
