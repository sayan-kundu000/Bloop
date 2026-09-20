# Bloop — Dependency Management & Security Audit Policy

**Document Identifier:** BLOOP-DEP-MGMT-V1  
**Project:** Bloop — AI Text-to-Speech & Quantum Intelligence Platform  
**Target Milestone:** Dependency Governance & Supply Chain Security  
**Status:** Approved Technical Guide  
**Authority:** Bloop Master Prompt & Prompt 03  

---

## 1. Governance Principles

To prevent dependency bloat, security vulnerabilities, and maintenance rot, Bloop enforces four non-negotiable package management rules:
1. **The Justification Gate:** Every new package must solve a problem that cannot be addressed cleanly using native language standard libraries or the existing framework stack.
2. **Minimal Bundle & Container Weight:** Frontend libraries must be tree-shakeable. Python libraries must provide pre-compiled wheels for Linux x86_64 to ensure fast Render builds.
3. **Continuous Vulnerability Auditing:** Dependencies are audited regularly against national vulnerability databases using `pip-audit` and `npm audit`.
4. **No Unapproved Infrastructure Tools:** Introducing distributed infrastructure (Kafka, Celery, Redis, Kubernetes) is strictly prohibited without formal architectural approval.

---

## 2. Python Dependency Management (`backend/`)

### 2.1 Dependency File Structure
- **`backend/requirements.txt`:** Production dependencies required to execute the FastAPI application, manage PostgreSQL persistence, communicate with ElevenLabs, and run Qiskit/PennyLane simulations.
- **`backend/requirements-dev.txt`:** Development, testing, linting, and formatting tools. References `requirements.txt` via `-r requirements.txt`.

### 2.2 Adding a Python Dependency
When adding a dependency to `backend/requirements.txt`:
1. Check whether Python 3.11's standard library (`asyncio`, `dataclasses`, `uuid`, `math`, `json`, `datetime`) already provides the capability.
2. Pin the dependency using a verified compatible release constraint:
   ```text
   # CORRECT: Specifies minimum verified version with major breaking protection
   httpx>=0.27.0,<1.0.0

   # PROHIBITED: Unpinned, risks silent breaking changes
   httpx
   ```
3. Test compatibility locally in your virtual environment:
   ```bash
   pip install -r backend/requirements.txt
   pytest backend/tests -v
   ```

### 2.3 Python Security Auditing
Audit Python dependencies for known Common Vulnerabilities and Exposures (CVEs) using `pip-audit`:

```bash
# Install pip-audit if not present
pip install pip-audit

# Scan production requirements
pip-audit -r backend/requirements.txt
```

---

## 3. Frontend Dependency Management (`frontend/`)

### 3.1 State and Utility Boundary Rules
- **Server State:** Use `@tanstack/react-query`. Do **not** install SWR, RTK Query, or custom caching libraries.
- **Client State:** Use `zustand`. Do **not** install Redux, MobX, Recoil, or Jotai.
- **Icons:** Use `lucide-react`. Do **not** import multiple disparate icon packages.
- **Utilities:** Prefer modern native JavaScript (`Intl.DateTimeFormat`, `Intl.NumberFormat`, `Array.prototype.flatMap`) over heavyweight utility libraries like `lodash` or `moment.js`.

### 3.2 Adding a Frontend Dependency
```bash
cd frontend

# Production runtime dependency
npm install <package-name>

# Development or test-only dependency
npm install -D <package-name>
```

### 3.3 Frontend Security Auditing
Scan Node packages for vulnerabilities:

```bash
cd frontend
npm audit
```

If vulnerabilities are detected, review the fix before running `npm audit fix`. Never run `npm audit fix --force` without verifying breaking changes.

---

## 4. Prohibited Dependencies Quick Reference

The following packages are **explicitly disallowed** in the Bloop codebase:

| Disallowed Package | Reason | Approved In-Tree Alternative |
| :--- | :--- | :--- |
| `celery`, `rq`, `dramatiq` | Adds worker containers, task queues, and deployment overhead. | Native FastAPI `asyncio` tasks with strict execution limits. |
| `redis`, `memcached` | Adds an external stateful caching cluster to maintain and pay for. | In-memory TanStack Query client cache & PostgreSQL indexes. |
| `pika`, `confluent-kafka` | Event-driven broker complexity unwarranted for intermediate scale. | Direct, synchronous/async REST JSON communication. |
| `moment`, `date-fns` | Heavy bundle size (~70 KB) for simple formatting needs. | Native browser `Intl.DateTimeFormat` API. |
| `lodash`, `underscore` | Native ES2022+ features replace almost all legacy utility functions. | Native JavaScript Array, Object, and String methods. |
| `redux`, `mobx` | Excessive boilerplate, state duplication, and performance traps. | TanStack Query for server data + Zustand for UI state. |
