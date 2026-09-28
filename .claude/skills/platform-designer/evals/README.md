# Running the platform-designer evals

`run_evals.py` runs each scenario in `evals.json` twice, once **with the skill** and once as a **baseline with no skill**, using the same model and settings. It then grades every answer in a **separate API call**. The grader sees only the user prompt, the answer, and the assertions. It never sees the skill text, the other answer, or which variant it's grading.

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
  - **format**: the skill's output shape (assumptions table, closing question). Baselines are expected to miss these, so judge them separately.
  - **substance**: correctness and safety. This is the comparison that matters. The skill should beat the baseline here.
- **Prompt modes:**
  - Each prompt either includes scripted answers (eval 1) or ends with "Don't ask questions; infer anything missing."
  - Every run should therefore produce a plan, and an answer that stops at questions fails `plan_produced`.

## Setup (one time)

1. Use Python 3.10 or newer.
2. Install the SDK:
   ```bash
   pip install anthropic
   ```
3. Provide credentials, using one of:
   - `export ANTHROPIC_API_KEY=...`
   - `ant auth login`

## Run

Run from the repository root.

1. **Preview without spending anything.** This writes the exact prompts to `evals/results/<timestamp>/`:
   ```bash
   python3 .claude/skills/platform-designer/evals/run_evals.py --dry-run
   ```
2. **Run all 8 evals, 1 run each, with the baseline:**
   ```bash
   python3 .claude/skills/platform-designer/evals/run_evals.py
   ```
3. **Check variance (recommended before trusting a result):**
   ```bash
   python3 .claude/skills/platform-designer/evals/run_evals.py --runs 3
   ```
4. **Re-run specific evals after a fix:**
   ```bash
   python3 .claude/skills/platform-designer/evals/run_evals.py --ids 3 4 --runs 3
   ```

## Options

| Flag | Default | Purpose |
|---|---|---|
| `--runs N` | 1 | Runs per variant. Model output varies; 3+ shows whether a pass is stable |
| `--ids ...` | all | Only run these eval ids |
| `--gen-model` | `claude-opus-5` | Model that writes the plans |
| `--grader-model` | `claude-opus-5` | Model that grades. A different model (e.g., `claude-fable-5-1`) reduces shared blind spots between writer and grader |
| `--effort` | `high` | Generator effort level |
| `--workers` | 4 | Parallel requests; lower it if you hit rate limits |
| `--no-baseline` | off | Skip the no-skill baseline |
| `--dry-run` | off | Write prompts only; no API calls |

## Cost

This is a rough estimate from prompt sizes, not a measured cost:
- **Size of each call:**
  - The skill system prompt is ~26k tokens; it's cached after the first call.
  - Each answer is a few thousand tokens plus thinking.
- **Estimated total:**
  - One full run (8 evals × 2 variants + 16 gradings) with Opus 5 is on the order of **$5–10**.
  - `--runs 3` is roughly 3×.
- **Measuring it yourself:** check actual usage in `results.json` (`usage` per call) after a small run such as `--ids 1`.

## Output

Each run creates `evals/results/<timestamp>/` (git-ignored) containing:

| File | Contents |
|---|---|
| `report.md` | Summary table + per-assertion table with the grader's evidence. Paste the Summary table into the PR |
| `answers/eval<N>-<variant>-run<R>.md` | Raw answers |
| `grades/eval<N>-<variant>-run<R>.json` | Per-assertion verdicts and quoted evidence |
| `results.json` | Everything, including token usage and request IDs |

## Reading the results

- **The skill is doing its job** when:
  - Skill substance pass rates are high.
  - They're clearly above the baseline.
  - They're stable across runs.
- **Verdicts:**
  - `unsure` means the grader couldn't verify something (e.g., whether a URL resolves), so a person should check it.
  - A missing verdict counts as `fail`, never as a silent pass.
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

- **Setup differs from real use:** the skill is given to the model as its system prompt. That tests the skill's instructions, not whether Claude Code triggers the skill or reads the template files on its own.
- **The grader has no web access:** it checks facts from its own knowledge and marks what it can't verify as `unsure`.
- **No automatic fallback:** the script doesn't use server-side model fallbacks, because a fallback would silently change the model under test. A refusal shows up as a failed or empty answer in the report.
