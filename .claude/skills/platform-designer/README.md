# Software Platform Architect

Turn an app idea into a platform architecture plan you can build from. Describe what you want to make, and Software Platform Architect recommends which platform to ship first, whether to go native or cross-platform, and a tier-by-tier rollout. The plan includes timelines scaled to your team, and each later tier waits on a measurable gate instead of a date. Compliance items that change your architecture are built into the launch checklist.

## What you get

- **A recommendation from six templates:** Mobile-First, Web-First, iOS-First, Android-First, Desktop-First, or Browser Extension. Ideas that don't fit one template, like marketplaces, hardware companion apps, API products, or web-only tools, get a named combination.
- **An implementation approach:** native, cross-platform (React Native/Expo, Flutter, Kotlin Multiplatform), web-wrapped, or desktop cross-platform, chosen for your team.
- **A platform table** with estimated timelines. The timelines are labelled as estimates and scaled to your team size. When you don't give a team size, the plan assumes one part-time developer.
- **Release gates for launch**, plus the metric that should trigger each later tier.
- **Compliance built into the gates** when your data calls for it:
  - HIPAA and business-associate obligations
  - the FTC Health Breach Notification Rule
  - GDPR, and India's DPDP Act
  - PCI
  - COPPA
  - SOC 2
  - crisis protocols for mental-health apps
  - deletion vs record-retention rules
  - licensing for regulated goods
- **An Assumptions → Decisions table**, so you can spot a wrong guess and see what it changes.
- **An offer to compare two or more alternative architectures** side by side.

## How to use it

In Claude, describe a new app idea, or ask "what platforms should I build first?" In Claude Code you can also call it directly:

```
/software-platform-architect:platform-designer A habit tracker for two React developers, shipping in 3 months
```

It asks up to three questions at a time. To skip them, say "don't ask questions", and it infers conservative defaults and lists every assumption it made.

## What it runs and sends

Software Platform Architect is instructions only:
- **No code:** it runs no scripts, hooks, or MCP servers.
- **No network or storage:** it makes no network requests and stores no data.
- **What Claude reads:** Claude reads the skill's own template files from this folder to build the plan.
- **The `evals/` folder:** it contains optional developer tooling, prompts and a test runner that compares the skill against a no-skill baseline. The plugin never runs it. A developer runs it by hand to measure quality.

## Limits

- **Compliance:** the guidance covers architecture only and isn't legal advice. The plan tells you to confirm your approach with counsel.
- **Timelines and thresholds:** these are estimates and suggested starting values, not guarantees.
- **Out of scope:** games, embedded firmware, and smart-TV-first products fall outside the templates. For those it gives only general platform-order guidance.

## License

MIT. See [LICENSE](LICENSE).
