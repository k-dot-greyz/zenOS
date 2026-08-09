.PHONY: doctor setup

# Read-only environment audit (env-doctor.sh — see third_party/README.md for
# provenance/license). Safe to run anytime, changes nothing.
doctor:
	@bash env-doctor.sh --with-submodules

# Progressive environment init: venv + core deps (tier 0/1). Does not touch
# Docker services (tier 3) — run `bash env-doctor.sh --init --tier 3` for that.
setup:
	@bash env-doctor.sh --init --tier 1
