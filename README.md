# Platform-Architecture

**platform-designer** is a Claude skill that turns an app idea into a platform architecture plan. It covers:
- which platforms to ship first
- native vs cross-platform
- a tier-by-tier rollout with metric gates
- the compliance items (HIPAA, GDPR, PCI, India's DPDP Act and more) that belong in the launch checklist

## Use it in Claude Code (plugin)

1. Add this repository as a plugin marketplace, then install the plugin:
   ```bash
   claude plugin marketplace add BenFlash-Public/Platform-Architecture
   claude plugin install platform-designer@benflash
   ```
2. Start a new Claude Code session, or run `/reload-plugins` in an open one.
3. Use it:
   - **Directly:** `/platform-designer:platform-designer <your app idea>`
   - **Automatically:** describe a new app idea, and Claude picks up the skill when platform or architecture questions come up.

Update or remove it later:
```bash
claude plugin marketplace update benflash
claude plugin uninstall platform-designer@benflash
```

Working inside this repository, the skill also loads as a project skill, so no install is needed there: use `/platform-designer`.

## Use it on claude.ai

1. Build the upload file:
   ```bash
   ./scripts/build-claude-ai-skill.sh
   ```
   This writes `dist/platform-designer.zip`, containing the skill and its templates; evals are left out.
2. In claude.ai, go to **Settings → Capabilities → Skills**, choose upload, and select `dist/platform-designer.zip`.
3. In a chat, describe your app idea, or ask for the platform-designer skill by name.

## Repository layout

| Path | What it is |
|---|---|
| `.claude/skills/platform-designer/SKILL.md` | The skill's instructions |
| `.claude/skills/platform-designer/*-Template.md` | Six architecture templates: Mobile-, Web-, iOS-, Android-, Desktop-first, and Browser Extension |
| `.claude/skills/platform-designer/.claude-plugin/plugin.json` | Claude Code plugin manifest |
| `.claude-plugin/marketplace.json` | Marketplace entry that makes the plugin installable from this repo |
| `.claude/skills/platform-designer/evals/` | Eval prompts, assertions, and a runner that compares the skill against a no-skill baseline. See its README |
| `scripts/build-claude-ai-skill.sh` | Builds the claude.ai upload zip |

## Status

- **Version:** 0.1.0.
- **Eval results so far:**
  - The skill scores about 80% on correctness checks vs about 53% without it (Sonnet, single runs; see PR #3).
  - The latest skill changes haven't been through a multi-run eval yet.
- **Compliance guidance:** it's architecture guidance, not legal advice. The skill tells users to confirm with counsel.
- **License:** MIT (see `LICENSE`).
