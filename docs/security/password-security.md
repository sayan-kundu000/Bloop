# Bloop Password Security Specification

## 1. Password Storage Standard

Bloop enforces **zero plaintext password storage**. Under no circumstances are raw passwords, plaintext credentials, or simple hashes (MD5, SHA-1, SHA-256) stored in the database, caches, logs, or backups.

Passwords are exclusively persisted as salted, one-way adaptive cryptographic hashes using **bcrypt**:

```python
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
```

---

## 2. Password Policy Rules

Application policy validates credentials prior to database transaction execution:

- **Required**: Passwords cannot be missing, empty (`""`), or contain whitespace only.
- **Minimum Length**: 6 characters (avoids arbitrary friction while preventing trivial passwords).
- **Maximum Length**: 100 characters (mitigates denial-of-service via massive hash payloads).
- **Policy Enforcement**: Handled by `validate_password_policy(password)` in `backend.app.services.auth.password`.

---

## 3. Timing-Safe Verification

To mitigate user enumeration and timing side-channel attacks:

1. Verification uses `bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))`, which executes in constant time.
2. If an account lookup yields no user in the database, `AuthService.authenticate_user` executes verification against a pre-computed dummy hash before raising `InvalidCredentialsException`.
3. Login responses return the uniform error code `INVALID_CREDENTIALS` (HTTP 401) regardless of whether the email was not found or the password was incorrect.

---

## 4. Secret Masking & Redaction

- **Responses**: The User API schemas (`UserResponse`, `UserDetailResponse`) strictly exclude `hashed_password` and any credential fields.
- **Logging**: The centralized `SecretMaskingFilter` scrubs credential patterns from logging records.
- **Exceptions**: Exception handlers catch and redact internal details, preventing stack traces or hash leakage to external clients.
