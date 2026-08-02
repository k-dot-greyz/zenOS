"""
dex constants and regex patterns
"""
import re

# Regex for YAML frontmatter
YAML_FRONT_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL | re.MULTILINE)

# Regex for Python docstring frontmatter
PYTHON_DOCSTRING_RE = re.compile(r'^\s*"""(.*?)"""', re.DOTALL)

# Common regex patterns for field extraction
DEX_ID_PATTERN = r"^dex_id:\s*[\"']?(0x[0-9A-Fa-f]{2}:0x[0-9A-Fa-f]{2})[\"']?"
DEX_TYPE_PATTERN = r"^dex_type:\s*[\"']?(\w+)[\"']?"
STATUS_PATTERN = r"^status:\s*[\"']?(\w+)[\"']?"
PE_ID_PATTERN = r"property_exchange_id:\s*[\"']?([a-zA-Z0-9:\-\.]+)[\"']?"

# Compiled regex for efficient reuse
PATTERNS = {
    "dex_id": re.compile(DEX_ID_PATTERN, re.MULTILINE),
    "dex_type": re.compile(DEX_TYPE_PATTERN, re.MULTILINE),
    "status": re.compile(STATUS_PATTERN, re.MULTILINE),
    "pe_id": re.compile(PE_ID_PATTERN, re.MULTILINE)
}
