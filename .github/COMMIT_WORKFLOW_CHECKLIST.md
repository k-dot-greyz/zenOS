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
- [ ] CHANGELOG.md updated in [Unreleased] section
- [ ] Following conventional commit format (see CONTRIBUTING.md)

### Security & Dependencies
- [ ] No security vulnerabilities introduced
- [ ] No sensitive data (keys, passwords, tokens) in code
- [ ] Dependencies are up to date and necessary
- [ ] No debugging code or console logs left in production code

### Git & Version Control
- [ ] Commit message follows conventional format: type(scope): description
- [ ] Changes are atomic and focused on a single concern
- [ ] Branch is up to date with main/target branch
- [ ] No merge conflicts
- [ ] Files staged for commit are correct
- [ ] Breaking changes noted with BREAKING CHANGE: footer

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
