# diagram-url

Convert between diagram source (Mermaid, PlantUML, Graphviz, etc.) and shareable URLs.

Works as a **standalone CLI script**, a **Python library**, or an **AI coding assistant skill** (Claude Code, Cursor, Windsurf, etc.).

No dependencies — pure Python 3 stdlib (`json`, `zlib`, `base64`).

## Supported engines

| Engine | Default for | URL format |
|--------|------------|------------|
| **kroki.io** | All diagram types | `https://kroki.io/{type}/{format}/{encoded}` |
| **mermaid.live** | — (opt-in via `-e mermaid_dot_live`) | `https://mermaid.live/edit#pako:{encoded}` |

## Standalone CLI usage

```bash
# Download the script
curl -O https://raw.githubusercontent.com/absent1706/diagram-url-skill/main/diagram_url.py

# Mermaid diagram → kroki.io URL (default)
python3 diagram_url.py to-url diagram.mmd

# PlantUML diagram → kroki.io URL
python3 diagram_url.py to-url -t plantuml diagram.puml

# Mermaid diagram → mermaid.live URL
python3 diagram_url.py to-url -e mermaid_dot_live diagram.mmd

# Pipe from stdin
echo 'graph TD; A-->B' | python3 diagram_url.py to-url -

# URL → diagram text (auto-detects engine)
python3 diagram_url.py to-diagram 'https://kroki.io/mermaid/svg/eNp...'
python3 diagram_url.py to-diagram 'https://mermaid.live/edit#pako:...'
```

### CLI options for `to-url`

| Flag | Description | Default |
|------|-------------|---------|
| `-t`, `--type` | Diagram type (`mermaid`, `plantuml`, `graphviz`, etc.) | `mermaid` |
| `-f`, `--format` | Output format for kroki (`svg`, `png`, `pdf`) | `svg` |
| `-e`, `--engine` | Engine: `kroki` or `mermaid_dot_live` | `kroki` |

## Python library usage

```python
from diagram_url import to_url, to_diagram

# Encode (default: kroki.io)
url = to_url("graph TD\n    A-->B")
url = to_url("graph TD\n    A-->B", engine="mermaid_dot_live")
url = to_url("@startuml\nA -> B\n@enduml", diagram_type="plantuml")

# Decode (auto-detects engine from URL)
text, diagram_type = to_diagram(url)
```

## Installation as AI assistant skill

### Claude Code

```bash
git clone https://github.com/absent1706/diagram-url-skill.git ~/.claude/skills/diagram-url
```

Then use:
```
/diagram-url to-url diagram.mmd
/diagram-url to-url -t plantuml diagram.puml
/diagram-url to-diagram 'https://kroki.io/mermaid/svg/eNp...'
```

### Cursor / Windsurf / other AI assistants

Clone anywhere and add a rule pointing to the script:

```bash
git clone https://github.com/absent1706/diagram-url-skill.git ~/diagram-url-skill
```

Then add to your project rules (`.cursorrules`, `.windsurfrules`, or equivalent):

```
When the user asks to convert a diagram to a shareable URL or vice versa,
use the script at ~/diagram-url-skill/diagram_url.py:

  # Diagram → URL (kroki.io, default)
  python3 ~/diagram-url-skill/diagram_url.py to-url -t <type> <file>

  # Diagram → URL (mermaid.live)
  python3 ~/diagram-url-skill/diagram_url.py to-url -e mermaid_dot_live <file>

  # URL → Diagram (auto-detects engine)
  python3 ~/diagram-url-skill/diagram_url.py to-diagram '<url>'
```

## How the encoding works

### kroki.io

```
diagram text  →  zlib.compress (level 9)  →  base64url  →  https://kroki.io/{type}/{format}/{encoded}
```

### mermaid.live

```
JSON state  →  zlib compress  →  base64url (no padding)  →  #pako:<encoded>
```

The JSON state object:

```json
{
  "code": "<diagram text>",
  "mermaid": "{\"theme\":\"default\"}",
  "autoSync": true,
  "updateDiagram": true,
  "updateEditor": true
}
```

## License

MIT
