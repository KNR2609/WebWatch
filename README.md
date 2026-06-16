# WebWatch: Unified Web & API Monitoring System

WebWatch is a comprehensive web and API health, performance, and visual regression monitoring pipeline. It integrates website availability checks, visual change detection (automated screenshots and SSIM image diffing via Playwright), DOM text comparison, and API schema drift approval workflows under a unified React + Flask web dashboard.

---

## 📂 Project Structure

The codebase is organized into modular phases, coordinating background check routines and exposing REST APIs for the frontend dashboard:

```text
WebWatch/
├── run_project.py       # Unified backend launcher script
├── phase-1/             # Phase 1: Website Health & Response-Time monitoring
│   ├── app.py           # Flask server & scheduler for Phase 1
│   ├── monitor.py       # Health check HTTP request script
│   └── sites.json       # Monitored website configuration list
├── phase-2/             # Phase 2: Visual UI & Text Regression testing
│   ├── app.py           # Flask endpoints for visual difference review & approvals
│   ├── core/            # Core screenshot comparison modules (ImageComparator)
│   └── data/            # Local directory for baseline, current, and difference images
├── phase-4/             # Phase 4: API Drift approval manager & scheduling
│   ├── dashboard/       # HTML template fallback dashboards and routes
│   ├── monitors/        # Cron-like schedulers and change approval manager
│   └── storage/         # Storage for API schema diff results (.json)
├── api_monitor/         # Low-level API monitor modules and schemas
├── text-extraction/     # Standalone DOM text content extraction tooling
├── frontend/            # Vite + React + TypeScript + Tailwind CSS Frontend App
└── results/             # Shared check reports and historical logs
```

---

## 🚀 Key Features

1. **Availability & Status Monitoring (Phase 1)**
   * Parses the list of domains in `sites.json`.
   * Leverages a multithreaded `ThreadPoolExecutor` (10 worker threads) for parallelized latency checks.
   * Auto-schedules status runs every 10 minutes and exposes status groups (`Good`, `Slow`, `Very Slow`, `Server Down`, `Website Down`).

2. **Visual & Text Regression Detection (Phase 2)**
   * Automates Playwright (headless Chromium) context loads utilizing stealth options to bypass bot mitigation.
   * Extracts visual layout states (screenshots) and raw DOM text content.
   * Compares them against baseline states using SSIM difference mapping to highlight structural and copy changes.
   * Rest API triggers and action approvals (`/api/phase-2/action`) allow overwriting or discarding baselines.

3. **API Endpoint Schema drift & Approvals (Phase 4)**
   * Validates API endpoints, tracking structure, field datatype, and value changes.
   * Diffs are serialized inside `storage/pending/` files.
   * Interactive notification bell badge updates in real-time, allowing developers to review and approve/reject schema modifications.

---

## 🛠️ Installation & Getting Started

### Prerequisites
* Python 3.9+
* Node.js v16+
* NPM or PNPM

### 1. Backend Setup & Run

1. Open your terminal in the root directory.
2. Install Python dependencies:
   ```bash
   pip install -r phase-4/requirements.txt
   # Ensure playwright is installed for visual checks
   playwright install
   ```
3. Run the unified launcher script:
   ```bash
   python run_project.py
   ```
   *This starts the Flask server on `http://localhost:5000` registering all Phase 1, Phase 2, and Phase 4 API routers and starting background scheduler loops.*

### 2. Frontend Setup & Run

1. Open a separate terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   *Access the web dashboard in your browser (typically `http://localhost:5173`).*

---

## 📡 Core API Endpoints

The unified Flask app handles all dashboard actions:
* `GET /api/monitor` - Returns availability statistics and logs for all domains (Phase 1).
* `GET /api/dp-issues` - Returns detected screenshots & text difference reports for UI review (Phase 2).
* `POST /api/phase-2/action` - Approves or rejects screenshot/text changes (Phase 2).
* `GET /api/pending-changes` - Returns lists and change counts for modified API endpoints (Phase 4).
* `GET /api/approve/<filename>` - Approves pending API schema changes (Phase 4).
* `GET /api/reject/<filename>` - Discards pending API schema changes (Phase 4).
