# Bloop — Monorepo Test Architecture & Execution Guide

This directory contains cross-cutting integration, smoke, and end-to-end tests for the Bloop full-stack platform:

```
tests/
├── e2e/           # End-to-end multi-service API flow tests
├── smoke/         # Fast sanity and deployment verification probes
└── fixtures/      # Reusable JSON test payloads and mock inputs
```

## Running Smoke & E2E Tests

From the project root:

```bash
# Run smoke tests
pytest tests/smoke -v

# Run E2E integration tests
pytest tests/e2e -v

# Run all monorepo root tests
pytest tests/ -v
```
