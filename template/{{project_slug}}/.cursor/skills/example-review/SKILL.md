---
name: code-review
description: Systematic code review with security, quality, and architecture checks.
trigger_phrases:
  - "review this code"
  - "check this PR"
  - "code review"
  - "review my changes"
degrees_of_freedom: medium
---

# Code Review Skill

When triggered, follow this protocol:

## Steps

1. **Scope**: Identify the changed files and understand the diff
2. **Architecture**: Check against `docs/ARCHITECTURE.md` layering rules
3. **Security**: Look for injection risks, hardcoded secrets, unsafe operations
4. **Quality**: Verify file size limits, naming conventions, test coverage
5. **Evidence**: Cite specific lines for each finding

## Output Format

For each finding:
- **Severity**: BLOCKING / WARNING / INFO
- **File**: path and line number
- **Issue**: what's wrong (specific, not vague)
- **Fix**: how to fix it (actionable)

## Boundaries

This skill reviews code quality and security. It does NOT:
- Make architectural decisions (use solution-architect agent)
- Write tests (use test-architect agent)
- Fix the issues it finds (it reports, you fix)

## References

See `references/review-checklist.md` for the detailed checklist.
