# Commit Workflow Checklist

**Remember to carefully review the code before committing. Ensure that it accurately replaces the highlighted code, contains no missing lines, and has no issues with indentation. Thoroughly test & benchmark the code to ensure it meets the requirements.**

---

## Pre-Commit Review

### Code Quality
- [ ] Code has been carefully reviewed for accuracy
- [ ] All highlighted code sections have been properly replaced
- [ ] No missing lines or incomplete implementations
- [ ] Indentation is correct and consistent throughout
- [ ] Code follows project style guidelines and conventions
- [ ] Variable and function names are descriptive and clear
- [ ] No unused variables, imports, or commented-out code
- [ ] Error handling is appropriate and comprehensive

### Testing & Validation
- [ ] Code has been thoroughly tested locally
- [ ] All existing tests pass successfully
- [ ] New tests have been added for new functionality
- [ ] Code has been benchmarked for performance
- [ ] Edge cases have been identified and tested
- [ ] Integration with existing code has been verified
- [ ] Manual testing completed where appropriate

### Documentation
- [ ] Code includes clear and helpful comments
- [ ] Complex logic is well-documented
- [ ] API changes are documented
- [ ] README updated if necessary
- [ ] CHANGELOG updated if applicable

#### Documentation maintenance
When your change affects platform behavior, public APIs, or repository relationships, also verify:

- [ ] **Feature docs** — Updated guides under `docs/` (and `README.md` when user-facing setup or overview changes) if behavior, CLI flags, or setup steps changed
- [ ] **Architecture decisions** — Added or updated an ADR entry in `DECISION_LOG.md` when introducing, reversing, or materially changing an architectural decision
- [ ] **Conversation archive** — Archived valuable design conversations or session notes to `docs/archive/` when they contain durable rationale not captured in active docs
- [ ] **Repository switchboard** — Updated `repos/registry.yaml` when repository relationships, remotes, or ecosystem switchboard entries changed

> **Boundary reminder** ([CONTRIBUTING.md](../CONTRIBUTING.md)): platform documentation belongs in this repo (`docs/`, `pokedex/`). Internal dev-master monorepo guides stay in the superproject — never commit dex routing or fork-only SOPs here.
>
> **Rollout note**: `DECISION_LOG.md`, `docs/archive/`, and `repos/registry.yaml` are introduced by the documentation knowledge-management epic (issues #21–#27). If a path is not present yet, record the decision or relationship change in the relevant tracking issue until that file lands.

### Security & Dependencies
- [ ] No security vulnerabilities introduced
- [ ] No sensitive data (keys, passwords, tokens) in code
- [ ] Dependencies are up to date and necessary
- [ ] No debugging code or console logs left in production code

### Git & Version Control
- [ ] Commit message is clear and descriptive
- [ ] Changes are atomic and focused on a single concern
- [ ] Branch is up to date with main/target branch
- [ ] No merge conflicts
- [ ] Files staged for commit are correct

---

## Post-Commit Actions

- [ ] Push changes to remote repository
- [ ] Create pull request with proper description
- [ ] Link related issues in PR
- [ ] Request reviews from appropriate team members
- [ ] Monitor CI/CD pipeline status
- [ ] Address any automated test failures

---

## Notes

Use this checklist before every commit to maintain code quality and reduce errors. Taking the time to review thoroughly now saves debugging time later.
