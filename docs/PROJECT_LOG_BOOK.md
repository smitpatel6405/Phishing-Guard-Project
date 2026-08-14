# Project Log Book – PhishGuard

Project: Real‑time Phishing Detection (Flask + Chrome Extension)

Prepared for: Hackathon / Faculty Submission

## Weekly Summary

| Week | Goals | Key Work Done | Deliverables | Issues/Fixes | Next Focus |
|---|---|---|---|---|---|
| Week 1 | Bootstrap backend + MVP model | Created Flask app structure, `app.py`, `models/`; added `requirements.txt`; implemented `extract_features` (9 URL features); loaded Random Forest model; `/predict` API; Chrome extension scaffold (manifest, popup, background, content); Dockerfile | Running API on 5000; Extension MVP sending URL to backend | Python env mismatch (3.13 vs 3.8) fixed by reinstall; basic tests pass | Add quick start docs; refine UI states |
| Week 2 | UX, clarity, and false‑positive control | Wrote Quick Start + Next Steps; explained color codes; added allowlist/denylist + threshold; added yellow “Caution”; “Why this decision?” in popup | Updated popup with Decision Details + Reasons | Fixed CORS (“Failed to fetch”) by `Flask-CORS`; corrected PowerShell headers | Prepare advanced visual module plan |
| Week 3 | Advanced copy + visual analysis | Duplicated project as Advanced (5001); added `/analyze_screen`, OCR/CV stubs, brand keywords; fusion endpoint `/predict_fused`; brand profiles JSON; consent toggle; background screenshot capture | Advanced backend online on 5001; Visual scan button | 5001 not running → fixed app.run port, killed lingering procs; 404 on visual scan → endpoint wiring fixed | Improve fusion thresholds; add demo fake site |
| Week 4 | Stability + automation | One‑click `START_BOTH_AND_TEST.bat`; expanded brand profiles; allowlist/paypal false positive tuning; integrated Safe Browsing hook; content heuristics (iframes/scripts/urgent) | E2E smoke tests; latency checks | Start/health scripts refined; popup spinner + loading polish | Presentation content (algorithms, tech, design) |
| Week 5 | Docs + presentation | Faculty presentation outline; Gamma prompt for 13 slides; AEIOU canvas; research gap + references; short project summary; domain name for slides | Slide content package; AEIOU canvas | N/A | Finalize demo flow; record fallback |
| Week 6 | Polishing + bug fixes | Fixed extension icon; CORS again; ensured Current can call Advanced fusion; normalized confidence (no negatives); manifest host permissions for 5001; popup→page sync; “no downgrade” rule (keep highest risk) | Stable extension v1.0.1; consistent banners; updated brand profiles (google, gmail, amazon, primevideo, netflix, boAt, gamma) | Health showed offline in old build → reloaded; visual-green vs URL-red clarified and fused | Final QA and demo checklist |

## Milestones & Artefacts

- Backend: `app.py` (5000), `Advanced/app.py` (5001), `requirements.txt`
- Visual: `/analyze_screen`, `/predict_fused`, OCR/CV pipeline (optional)
- Extension: `manifest.json`, `background.js`, `content.js`, `popup.html/js`
- Policies: Allowlist/Denylist, brand profiles (`Advanced/brand_profiles.json`), thresholds
- Automation: `START_BOTH_AND_TEST.bat`
- Docs: Quick Start, AEIOU Canvas, Presentation outline

## Notes

- Fusion logic: final decision uses max(URL risk, visual risk) with thresholds; UI shows red/yellow/green with reasons.
- Privacy: visual scan requires explicit consent; screenshots processed locally + backend.

---

Export tips:
- PDF: Open this file in VS Code → Markdown: Open Preview → Print to PDF.
- Google Docs: Copy table into a Doc; keep monospace for file paths.








