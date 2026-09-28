#!/usr/bin/env bash
# Build dist/platform-designer.zip for uploading to claude.ai (Settings > Capabilities > Skills).
# The zip holds one folder, platform-designer/, with SKILL.md and the templates.
# Evals and the Claude Code plugin manifest are left out: claude.ai doesn't use them.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
src="$root/.claude/skills/platform-designer"
out="$root/dist"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

mkdir -p "$stage/platform-designer" "$out"
cp "$src/SKILL.md" "$src"/*-Template.md "$stage/platform-designer/"
rm -f "$out/platform-designer.zip"
(cd "$stage" && zip -qr "$out/platform-designer.zip" platform-designer)
echo "Built $out/platform-designer.zip:"
unzip -l "$out/platform-designer.zip"
