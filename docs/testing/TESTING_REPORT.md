# Executed testing report

The final local checks completed during the 23-24 November 2026 development
session. Evidence files are committed alongside this report.

| Check | Executed result | Evidence |
| --- | --- | --- |
| FastAPI/service integration with isolated SQLite and foreign keys | 48 passed | pytest-results.xml; backend/tests |
| React components and API client contracts | 9 passed | vitest-results.json; frontend/src/tests |
| Running local application in headless Chrome | 8 passed | playwright-results.xml; frontend/e2e |
| TypeScript and Vite production build | Passed | build result recorded in artifact validation; dependency locks |
| Native diagram XML, references, PNG/PDF structure | 8 sources plus 8 PNG/PDF pairs validated | diagrams/validation.json |

Total: **65 passing automated tests/scenarios**. This is a count of executed tests,
not a code-coverage percentage. Complete functional requirement coverage is
46/50 (92%), with four partial requirements contributing zero.

## What was exercised

Authentication tests cover valid/invalid/expired tokens, salted password hashes,
registration, school association, teacher activation, profile preferences,
all four roles and immediate denial after account deactivation. Academic tests
cover assigned-course creation/update, protected uploads/downloads, HTTPS video
links, assignment deadlines and duplicate submissions, grading, family alerts,
objective key secrecy, invalid answers, automatic grades and scoped CSV reports.

AI tests cover evidence-backed drafts, hidden pending recommendations, student
self-approval denial, unassigned reviewer denial, rejection, regeneration,
versions, review history, archival, own-student view marking, bilingual retrieval,
no-match handling, private conversation history and entitled teacher draft tools.
Risk tests exercise missing data and threshold boundaries without claiming ML
accuracy. Explicit study-action tests ensure GET requests do not fabricate activity.

Family/admin tests cover pending and revoked links, unrelated student/school
access, valid and invalid teacher-parent messages, private notifications, teacher
assignment/removal, school reporting, plan editing and school-plan isolation.
Billing tests cover forged success fields, mismatched amounts, unauthorized
verification, failed/rejected providers, receipts, idempotency, expiry, suspension,
unverified entitlement denial, manual activation bypass attempts and disabled
demo provider behavior.

Browser scenarios cover landing/registration entry, student pathways, teacher
lesson persistence, parent reports, administrator reports, English/Kiswahili
tutoring, separate payment verification and mobile content fitting at 390 pixels.
Screenshots in docs/screenshots come from the real running interface.

## Failures found and corrected

The first browser run had four failures. Explicit form-label associations were
missing for controls whose wrapper labels included option/textarea text. Field
components now use unique IDs and htmlFor. One assertion also matched a hidden
select option rather than the visible heading and was made role-specific. The
same eight scenarios then passed, and passed again after the final chart change.

Chart animation was disabled so displayed values and captured screenshots show
the recorded data immediately. UML visual review corrected reversed state ports,
connector/text crossings, fragment boundaries and a combined class box that was
split into actual Grade and Submission entities. An original remote README
add/add conflict was resolved by retaining the remote description and both histories.

## Practical limits

One upstream Starlette/httpx TestClient deprecation warning remains; it did not
fail any test. Vite reports a large JavaScript chunk (about 766 kB raw, 229 kB
gzip); code splitting is future performance work. No PostgreSQL, load, real
payment, real-school study, independent penetration or accessibility certification
is claimed. Component network responses are mocked; API integration and browser
checks exercise actual application behavior.

The browser preview integration itself timed out; the explicitly requested
Playwright option supplied real browser verification instead. Online native
draw.io embed initialization timed out before loading a source. The packaged
DOCX renderer failed because LibreOffice soffice.exe was unavailable. The proposal
PDF is rendered and reviewed independently; Word pagination remains unverified.
GitHub Actions has not been observed running remotely. Authentication limits and
the final push outcome are reported separately from local test success.
