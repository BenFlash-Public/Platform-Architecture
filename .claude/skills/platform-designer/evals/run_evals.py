#!/usr/bin/env python3
"""Run the platform-designer evals with and without the skill, then grade blind.

For every eval in evals.json this script:
  1. Generates an answer WITH the skill.
  2. Generates a BASELINE answer with no skill (same model, same settings).
  3. Grades each answer in a separate call. The grader sees only the user
     prompt, the answer, and the assertions -- never the skill text, the other
     answer, or which variant it is grading.

Two backends:
  --backend cli (default): runs everything through Claude Code in headless mode
      (`claude -p`), so it uses your Claude subscription's usage limits instead of
      API billing. The skill run invokes /platform-designer in this repo; the
      baseline runs in an empty temp folder with all skills disabled.
  --backend api: calls the Claude API with the Anthropic SDK (billed per token).
      The skill run gets SKILL.md + templates as its system prompt.

Outputs land in evals/results/<timestamp>/: raw answers, per-answer grades,
results.json, and report.md (a Markdown table ready to paste into a PR).

Usage: see evals/README.md.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SKILL_DIR.parents[2]
CLI_TOOLS = "Read,Glob,Grep,Skill"
CLI_TIMEOUT = 1200  # seconds per claude -p call
EVALS_FILE = SKILL_DIR / "evals" / "evals.json"
TEMPLATES = sorted(SKILL_DIR.glob("*-Template.md"))

VERDICTS = ["pass", "fail", "na", "unsure"]

GRADE_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "verdict": {"type": "string", "enum": VERDICTS},
                    "evidence": {"type": "string"},
                },
                "required": ["id", "verdict", "evidence"],
                "additionalProperties": False,
            },
        },
        "notes": {"type": "string"},
    },
    "required": ["results", "notes"],
    "additionalProperties": False,
}


def skill_system_prompt(today: str) -> str:
    parts = [
        f"Today's date is {today}.",
        "The following skill is loaded. Follow its instructions for this request. "
        "Its template files are included after it; when the skill says to read a "
        "template file, use the text provided here.",
        "=== SKILL.md ===",
        (SKILL_DIR / "SKILL.md").read_text(),
    ]
    for t in TEMPLATES:
        parts += [f"=== {t.name} ===", t.read_text()]
    return "\n\n".join(parts)


def baseline_system_prompt(today: str) -> str:
    return f"Today's date is {today}. You are a helpful assistant."


def grader_system_prompt(today: str) -> str:
    return (
        f"Today's date is {today}. You are a strict, independent grader. "
        "You will see a user's request, an answer written by an AI assistant, and a list of assertions. "
        "Judge each assertion ONLY against the answer text.\n"
        "- pass: the answer clearly satisfies the assertion. Quote the supporting text as evidence.\n"
        "- fail: it does not, or it only partly does. Quote the offending text, or state what is missing.\n"
        "- na: only when the assertion itself says when it is N/A and that condition holds.\n"
        "- unsure: you cannot tell without information you don't have (e.g., whether a URL resolves). Explain why.\n"
        "Do not give credit for intent, and do not reward length. Check numbers, names, and dates skeptically: "
        "an invented figure, a wrong fact, or two statements that contradict each other is a fail. "
        "Return one result per assertion, using the assertion ids exactly as given."
    )


def assertions_for(ev: dict, common: list[dict]) -> list[dict]:
    return ev["assertions"] + ([] if ev.get("skip_common") else common)


def text_of(message) -> str:
    return "\n".join(b.text for b in message.content if b.type == "text")


def generate(client, model: str, effort: str, system: str, prompt: str) -> dict:
    with client.messages.stream(
        model=model,
        max_tokens=32000,
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        msg = stream.get_final_message()
    return {
        "text": text_of(msg),
        "stop_reason": msg.stop_reason,
        "usage": msg.usage.to_dict(),
        "request_id": msg._request_id,
    }


def grade(client, model: str, today: str, prompt: str, answer: str, assertions: list[dict]) -> dict:
    listed = "\n".join(f"- {a['id']}: {a['check']}" for a in assertions)
    user = (
        f"<user_request>\n{prompt}\n</user_request>\n\n"
        f"<answer>\n{answer}\n</answer>\n\n"
        f"<assertions>\n{listed}\n</assertions>"
    )
    msg = client.messages.create(
        model=model,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": GRADE_SCHEMA}},
        system=grader_system_prompt(today),
        messages=[{"role": "user", "content": user}],
    )
    if msg.stop_reason == "refusal":
        return {"results": [], "notes": "grader refused", "stop_reason": "refusal"}
    data = json.loads(text_of(msg))
    got = {r["id"] for r in data["results"]}
    for a in assertions:  # a missing verdict counts as a failure, never a silent pass
        if a["id"] not in got:
            data["results"].append({"id": a["id"], "verdict": "fail", "evidence": "grader returned no verdict"})
    data["usage"] = msg.usage.to_dict()
    return data


def _claude_cmd(prompt: str, model: str | None, effort: str | None, extra: list[str]) -> list[str]:
    cmd = ["claude", "-p", prompt, "--no-session-persistence", *extra]
    if model:
        cmd += ["--model", model]
    if effort:
        cmd += ["--effort", effort]
    return cmd


def cli_generate(variant: str, prompt: str, model: str | None, effort: str | None) -> dict:
    extra = ["--output-format", "stream-json", "--verbose", "--tools", CLI_TOOLS]
    tmp = None
    if variant == "skill":
        cwd, prompt = REPO_ROOT, f"/platform-designer {prompt}"
    else:
        tmp = tempfile.mkdtemp(prefix="pd-baseline-")
        cwd = Path(tmp)
        extra.append("--disable-slash-commands")  # no skills at all for the baseline
    try:
        proc = subprocess.run(_claude_cmd(prompt, model, effort, extra), cwd=cwd,
                              capture_output=True, text=True, timeout=CLI_TIMEOUT)
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    tools, result, registered = [], None, False
    for line in proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            registered = "platform-designer" in json.dumps(event.get("skills", []))
        elif event.get("type") == "assistant":
            for block in event["message"].get("content", []):
                if block.get("type") == "tool_use":
                    tools.append({"name": block["name"], "input": json.dumps(block["input"])[:200]})
        elif event.get("type") == "result":
            result = event
    if result is None:
        raise RuntimeError(f"claude -p produced no result (exit {proc.returncode}): {proc.stderr[-500:]}")
    # The /platform-designer prefix expands the skill into the prompt, so it counts as loaded
    # whenever Claude Code registered the skill. A baseline must never have it registered.
    skill_loaded = registered if variant == "skill" else (
        registered or any(t["name"] == "Skill" or "platform-designer" in t["input"] for t in tools))
    return {
        "text": result.get("result", ""),
        "stop_reason": "end_turn" if result.get("subtype") == "success" else result.get("subtype"),
        "is_error": result.get("is_error"),
        "tools_used": tools,
        "skill_loaded": skill_loaded,
        "notional_cost_usd": result.get("total_cost_usd"),
        "usage": result.get("usage"),
    }


def cli_grade(model: str | None, today: str, prompt: str, answer: str, assertions: list[dict]) -> dict:
    listed = "\n".join(f"- {a['id']}: {a['check']}" for a in assertions)
    user = (
        f"<user_request>\n{prompt}\n</user_request>\n\n"
        f"<answer>\n{answer}\n</answer>\n\n"
        f"<assertions>\n{listed}\n</assertions>"
    )
    extra = ["--output-format", "json", "--tools", "", "--disable-slash-commands",
             "--system-prompt", grader_system_prompt(today), "--json-schema", json.dumps(GRADE_SCHEMA)]
    with tempfile.TemporaryDirectory(prefix="pd-grader-") as tmp:
        proc = subprocess.run(_claude_cmd(user, model, "high", extra), cwd=tmp,
                              capture_output=True, text=True, timeout=CLI_TIMEOUT)
    out = json.loads(proc.stdout)
    if out.get("is_error"):
        raise RuntimeError(f"grader error: {out.get('result', '')[:300]}")
    data = out.get("structured_output") or json.loads(out["result"])
    got = {r["id"] for r in data["results"]}
    for a in assertions:  # a missing verdict counts as a failure, never a silent pass
        if a["id"] not in got:
            data["results"].append({"id": a["id"], "verdict": "fail", "evidence": "grader returned no verdict"})
    data["notional_cost_usd"] = out.get("total_cost_usd")
    return data


def run_job(client, args, today, ev, common, variant, run_idx, outdir: Path) -> dict:
    tag = f"eval{ev['id']}-{variant}-run{run_idx}"
    if args.backend == "cli":
        gen = cli_generate(variant, ev["prompt"], args.gen_model, args.effort)
        if variant == "skill" and not gen["skill_loaded"]:
            print(f"  ! {tag}: skill not registered -- run from the repo root on the branch with the skill", file=sys.stderr)
        if variant == "baseline" and gen["skill_loaded"]:
            print(f"  ! {tag}: baseline could see the skill; its result is contaminated", file=sys.stderr)
        (outdir / "answers" / f"{tag}.md").write_text(gen["text"])
        graded = cli_grade(args.grader_model, today, ev["prompt"], gen["text"], assertions_for(ev, common))
        (outdir / "grades" / f"{tag}.json").write_text(json.dumps(graded, indent=2))
        print(f"  done {tag}")
        return {"eval": ev["id"], "variant": variant, "run": run_idx, "gen": gen, "grade": graded}
    system = skill_system_prompt(today) if variant == "skill" else baseline_system_prompt(today)
    gen = generate(client, args.gen_model, args.effort, system, ev["prompt"])
    (outdir / "answers" / f"{tag}.md").write_text(gen["text"])
    if gen["stop_reason"] != "end_turn":
        print(f"  ! {tag}: stop_reason={gen['stop_reason']}", file=sys.stderr)
    graded = grade(client, args.grader_model, today, ev["prompt"], gen["text"], assertions_for(ev, common))
    (outdir / "grades" / f"{tag}.json").write_text(json.dumps(graded, indent=2))
    print(f"  done {tag}")
    return {"eval": ev["id"], "variant": variant, "run": run_idx, "gen": gen, "grade": graded}


def rate(verdicts: list[str]) -> str:
    scored = [v for v in verdicts if v != "na"]
    if not scored:
        return "n/a"
    return f"{sum(v == 'pass' for v in scored)}/{len(scored)}"


def build_report(results: list[dict], data: dict, args, today: str) -> str:
    common = data["common_assertions"]
    ran = {r["eval"] for r in results}
    data = {**data, "evals": [e for e in data["evals"] if e["id"] in ran]}
    lines = [
        f"# platform-designer eval results ({today})",
        "",
        f"- Backend: `{args.backend}`; generator: `{args.gen_model or 'CLI default'}` (effort `{args.effort or 'default'}`), runs per variant: {args.runs}",
        f"- Grader: `{args.grader_model or 'CLI default'}`, separate call, blind to variant and skill text",
        "- Cells show passes / graded runs (N/A excluded). **format** = skill output shape; **substance** = correctness and safety.",
        "",
        "## Summary",
        "",
        "| Eval | Skill: substance | Baseline: substance | Skill: format | Baseline: format |",
        "|---|---|---|---|---|",
    ]
    by = {}
    for r in results:
        by.setdefault((r["eval"], r["variant"]), []).append(r)

    def verdicts(ev, variant, kind=None, aid=None):
        out = []
        kinds = {a["id"]: a["kind"] for a in assertions_for(ev, common)}
        for r in by.get((ev["id"], variant), []):
            for res in r["grade"]["results"]:
                if aid and res["id"] != aid:
                    continue
                if kind and kinds.get(res["id"]) != kind:
                    continue
                out.append(res["verdict"])
        return out

    for ev in data["evals"]:
        lines.append(
            f"| {ev['id']} | {rate(verdicts(ev, 'skill', 'substance'))} | {rate(verdicts(ev, 'baseline', 'substance'))} "
            f"| {rate(verdicts(ev, 'skill', 'format'))} | {rate(verdicts(ev, 'baseline', 'format'))} |"
        )
    lines += ["", "## Per assertion", ""]
    for ev in data["evals"]:
        lines += [f"### Eval {ev['id']}", "", "| Assertion | Kind | Skill | Baseline | Skill evidence (run 0) |", "|---|---|---|---|---|"]
        first = next((r for r in by.get((ev["id"], "skill"), []) if r["run"] == 0), None)
        ev0 = {x["id"]: x for x in first["grade"]["results"]} if first else {}
        for a in assertions_for(ev, common):
            evidence = ev0.get(a["id"], {}).get("evidence", "").replace("|", "\\|").replace("\n", " ")[:160]
            lines.append(
                f"| `{a['id']}` | {a['kind']} | {rate(verdicts(ev, 'skill', aid=a['id']))} "
                f"| {rate(verdicts(ev, 'baseline', aid=a['id']))} | {evidence} |"
            )
        lines.append("")
    not_loaded = [f"eval{r['eval']} run{r['run']}" for r in results
                  if r["variant"] == "skill" and r["gen"].get("skill_loaded") is False]
    leaked = [f"eval{r['eval']} run{r['run']}" for r in results
              if r["variant"] == "baseline" and r["gen"].get("skill_loaded")]
    if not_loaded:
        lines.append(f"**Warning:** the skill did not load in: {', '.join(not_loaded)}. Treat those skill results as invalid.\n")
    if leaked:
        lines.append(f"**Warning:** the baseline could see the skill in: {', '.join(leaked)}. Treat those baseline results as invalid.\n")
    unsure = sum(res["verdict"] == "unsure" for r in results for res in r["grade"]["results"])
    lines.append(f"_{unsure} verdict(s) marked `unsure` need a human check (see grades/*.json)._")
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ids", type=int, nargs="*", help="eval ids to run (default: all)")
    p.add_argument("--runs", type=int, default=1, help="runs per variant; use 3+ to see variance")
    p.add_argument("--backend", choices=["cli", "api"], default="cli",
                   help="cli = Claude Code on your subscription (default); api = Anthropic SDK, billed per token")
    p.add_argument("--gen-model", help="default: CLI's default model (cli) or claude-opus-5 (api); cli accepts aliases like 'sonnet'")
    p.add_argument("--grader-model", help="same defaults as --gen-model")
    p.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"],
                   help="generator effort (default: CLI default for cli, high for api)")
    p.add_argument("--workers", type=int, help="parallel jobs (default: 1 for cli, 4 for api)")
    p.add_argument("--no-baseline", action="store_true", help="skip the no-skill baseline")
    p.add_argument("--dry-run", action="store_true", help="write the prompts that would be sent; call no API")
    args = p.parse_args()
    if args.backend == "api":
        args.gen_model = args.gen_model or "claude-opus-5"
        args.grader_model = args.grader_model or "claude-opus-5"
        args.effort = args.effort or "high"
    args.workers = args.workers or (1 if args.backend == "cli" else 4)

    data = json.loads(EVALS_FILE.read_text())
    evals = [e for e in data["evals"] if not args.ids or e["id"] in args.ids]
    variants = ["skill"] + ([] if args.no_baseline else ["baseline"])
    today = dt.date.today().isoformat()
    outdir = SKILL_DIR / "evals" / "results" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    (outdir / "answers").mkdir(parents=True)
    (outdir / "grades").mkdir()

    jobs = [(ev, v, r) for ev in evals for v in variants for r in range(args.runs)]
    random.shuffle(jobs)  # interleave variants so rate limits or drift don't favour one side
    print(f"{len(jobs)} generations + {len(jobs)} gradings -> {outdir}")

    if args.dry_run:
        (outdir / "system-skill.txt").write_text(skill_system_prompt(today))
        (outdir / "system-baseline.txt").write_text(baseline_system_prompt(today))
        (outdir / "system-grader.txt").write_text(grader_system_prompt(today))
        for ev in evals:
            (outdir / f"eval{ev['id']}-prompt.txt").write_text(ev["prompt"])
            (outdir / f"eval{ev['id']}-assertions.json").write_text(
                json.dumps(assertions_for(ev, data["common_assertions"]), indent=2))
        print("dry run: prompts written, no API calls made")
        return

    if args.backend == "cli":
        if not shutil.which("claude"):
            sys.exit("claude CLI not found. Install Claude Code, run `claude` once to log in, then retry.")
        client = None
        api_errors: tuple = ()
    else:
        import anthropic

        client = anthropic.Anthropic()
        api_errors = (anthropic.APIStatusError, anthropic.APIConnectionError)
    results, failures = [], []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(run_job, client, args, today, ev, data["common_assertions"], v, r, outdir): (ev["id"], v, r)
                for ev, v, r in jobs}
        for f in cf.as_completed(futs):
            try:
                results.append(f.result())
            except api_errors as e:
                failures.append((futs[f], f"API error: {e}"))
            except subprocess.TimeoutExpired:
                failures.append((futs[f], f"claude -p timed out after {CLI_TIMEOUT}s"))
            except (RuntimeError, json.JSONDecodeError, KeyError) as e:
                failures.append((futs[f], f"{type(e).__name__}: {e}"))

    (outdir / "results.json").write_text(json.dumps(results, indent=2, default=str))
    report = build_report(results, data, args, today)
    if failures:
        report += "\n## Failed jobs\n\n" + "\n".join(f"- {j}: {msg}" for j, msg in failures) + "\n"
    (outdir / "report.md").write_text(report)
    print(f"\nReport: {outdir / 'report.md'}")
    if failures:
        print(f"{len(failures)} job(s) failed; see the report.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
