# Contributing to zenOS 🌌

Thank you for considering contributing to zenOS! This repository is the **core platform** of the zenOS ecosystem—the standalone product repo at [k-dot-greyz/zenOS](https://github.com/k-dot-greyz/zenOS). It is also linked as a git submodule from the private superproject [`dev-master`](https://github.com/k-dot-greyz/dev-master) at `dex/09-repos/zenOS`.

To keep the platform clean, maintainable, and decoupled, all contributions must follow the standards below.

---

## 🏁 1. The Prime Directive: Platform Code Here, Internal Guides in dev-master

We maintain a strict boundary between this repository and the monorepo workspace:

1. **This repository (`zenOS`)**: Core platform code, public-facing docs, tests, CI, and product configuration (for example `docs/`, `pokedex/`, plugin manifests).
2. **The superproject (`dev-master`)**: Private workspace orchestration, dex routing, submodule bump workflows, and **internal** monorepo guides.

### ⚠️ The Boundary Violation Rule

**NEVER commit internal monorepo documentation, fork-specific guides, or dev-master-only configuration into this repository.**

* **Why?** zenOS is designed to stand alone as a product. Misplacing internal files (fork notes, superproject SOPs, dex routing docs) pollutes upstream history, causes PR rejections, and leaks private workspace details.
* **What belongs here**: Application code under `zen/`, public guides under `docs/`, platform YAML such as `pokedex/` and plugin specs, tests, scripts, and CI under `.github/`.
* **What belongs in dev-master**: Internal guides under `dex/03-docs/guides/` (for example submodule bump, fork workflow, and monorepo agent protocols).

---

## 🗂️ 2. Repository Layout

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
| `test_*.py` | Root-level pytest modules (see CI) |

For AI agent onboarding and platform conventions, start with [`docs/AI_INSTRUCTIONS.md`](docs/AI_INSTRUCTIONS.md). For local environment setup, see [`docs/guides/DEV_ENVIRONMENT_SETUP.md`](docs/guides/DEV_ENVIRONMENT_SETUP.md).

---

## 🔄 3. The Fork-and-PR Workflow

Whether you cloned zenOS directly or via `dev-master`, use this workflow for upstream contributions:

### Step 1: Configure Remotes

Ensure your local clone can reach the canonical repo and your fork (if you use one):

```bash
git remote -v

# Canonical upstream (required)
git remote add upstream https://github.com/k-dot-greyz/zenOS.git 2>/dev/null || true

# Personal fork (recommended for external contributors)
# git remote set-url origin https://github.com/<your-user>/zenOS.git
```

Maintainers with direct push access may use `origin` as the canonical repo; fork contributors should push feature branches to their fork and open PRs against `k-dot-greyz/zenOS`.

### Step 2: Create a Clean Feature Branch

Branch from the latest upstream default branch (`main`):

```bash
git fetch upstream
git checkout -b feat/your-feature-name upstream/main
```

Use branch prefixes such as `feat/`, `fix/`, `docs/`, `refactor/`, `test/`, or `chore/`.

### Step 3: Implement Focused Changes

Make scoped changes that match existing conventions:

* No tracked secrets, local `.env` files, or temporary logs.
* No dev-master-only markdown or monorepo routing docs.
* Public documentation updates belong in `docs/` when they describe zenOS itself.
* Match existing Python style (`black` line length 100) and module layout under `zen/`.

### Step 4: Run Local Quality Gates

Before committing, run the checks CI expects (see [`.github/workflows/zenos-ci.yml`](.github/workflows/zenos-ci.yml)):

```bash
python -m pip install -e ".[dev]"
cp env.example .env  # configure keys locally; never commit .env

# Formatting & lint (CI uses black/isort/flake8; pyproject also defines ruff/mypy)
black --check .
isort --check-only .

# Tests (root-level test_*.py modules)
pytest --cov=. --cov-report=term-missing -v
```

Optional but recommended during development:

```bash
ruff check .
mypy zen/ --ignore-missing-imports --no-strict-optional
```

### Step 5: Pre-Commit Audit

Run the checklist in [Section 6](#-6-pre-commit-audit-checklist) and review [`.github/COMMIT_WORKFLOW_CHECKLIST.md`](.github/COMMIT_WORKFLOW_CHECKLIST.md).

### Step 6: Commit and Push

Use [conventional commits](#-7-commit-message-style):

```bash
git commit -m "feat(pkm): implement dynamic schema validation for incoming packets"
git push -u origin HEAD
```

### Step 7: Open a Pull Request

Target `main` on the upstream repository. Use the PR template and `gh` when possible:

```bash
gh pr create --repo k-dot-greyz/zenOS \
  --base main \
  --title "feat(pkm): implement dynamic schema validation" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md
```

---

## 🏛️ 4. GlitchWorks Agnostic Architecture Protocol (/architecture-base)

All development within zenOS must adhere to the **GlitchWorks Agnostic Architecture Protocol**. This keeps modules decoupled, testable, and portable across desktop, mobile (Termux), and offline modes.

### 4.1. Zero Hardcoding (Dynamic State Configuration)

* **Rule**: No magic strings, static network ports, or fixed directory paths in domain logic.
* **Application**: Never hardcode hostnames, ports, or dev-master paths. Configure API endpoints, storage paths, and service ports via environment variables, config files, or dependency injection at startup (`env.example` documents common variables).

### 4.2. Polymorphism by Default (Interface-Driven Contracts)

* **Rule**: Depend on abstractions, not concretions.
* **Application**: Core logic should interact with LLM providers, storage, and telemetry through injectable interfaces so implementations can be swapped (for example OpenRouter vs offline providers under `zen/providers/`).

### 4.3. Open Piping (Strict Inter-Process Communication)

* **Rule**: Modules communicate via strictly typed, isolated message events rather than direct state mutation.
* **Application**: Use serializable contracts for agent orchestration, plugin events, and CLI I/O. Avoid hidden global singletons for cross-module state.

### 4.4. Boundary Validation (The "Hostile Edge")

* **Rule**: Never trust incoming payloads.
* **Application**: Validate external input at boundaries—CLI arguments, plugin manifests, inbox ingestion, and provider responses—before domain logic runs (Pydantic models and schema checks are preferred).

### 4.5. State Hydration & Dehydration

* **Rule**: Systems must export and restore their truth from snapshots.
* **Application**: Stateful subsystems (PKM storage, context managers, plugin registry) should support serialize/restore flows using standard formats (JSON, SQLite, YAML).

### 4.6. Graceful Degradation (Predictable Failure)

* **Rule**: When a dependency fails, the system must fail safely and transparently.
* **Application**: Missing API keys, offline providers, or unavailable MCP services must surface actionable errors and safe fallbacks—not unhandled crashes in the host process.

### 4.7. Agnostic Telemetry & Observability

* **Rule**: Domain logic emits telemetry without knowing the sink.
* **Application**: Inject loggers or structured event emitters. Host environments decide whether output goes to `stdout`, files, or remote ingestion.

---

## 🤝 5. Contributing from dev-master (Submodule Checkout)

If you work inside the monorepo at `dex/09-repos/zenOS`:

1. Make **zenOS-only** changes inside this submodule directory.
2. Follow the fork-and-PR workflow above against `k-dot-greyz/zenOS`.
3. Move any internal monorepo notes to `dev-master/dex/03-docs/guides/`—never commit them here.
4. After the upstream PR merges, bump the submodule pointer in dev-master using the superproject's submodule bump workflow.

---

## 📋 6. Pre-Commit Audit Checklist

Before committing, verify boundary hygiene and diff scope:

1. **Check for misplaced monorepo docs**
   * Run `git status`.
   * Are you adding `.md`, `.txt`, `.json`, or `.yaml` files that describe **dev-master internals**, fork notes, or dex routing—not zenOS product behavior?
   * *Action*: Move those files to `dev-master/dex/03-docs/guides/` and remove them from this repo's staging area.
   * *Note*: Legitimate platform docs (`docs/`), Pokédex catalogs (`pokedex/`), and plugin manifests (`examples/`, `zen/pkm/`) **do** belong here.

2. **Verify diff scope**
   * Run `git diff --name-status upstream/main`.
   * Revert unrelated files with `git restore <file>`.

3. **Check for diff noise**
   * Inspect `git diff` for formatting-only churn, debug prints, or commented-out code.
   * *Action*: Clean up before committing.

4. **Confirm secrets stay untracked**
   * Ensure `.env`, credentials, and local inbox payloads are not staged.

---

## 📝 7. Commit Message Style

We use [Conventional Commits](https://www.conventionalcommits.org/) for readable history:

```
<type>(<scope>): <short summary>
```

### Common types

* `feat`: New feature
* `fix`: Bug fix
* `docs`: Documentation only
* `style`: Formatting (no logic change)
* `refactor`: Code restructuring
* `perf`: Performance improvement
* `test`: Tests only
* `chore`: Maintenance or dependency updates
* `ci`: CI/workflow changes

### Example

```bash
docs(contributing): add baseline contributing workflow and agnostic architecture guidelines
```

---

*Every contribution makes zenOS better. Thank you for building with us!* 🧘⚡
