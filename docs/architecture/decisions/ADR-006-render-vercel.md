# ADR-006: Cloud Deployment on Render (FastAPI + PostgreSQL) and Vercel (React SPA)

## Status
**Accepted**

## Context
Bloop needs a reliable, cost-effective, and low-maintenance deployment architecture for continuous delivery from GitHub. The deployment target must satisfy intermediate-level engineering practices without the operational burden of Kubernetes, multi-cloud setups, or complex server management.

Alternatives considered:
1. **Self-hosted VPS (DigitalOcean / AWS EC2):** Full control, but requires manual OS patching, reverse proxy (Nginx) configuration, SSL certificate renewal (Certbot), and custom deployment scripts.
2. **All-in-one Docker on single VM:** Good portability, but single point of failure and manual database backup management.
3. **PaaS Split Architecture (Render + Vercel):** Render manages the containerized Python web service and managed PostgreSQL database; Vercel provides global CDN edge hosting for the static React SPA.

## Decision
Adopt a dual-platform PaaS model:
1. **Render:** Hosts the Python FastAPI backend service and the managed PostgreSQL database instance.
2. **Vercel:** Hosts the compiled React 19 + Vite frontend Single Page Application on its global Edge Network.
3. **GitHub:** Serves as the single source of truth for continuous deployment via webhook triggers.

## Rationale
1. **Zero Server Maintenance:** Both platforms provide automated SSL/TLS provisioning, HTTP/2 and HTTP/3 support, health checks, and Git-driven deployments.
2. **Optimal Edge Delivery:** The static React bundle is cached worldwide on Vercel's CDN, ensuring sub-100ms first contentful paint across geographies.
3. **Unified Environment Configuration:** Render natively connects backend web services to managed PostgreSQL instances via automatic `DATABASE_URL` environment variable binding.
4. **Independent Scalability & Decoupling:** Frontend deployments cannot break backend operations, and backend updates deploy with zero-downtime health checking against `/api/v1/health`.

## Consequences
### Positive
- Fully automated CI/CD: pushing to `main` on GitHub triggers immediate tests and deployments on both platforms.
- Clear operational separation: frontend asset delivery is entirely offloaded from the backend Python server.
- Built-in database backups, connection pooling, and SSL encryption on Render.

### Negative / Trade-offs
- Cross-origin requests: requires strict CORS configuration on FastAPI (`ALLOWED_ORIGINS` pointing to the Vercel production domain).
- Cold starts: free-tier Render instances experience sleep after inactivity (mitigated by configuring health check pings or utilizing Render starter/standard tiers).
