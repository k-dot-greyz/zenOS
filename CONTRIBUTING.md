# Contributing to zenOS

Thank you for considering contributing to zenOS. This repository is the **core platform** of the zenOS ecosystem—the standalone product repo at [k-dot-greyz/zenOS](https://github.com/k-dot-greyz/zenOS). It is also linked as a git submodule from the private superproject [`dev-master`](https://github.com/k-dot-greyz/dev-master) at `dex/09-repos/zenOS`.

This guide adapts proven open-source contribution practices (including patterns from [Gumroad's public contributing guide](https://github.com/antiwork/gumroad/blob/main/CONTRIBUTING.md)) to zenOS's Python CLI, plugin ecosystem, and monorepo boundary rules.

---

## Overall

Use clear, native-sounding English in all communication. Avoid excessive capitalization, stacked punctuation, or typos that make intent harder to parse.

- ❌ Before: "is this still open ?? I am happy to work on it ??"
- ✅ After: "Is this actively being worked on? I've started work on it here…"

Explain the reasoning behind your changes, not just the change itself. Describe the architectural decision or the specific problem being solved. For bug fixes, identify the root cause. Do not apply a fix without explaining how the invalid state occurred.

---

## The prime directive: platform code here, internal guides in dev-master

We maintain a strict boundary between this repository and the monorepo workspace:

1. **This repository (`zenOS`)**: Core platform code, public-facing docs, tests, CI, and product configuration (for example `docs/`, `pokedex/`, plugin manifests).
2. **The superproject (`dev-master`)**: Private workspace orchestration, dex routing, submodule bump workflows, and **internal** monorepo guides.

### The boundary violation rule

**Never commit internal monorepo documentation, fork-specific guides, or dev-master-only configuration into this repository.**

- **Why?** zenOS is designed to stand alone as a product. Misplacing internal files pollutes upstream history, causes PR rejections, and leaks private workspace details.
- **What belongs here**: Application code under `zen/`, public guides under `docs/`, platform YAML such as `pokedex/` and plugin specs, tests, scripts, and CI under `.github/`.
- **What belongs in dev-master**: Internal guides under `dex/03-docs/guides/` (for example submodule bump, fork workflow, and monorepo agent protocols).

---

## Repository layout

Know where changes belong before you open a PR:

| Path | Purpose |
| :--- | :--- |
| `zen/` | Core Python package (CLI, agents, PKM, plugins, providers, UI) |
| `docs/` | Public platform documentation and planning |
| `pokedex/` | Model and procedure catalog YAML |
| `examples/` | Sample plugins and demos |
| `scripts/` | Setup, bridge, and platform shell scripts |
| `n8n/` | n8n workflow integration assets |
| `inbox/` | Ingestion staging (keep runtime artifacts untracked) |
| `.github/` | CI workflows, PR template, commit checklist |
| `tests/`, `test_*.py` | Pytest modules (see CI) |

For AI agent onboarding and platform conventions, start with [`docs/AI_INSTRUCTIONS.md`](docs/AI_INSTRUCTIONS.md). For local environment setup, see [`docs/guides/DEV_ENVIRONMENT_SETUP.md`](docs/guides/DEV_ENVIRONMENT_SETUP.md).

---

## Fork-and-PR workflow

Whether you cloned zenOS directly or via `dev-master`, use this workflow for upstream contributions:

### Step 1: Configure remotes

```bash
git remote -v

# Canonical upstream (required for fork contributors)
git remote add upstream https://github.com/k-dot-greyz/zenOS.git 2>/dev/null || true

# Personal fork (recommended for external contributors)
# git remote set-url origin https://github.com/<your-user>/zenOS.git
```

Maintainers with direct push access may use `origin` as the canonical repo. Fork contributors should push feature branches to their fork and open PRs against `k-dot-greyz/zenOS`.

### Step 2: Branch hygiene

Rebase your branch onto `main` when starting work and before every commit:

```bash
git fetch upstream   # or origin, if you have direct access
git rebase upstream/main
```

Resolve conflicts locally before pushing. PRs with stale branches may be sent back for a rebase.

Working from a fork, `origin` is your fork—and your fork's `main` goes stale the moment this repo moves. Add this repo as `upstream` once and rebase onto `upstream/main`.

### Step 3: Create a clean feature branch

```bash
git checkout -b feat/your-feature-name upstream/main
```

Use branch prefixes such as `feat/`, `fix/`, `docs/`, `refactor/`, `test/`, or `chore/`.

### Step 4: Implement focused changes

- No tracked secrets, local `.env` files, or temporary logs.
- No dev-master-only markdown or monorepo routing docs.
- Public documentation updates belong in `docs/` when they describe zenOS itself.
- Match existing Python style (`black` line length 100) and module layout under `zen/`.
- Prefer small, reviewable PRs. Break work larger than ~100 lines of meaningful change into stacked PRs when possible.

### Step 5: Run local quality gates

Before committing, run the checks CI expects (see [`.github/workflows/zenos-ci.yml`](.github/workflows/zenos-ci.yml)):

```bash
python -m pip install -e ".[dev]"
cp env.example .env  # configure keys locally; never commit .env

black --check .
isort --check-only .
pytest --cov=. --cov-report=term-missing -v
```

Optional but recommended during development:

```bash
ruff check .
mypy zen/ --ignore-missing-imports --no-strict-optional
```

Do not push code with failing tests. CI is not a substitute for local verification.

### Step 6: Pre-commit audit

Run the checklist in [Section: Pre-commit audit](#pre-commit-audit) and review [`.github/COMMIT_WORKFLOW_CHECKLIST.md`](.github/COMMIT_WORKFLOW_CHECKLIST.md).

### Step 7: Commit and push

Use [conventional commits](#commit-message-style):

```bash
git commit -m "feat(pkm): implement dynamic schema validation for incoming packets"
git push -u origin HEAD
```

### Step 8: Open a pull request

Target `main` on the upstream repository. Use the PR template and `gh` when possible:

```bash
gh pr create --repo k-dot-greyz/zenOS \
  --base main \
  --title "feat(pkm): implement dynamic schema validation" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md
```

---

## Pull requests

> ### Show CLI and UI changes
>
> **Every PR that changes anything a user can see or experience in the terminal, TUI, or web UI should include before/after evidence—a short video (preferred) or screenshots.** This includes layout tweaks, Rich output formatting, mobile/Termux behavior, and plugin manifest UX. A PR that only touches documentation, agent skill files, or internal CI config needs no video—the diff is the reviewable artifact.

Every non-trivial PR should include:

- **What / Why / Before-After / Test Results** (see [PR description structure](#pr-description-structure))
- **An AI disclosure** naming the specific model, after a `---` separator (if AI assisted)
- **A self-review** comment on your own diff
- **Updated tests** where behavior changed
- **QA steps** someone else can follow to verify the change

Attach visual evidence directly to the PR with the GitHub CLI's `--attach` flag (`gh` 2.99+)—do not commit media files to the repo:

```bash
gh pr create --title "..." --body-file body.md --attach './before.png#CLI before' --attach './after.png#CLI after'
gh pr comment <number> --attach './demo.mp4'
```

Reference an attachment inline in the body as `![alt](./before.png)` and the CLI rewrites it to the uploaded asset URL. Drag-and-drop in the web UI does the same thing.

### PR description structure

Non-trivial PRs should follow this structure (also reflected in [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md)):

- **What** — Concrete changes, not a list of files.
- **Why** — Why this change exists and why this approach was chosen over alternatives. When other PRs or approaches exist for the same problem, name them and say why this one wins.
- **Before/After** — Video or screenshots for user-facing CLI/TUI/UI changes. For non-user-facing changes, a short terminal walkthrough of the relevant flow is enough. Docs-only PRs: the diff is sufficient.
- **Test Results** — List the relevant commands/checks run (for example `pytest`, `black --check`, `zen doctor`). No screenshot of passing specs is required.

End with an AI disclosure after a `---` separator when applicable. Name the specific model (for example, "Claude Opus 4.6") and summarize the prompts or agent context given.

---

## AI-assisted contributions

zenOS welcomes contributions from humans and AI agents. When AI assists your work:

- Disclose the model and version in the PR (see above).
- You are responsible for the correctness, security, and scope of the diff—not the model.
- Follow [`docs/AI_INSTRUCTIONS.md`](docs/AI_INSTRUCTIONS.md) for agent-specific onboarding.
- Prefer current-generation models with strong reasoning for non-trivial changes; verify outputs against tests and project conventions.

---

## Development guidelines

### Testing guidelines

- Write descriptive test names that explain the behavior being tested.
- Group related tests together; keep tests independent and isolated.
- Use factories or fixtures for test data instead of duplicating setup inline.
- Tests must fail when the fix is reverted. If the test passes without the application code change, it is invalid.
- Prefer `tests/` for new modules; root-level `test_*.py` files remain supported for legacy coverage.
- Do not use "should" in test descriptions (see [Better Specs](https://www.betterspecs.org/#should)).
- Mock external APIs (OpenRouter, MCP, TTS) at boundaries—do not hit live services in unit tests unless the test is explicitly marked for integration.

### Code standards

- Python 3.8+ compatibility unless a deliberate bump is documented.
- Sentence case for user-facing strings and docs headers unless matching an existing convention.
- Comments earn their place: explain *why*, not what the code already says.
- Business logic and validation belong in Python modules under `zen/`, not scattered in shell scripts.
- Assign magic numbers to named constants to clarify intent.
- Avoid premature abstraction—duplicate code that serves different domains (CLI vs plugin host vs PKM) may stay separate.

### GlitchWorks agnostic architecture protocol

All development within zenOS should adhere to the **GlitchWorks Agnostic Architecture Protocol** (see also `/architecture-base` in agent workflows):

| Principle | Rule |
| :--- | :--- |
| Zero hardcoding | Configure endpoints, paths, and ports via env vars or injected config—never hardcode dev-master paths. |
| Polymorphism by default | Depend on abstractions (providers, storage, telemetry sinks), not concretions. |
| Open piping | Modules communicate via typed, serializable messages—not hidden global state. |
| Boundary validation | Validate CLI args, plugin manifests, inbox payloads, and provider responses before domain logic. |
| State hydration | Stateful subsystems should support serialize/restore (JSON, SQLite, YAML). |
| Graceful degradation | Missing API keys or offline providers must surface actionable errors, not crash the host. |
| Agnostic telemetry | Domain logic emits events; the host decides stdout, files, or remote sinks. |

---

## Contributing from dev-master (submodule checkout)

If you work inside the monorepo at `dex/09-repos/zenOS`:

1. Make **zenOS-only** changes inside this submodule directory.
2. Follow the fork-and-PR workflow above against `k-dot-greyz/zenOS`.
3. Move any internal monorepo notes to `dev-master/dex/03-docs/guides/`—never commit them here.
4. After the upstream PR merges, bump the submodule pointer in dev-master using the superproject's submodule bump workflow.

---

## Pre-commit audit

Before committing, verify boundary hygiene and diff scope:

1. **Check for misplaced monorepo docs**
   - Run `git status`.
   - Are you adding files that describe **dev-master internals**, fork notes, or dex routing—not zenOS product behavior?
   - *Action*: Move those files to `dev-master/dex/03-docs/guides/` and unstage them here.
   - *Note*: Legitimate platform docs (`docs/`), Pokédex catalogs (`pokedex/`), and plugin manifests **do** belong here.

2. **Verify diff scope**
   - Run `git diff --name-status upstream/main` (or `origin/main`).
   - Revert unrelated files with `git restore <file>`.

3. **Check for diff noise**
   - Inspect `git diff` for formatting-only churn, debug prints, or commented-out code.

4. **Confirm secrets stay untracked**
   - Ensure `.env`, credentials, and local inbox payloads are not staged.

---

## Commit message style

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>
```

Common types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`.

Example:

```bash
docs(contributing): add Gumroad-inspired PR and issue guidelines
```

---

## Writing issues

Issues for enhancements, features, or refactors use this structure (templates in [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/)):

### What

What needs to change. Be concrete:

- Describe current behavior and desired behavior
- Who is affected (CLI users, plugin authors, mobile/Termux users, maintainers)
- Use a checkbox task list for multiple deliverables

### Why

Why this change matters:

- What user or maintainer problem does this solve?
- Link related issues, discussions, or prior PRs for context

Keep it short. The title should carry most of the weight—the body adds context the title cannot.

---

## Writing bug reports

A useful bug report includes:

- A quick summary and background
- Steps to reproduce (be specific; include sample commands or config)
- What you expected to happen
- What actually happens
- Environment (`python --version`, OS, Termux vs desktop, relevant `.env` keys redacted)
- Notes (suspected cause, things you tried)

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml) when filing on GitHub.

---

## Help

- [Open issues](https://github.com/k-dot-greyz/zenOS/issues) for bugs and feature requests.
- [Discussions](https://github.com/k-dot-greyz/zenOS/discussions) for questions and design brainstorming.
- Issues labeled `help wanted` are especially welcome for community PRs.

---

## When you're corrected, fix the docs

If a maintainer corrects your approach in review—a convention, a workflow, a gotcha that is not written down—do not only fix the code. Propose an edit to this guide in the same PR (or a fast follow-up) so the correction is captured once. The contributing guide should get a little smarter every time someone gets corrected.

---

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
