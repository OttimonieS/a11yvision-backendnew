Real Time Accessibility Auditor using Vision AI
Complete Product Specification

1. High level product overview

The application is a cloud-based accessibility testing service. Users open the web frontend, enter any URL, and the system loads the page in a headless renderer, captures screenshots and the DOM, analyzes visual and structural accessibility using a combination of computer vision and WCAG rule logic, then presents results in an interactive dashboard.

Key qualities: fast feedback, evidence-backed findings, clear remediation, exportable reports, and configurable privacy/retention.

2. Core capabilities

- Visual accessibility scanning: detect low-contrast text, unreadable text, cramped or overlapping UI, too-small clickable elements, non-interactive elements that look interactive, visual hierarchy problems.
- Structural scanning: detect semantic HTML errors, missing or incorrect labels, missing alt text, ARIA issues, incorrect heading order, and tabindex inconsistencies.
- Behavioral checks: simulate keyboard navigation and detect tab-order problems, focus visibility, modal/overlay focus trapping, and interactive element sizing.
- Real-time results: incremental findings streamed to the dashboard with severity, confidence, WCAG references and suggested fixes.

3. User experience flow

1. User opens the web app and enters a URL.
1. Backend spins a headless browser to load the page and capture: screenshots, DOM, computed styles and element coordinates, plus optional accessibility tree.
1. Preprocessing computes contrast, bounding rectangles and reduced-noise screenshots.
1. Vision models + OCR + structural rule engine analyze the capture and produce issues with evidence.
1. Results are saved and streamed to the frontend where users inspect, filter, and export findings.

1. Frontend (what to build)

4.1 Landing page

- Clean URL input field and prominent CTA to run analysis.
- Short explainer of what vision-based auditing detects and benefits.
- Example screenshots and a short demo clip/animation.

  4.2 Scan progress screen

- Stepper listing phases: render, capture, preprocessing, AI inference, analysis, packaging.
- Loading indicator, per-step progress, estimated wait time, and ability to cancel.

  4.3 Results dashboard (core interface)

A. Screenshot viewer

- Screenshot with overlay bounding boxes, labels, severity colorization and hover tooltips.
- Viewer supports pan, zoom, highlight-on-hover and click-to-open details.

B. Issue list

- Title, severity (critical/major/minor), summary, WCAG references, suggested fixes and link to the screenshot highlight.
- Sort, filter by category, search, bulk export actions.

C. WCAG compliance overview

- Percentage score and breakdown across perceivable/operable/understandable/robust with counts per category.

D. DOM inspector

- Show the exact HTML node, attributes (role, alt, ARIA), computed contrast and a copyable DOM selector.

E. Export panel

- Export to PDF and JSON, generate shareable links (if history is enabled).

  4.4 History & Settings (optional)

- History page for accounts, compare previous scans and view trends.
- Settings: reduced motion, theme, WCAG target version, max scan depth, privacy/retention.

5. Backend (what to build)

5.1 URL handler

- Validate URL, enforce security policy (block local IPs, internal-only hosts), and sanitize input.

  5.2 Headless browser renderer

- Use Playwright (recommended) or Puppeteer to load pages and capture: full-page & viewport screenshots, raw DOM HTML, computed styles, element bounding boxes and optional accessibility tree.

  5.3 Preprocessing engine

- Produce cleaned DOM, compute contrast ratios per text node, generate bounding rectangles and a color map; strip noise from screenshots and tile large images.

  5.4 Vision AI processor

- Use OpenCV for deterministic ops (edge detection, contrast tests), and PyTorch (preferred) models for layout/element detection and advanced inference. Produce boxes, categories, confidence scores and OCR output.

  5.5 Structural rule engine

- Apply WCAG logic to DOM and model outputs: alt text checks, ARIA verification, label associations, heading hierarchy, tabindex and focus order rules.

  5.6 Issue aggregator

- Merge visual findings, DOM issues and model inferences, deduplicate evidence, compute final severity and confidence, and attach remediation suggestions.

  5.7 API endpoints (minimal set)

- `POST /api/v1/scans` – submit scan request.
- `POST /api/v1/uploads` – request presigned upload URL.
- `GET /api/v1/scans/{scanId}` – fetch results.
- `GET /ws/scans/{scanId}` – realtime updates.
- `GET /api/v1/export/{scanId}` – export report.

  5.8 Optional features

- Auth/accounts, rate-limiting, caching, storage of screenshots and DOM trees, user history and billing/quotas.

6. AI pipeline overview

Stage 1: Visual capture — Input screenshot; output: tiles, preprocessed images and OCR text.
Stage 2: Vision inference — Detect text readability, spacing errors, clickable target sizing, and elements that visually look interactive.
Stage 3: DOM analysis — Structural checks and attribute extraction.
Stage 4: Fusion — Align DOM nodes with detected bounding boxes and OCR, compute per-element feature vectors.
Stage 5: Scoring — Produce final issues with `confidence`, `severity`, `suggested_fix` and `wcag_references`.

7. Final product qualities

- Professional auditing dashboard, instant and evidence-backed findings, high-quality remediation suggestions, export-friendly reports, and accessible UI.

8. Target users

- Developers, UI designers, QA teams, accessibility consultants and product managers seeking automated pre-release compliance checks.

9. Premium features (roadmap)

- Auto-fix suggestions that produce code snippets.
- Interactive keyboard replay and focus tracing.
- API access for automated pipelines and CI integration.

10. Next steps / handoff

- Provide OpenAPI spec and FastAPI starter routes.
- Add `injector.js` skeleton and browser extension manifest.
- Create `docker-compose` for local dev: FastAPI, Redis, Postgres, MinIO, worker.
- Provide sample pages (+testcases) for E2E and model validation.

---

File created for engineering handoff: `PRODUCT_SPEC.md` (root).
