# Bloop — Git & Version Control Conventions

**Document Identifier:** BLOOP-GIT-CONV-V1  
**Authority:** Bloop Master Prompt & Prompt 04  

---

## 1. Branch Strategy

The Bloop monorepo uses a streamlined GitHub Flow model:
- `main`: The single authoritative production-ready branch. All commits must be verified via automated CI before merging.
- Feature branches: `feat/<feature-name>` (e.g. `feat/quantum-emotion-qnn`).
- Bugfix branches: `fix/<bug-description>` (e.g. `fix/tts-empty-text-validation`).
- Documentation branches: `docs/<doc-topic>` (e.g. `docs/architecture-suite`).

---

## 2. Conventional Commits Standard

All commit messages must adhere to the **Conventional Commits 1.0.0** specification:

```text
<type>(<scope>): <short summary>

[optional body explaining context and rationale]

[optional footer(s)]
```

### Approved Types:
- `feat`: A new feature (e.g. `feat(tts): add dynamic voice ingestion modal`).
- `fix`: A bug fix (e.g. `fix(audio): handle HTTP 206 range header seek offset`).
- `docs`: Documentation changes only (e.g. `docs(arch): add ADR-010 on microservices`).
- `style`: Formatting, missing semicolons, no code change.
- `refactor`: Code refactoring that neither fixes a bug nor adds a feature.
- `perf`: Performance improvements.
- `test`: Adding or correcting tests.
- `chore`: Build process, dependency updates, CI workflows.

---

## 3. Pull Request Guidelines

1. Every PR must pass all backend tests (`pytest`) and frontend tests/builds (`vitest`, `tsc -b`) in GitHub Actions.
2. PR descriptions should reference relevant requirement IDs (e.g. `Closes FR-001`).
3. PRs must contain zero secrets or sensitive keys.
