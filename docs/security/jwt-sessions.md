# Bloop JWT Session Architecture

## 1. Token Anatomy & Claims

Bloop JSON Web Tokens (JWT) are cryptographically signed identity assertions containing strictly minimal claims:

```json
{
  "sub": "42",
  "iat": 1726590000,
  "exp": 1726676400
}
```

### Claim Definitions:
- **`sub` (Subject)**: Stable canonical user identifier (`str(user.id)`). Email is intentionally omitted to avoid identity drift on email updates.
- **`iat` (Issued At)**: UTC timestamp recording token generation.
- **`exp` (Expiration)**: UTC timestamp defining token expiration window (`ACCESS_TOKEN_EXPIRE_MINUTES`).

### Explicitly Excluded Claims:
- Passwords or password hashes.
- External API keys (e.g. ElevenLabs secret key).
- User profile data, audio text, or file paths.

---

## 2. Cryptographic Algorithm & Secret Management

- **Algorithm**: Pinned strictly to `HS256` (`settings.JWT_ALGORITHM`). Tokens with `alg: "none"` or mismatched algorithms are rejected immediately.
- **Signing Secret**: Loaded from `JWT_SECRET_KEY` via Twelve-Factor environment configuration.
- **Production Guardrails**: In `APP_ENV=production`, `Settings` validator enforces `JWT_SECRET_KEY` length >= 32 characters and forbids known default development placeholders.

---

## 3. Cookie Configuration & Session Transport

```python
response.set_cookie(
    key="access_token",
    value=token_string,
    httponly=True,
    secure=(settings.APP_ENV == "production"),
    samesite="none" if settings.APP_ENV == "production" else "lax",
    path="/",
    max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
)
```

- **HttpOnly**: Completely blocks JavaScript `document.cookie` access, protecting against XSS credential theft.
- **Secure**: Guaranteed over HTTPS in production.
- **SameSite**: Set to `None` in production to allow credentialed cross-origin requests between Vercel (`bloop.vercel.app`) and Render (`bloop.onrender.com`), and `Lax` in local development.

---

## 4. CSRF Defense Strategy

Cross-Site Request Forgery (CSRF) protection is maintained through defense-in-depth:
1. **CORS Origin Validation**: Starlette `CORSMiddleware` strictly validates incoming `Origin` headers against the approved `CORS_ORIGINS` whitelist. Wildcard `*` origins with credentials are expressly prohibited.
2. **SameSite Cookie Controls**: Restricts unintended browser transmission of authentication cookies on cross-origin navigation.
3. **Custom Headers**: For programmatic API interactions, client applications transmit `Authorization: Bearer <token>`, which cannot be forged cross-origin without a preflight CORS check.
