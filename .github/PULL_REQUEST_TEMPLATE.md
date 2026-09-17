## Intent

What changed, and why?

## How to verify

Commands a reviewer can actually run, for example:

```bash
uvx --python 3.14 black --check .
python scripts/check_no_identity_leaks.py
pytest tests/ -o addopts=
```

## Origin / `.env` impact

Does this touch `ZENOS_*` origin keys, installers, or `.env`? If yes, say how a fork should set them. If no, say "none".

## Intentionally skipped

What we chose not to do, and why. Agents: reply on review threads; do not resolve them.

## Related

Closes #
