import unittest
import tempfile
import os
from pathlib import Path
from zen.utils.dex import DexReader, get_dex_metadata

class TestDexReader(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.index_path = Path(self.test_dir.name) / "test_index.md"
        
        # Create a dummy index file
        with open(self.index_path, 'w', encoding='utf-8') as f:
            f.write("""---
dex_id: "0x7E:0x00"
---

| dex id | type | status | file name | urn (pe id) |
| :--- | :--- | :--- | :--- | :--- |
| `0x7C:0x01` | `utility` | 🟢 | [dex.py](zen/utils/dex.py) | `urn:zenos:agents:dex-reader` |
| `0x7E:0x01` | `script` | 🟢 | [yoinker.py](dex/yoinker.py) | `urn:zenos:ops:dex-yoinker` |
""")
        self.reader = DexReader(str(self.index_path))

    def tearDown(self):
        self.test_dir.cleanup()

    def test_get_by_id(self):
        entry = self.reader.get("0x7C:0x01")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["dex_id"], "0x7C:0x01")
        self.assertEqual(entry["type"], "utility")
        
        # Test non-existent
        self.assertIsNone(self.reader.get("0x00:00"))

    def test_by_bank(self):
        entries = self.reader.by_bank(0x7C)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["dex_id"], "0x7C:0x01")
        
        entries_7e = self.reader.by_bank(0x7E)
        self.assertEqual(len(entries_7e), 1)
        self.assertEqual(entries_7e[0]["dex_id"], "0x7E:0x01")

    def test_by_type(self):
        entries = self.reader.by_type("utility")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["dex_id"], "0x7C:0x01")

    def test_search(self):
        # Search by filename
        results = self.reader.search("yoinker")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["filename"], "yoinker.py")
        
        # Search by pe_id
        results = self.reader.search("urn:zenos:agents")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["dex_id"], "0x7C:0x01")

    def test_refresh(self):
        # Modify index
        with open(self.index_path, 'a', encoding='utf-8') as f:
            f.write("| `0x7F:0xFF` | `test` | 🟢 | [test.py](test.py) | `urn:test` |\n")
        
        self.reader.refresh()
        entry = self.reader.get("0x7F:0xFF")
        self.assertIsNotNone(entry)

class TestGetDexMetadata(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.dir_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_yaml_frontmatter(self):
        p = self.dir_path / "test.md"
        with open(p, 'w', encoding='utf-8') as f:
            f.write("""---
dex_id: "0x12:0x34"
dex_type: "test"
status: "active"
property_exchange_id: "urn:test"
---
content
""")
        meta = get_dex_metadata(p)
        self.assertIsNotNone(meta)
        self.assertEqual(meta["dex_id"], "0x12:0x34")
        self.assertEqual(meta["dex_type"], "test")

    def test_python_docstring(self):
        p = self.dir_path / "test.py"
        with open(p, 'w', encoding='utf-8') as f:
            f.write('''"""
---
dex_id: "0xAB:0xCD"
dex_type: "script"
status: "draft"
property_exchange_id: "urn:py:test"
---
"""
print("hello")
''')
        meta = get_dex_metadata(p)
        self.assertIsNotNone(meta)
        self.assertEqual(meta["dex_id"], "0xAB:0xCD")
        self.assertEqual(meta["pe_id"], "urn:py:test")

    def test_no_metadata(self):
        p = self.dir_path / "empty.txt"
        with open(p, 'w', encoding='utf-8') as f:
            f.write("just text")
        meta = get_dex_metadata(p)
        self.assertIsNone(meta)

    def test_malformed_file(self):
        # Should handle gracefully
        p = self.dir_path / "bad.bin"
        with open(p, 'wb') as f:
            f.write(b'\x80\x81\xff') # Invalid utf-8
        
        # Depending on implementation, might raise or return None. 
        # The current impl catches UnicodeDecodeError and returns None.
        meta = get_dex_metadata(p)
        self.assertIsNone(meta)

if __name__ == '__main__':
    unittest.main()
