# Executed enhancement testing report

The 24 November 2026 enhancement preserves the baseline tests and adds actual feature checks. Machine-readable results are committed alongside this report.

| Check | Result | Evidence |
| --- | --- | --- |
| FastAPI and services, isolated SQLite | 95 passed | pytest-results.xml |
| React components and API client | 12 passed | vitest-results.json |
| Running enhanced application in headless Chrome | 12 passed | playwright-results.xml |
| TypeScript and Vite production build | Passed | artifact-validation.json |
| Static localization keys | 277 checked; none missing | scripts/check_i18n.mjs |
| Editable diagrams and local PNG/vector exports | 8 sources and export pairs | diagrams/validation.json |
| Diagram text layout | 737 cells; no overflow | diagrams/layout-validation.json |
| Interaction consistency | All 72 direct messages in both views | scripts/check_interactions.py |

Total: **119 passing automated tests/scenarios**. This count is not line or branch coverage. Original functional coverage is **49/50 (98%)**, with AD-02 partial. The original 65 checks and 92 percent are historical baseline evidence.

## Added verification

Math tests cover linear/quadratic equations, fractions, simultaneous equations, simplification, factorization, substitution, calculus, basic trigonometry, malformed syntax, unsafe names and computation bounds. Topic tests cover all eight subjects, calculus relevance, scoped follow-ups and selected-language output. Optional-provider tests use mocks to exercise missing models, invalid sources, bounded structured requests and quiz schema validation without mark writes.

Assignment tests cover three attempts, caps, feedback and deadline gates, approval, reopening, assigned-teacher marking, feedback revisions, parent/privacy scopes and final selection. Official-score tests count each assessment once and verify first/best/latest/selected behavior. Pathway tests demonstrate 45-to-80-to-100 progress, unchanged approval gates and immutable content versions. Quiz tests cover typed keys, publication review, symbolic equivalence, hidden answer keys, pending written answers and immutable objective components.

The migration fixture uses frozen actual version-1 DDL and populated fictional records. The upgrade helper creates and integrity-checks a backup, compares every pre-existing row, applies additive versions 2/3 and repeats the migration idempotently. No existing demonstration database is reset or deleted. Browser QA uses a separate fictional database, which is retained outside version control.

All four added browser scenarios execute the actual enhanced UI: teacher policy creation, three separately graded attempts and extra approval, mobile history, equations/calculus and Kiswahili persistence, editable numerical quiz generation/publication/grading, and public/all-role language switching. Original eight scenarios remain. Twenty screenshots are captured from the running application.

## Failures found and corrected

Early tests detected an incorrect derived linear-equation step, subject ambiguity in map reading, a legacy migration fixture calling the new service too early, and Windows backup-journal filename limits. These were corrected before their milestones were committed. The backup destination is a new checked backup; live database journaling is never disabled.

The first browser run encountered an older server on the default ports. The enhanced application was isolated at ports 8011/5181. Browser checks then caught a tutor race that cleared newly typed text after an earlier answer completed, a partially translated dynamic public feature strip, and assertions matching old history before a new response arrived. The corrected application and response-aware scenarios all passed. Diagram review corrected text bounds, multiplicity spacing, subscription paths crossing states and largely blank continuation pages.

## Verification boundaries

Provider success/failure is mocked; no real Ollama model was installed or run. SQLite is the exercised database. One upstream TestClient deprecation warning and an 805 kB raw / 240 kB gzip bundle warning remain. No production, real payment, load, educational outcome or independent security certification is claimed.

The final 53-page PDF is independently rendered from the same proposal content and reviewed as page contact sheets with enlarged detail checks. The DOCX is structurally verified with 31 required sections and 39 figures. Native DOCX pagination is unverified: LibreOffice is missing, Word COM returned Access denied, and desktop launching returned no Word window. Native draw.io embed initialization timed out before any source loaded. These checks are not counted as passed. GitHub synchronization and any observed remote CI result are reported separately.
