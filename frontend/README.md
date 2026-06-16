# WebWatch Frontend Dashboard

A modern, fast React dashboard built on Vite, TypeScript, and Tailwind CSS. It serves as the visual interface for the WebWatch unified monitoring backend, highlighting server latency checks, UI screenshot regressions, and API schema drift.

---

## 📂 Frontend File Structure

The project has been structured for scalability and clear separation of concerns:

```text
frontend/
├── src/
│   ├── app/
│   │   ├── components/         # Reusable dashboard UI blocks
│   │   │   ├── Header.tsx      # App Navbar, navigation tabs, and pending-changes notification
│   │   │   ├── Phase1.tsx      # Dashboard panel for Website Availability & Latency statistics
│   │   │   ├── Phase2.tsx      # Interactive visual review board for screenshot & text diffs
│   │   │   ├── TextDiff.tsx    # Line-by-line helper diff text visualization component
│   │   │   └── PendingChangesPopup.tsx # Sidebar modal to approve/reject Phase 4 schema changes
│   │   ├── data/
│   │   │   └── phase2Data.ts   # Formatting wrappers for visual diff entities
│   │   ├── App.tsx             # Root router, tab status state, and interval fetching
│   │   ├── config.ts           # Global configuration loading VITE_API_URL
│   │   └── types.ts            # TypeScript interfaces (Site, Issue, PendingChange)
│   ├── assets/                 # Icons and image files
│   ├── index.css               # Tailored styles, color palette systems, and fonts
│   ├── main.tsx                # App entry point bootstrapping React
│   └── vite-env.d.ts           # Vite TypeScript environment definitions
├── index.html                  # Main HTML document template
├── package.json                # Project dependencies and build script commands
├── postcss.config.mjs          # PostCSS layout loader configuration
├── tailwind.config.js          # Tailwind styling custom design variables
└── vite.config.ts              # Vite configurations (React and Tailwind plugins)
```

---

## ⚙️ Configuration & Environment Variables

The frontend communicates with the unified Flask backend via `API_BASE_URL` defined in `src/app/config.ts`. By default, it looks for an environment variable, fallbacking to `http://localhost:5000`:

```typescript
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
```

If your backend is running on a different port or exposed via ngrok, create a `.env.local` file inside the `frontend` folder:

```env
VITE_API_URL=https://your-backend-url.ngrok-free.app
```

---

## 🛠️ Scripts & Running Locally

Install dependencies first:
```bash
npm install
```

### Development Server
Runs the application locally with hot module replacement (HMR) on `http://localhost:5173`:
```bash
npm run dev
```

### Build for Production
Compiles and optimizes static assets to the `dist/` directory:
```bash
npm run build
```

---

## 🎨 Design Systems & UI Layouts
* **Tailwind CSS & Vanilla Styling**: Leveraging a responsive grids layout and modern Tailwind utilities.
* **Component Modularity**: 
  * `Phase1.tsx` maps status responses, listing response times and generating visual metrics charts.
  * `Phase2.tsx` provides side-by-side comparisons of **Baseline vs. Current** screenshots, and utilizes a difference image overlay selector for visual audit verification.
  * `PendingChangesPopup.tsx` connects directly to the backend approval service to allow quick merging of updated schema configuration files.