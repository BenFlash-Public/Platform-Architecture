# Running the platform-designer evals

`run_evals.py` runs each scenario in `evals.json` twice, once **with the skill** and once as a **baseline with no skill**, using the same model and settings. It then grades every answer in a **separate call**. The grader sees only the user prompt, the answer, and the assertions. It never sees the skill text, the other answer, or which variant it's grading.

## Two ways to run it

| Backend | Pays with | How the skill is loaded |
|---|---|---|
| `--backend cli` (default) | Your **Claude subscription's usage limits**, via Claude Code headless mode (`claude -p`). No API bill | Skill run: `/platform-designer <prompt>` from the repo root, exactly as you'd use it. Baseline: an empty temp folder with all skills disabled |
| `--backend api` | Claude API credits, billed per token | The skill (SKILL.md + templates) is passed to the model as its system prompt |

Use the default `cli` backend unless you want API billing.

## What gets checked

- **Per-eval assertions**: the scenario-specific checks (e.g., "flags cottage food laws").
- **Common assertions** (`common_assertions`): rule checks applied to every plan. They cover:
  - no unsourced numbers
  - no unverified vendor compliance claims
  - no internal contradictions
  - tier/timeline consistency
  - platform consistency
  - the solo-developer default
  - current facts
- **Assertion kinds:**
  - **format**: the skill's own output shape and scope (assumptions table, closing question, "games are out of scope"). Baselines are expected to miss these.
  - **substance**: correctness and safety. This is the comparison that matters. The skill should beat the baseline here.
- **Prompt modes:**
  - Each prompt includes scripted answers (eval 1) or ends with "Don't ask questions; infer anything missing."
  - Every run should therefore produce a plan, and an answer that stops at questions fails `plan_produced`.

## Setup (CLI backend, one time)

1. **Install Claude Code.** Follow [code.claude.com](https://code.claude.com/docs/en/overview), or check whether you already have it with `claude --version`.
2. **Check how Claude Code is logged in.** Run `claude`, then type `/status`.
   - It must show your **Claude subscription** (Pro/Max).
   - If it shows an API key or Console account, runs are billed to that account instead.
   - Also make sure `ANTHROPIC_API_KEY` isn't exported in your shell. If it is, run `unset ANTHROPIC_API_KEY`.
3. **Check your branch.** Work from the repo root, on a branch that contains this skill.

No Python packages are needed for the CLI backend.

## Run

Run from the repository root.

1. **Preview the prompts** (no model calls):
   ```bash
   python3 .claude/skills/platform-designer/evals/run_evals.py --dry-run
   ```
2. **Try one eval first** to see how much of your usage it takes:
   ```bash
   python3 .claude/skills/platform-designer/evals/run_evals.py --ids 8
   ```
3. **Run all 8:**
   ```bash
   python3 .claude/skills/platform-designer/evals/run_evals.py
   ```
4. **Check variance** before trusting a result:
   ```bash
   python3 .claude/skills/platform-designer/evals/run_evals.py --runs 3
   ```
5. **Re-run specific evals after a fix:**
   ```bash
   python3 .claude/skills/platform-designer/evals/run_evals.py --ids 3 4 --runs 3
   ```

## Usage limits (CLI backend)

- **Size of one run:** a full run is 16 generations + 16 gradings, all counted against your plan's usage limits.
  - Each skill run loads the skill (~26k tokens).
  - Opus uses limits faster than Sonnet.
- **If you hit a limit:**
  - Use `--gen-model sonnet --grader-model sonnet`.
  - Run a few ids at a time (`--ids 1 2 3`).
  - Keep `--workers` at 1 (the default).
- **The `notional_cost_usd` numbers in `results.json`** are what the same calls would cost on the API. On a subscription they're not billed; they're just a size gauge.

## Options

| Flag | Default | Purpose |
|---|---|---|
| `--backend` | `cli` | `cli` = subscription via Claude Code; `api` = billed API |
| `--runs N` | 1 | Runs per variant. Output varies; 3+ shows whether a pass is stable |
| `--ids ...` | all | Only run these eval ids |
| `--gen-model` | CLI default (`api`: `claude-opus-5`) | Model that writes the plans. CLI accepts aliases like `sonnet`, `opus` |
| `--grader-model` | CLI default (`api`: `claude-opus-5`) | Model that grades |
| `--effort` | CLI default (`api`: `high`) | Generator effort level |
| `--workers` | 1 (`api`: 4) | Parallel jobs. The CLI backend runs one at a time by default to stay under subscription rate limits |
| `--no-baseline` | off | Skip the no-skill baseline |
| `--dry-run` | off | Write prompts only; no model calls |

## Output

Each run creates `evals/results/<timestamp>/` (git-ignored) containing:

| File | Contents |
|---|---|
| `report.md` | Summary table + per-assertion table with the grader's evidence. Paste the Summary table into the PR |
| `answers/eval<N>-<variant>-run<R>.md` | Raw answers |
| `grades/eval<N>-<variant>-run<R>.json` | Per-assertion verdicts and quoted evidence |
| `results.json` | Everything: tools used, whether the skill loaded, token usage |

## Reading the results

- **The skill is doing its job** when:
  - Skill substance pass rates are high.
  - They're clearly above the baseline.
  - They're stable across runs.
- **Contaminated runs:** the report warns if a skill run didn't load the skill, or if a baseline could see it. Treat those rows as invalid.
- **Verdicts:**
  - `unsure` means the grader couldn't verify something (e.g., whether a URL resolves), so a person should check it.
  - A missing verdict counts as `fail`.
- **Spot-check the grader.** Read 2–3 answers yourself and compare with the grader's evidence. If the grader is lenient, tighten the assertion wording in `evals.json`; don't loosen the skill.
- **When to fix the skill:** only when a failure repeats across runs, not after a single bad sample.

## Posting to the PR

1. Copy the **Summary** table from `report.md`.
2. Add a line with the commit SHA you tested:
   ```bash
   git rev-parse --short HEAD
   ```
3. Post both as a comment on the PR, then list any assertion that failed in 2 or more runs as a follow-up fix.

## Limits

- **Your own Claude Code setup applies (CLI backend):** your user-level `CLAUDE.md` and other skills apply to both variants and the grader.
  - The comparison stays fair, because both sides get the same setup.
  - Results do reflect your setup, not a clean one.
- **The skill is invoked explicitly (CLI backend):** it's called with `/platform-designer`, so this tests its instructions, not whether Claude Code would pick it on its own.
- **The grader has no web access:** it checks facts from its own knowledge and marks what it can't verify as `unsure`.
- **Writer and grader are both Claude:** that means they can share blind spots.
  - A grader from another model family would be more independent, e.g. Gemini on its free tier.
  - That isn't built in yet.
