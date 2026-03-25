"""
---
dex_id: "0x7E:0x01"
dex_type: "script"
midi_2_0_context:
  resource_type: "Utility"
  property_exchange_id: "urn:zenos:ops:dex-yoinker"
legacy_map:
  midi_1_0_bank: 126
  midi_1_0_prog: 1
status: "active"
tags: ["python", "ops", "metadata", "indexing"]
---
"""

import os
import re
import datetime
from pathlib import Path

# Configuration
ROOT_DIR = Path(".") 
DEX_DIR = ROOT_DIR / "dex"
OUTPUT_FILE = DEX_DIR / "7E-00_dex-index.md"

# Regex for YAML frontmatter
YAML_FRONT_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL | re.MULTILINE)

# Keys to extract
KEYS_TO_YOINK = {
    "dex_id": re.compile(r"^dex_id:\s*[\"']?(0x[0-9A-Fa-f]{2}:0x[0-9A-Fa-f]{2})[\"']?", re.MULTILINE),
    "dex_type": re.compile(r"^dex_type:\s*[\"']?(\w+)[\"']?", re.MULTILINE),
    "status": re.compile(r"^status:\s*[\"']?(\w+)[\"']?", re.MULTILINE),
    "pe_id": re.compile(r"property_exchange_id:\s*[\"']?([a-zA-Z0-9:\-\.]+)[\"']?", re.MULTILINE)
}

def parse_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        match = YAML_FRONT_RE.match(content)
        
        # Also check for triple-quoted string blocks (common in Python scripts)
        if not match and filepath.suffix == '.py':
             match = re.match(r'^\s*"""(.*?)"""', content, re.DOTALL)
             if match:
                 # Check if the inner content looks like frontmatter
                 inner = match.group(1)
                 fm_match = YAML_FRONT_RE.match(inner.strip() + "\n")
                 if fm_match:
                     yaml_block = fm_match.group(1)
                 else:
                     # Try matching without the --- delimiters if inside triple quotes
                     yaml_block = inner
             else:
                 return None
        elif match:
            yaml_block = match.group(1)
        else:
            return None

        metadata = {"path": str(filepath), "filename": filepath.name}
        for key, regex in KEYS_TO_YOINK.items():
            found = regex.search(yaml_block)
            metadata[key] = found.group(1) if found else "N/A"
        
        # Only include files that actually have a dex_id
        if metadata.get("dex_id") == "N/A":
            return None
            
        return metadata
    except (OSError, UnicodeDecodeError):
        # Skip files that can't be read or decoded
        return None

def generate_markdown_index(entries):
    # Sort High to Low (0x7F -> 0x00)
    entries.sort(key=lambda x: x.get("dex_id", "0x00:00"), reverse=True)
    
    md_lines = [
        "---",
        "dex_id: \"0x7E:0x00\"",
        "dex_type: \"index\"",
        "status: \"active\"",
        "tags: [\"index\", \"generated\"]",
        "---",
        "",
        "# zenOS dex index",
        f"> **last updated:** {datetime.datetime.now().isoformat()}",
        "",
        "| dex id | type | status | file name | urn (pe id) |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]
    
    for entry in entries:
        if entry["dex_id"] == "N/A": continue
        link = f"[{entry['filename']}]({entry['path']})"
        emoji = "🟢" if entry['status'] == "active" else "⚪"
        row = f"| `{entry['dex_id']}` | `{entry['dex_type']}` | {emoji} | {link} | `{entry['pe_id']}` |"
        md_lines.append(row)
        
    return "\n".join(md_lines)

def main():
    print("🎹 starting dex yoinker...")
    valid_entries = []
    for root, dirs, files in os.walk(ROOT_DIR):
        if ".git" in dirs: dirs.remove(".git")
        if "node_modules" in dirs: dirs.remove("node_modules")
        if "__pycache__" in dirs: dirs.remove("__pycache__")
        
        for file in files:
            if file.endswith((".md", ".py", ".yaml")) and Path(root)/file != OUTPUT_FILE:
                meta = parse_file(Path(root) / file)
                if meta: valid_entries.append(meta)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(generate_markdown_index(valid_entries) + "\n")
    print(f"✅ yoink complete. found {len(valid_entries)} entries")
    print(f"   index: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

