Real Time Accessibility Auditor — Backend Product Specification

This document summarizes backend-specific responsibilities, API contracts, processing pipeline and infra requirements from `PRODUCT_SPEC.md`.

1. Key responsibilities

- Ingest scan requests and validate URLs.
- Drive headless renderer (Playwright/Puppeteer) to capture screenshots, DOM and computed styles.
- Provide presigned upload flow for large binaries to S3/MinIO.
- Orchestrate preprocessing, model inference, rule evaluation and result aggregation.
- Persist metadata, issues and evidence references to PostgreSQL and object storage.

2. Core services

- **API service (FastAPI)** — REST and WebSocket endpoints, authentication, input validation, and metadata persistence.
- **Worker service** — dequeues jobs, runs OpenCV preprocessing and model inference, runs rule engine, writes results.
- **Model serving** — either embedded in worker pods (TorchScript/ONNX) or a dedicated model server (Triton/TorchServe).
- **Queue & cache** — Redis for job queueing, caching and rate-limiting.

3. Data model (summary)

- `projects`, `users`, `scans` (scan metadata & status), `images` (s3 key + scan id), `issues` (rule, severity, selector, bbox, evidence_id), `audit_logs`.

4. API endpoints (minimal)

- `POST /api/v1/scans` — submit scan; returns `scanId`.
- `POST /api/v1/uploads` — return presigned upload URL and `imageId`.
- `GET /api/v1/scans/{scanId}` — fetch scan results.
- `GET /ws/scans/{scanId}` — realtime stream of incremental results.

5. Processing pipeline

1. Validate and persist request, return `scanId`.
1. Enqueue job to Redis.
1. Worker downloads images (or reads from S3), preprocesses with OpenCV (contrast, tile, denoise), runs detection and OCR, maps detections to DOM, applies rule engine.
1. Aggregate issues, persist to DB and S3, notify frontend via WebSocket.

1. Infra & deployment

- Kubernetes with GPU node pool and device-plugin for inference.
- Use HPA plus custom metrics (queue length/GPU utilization) and node autoscaling.
- CI: build images, run tests, model validation and deploy via GitOps or pipeline with canary.

7. Security & privacy

- Presigned uploads to avoid routing images through API servers.
- Masking/redaction of sensitive inputs by default.
- RBAC, audit logs and encrypted storage.

---

Place this file under `backend/` to guide backend engineering.
