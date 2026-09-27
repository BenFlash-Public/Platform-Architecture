---
name: Web-First App Template
description: For B2B SaaS, data dashboards, admin tools where desktop web is primary. Ship web first (instant deploy, no review), then mobile web PWA, then native mobile later.
---

# Web-First App Architecture Template

**Best for:** B2B SaaS, CRM, project management, data analytics dashboards, admin tools, knowledge worker apps where users expect wide tables, bulk operations, and rich desktop experiences.

**Platform sequence:** Desktop Web (Tier 1) → Mobile Web PWA (Tier 2) → iOS native (Tier 3) → Android native (Tier 4) → Desktop native (Tier 5)

**Last verified:** 2026-09-27 (App Store commission rates, Play Store requirements, PWA Service Worker support)

---

## Platform Status Table

| Tier | Platform | Timeline | Tech Stack | Status | Notes |
|------|----------|----------|-----------|--------|-------|
| **1** | Desktop Web | Weeks 1–6 | Next.js, TypeScript, Tailwind, PostgreSQL | Critical path | Ship immediately; no App Store review; instant updates |
| **2** | Mobile Web PWA | Weeks 5–8 | React, Service Worker, IndexedDB | Parallel | Responsive design; offline queue; reuse backend |
| **3** | iOS native | Weeks 9–18 | Swift, SwiftUI, Core Data | Post-launch | App Store presence; premium tier incentive |
| **4** | Android native | Weeks 19–28 | Kotlin, Jetpack Compose, Room | Post-launch | Leverage iOS codebase learnings; Play Store |
| **5** | Desktop native (macOS/Windows) | Weeks 29+ | Electron or Tauri (optional) | Optional | Power users; offline-first; advanced sync |

---

## Key Architectural Decisions

### 1. Cross-Platform Sync Strategy

**Question:** Do users create/edit data on desktop and expect to see changes immediately on mobile, and vice versa?

**If YES (real-time multi-device sync):**
- Architecture: Cloud-first with WebSocket or gRPC for real-time updates
- Implementation:
  - Web client connects via WebSocket for live updates
  - Mobile PWA uses Service Worker offline queue + reconnect polling
  - Native apps use push notifications + background sync
  - Backend maintains a versioned event log (all changes timestamped + user ID)
  - Conflict resolution: last-write-wins with user override capability
  - Broadcast changes to all connected sessions within 1 second

**If NO (session-isolated or primarily web):**
- Architecture: Simpler REST API with eventual consistency
- Implementation:
  - Each client polls or uses short-polling for updates
  - Native apps fetch on foreground
  - No real-time expectation

### 2. Backend Architecture

**Recommended:** Monolithic API + managed database + cache layer (no message queue needed initially)

```
Desktop Web ──┐
              ├──> API Gateway ──> Auth ──> PostgreSQL + Redis
Mobile PWA ───┤                 ├──> Business Logic
Native Apps ──┘                 └──> WebSocket Server (for real-time)
```

**Tech choices:**
- **API:** Next.js API routes, Node.js/Express, or Python/FastAPI (pick based on team expertise)
- **Database:** PostgreSQL (ACID guarantees, excellent for SaaS); avoid NoSQL unless specific reason
- **Cache:** Redis for session store, real-time presence, feature flags
- **Storage:** S3 or Cloud Storage for file uploads
- **Real-time:** Socket.io or native WebSocket if real-time sync needed

### 3. Authentication & Access Control

**Critical for B2B:** Multi-tenant architecture with role-based access control (RBAC)

- **SSO:** Support OAuth 2.0 (Google, Microsoft) + SAML for enterprise
- **Session:** JWT tokens with 1-hour expiry, refresh token rotation
- **Mobile:** Mobile PWA uses same JWT; native apps store securely in keychain/secure storage
- **Offline fallback:** Cache last-known permissions; sync on reconnect

### 4. Monetization Gating

**Common patterns for B2B SaaS:**

| Model | Tier 1 Strategy | Implementation |
|-------|---|---|
| **Usage-Based** | Free tier (up to 100 users); per-user pricing above | Seed count in user preferences; gate in API middleware |
| **Subscription** | Starter ($29/mo), Pro ($99/mo), Enterprise (custom) | Stripe Billing; webhooks for upgrades/downgrades |
| **Hybrid** | Base subscription + per-feature add-ons | Subscription + feature flags in auth token |

**Critical rule:** All platforms charge the same. No desktop-only pricing tiers.

---

## Tier 1 Release Gates

**Must pass before launching web Tier 1 MVP:**

### Code Quality
- [ ] Unit test coverage ≥ 75% on auth, data models, critical business logic
- [ ] Integration tests for core workflows (login → create → share → view)
- [ ] No console errors in browser DevTools on Chrome/Firefox/Safari
- [ ] Lint passing (ESLint); no TypeScript errors
- [ ] Database migrations tested on staging database

### Performance
- [ ] Web app loads in < 2 seconds (desktop 10Mbps), < 4 seconds (mobile 4G)
- [ ] Time to interactive < 3 seconds (Lighthouse target)
- [ ] API response times: p50 < 100ms, p95 < 500ms for typical queries
- [ ] Database queries optimized (no N+1, indexes on join columns)
- [ ] Bundle size < 150KB (gzipped)

### Security
- [ ] All API calls over HTTPS; enforce HSTS
- [ ] JWT tokens include user ID, org ID, scopes; signed with RS256
- [ ] Passwords hashed with bcrypt (cost ≥ 12); no plaintext storage
- [ ] CSRF tokens on state-changing requests (POST/PUT/DELETE)
- [ ] Rate limiting on auth endpoints (5 attempts/10 minutes)
- [ ] Secrets (API keys, DB password) in environment variables, never in code
- [ ] SQL injection tests pass (use parameterized queries)
- [ ] XSS tests pass (sanitize user input; CSP headers)

### User Experience
- [ ] Onboarding flow completes in < 3 minutes (for new user)
- [ ] Core workflow (e.g., create item → invite team → view together) works without tutorial
- [ ] Error messages are specific: not "Error 500", but "Failed to save: name is required"
- [ ] Loading states visible (spinners, skeleton screens)
- [ ] Form validation clear (client-side + server-side)
- [ ] Empty states have helpful copy

### Data & Privacy
- [ ] Privacy policy and ToS live on site
- [ ] GDPR/CCPA compliance: data export, deletion workflows built
- [ ] Database backups automated (daily snapshots, 30-day retention)
- [ ] Audit logging for sensitive actions (user added to org, permissions changed)

### Business
- [ ] Revenue flow tested (subscription purchase → stripe webhook → db flag → gated feature works)
- [ ] Analytics firing: track signup, first action, invitation sent, paid conversion, churn
- [ ] Support process defined (email ticketing or Intercom chat)
- [ ] Pricing page live with clear feature matrix

---

## Tech Stack Rationale

### Web (Next.js + React)
- **Next.js:** Built-in SSR, API routes, instant static exports, excellent DX
- **React:** Largest ecosystem; easy to hire; 1000+ UI libraries
- **TypeScript:** Catches bugs before runtime; improves IDE support
- **Tailwind CSS:** Rapid prototyping; consistent design tokens
- **SWR or TanStack Query:** Data fetching + caching; automatic stale-while-revalidate
- **Prisma or TypeORM:** Type-safe database queries; auto-migrations

**Alternatives:** Vue + Nuxt (smaller ecosystem), Svelte (smaller team base)

### Database (PostgreSQL)
- **PostgreSQL:** ACID compliance; excellent for financial/SaaS data; scales to billions of rows
- **Row-level security (RLS):** Native multi-tenant isolation at DB level
- **JSONB columns:** Flexible schema for nested data; queryable + indexable
- **Listen/Notify:** Pub/Sub for real-time features without external message queue

**Alternatives:** MySQL (similar but RLS is weaker), MongoDB (lose ACID guarantees)

### Cache (Redis)
- **Session store:** JWT validation cache; user permissions
- **Real-time presence:** Who's online, typing indicators
- **Rate limiting:** Track login attempts, API quota
- **Feature flags:** Quick rollout without deploy

### Hosting
- **Recommended:** Vercel (for Next.js, auto-deploys on git push, edge functions) or Railway/Render (full-stack)
- **Database:** Managed PostgreSQL (Supabase, Railway, Neon) — avoid self-hosted
- **Storage:** AWS S3 or Cloudflare R2

---

## Sample Feature Roadmap (16 weeks to Tier 3)

### Tier 1 (Weeks 1–6): Desktop Web MVP
- Auth (email/password, OAuth)
- Core feature (user creates/edits content)
- Team invite system (email-based)
- Basic sharing (view-only or edit)
- Desktop web launch
- Stripe integration for subscription

### Tier 2 (Weeks 5–8 parallel): Mobile Web PWA + Growth
- Mobile PWA (responsive design)
- Offline sync (Service Worker + IndexedDB)
- Push notifications (web push API)
- Basic analytics dashboard

### Tier 3 (Weeks 9–18): iOS + Retention & Features
- Audit logging (who changed what)
- Advanced permissions (roles: owner, editor, viewer)
- Bulk operations (CSV import/export)
- Native iOS app launch (Code reuse from web backend)

### Tier 4 (Weeks 19–28): Android + Scale
- Native Android app
- Advanced reporting (charts, custom reports)
- Automation/webhooks (trigger actions on events)
- Single Sign-On (SAML for enterprise)
- Desktop app (Electron, optional)

---

## Known Pitfalls & How to Avoid

| Pitfall | Why It Hurts | Mitigation |
|---------|---|---|
| **Shipping with sync bugs** | Multi-tenant data corruption; user trust destroyed | Test conflict resolution thoroughly; real-time sync testing framework |
| **Ignoring mobile early** | Desktop works, mobile feels broken; poor adoption | Responsive design from day 1; test on real devices weekly |
| **No audit logging** | Can't debug issues; SOC 2 compliance fails | Log all state changes with user ID + timestamp from day 1 |
| **SQL injection or XSS** | Data breach; regulatory fines | Use parameterized queries + ORM; sanitize all user input |
| **No backup strategy** | Data loss = business failure | Automated daily backups + monthly restore tests |
| **Scaling database too late** | Slow queries tank performance; customer churn | Index join columns early; use EXPLAIN ANALYZE |
| **Building native too early** | Slow MVP; native code duplicates logic | Max out web first; native comes after web is stable |

---

## Checklist for Tier 1 MVP Launch

- [ ] Web app deployed to production (Vercel, Railway, or similar)
- [ ] Custom domain configured with HTTPS
- [ ] Database (PostgreSQL) running with backups enabled
- [ ] Redis cache deployed and integrated
- [ ] Stripe account connected; subscription billing working
- [ ] Auth flow tested end-to-end (signup, login, logout, password reset)
- [ ] Core feature works without errors (create, edit, delete, view)
- [ ] Team invite system tested (send invite, accept, permissions enforced)
- [ ] Permissions tested (user A can't see user B's private data)
- [ ] API tested for N+1 queries and slowness
- [ ] Error handling: no 500 errors on client, all errors logged server-side
- [ ] Analytics integrated (Mixpanel, Segment, or custom)
- [ ] Error tracking (Sentry or equivalent) set up
- [ ] Privacy policy and ToS published
- [ ] Support email or chat live (@yourcompany.com or Intercom)
- [ ] Real users (friends, beta testers) can sign up and use core feature
- [ ] Browser testing passed (Chrome, Firefox, Safari, mobile Safari)
- [ ] Load testing: 100 concurrent users, API stays responsive
