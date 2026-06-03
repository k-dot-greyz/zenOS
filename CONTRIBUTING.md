# Contributing to zenOS 🌌

Thank you for considering contributing to zenOS! This repository is the core platform repository of the zenOS ecosystem. To ensure a clean, maintainable, and highly decoupled architecture, all contributions must strictly adhere to our development standards and protocols.

---

## 🏁 1. The Prime Directive: Pure Code in Submodules, Guides in Superproject

When working within the zenOS ecosystem, we maintain a strict boundary between the superproject and its submodules:
1. **The Superproject (`dev-master`)**: Our private workspace, orchestration framework, and internal documentation repository.
2. **This Submodule (`zenOS`)**: The core, open-source-ready platform repository.

### ⚠️ The Boundary Violation Rule
**NEVER commit internal documentation, fork-specific guides, or monorepo-specific configurations into this repository.**

* **Why?** This repository is designed to be a clean, independent product. Misplacing internal files (like fork notes or superproject-specific guides) inside this directory structure pollutes the upstream repository, causes PR rejections, and leaks internal workspace details.
* **The Standard**: Keep this repository strictly limited to **pure code changes** (and its own public-facing documentation/API references) that directly implement features or bug fixes. All internal guides, fork-specific documentation, and monorepo-specific notes must live in the superproject under `dex/03-docs/guides/`.

---

## 🔄 2. The Fork-and-PR Workflow

When contributing to zenOS, follow this precise workflow to ensure a clean, isolated, and mergeable contribution:

### Step 1: Configure Remotes
Ensure your local clone has both the official `upstream` and your personal fork `origin` configured:
```bash
# Check existing remotes
git remote -v

# If upstream is missing, add it
git remote add upstream https://github.com/k-dot-greyz/zenOS.git
```

### Step 2: Create a Clean Feature Branch
Always branch off the latest `upstream/main`:
```bash
git fetch upstream
git checkout -b feat/your-feature-name upstream/main
```

### Step 3: Implement Pure Code Changes
Make your changes to the application code. Ensure:
* No temporary files, local logs, or environment files are tracked.
* No internal markdown files or monorepo-specific guides are created here.
* Code matches the existing style and conventions.

### Step 4: Run Pre-Commit Audit Checks
Before staging or committing, run the audit checklist (see Section 4).

### Step 5: Commit and Push to Your Fork
Commit with a clear, conventional commit message and push to your fork (`origin`):
```bash
git commit -m "feat(pkm): implement dynamic schema validation for incoming packets"
git push -u origin HEAD
```

### Step 6: Create the Pull Request
Create the PR against the upstream repository using the `gh` CLI or the GitHub UI:
```bash
gh pr create --repo k-dot-greyz/zenOS --title "feat(pkm): implement dynamic schema validation" --body "..."
```

---

## 🏛️ 3. GlitchWorks Agnostic Architecture Protocol (/architecture-base)

All development within zenOS must strictly adhere to the **GlitchWorks Agnostic Architecture Protocol**. This ensures that all modules remain completely decoupled, self-contained, and highly maintainable.

### 3.1. Zero Hardcoding (Dynamic State Configuration)
* **Rule**: No magic strings, static network ports, or fixed directory paths shall exist within the domain logic.
* **Application**: zenOS must never contain hardcoded hostnames, ports, or superproject-specific paths. All configurations (such as API endpoints, database paths, and server ports) must be dynamically configured via environment variables, configuration files, or dependency injection at startup.

### 3.2. Polymorphism by Default (Interface-Driven Contracts)
* **Rule**: Depend on abstractions, not concretions.
* **Application**: Core logic must interact with external dependencies through abstract interfaces or standard APIs. You must be able to swap out a real service (e.g., a database or LLM provider) for a dummy/mock service at initialization without altering a single line of the internal domain logic.

### 3.3. Open Piping (Strict Inter-Process Communication)
* **Rule**: Modules must communicate via strictly typed, isolated message events rather than direct state mutation.
* **Application**: Establish strict, serializable contracts for inter-module communication. Utilize message passing or standard event routers rather than direct state mutation or global variable sharing.

### 3.4. Boundary Validation (The "Hostile Edge")
* **Rule**: Never trust incoming payloads. The core logic must be protected by a rigorous validation layer.
* **Application**: Validate all incoming payloads at the boundary (e.g., using schema validation, JSON parsing try-catch blocks, or strict type checks) before processing them in the domain logic.

### 3.5. State Hydration & Dehydration
* **Rule**: Systems must be capable of pausing, exporting their truth, and resuming from a snapshot.
* **Application**: Systems that maintain state must support serializing their state to standard formats (JSON, SQLite dumps, etc.) and cleanly restoring from them, allowing seamless teardown and reconstruction.

### 3.6. Graceful Degradation (Predictable Failure)
* **Rule**: When a pipe breaks or a dependency fails, the system must fail safely and transparently.
* **Application**: Avoid unhandled exceptions. If an external API or service goes offline, the system must catch the timeout/error, log the failure, and return a safe fallback state rather than crashing the host process.

### 3.7. Agnostic Telemetry & Observability
* **Rule**: Domain logic must emit its telemetry without knowing where the logs are going.
* **Application**: Inject a generic logging or telemetry provider into constructors/initializers. The core logic emits structured event data, leaving the host environment to decide if this goes to `stdout`, a local file, or a remote ingestion webhook.

---

## 📋 4. Pre-Commit Submodule Audit Checklist

Before committing changes, run this quick checklist to verify boundary hygiene:

1. **Check for Misplaced Files**:
   * Run `git status` inside the repository.
   * Are there any `.md`, `.txt`, `.json`, or `.yaml` files that describe internal workflows, fork notes, or monorepo standards?
   * *Action*: Move them to the superproject's `dex/03-docs/guides/` and delete them from this repository's staging area.
2. **Verify Diff Scope**:
   * Run `git diff --name-status upstream/main`.
   * Are there any unexpected files modified?
   * Are there any changes to files that are unrelated to the feature or bug fix?
   * *Action*: Revert unrelated changes using `git restore <file>`.
3. **Check for "Diff Noise"**:
   * Run `git diff` and inspect the changes.
   * Did you introduce any formatting-only changes, trailing whitespace, or commented-out debug code?
   * *Action*: Clean up formatting and debug code before committing.

---

## 📝 5. Commit Message Style

We use conventional commits for a clear, readable project history:
```
<type>(<scope>): <short summary>
```

### Common Types:
* `feat`: A new feature
* `fix`: A bug fix
* `docs`: Documentation changes
* `style`: Code style/formatting (no functional changes)
* `refactor`: Code refactoring (no new features or bug fixes)
* `perf`: Performance improvements
* `test`: Adding or updating tests
* `chore`: Maintenance tasks or dependency updates

### Example:
```bash
docs(contributing): add baseline contributing workflow and agnostic architecture guidelines
```

---

*Remember: Every contribution, no matter how small, makes zenOS better. Thank you for building with us!* 🧘⚡
