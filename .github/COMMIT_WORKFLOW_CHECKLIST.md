# Commit workflow

The real process is [docs/guides/REVIEW.md](../docs/guides/REVIEW.md). This file is a short reminder, not a second review.

Before you push:

- [ ] `uvx --python 3.14 black .`
- [ ] `python scripts/check_no_identity_leaks.py` if you touched docs, installers, or origin
- [ ] `pytest tests/ -o addopts=`
- [ ] PR template filled: intent, how to verify, origin/`.env` impact, intentionally skipped, `Closes #`

Reply on review threads. Do not resolve them. CodeRabbit is suggestions, not merge law.
