# ADR-007: Cloud Deployment Strategy on Vercel and Render

## Status
**Accepted**

## Context
Bloop needs a reliable, cost-effective, deployment-first infrastructure model for continuous deployment from a single GitHub repository. The deployment architecture must minimize operational maintenance, provide automated SSL/TLS termination, support environment variable secret injection, handle database migrations cleanly, and offer zero-downtime deployments without requiring Kubernetes, Docker Swarm, or complex cloud orchestration.

## Decision
Adopt a dual-platform PaaS architecture:
1. **Frontend:** Deployed to **Vercel** as a static Single Page Application (SPA) on its global Edge Network CDN.
2. **Backend:** Deployed to **Render** as a Python Web Service running FastAPI under Uvicorn.
3. **Database:** Deployed to **Render Managed PostgreSQL 16**, automatically provisioned and linked via `DATABASE_URL`.
4. **Continuous Delivery:** Automated GitHub webhook triggers build and deploy pipelines on every push to `main`.

## Alternatives Considered
1. **Single Virtual Private Server (VPS) via DigitalOcean / AWS EC2:** Full root control, but requires manual OS patching, reverse proxy (Nginx) setup, Certbot SSL renewal, custom systemd daemon scripts, and manual database backup management.
2. **Full AWS / GCP Architecture (ECS, EKS, Cloud Run, RDS, S3, CloudFront):** Comprehensive and enterprise-grade, but introduces high cloud complexity (IAM policies, VPC peering, NAT gateways, Terraform configurations) that violates our intermediate-level simplicity rule.
3. **Heroku:** Similar PaaS model, but has higher pricing tiers, fewer modern global edge frontend routing capabilities compared to Vercel, and deprecated free database tiers.

## Consequences

### Positive
- **Zero Server Management:** Both platforms provide fully automated SSL certificates, DDoS mitigation, HTTP/2 & HTTP/3 support, and automated container health checks.
- **Sub-100ms Frontend Delivery:** Vercel edge caching delivers static HTML/JS/CSS assets immediately to global users, offloading all static asset traffic from the Python backend.
- **Unified Render Blueprint:** The `render.yaml` infrastructure-as-code blueprint declaratively specifies backend web service configuration, PostgreSQL database instances, environment variable bindings, and pre-deploy migration hooks (`alembic upgrade head`).
- **Zero-Downtime Rolling Deploys:** Render tests the `GET /api/v1/health` endpoint before switching live traffic to newly built containers.

### Negative / Trade-offs
- **CORS Configuration:** Requires explicit cross-origin resource sharing configuration on FastAPI (`BACKEND_CORS_ORIGINS`) to permit requests from the Vercel production domain.
- **Cold Starts:** Free-tier instances on Render spin down after 15 minutes of inactivity (mitigated by configuring health check pings or utilizing Render starter/standard tiers for production).
