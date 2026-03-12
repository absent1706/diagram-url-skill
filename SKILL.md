---
name: diagram-url
description: Convert between diagram source (Mermaid, PlantUML, Graphviz, etc.) and shareable URLs (mermaid.live or kroki.io). Use when the user wants to encode a diagram into a URL or decode a diagram URL back to text.
argument-hint: to-url [-t type] [-e engine] <file-or-text> | to-diagram <url>
---

# Diagram URL Encoder/Decoder

Convert between diagram source and shareable URLs.

Two engines:
- **kroki.io** — universal renderer (default for all diagram types)
- **mermaid.live** — interactive editor (alternative for Mermaid, use `-e mermaid_dot_live`)

The encoding script is bundled at `${CLAUDE_SKILL_DIR}/diagram_url.py`.

## Handling commands

When the user invokes this skill, determine which subcommand they want based on `$ARGUMENTS`:

### `to-url` — Diagram → URL

The user wants to convert diagram text into a shareable URL.

Input can be:
- A file path (pass directly to the script)
- Inline diagram text (from the argument or conversation context — save to a temp file, then pass)
- A code block from the conversation

Determine the diagram type from context (mermaid, plantuml, graphviz, etc.). Default to `mermaid` if unclear.

Run:

```bash
python3 "${CLAUDE_SKILL_DIR}/diagram_url.py" to-url -t <type> <file>
```

To use mermaid.live instead of kroki for Mermaid diagrams:

```bash
python3 "${CLAUDE_SKILL_DIR}/diagram_url.py" to-url -t mermaid -e mermaid_dot_live <file>
```

Or pipe from stdin:

```bash
echo '<diagram text>' | python3 "${CLAUDE_SKILL_DIR}/diagram_url.py" to-url -t <type> -
```

Return the resulting URL to the user.

### `to-diagram` — URL → Diagram

The user wants to decode a mermaid.live or kroki.io URL back to diagram source. The engine is auto-detected from the URL.

Run:

```bash
python3 "${CLAUDE_SKILL_DIR}/diagram_url.py" to-diagram '<url>'
```

Return the diagram text to the user in a code block with the appropriate language tag.

### No explicit subcommand — infer from input

If the user omits `to-url` / `to-diagram`, infer the intent:
- **Input looks like a URL** (starts with `http://` or `https://`, contains `kroki.io` or `#pako:`) → treat as `to-diagram`
- **Input looks like a file path** (ends with `.mmd`, `.puml`, `.gv`, etc., or is a valid path) → treat as `to-url`
- **Input looks like diagram text** (code block, or starts with `graph`, `sequenceDiagram`, `@startuml`, `digraph`, etc.) → treat as `to-url`
- **Truly ambiguous** → ask the user
