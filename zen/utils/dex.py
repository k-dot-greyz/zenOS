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

from zen.utils.dex_constants import PATTERNS, PYTHON_DOCSTRING_RE, YAML_FRONT_RE


class DexReader:
    """reader for dex protocol metadata"""

    def __init__(self, index_path: str = "dex/7E-00_dex-index.md"):
        """Initialize a DEX reader and load entries from the specified Markdown index.
        
        Parameters:
        	index_path (str): Path to the Markdown index containing DEX entries.
        """
        self.index_path = Path(index_path)
        self.entries = []
        self._index_by_id: Dict[str, Dict] = {}
        self._load_index()

    def _load_index(self):
        """
        Load DEX entries from the configured Markdown index into the reader's collections.
        
        The current entries are cleared before loading. If the index file does not exist,
        the collections remain empty.
        """
        self.entries = []
        self._index_by_id = {}

        if not self.index_path.exists():
            return

        with open(self.index_path, "r", encoding="utf-8") as f:
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
                        "pe_id": parts[4].strip("`"),
                    }
                    self.entries.append(entry)
                    self._index_by_id[dex_id] = entry

    def _extract_filename(self, markdown_link: str) -> str:
        """
        Extract the filename from Markdown link text.
        
        Parameters:
            markdown_link (str): Markdown text in the form `[filename](path)`.
        
        Returns:
            str: The link text, or the original input when no link text is present.
        """
        match = re.search(r"\[(.*?)\]", markdown_link)
        return match.group(1) if match else markdown_link

    def _extract_path(self, markdown_link: str) -> str:
        """
        Extracts the target path from a Markdown link.
        
        Parameters:
            markdown_link (str): Markdown link text in the form `[text](path)`.
        
        Returns:
            str: The extracted path, or an empty string when no path is present.
        """
        match = re.search(r"\((.*?)\)", markdown_link)
        return match.group(1) if match else ""

    def get(self, dex_id: str) -> Optional[Dict]:
        """
        Retrieve the DEX entry with the specified identifier.
        
        Returns:
            Optional[Dict]: The matching DEX entry, or `None` if no entry exists.
        """
        return self._index_by_id.get(dex_id)

    def by_bank(self, bank: int) -> List[Dict]:
        """Return all DEX entries whose IDs belong to the specified hexadecimal bank.
        
        Parameters:
        	bank (int): The numeric bank identifier.
        
        Returns:
        	List[Dict]: Entries with IDs matching the bank prefix.
        """
        bank_hex = f"0x{bank:02X}"
        return [e for e in self.entries if e["dex_id"].startswith(bank_hex)]

    def by_type(self, dex_type: str) -> List[Dict]:
        """
        Retrieve all DEX entries with the specified type.
        
        Parameters:
        	dex_type (str): DEX type to match exactly.
        
        Returns:
        	List[Dict]: Entries whose type matches `dex_type`.
        """
        return [e for e in self.entries if e["type"] == dex_type]

    def search(self, query: str) -> List[Dict]:
        """
        Search entries by filename or property-exchange ID.
        
        Parameters:
        	query (str): The case-insensitive text to find.
        
        Returns:
        	List[Dict]: Entries whose filename or property-exchange ID contains the query.
        """
        query_lower = query.lower()
        return [
            e
            for e in self.entries
            if query_lower in e["filename"].lower() or query_lower in e["pe_id"].lower()
        ]

    def list_all(self) -> List[Dict]:
        """
        List all loaded DEX entries.
        
        Returns:
            List[Dict]: The loaded DEX entries.
        """
        return self.entries

    def refresh(self):
        """Reload the DEX index from disk."""
        self._load_index()


def get_dex_metadata(filepath: Path) -> Optional[Dict]:
    """
    Extract DEX metadata from a file's YAML frontmatter or Python docstring.
    
    Parameters:
        filepath (Path): Path to the file containing the metadata.
    
    Returns:
        Optional[Dict]: A mapping of extracted metadata fields, or `None` when the file is unreadable or does not contain a DEX ID.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # try standard frontmatter
        match = YAML_FRONT_RE.match(content)

        # try triple-quoted for python
        if not match and filepath.suffix == ".py":
            match = PYTHON_DOCSTRING_RE.match(content)

        if not match:
            return None

        yaml_block = match.group(1)

        # extract key fields
        metadata = {}
        for key, pattern in PATTERNS.items():
            found = pattern.search(yaml_block)
            metadata[key] = found.group(1) if found else None

        return metadata if metadata.get("dex_id") else None
    except (OSError, UnicodeDecodeError, AttributeError):
        return None
