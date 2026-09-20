# Bloop Secrets Management & Security Governance Policy

**Document Identifier:** BLOOP-SEC-SECRETS-006  
**Status:** Approved Security Standard  
**Applies to:** Engineering, DevOps, Deployment, and CI/CD Operations  

---

## 1. Core Security Principle

> **No real secrets, passwords, tokens, private keys, or credentials may EVER be committed to the Git repository, printed in log streams, exposed in client bundles, or returned in API responses.**

All sensitive credentials must be injected dynamically at runtime via external environment configurations.

---

## 2. Configuration Classification Scheme

All platform variables are strictly classified into one of three security tiers:

| Tier | Description | Examples | Target Location | Permitted in Git? |
| :--- | :--- | :--- | :--- | :---: |
| **Public** | Non-sensitive endpoints and build flags safely consumable by client browsers. | `VITE_API_BASE_URL` | Frontend client bundle (`frontend/.env`, Vercel) | **Only in `.env.example`** |
| **Private** | Operational backend runtime configurations that are non-sensitive but should not be exposed publicly. | `APP_ENV`, `APP_DEBUG`, `PORT`, `CORS_ORIGINS`, `LOG_LEVEL`, `QUANTUM_MAX_QUBITS` | Backend runtime (`backend/.env`, Render Dashboard) | **Only in `.env.example`** |
| **Secret** | Highly confidential cryptographic keys, vendor tokens, and database passwords. Exposure causes immediate security breach. | `JWT_SECRET_KEY`, `ELEVENLABS_API_KEY`, `DATABASE_URL` | Render Dashboard Secrets, local git-ignored `.env` | **NEVER** |

---

## 3. Cryptographic Secret Generation Standards

Never invent, guess, or use human-readable words (e.g. `password123`, `bloop-secret`, `secret`) as credentials. Always generate secrets using cryptographically secure pseudorandom number generators (CSPRNG).

### 3.1 Generating `JWT_SECRET_KEY` (Minimum 256-bit / 64 hex characters)

#### Using Python 3.12+ (Recommended)
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Using OpenSSL
```bash
openssl rand -hex 32
```

#### Using Windows PowerShell
```powershell
$bytes = New-Object byte[] 32; (New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes($bytes); [BitConverter]::ToString($bytes) -replace '-'
```

---

## 4. Secret Storage & Hosting Governance

### 4.1 Local Development
- Local secrets reside strictly in `backend/.env`.
- `backend/.env` is excluded by root `.gitignore` (`.env`, `.env.*`).
- Developers must never check in `.env` or paste credentials into shared chat channels or screenshots.

### 4.2 Production (Render Backend)
- Production secrets (`DATABASE_URL`, `JWT_SECRET_KEY`, `ELEVENLABS_API_KEY`, `CORS_ORIGINS`) must be set in the **Render Web Service Dashboard**:
  `Render Dashboard -> Services -> bloop-backend -> Environment`
- Never write secrets into `render.yaml` or infrastructure-as-code files.

### 4.3 Production (Vercel Frontend)
- Public environment variable `VITE_API_BASE_URL` is configured in:
  `Vercel Dashboard -> Project Settings -> Environment Variables`
- **STRICT PROHIBITION:** Never define `DATABASE_URL`, `JWT_SECRET_KEY`, or `ELEVENLABS_API_KEY` in Vercel project variables. Any variable in the frontend project is compiled into client JavaScript.

---

## 5. Secret Rotation Procedure

Secrets must be rotated periodically or immediately upon team member offboarding or suspicion of leakage.

### 5.1 Rotating `JWT_SECRET_KEY`
1. Generate a new 64-character hex secret using Python `secrets.token_hex(32)`.
2. Update `JWT_SECRET_KEY` in Render Environment Variables.
3. Trigger a deployment restart in Render.
4. *Effect:* Existing user sessions will expire upon restart, requiring users to log in again with their password to receive new valid HMAC-signed tokens.
5. Verify health endpoint and login flows.

### 5.2 Rotating `ELEVENLABS_API_KEY`
1. Log in to ElevenLabs Console and generate a new API key.
2. Update `ELEVENLABS_API_KEY` in Render Web Service Environment Variables.
3. Trigger a deployment restart in Render.
4. Test voice synthesis in production to confirm connectivity.
5. Revoke and delete the old API key in the ElevenLabs Console.

### 5.3 Rotating PostgreSQL `DATABASE_URL`
1. In Render Dashboard, open the managed PostgreSQL instance.
2. Navigate to Access -> Reset Password / Rotate Credentials.
3. Update `DATABASE_URL` in the FastAPI Web Service settings.
4. Restart the Web Service and confirm database connectivity via `/api/v1/health`.

---

## 6. Compromised Secret Incident Response Protocol

If a production credential, database URL, or private API key is ever accidentally committed to GitHub or exposed in logs:

```text
STEP 1: IMMEDIATE CREDENTIAL REVOCATION
        ↓
STEP 2: ROTATE & REDEPLOY PRODUCTION WITH NEW CREDENTIAL
        ↓
STEP 3: PURGE COMMIT FROM GIT HISTORY (git filter-repo / BFG)
        ↓
STEP 4: AUDIT ACCESS LOGS FOR MALICIOUS USE
        ↓
STEP 5: POST-MORTEM & AUTOMATED PRE-COMMIT ENFORCEMENT
```

### Detailed Actions:
1. **Immediate Revocation:** Never simply push a new commit that deletes the secret. Any credential pushed to GitHub must be considered immediately compromised by automated scanners. Revoke the key in the vendor dashboard (ElevenLabs / Render DB) immediately.
2. **Deploy Replacement:** Generate and configure a clean new credential in the production hosting dashboard.
3. **Purge Git History:** If pushed to remote, rewrite repository history using `git filter-repo` or contact repository administrator to force-push the purged tree.
4. **Audit Logs:** Review Render and ElevenLabs usage logs during the exposure window to identify unauthorized queries or credit drain.
5. **Post-Mortem:** Verify that `.gitignore` contains all relevant file patterns.

---

## 7. CI/CD & GitHub Actions Policy

1. **Least Privilege:** CI/CD runners only receive credentials required for their specific pipeline stage.
2. **Mocking External Services:** Automated unit and integration tests must run with `APP_ENV=test` and offline simulation. Tests must never require live ElevenLabs credentials or production database connections.
3. **No Secret Echoing:** CI scripts must never use `echo $SECRET` or print environment dumps in workflow runs.
