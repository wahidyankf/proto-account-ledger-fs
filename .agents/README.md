# Shared Agent Directory

This directory holds the canonical agent and skill definitions shared by every supported harness (Claude Code and
Codex). The harness adapters under `.claude/` and `.codex/` are generated from here with `npm run generate:bindings` and
only route back to these files; edit here, never in an adapter. See
[Harness Adapters](../repo-governance/development/agents/harness-adapters.md).

Most definitions are adopted copies from the `ose-rules` catalog; references to catalog artifacts this repository did
not adopt were unlinked.

## Directory Map

- [`agents/`](agents/README.md) — canonical custom-agent prompts and their capability contracts.
- [`skills/`](skills/README.md) — the shared skills available in this repository.
