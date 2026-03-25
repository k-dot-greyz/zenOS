"""
---
dex_id: "0x7C:0x01"
dex_type: "utility"
midi_2_0_context:
  resource_type: "Library"
  property_exchange_id: "urn:zenos:agents:dex-reader"
legacy_map:
  midi_1_0_bank: 124
  midi_1_0_prog: 1
status: "active"
tags: ["python", "utility", "dex", "metadata"]
---

dex reader utility for zenOS

provides runtime access to dex metadata from both:
- distributed frontmatter (0xNN:0xNN format)
- centralized registry (0xNN.NN.NN format)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


class DexReader:
    """reader for dex protocol metadata"""
    
    def __init__(self, index_path: str = "dex/7E-00_dex-index.md"):
        self.index_path = Path(index_path)
        self.entries = []
        self._load_index()
    
    def _load_index(self):
        """load entries from the dex index"""
        if not self.index_path.exists():
            return
        
        with open(self.index_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # parse markdown table
        in_table = False
        for line in lines:
            if line.startswith("| dex id"):
                in_table = True
                continue
            if line.startswith("| :---"):
                continue
            if in_table and line.startswith("|"):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 5:
                    # extract dex_id from backticks
                    dex_id = parts[0].strip("`")
                    entry = {
                        "dex_id": dex_id,
                        "type": parts[1].strip("`"),
                        "status": "active" if "🟢" in parts[2] else "inactive",
                        "filename": self._extract_filename(parts[3]),
                        "path": self._extract_path(parts[3]),
                        "pe_id": parts[4].strip("`")
                    }
                    self.entries.append(entry)
    
    def _extract_filename(self, markdown_link: str) -> str:
        """extract filename from [text](path) format"""
        match = re.search(r'\[(.*?)\]', markdown_link)
        return match.group(1) if match else markdown_link
    
    def _extract_path(self, markdown_link: str) -> str:
        """extract path from [text](path) format"""
        match = re.search(r'\((.*?)\)', markdown_link)
        return match.group(1) if match else ""
    
    def get(self, dex_id: str) -> Optional[Dict]:
        """get entry by dex_id"""
        for entry in self.entries:
            if entry["dex_id"] == dex_id:
                return entry
        return None
    
    def by_bank(self, bank: int) -> List[Dict]:
        """get all entries in a bank (e.g., 0x7E)"""
        bank_hex = f"0x{bank:02X}"
        return [e for e in self.entries if e["dex_id"].startswith(bank_hex)]
    
    def by_type(self, dex_type: str) -> List[Dict]:
        """get all entries of a specific type"""
        return [e for e in self.entries if e["type"] == dex_type]
    
    def search(self, query: str) -> List[Dict]:
        """search entries by filename or pe_id"""
        query_lower = query.lower()
        return [
            e for e in self.entries
            if query_lower in e["filename"].lower()
            or query_lower in e["pe_id"].lower()
        ]
    
    def list_all(self) -> List[Dict]:
        """return all entries"""
        return self.entries
    
    def refresh(self):
        """reload the index"""
        self.entries = []
        self._load_index()


def get_dex_metadata(filepath: Path) -> Optional[Dict]:
    """extract dex metadata from a file's frontmatter"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # try standard frontmatter
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL | re.MULTILINE)
        
        # try triple-quoted for python
        if not match and filepath.suffix == '.py':
            match = re.match(r'^\s*"""(.*?)"""', content, re.DOTALL)
        
        if not match:
            return None
        
        yaml_block = match.group(1)
        
        # extract key fields
        metadata = {}
        patterns = {
            "dex_id": r"^dex_id:\s*[\"']?(0x[0-9A-Fa-f]{2}:0x[0-9A-Fa-f]{2})[\"']?",
            "dex_type": r"^dex_type:\s*[\"']?(\w+)[\"']?",
            "status": r"^status:\s*[\"']?(\w+)[\"']?",
            "pe_id": r"property_exchange_id:\s*[\"']?([a-zA-Z0-9:\-\.]+)[\"']?"
        }
        
        for key, pattern in patterns.items():
            found = re.search(pattern, yaml_block, re.MULTILINE)
            metadata[key] = found.group(1) if found else None
        
        return metadata if metadata.get("dex_id") else None
    except (OSError, UnicodeDecodeError, AttributeError):
        return None

