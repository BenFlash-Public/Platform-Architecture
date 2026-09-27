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

## Step 2: Adaptive Interview

Ask only the questions that unlock the next decision. Don't ask all 6 — ask the ones that matter.

**ISOLATION FALLBACK:** If running in a non-interactive context (agent, batch, no follow-up interaction expected), skip Step 2 and proceed directly to Step 3 using inferred answers from the intake. Infer conservatively and note all assumptions in the final output (e.g., "Assuming solo developer, no explicit revenue model stated → freemium" or "Users not specified → mobile-first for consumer apps, web-first for B2B").

**Core questions** (ask in order, skip if already answered):

1. **First Platform** — "Given your users, which device/platform do you imagine them using first? Mobile phone, desktop web, native app, or are you genuinely uncertain?"
   - Their answer may guide platform choice (iOS-first vs web-first vs Android-first)

2. **Technical Comfort & Team** — "What's your team's technical background? Are they comfortable building native iOS/Android, or do you prefer web/cross-platform to move faster?"
   - Informs: native vs React Native vs Electron vs web

3. **Revenue Model** — "How are you planning to make money? (Default: freemium, but could be subscription SaaS, one-time purchase, or ads)"
   - Informs: release strategy, platform priority, monetization gating

4. **Timeline** — "When do you want to ship the first version? (MVP in weeks, months, or years?)"
   - Informs: build vs buy, MVP scope, platform sequencing

5. **Cross-Platform Sync** — "Do users need to access and sync the same data across multiple devices? (yes = cross-platform sync, no = multi-platform independent apps)"
   - Informs: backend complexity, which template (mobile-first vs multi-platform)

6. **Online/Offline** — "Does your app need to work offline? Or is it always-online?"
   - Informs: local-first architecture, database choices, sync protocol complexity

**Adaptive branching:**
- If the app is clearly B2B SaaS (CRM, project tool, data dashboard), skip #1 (desktop web is obvious) and focus on #2, #3, #5.
- If they say "mobile users first," focus on mobile-first template and ask #2, #3, #5 (timeline and sync).
- If they're unsure about everything, ask all 6 to build context.
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

**If none of the above fit** (e.g., web-only, CLI tools, APIs, games, hardware-paired apps):
- Combine two templates: e.g., "Web-First with optional Desktop (Electron)" or "Mobile-First with Browser Extension"
- Or ask follow-up clarification questions to narrow the decision

## Step 4: Fill In

Once you've recommended a template, provide:

1. **Empty Template** — Show the structure of the recommended template so they know what they're getting
2. **Filled-In Example** — Complete the template with their app's details at the appropriate detail level:

**Detail Level Guidance:**
- **Medium Detail** (default, unless user asked for "detailed" or "comprehensive" upfront):
  - Narrative summary (2–3 paragraphs: why this architecture fits their constraints)
  - Platform status table (with their app name, estimated timeline, tech stack)
  - Tier 1–2 architecture summary (why these platforms, why this order)
  - Key architectural decisions (sync needs, offline, database approach)
  - 2–3 critical release gates for Tier 1
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

Highlight what changes (e.g., "iOS-first reaches premium users faster but at 30% smaller addressable market than web-first").

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

### 2. Recommended Template (Empty)
Show the platform status table structure from the recommended template so they see the roadmap shape.

### 3. Filled-In Plan
Complete plan with their app's name, timeline, Tier 1–5 platforms, and key architectural decisions.

### 4. Exploration Question
Ask if they want to compare alternatives. If yes, show 2–3 side-by-side options. If no, you're done.

---

## Key Principles

- **Adaptive, not rigid.** Ask only the questions that unlock the next decision. If they've already answered, move on.
- **Generalize from their constraints.** Their budget, team, timeline, and user base are the *why* behind every recommendation. Explain it.
- **No platform is "better."** Native iOS is not better than web; it's different. Your job is to match the right platform to their constraints.
- **Sync is a game-changer.** Cross-platform sync fundamentally changes architecture complexity. Ask about it directly.
- **Show tradeoffs.** If they ask "but what about [other platform]?", show the real cost: timeline, complexity, money, maintenance burden.
