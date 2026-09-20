# Bloop — Vercel Deployment Specification & Runbook

**Document Identifier:** BLOOP-DEPLOY-VERCEL-006  
**Status:** Approved Deployment Guide  
**Target Platform:** Vercel Global Edge CDN (React 19 + Vite Rollup)  
**Authority:** Prompt 06 — Environment Configuration, Secrets Management & Profiles  

---

## 1. Executive Frontend Deployment Architecture

Bloop's Single Page Application (SPA) is hosted on **Vercel's Global Edge Network**:
- **Framework & Runtime:** React 19 + TypeScript bundled via Vite Rollup.
- **Delivery Model:** Pre-compiled immutable static assets (HTML, CSS, JS, SVG, WebP) cached across Vercel's worldwide Edge CDN nodes.
- **SPA Routing:** `frontend/vercel.json` provides rewrite rules ensuring client-side navigation (React Router) functions seamlessly on browser page reloads without 404 errors.

```
                   GitHub Repository (main branch)
                                 │
                                 ▼
                    Vercel Edge Pipeline Trigger
                                 │
                     ┌───────────┴───────────┐
                     ▼                       ▼
           cd frontend/            npm run build (Vite)
                     │                       │
                     └───────────┬───────────┘
                                 │
                                 ▼
                     Global Edge CDN Distribution
                                 │
                     ┌───────────┴───────────┐
                     ▼                       ▼
            https://bloop.vercel.app  (Sub-100ms FCP)
```

---

## 2. Declarative SPA Routing Rewrite (`frontend/vercel.json`)

To allow React Router to manage client routes (`/history`, `/favorites`, `/quantum`, `/profile`) on direct URL entry or refresh, `frontend/vercel.json` maps all paths to `index.html`:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

---

## 3. Project Configuration Settings in Vercel

When importing the GitHub repository into Vercel:

| Configuration Setting | Required Value | Notes |
| :--- | :--- | :--- |
| **Framework Preset** | `Vite` | Vercel automatically detects and optimizes Vite builds. |
| **Root Directory** | `frontend` | Monorepo target directory for client code. |
| **Build Command** | `npm run build` | Runs `tsc -b && vite build` (typechecking + bundling). |
| **Output Directory** | `dist` | Default production build output from Vite. |
| **Node.js Version** | `20.x` or `22.x` | Modern LTS Node.js engine. |

---

## 4. Environment Variables Specification

Under **Project Settings -> Environment Variables**, configure the single required public variable:

| Variable Name | Environment | Target Value | Description |
| :--- | :--- | :--- | :--- |
| `VITE_API_BASE_URL` | **Production** | `https://bloop-backend.onrender.com` | Production Render Web Service API. |
| `VITE_API_BASE_URL` | **Preview** | `https://bloop-backend-preview.onrender.com` (or dev staging URL) | Staging/Preview backend API. |

### Strict Frontend Security Invariants:
1. **Public-Only Configuration:** Only variables prefixed with `VITE_` can be processed by Vite.
2. **ZERO Backend Secrets:** Never configure `DATABASE_URL`, `JWT_SECRET_KEY`, or `ELEVENLABS_API_KEY` on Vercel. Any variable provided in Vercel is baked into client JavaScript bundles and visible to all users.
3. **Automated Audit:** The frontend configuration module (`frontend/src/app/config.ts`) runs a runtime security audit that checks `import.meta.env` and logs an alert if any private credential pattern is ever introduced.

---

## 5. Deployment Step-by-Step Runbook

1. Log into **Vercel Dashboard** (vercel.com).
2. Click **Add New...** > **Project**.
3. Import your GitHub repository (`bloop`).
4. In the Project Setup screen:
   - Click **Edit** next to **Root Directory** and select `frontend`.
   - Ensure **Framework Preset** is set to `Vite`.
5. Under **Environment Variables**:
   - Add `VITE_API_BASE_URL` with your Render backend URL (e.g. `https://bloop-backend.onrender.com`).
6. Click **Deploy**.
7. Vercel will build the TypeScript bundle, optimize assets, and distribute them to edge CDN nodes worldwide.
8. Copy your production Vercel domain (e.g. `https://bloop.vercel.app`) and ensure it is listed in the Render backend's `CORS_ORIGINS` environment variable.
