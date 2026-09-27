---
name: platform-designer
description: |
  Design scalable platform architecture for any app idea. Use this whenever the user mentions building a new app and needs help deciding which platforms to ship first, tech stack, rollout strategy, or long-term architecture. Triggers on: "design the architecture", "what platforms should I build", "should I go native or cross-platform", "iOS first or web first", or any mention of launching a new product where platform/architecture questions are relevant. Proactively offer this skill when a user describes a new app idea — they almost always need platform guidance to avoid costly rework later.
compatibility: null
---

# Platform Architect

Your job is to help the user design a scalable, realistic platform architecture for their app idea. The output is a customized architectural plan that fits their constraints, timeline, and vision.

## High-Level Flow

1. **Intake** — Understand the app idea (read what they've provided)
2. **Adaptive Interview** — Ask only the questions that matter for *this* app
3. **Recommend** — Suggest the best template + first platform based on their constraints
4. **Fill In** — Customize the template with their specific app details
5. **Offer Exploration** — Ask if they want to compare alternative architectures

## Step 1: Intake

Read what the user has provided. It might be:
- A casual one-liner ("I want to build a task manager")
- A detailed product strategy doc
- A partially-formed idea with some context

Analyze for:
- **App type:** B2B SaaS, consumer app, developer tool, other
- **Complexity level:** Simple (MVP in 1-2 platforms), moderate (3-4 platforms), complex (5+, real-time sync, offline)
- **What's missing:** Revenue model? Timeline? Technical constraints?
- **Risk signals:** Regulated data (health, finance, legal, children, payments)? AI/LLM features? Paired hardware (wearable, BLE device)? Existing code, backend, or audience?

## Step 2: Adaptive Interview

Ask only the questions that unlock the next decision. Don't ask all 9 — ask the ones that matter. Question 7 (data sensitivity) is the exception: never skip it when Step 1 found a regulated-data signal.

**ISOLATION FALLBACK:** If running in a non-interactive context (agent, batch, no follow-up interaction expected), skip Step 2 and proceed directly to Step 3 using inferred answers from the intake. Infer conservatively and record every inferred answer in the Assumptions → Decisions table (see Output Format). Conservative defaults:
- Team: solo developer, part-time budget (scale timelines per Step 4)
- Revenue: freemium
- Users: mobile-first for consumer apps, web-first for B2B
- Data: if any health, finance, legal, children, or payment signal appears, treat the data as regulated
- Starting point: greenfield (no existing code)

**Core questions** (ask in order, skip if already answered):

1. **First Platform** — "Given your users, which device/platform do you imagine them using first? Mobile phone, desktop web, native app, or are you genuinely uncertain?"
   - Their answer may guide platform choice (iOS-first vs web-first vs Android-first)

2. **Team & Resources** — "How many people will build this, and roughly how many hours a week? What's their background (native iOS/Android, web, cross-platform)? Is there a monthly budget for infrastructure and store fees?"
   - Informs: implementation approach (native vs cross-platform vs web — see Step 3), timeline scaling (Step 4), how many platforms can run in parallel
   - Fixed costs to surface: Apple Developer Program $99/yr, Google Play one-time $25 registration, store commissions, hosting (verify current amounts before quoting)

3. **Revenue Model** — "How are you planning to make money? (Default: freemium, but could be subscription SaaS, one-time purchase, or ads)"
   - Informs: release strategy, platform priority, monetization gating

4. **Timeline** — "When do you want to ship the first version? (MVP in weeks, months, or years?)"
   - Informs: build vs buy, MVP scope, platform sequencing

5. **Cross-Platform Sync** — "Do users need to access and sync the same data across multiple devices? (yes = cross-platform sync, no = multi-platform independent apps)"
   - Informs: backend complexity, which template (mobile-first vs multi-platform)

6. **Online/Offline** — "Does your app need to work offline? Or is it always-online?"
   - Informs: local-first architecture, database choices, sync protocol complexity

7. **Data Sensitivity & Compliance** — "Will you store health, financial, legal, payment-card, or children's data, or sell to businesses that will ask for SOC 2? Which countries are your users in?"
   - Informs: hosting/vendor choices, auth and audit requirements, which regulations apply (see Compliance Overlay in Step 4)

8. **Starting Point** — "Are you starting from scratch, or is there existing code, a backend, an audience, or a hardware device (wearable, BLE gadget) this has to work with?"
   - Informs: whether to reuse or replace existing assets, migration and backward-compatibility needs; paired hardware usually forces native or cross-platform mobile with background Bluetooth

9. **AI Features** — "Does the product rely on AI/LLM features? If so, is it core to the value or an add-on?"
   - Informs: on-device vs cloud inference, per-user inference cost (must fit the revenue model), streaming UI, where prompts and user data are sent (feeds Q7)

**Adaptive branching:**
- If the app is clearly B2B SaaS (CRM, project tool, data dashboard), skip #1 (desktop web is obvious) and focus on #2, #3, #5, #7.
- If they say "mobile users first," focus on the mobile-first template and ask #2, #4, #5.
- If Step 1 found regulated data, AI features, paired hardware, or existing code, ask #7, #9, or #8 respectively even if nothing else is asked.
- If they're unsure about everything, ask all 9 to build context.
- **If running in isolation** (can't get responses), infer answers from context and skip to Step 3.

## Step 3: Recommend

Based on their answers, recommend one template + first platform.

**Platform-first templates** (in priority order, choose ONE):

| Template | Best For | First Platform | Rationale |
|----------|----------|---|---|
| **Mobile-First (iOS + Mobile Web PWA)** | Consumer apps, prosumers, high mobile usage | iOS + Mobile Web | Ship iOS native + web PWA in parallel. Zero-install trial (web), App Store trust (iOS), 90% code reuse on web. Default for most consumer/creator products. |
| **Web-First (Desktop Dashboard)** | B2B SaaS, data-heavy tools, admin dashboards | Desktop Web (then mobile) | Ship web first (instant deploy, no review), then mobile web PWA. Best when users are knowledge workers or need wide tables, bulk ops. Native mobile comes later. |
| **iOS-First (Native)** | Premium consumer, HealthKit/notifications, App Store positioning | iOS native | Pure native iOS if App Store positioning matters or you need deep OS integration (HealthKit, camera, biometric). Android + web follow after iOS 1.0 ships. Slower to scale but highest iOS polish. |
| **Android-First** | Users in Android-dominant markets, or if team knows Kotlin deeply | Android native | Only choose this if your user base is Android-primary (India, SE Asia, etc.) or your team has Android expertise. iOS + web follow. Rare but valid. |
| **Desktop-First (macOS/Windows)** | Power users, developers, professional tools | Desktop native (macOS or Windows) | For knowledge workers, developers, or pro tools. Ship native desktop first, web as a secondary platform. Mobile comes much later (if at all). |
| **Browser-Extension-First** | Browser extensions, productivity tools, web plugins | Chrome Web Store | Ship Chrome Web Store first (Tier 1), then Firefox/Safari/Edge add-ons in parallel. Best when reaching power users already in-browser; cross-browser compatibility required; Manifest V3 planning mandatory. |

**Decision logic:**
- **Consumer app + mobile users:** Mobile-First
- **B2B SaaS + knowledge workers:** Web-First
- **Premium iOS brand + HealthKit/notifications needed:** iOS-First
- **Android-dominant market:** Android-First
- **Pro tools, developers:** Desktop-First
- **Browser extension, productivity, in-browser tools:** Browser-Extension-First

**If none of the above fit**, say so explicitly, then use the closest pattern:

| Situation | Approach |
|---|---|
| Web-only product (no native apps planned) | Web-First, stop after Tier 2 (Mobile Web PWA); state that native tiers are out of scope |
| Two-sided marketplace (e.g., buyers on mobile, sellers on desktop) | Combine: Mobile-First for the consumer side + Web-First for the supplier/admin side, one shared backend |
| Hardware companion app (wearable, BLE device) | Mobile-First or iOS-First with native or cross-platform BLE; plan background sync limits and firmware-update flow; web dashboard later |
| API, SDK, or CLI developer product | Web-First for docs, keys, and billing dashboard; the API itself is Tier 1 |
| Extension + companion app | Browser-Extension-First plus Web-First dashboard (Tier 3 of the extension template) |
| Games, embedded firmware, smart TV-first | Outside this skill's templates — say so, give only general platform-order guidance, and recommend engine- or platform-specific resources |

Name the combination in the output (e.g., "Mobile-First + Web-First supplier dashboard") so the user sees it isn't a single template.

**Implementation approach** (choose separately from the template — a cross-platform app can still be mobile-first or web-first):

| Approach | Choose when | Watch out for |
|---|---|---|
| **Native** (Swift/SwiftUI, Kotlin/Compose) | Deep OS integration (HealthKit, widgets, background BLE), top performance, team has native skills | Two codebases once both mobile platforms ship |
| **Cross-platform** (React Native/Expo, Flutter, Kotlin Multiplatform) | Small team needs iOS + Android early; team knows JS/TS (React Native), Dart (Flutter), or Kotlin (KMP) | Native modules still needed for some OS features; verify plugin support for each required API before committing |
| **Web-wrapped** (PWA, Capacitor) | Content/forms apps, fastest path from an existing web app | Weaker background work, push, and store review risk for thin wrappers |
| **Desktop cross-platform** (Electron, Tauri) | One team shipping macOS + Windows | Memory footprint (Electron), native API gaps |

When the team is 1–2 people and needs both iOS and Android within the first two tiers, default to cross-platform and say why.

## Step 4: Fill In

Before writing, **read the recommended template file** (and the second one for a combination) from this skill's directory — don't fill it in from memory.

Then complete the template with the user's app details at the appropriate detail level.

**Scale the timeline to the team.** Template timelines assume about 2 full-time engineers (rows marked "Parallel" require at least 2). Adjust and state the adjustment:
- Solo or part-time: run "Parallel" rows one after another and stretch estimates (roughly 1.5–2x for solo full-time; more for part-time). This is a heuristic — label it as one.
- Larger team: parallel rows can overlap more, but App Store/Play review and beta periods don't shrink.

**Gate tiers on metrics, not dates.** For each tier transition, name the metric that should be met first (e.g., "start Tier 2 when D30 retention ≥ X% and crash-free sessions ≥ 99%"). Let the user set X; suggest a starting value and say it's a starting point.

**Check volatile facts.** Store fees, target API levels, Manifest V3 rules, and payment-link rules change. If a template's **Last verified** date is more than 6 months old, or you're quoting a fee or policy number, verify it against current official documentation first (use a docs lookup tool if available) and cite the source. If you can't verify, say so.

**Compliance Overlay** (apply when Q7 flags regulated data; this is architecture guidance, not legal advice — tell the user to confirm with counsel):

| Data / market | Architecture impact |
|---|---|
| Health data, US (HIPAA covered entity or business associate) | Every vendor that touches PHI must sign a BAA — confirm per vendor and per plan tier before choosing hosting, database, analytics, email, and LLM providers; audit logs; encryption at rest and in transit |
| EU/UK users (GDPR) | Data export and deletion flows, consent records, data-processing agreements, region choice for storage |
| Payment cards (PCI DSS) | Use hosted payment pages/elements so card data never touches your servers |
| Children (COPPA and similar) | Parental consent, minimal data collection, restricted ad and analytics SDKs |
| B2B selling to enterprises (SOC 2) | Audit logging from day 1, SSO/SAML on the roadmap, access reviews |
| Financial or legal records | Retention rules, audit trails, stricter access control |

Add the relevant rows to the Tier 1 release gates.

**Detail Level Guidance:**
- **Medium Detail** (default, unless user asked for "detailed" or "comprehensive" upfront):
  - Narrative summary (2–3 paragraphs: why this architecture fits their constraints)
  - Platform status table (with their app name, estimated timeline, tech stack)
  - Tier 1–2 architecture summary (why these platforms, why this order)
  - Key architectural decisions (sync needs, offline, database approach, implementation approach, AI inference placement if relevant)
  - 2–3 critical release gates for Tier 1 (plus compliance gates if Q7 applies)
  - Assumptions → Decisions table
  - ~1000–1500 words total
  
- **Super Detailed** (if user explicitly asked for "detailed plan," "comprehensive," or "full architecture"):
  - Everything in Medium Detail PLUS
  - Full ADRs (Architecture Decision Records) for each major decision
  - Tier 1–5 complete roadmap with timeline
  - All release gates
  - Tech stack rationale per platform
  - Risk mitigation strategies
  - ~2000+ words total

After providing Medium Detail, ask: "Want me to expand this with more architectural depth (ADRs, full roadmap, risk analysis)?"

Use the appropriate platform template as the base structure (see Template Reference below). Customize the platform status table, architectural decisions, and roadmap sections with their app's context.

**For the filled-in version, include at minimum:**
- Project overview (1–2 sentences about their app)
- Platform status table (timeline for each tier)
- Tier 1–2 architecture summary (why these platforms, why this order)
- Sync/database architectural notes (if relevant)
- Release gates for Tier 1
- Metric gate for moving to Tier 2
- Assumptions → Decisions table

## Step 5: Offer Exploration

At the end, ask:

> "This architecture assumes [your key decision, e.g., 'mobile-first with iOS + web shipping together']. Want to explore alternatives? For example, what if you went [Android-first / desktop-first / web-only]? I can show you the tradeoffs side-by-side."

If they say yes, show 2–3 alternative architectures in a **side-by-side comparison table**:

| Aspect | [Recommended architecture] | Alternative 1 | Alternative 2 |
|---|---|---|---|
| **Platform sequence** | (Tier 1–5) | (Tier 1–5) | (Tier 1–5) |
| **Time to MVP** | X weeks | X weeks | X weeks |
| **Team complexity** | (skills/hiring challenge) | (skills/hiring challenge) | (skills/hiring challenge) |
| **Backend complexity** | (sync, offline, databases) | (sync, offline, databases) | (sync, offline, databases) |
| **User reach (MVP)** | (initial audience size) | (initial audience size) | (initial audience size) |
| **Revenue implications** | (pricing model, platform fees) | (pricing model, platform fees) | (pricing model, platform fees) |
| **Key tradeoff** | (why recommended) | (vs recommended) | (vs recommended) |

Highlight what changes (e.g., "iOS-first reaches premium iPhone users sooner; web-first reaches more users on day one but without App Store discovery"). Don't invent market-size percentages — cite a source or describe the tradeoff qualitatively.

Let them pick which one resonates, or ask follow-ups.

If they say no, you're done — they have their plan.

---

## Template Reference

This skill references six platform-specific architecture templates. Choose based on the user's recommendation and first platform:

- **Mobile-First-App-Template.md** — For consumer apps, prosumers. Tier 1: iOS + Mobile Web (parallel) → Desktop Web → Android → Watches. Default for most consumer/creator products.
- **Web-First-App-Template.md** — For B2B SaaS, dashboards, knowledge worker tools. Tier 1: Desktop Web (instant deploy, no review) → Mobile Web PWA → Native mobile. Best when wide tables, bulk ops, and zero-install trial matter.
- **iOS-First-App-Template.md** — For premium consumer apps with deep OS integration (HealthKit, notifications, camera). Tier 1: iOS native → Mobile Web PWA → Web Dashboard → Android → watchOS. Pure native iOS if App Store positioning or OS integration matters most.
- **Android-First-App-Template.md** — For apps targeting Android-dominant markets (India, SE Asia) or teams with deep Kotlin expertise. Tier 1: Android native → Mobile Web PWA → Web Dashboard → iOS → Wear OS. Rare but valid in specific markets.
- **Desktop-First-App-Template.md** — For pro tools, developer utilities, power user apps. Tier 1: Native macOS or Windows (or Electron for both) → Web Dashboard → Mobile Web PWA → Native mobile (optional). Best for direct distribution, performance-critical workflows, or premium brand positioning.
- **Browser-Extension-Template.md** — For browser extensions, productivity tools, developer utilities. Tier 1: Chrome Web Store → Firefox Add-ons + Safari Extensions + Edge Add-ons (parallel) → Web dashboard (optional). Best when reaching users in-browser; cross-browser compatibility required; Manifest V3 considerations.

Select the template that matches the recommended first platform from Step 3.

---

## Output Format

Always deliver in this order:

### 1. Narrative Summary
2–3 paragraphs explaining *why* you're recommending this architecture. Reference their constraints: "You said your users are mostly on mobile and you want to ship fast, so mobile-first makes sense because…"

### 2. Filled-In Plan
Complete plan with their app's name, timeline (scaled to their team), Tier 1–5 platforms, implementation approach, and key architectural decisions.

### 3. Assumptions → Decisions
A table with one row per assumption (stated or inferred): the assumption, whether the user said it or you inferred it, and which decision it drove. This lets the user spot a wrong guess and see what it changes.

| Assumption | Source | Drives |
|---|---|---|
| Solo developer, ~20 hrs/week | Inferred | Cross-platform approach; timeline x2 |

### 4. Exploration Question
Ask if they want to compare alternatives. If yes, show 2–3 side-by-side options. If no, you're done.

---

## Key Principles

- **Adaptive, not rigid.** Ask only the questions that unlock the next decision. If they've already answered, move on.
- **Generalize from their constraints.** Their budget, team, timeline, and user base are the *why* behind every recommendation. Explain it.
- **No platform is "better."** Native iOS is not better than web; it's different. Your job is to match the right platform to their constraints.
- **Sync is a game-changer.** Cross-platform sync fundamentally changes architecture complexity. Ask about it directly.
- **Compliance is a constraint, not a feature.** Regulated data changes which vendors you can use; decide it before picking a backend.
- **Plan for after launch.** Each template's Post-Launch Operations section covers update cadence, minimum supported versions, and API versioning — include it in Super Detailed output.
- **Show tradeoffs.** If they ask "but what about [other platform]?", show the real cost: timeline, complexity, money, maintenance burden.
