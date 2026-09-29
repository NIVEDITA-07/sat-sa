# SAT-SA examiner workspace

This React and TypeScript interface uses the existing SAT-SA Python analytics engine. The adapter in `api.py` loads the repository's bundled CSV submission and exposes a read-only local API. No engine, rule, source CSV, or Streamlit file is changed by the frontend.

For low-resource demo hosting, `demo_cache.json.gz` contains a precomputed export of the bundled controlled data. The adapter serves that export when present. To regenerate it after changing demo CSVs or engine logic, run `python frontend/build_demo_cache.py` from the repository root. Set `SATSA_LIVE_PIPELINE=1` to run the analytics pipeline at request time instead.

## Run locally

From the repository root, install the Python packages listed in `requirements.txt`. Then:

```powershell
cd frontend
npm ci
npm run build
cd ..
python frontend/api.py
```

Open `http://127.0.0.1:8000`. The first request runs the complete analytical and ground-truth validation pipeline, so it can take several seconds. Results are cached in memory for the life of the adapter process. Restart the process to load changed CSVs.

For frontend development, run `npm run dev` in `frontend` and the Python adapter in a second terminal. Vite proxies `/api` to port 8000.

## Offline deployment

Build `frontend/dist` ahead of time and transfer that directory together with the repository and local Python dependencies into the restricted network. The app loads no fonts, scripts, images, APIs, or models from the internet at runtime. By default the adapter binds to `127.0.0.1:8000`; set `SATSA_HOST` and `SATSA_PORT` for an internal deployment. Place an approved reverse proxy and authentication layer in front of it before multi-user use.

## Current scope

- Overview with entity rankings and sector-wide signals from the engine.
- CSE profiles, reported indicators, and evidence availability.
- Searchable and filterable findings with rule rationale and evidence references.
- Alert, case, and asset record inspection, including linked records where available.
- Ground-truth validation summary from the existing pipeline.

The adapter is read-only. Examiner decisions, account management, audit logging, CSV upload, and multi-user persistence are **not** implemented. The interface does not imply those actions are saved. This prototype uses the repository's controlled demo submission; the adapter can be extended to use the existing ingestion entry point for authorised periodic submissions.
