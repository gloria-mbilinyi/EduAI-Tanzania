# EduAI Tanzania Ltd

AI-Powered Learning and School Management Platform for Tanzanian Secondary Schools

A locally runnable React/TypeScript and FastAPI prototype with 28 relational
tables, four role workspaces, teacher-supervised learning assistance, protected
academic records and verified **simulated** payments. Every demo person and
school is fictional. No paid model, payment gateway or hosting is required.

**Verified functional coverage: 46/50 requirements (92%); four partial items are
excluded.** Tests: 48 API/service checks, 9 component/client checks and 8 local
Chrome browser scenarios pass. This is an academic prototype, not a validated
predictor of educational outcomes or a production-ready service.

## Start locally on Windows

Prerequisites: Python 3.12+ and Node.js 22+. The executed environment used Python
3.14 and Node 24. Chrome is needed only for the optional browser suite.

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.lock.txt
cd backend
..\.venv\Scripts\python.exe -m app.seed
```

Choose a shared **fictional demo password of at least 10 characters** when
prompted. No password is hardcoded or committed. The seed is idempotent: it
skips an already populated database and never overwrites existing users.

Start the API in that terminal:

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal, from the repository root:

```powershell
cd frontend
npm ci
npm run dev
```

Open [the application](http://127.0.0.1:5173/). API contract:
[interactive documentation](http://127.0.0.1:8000/docs) or the offline
[OpenAPI file](docs/api/openapi.json). Keep both terminals running. Ctrl+C stops
each service. Optional PowerShell helpers are `scripts/setup.ps1` and
`scripts/run.ps1`; the explicit terminal commands also work when local script
execution policy prevents running those helpers.

## Fictional demonstration accounts

Use the password you chose during seed setup for all accounts.

| Role | Login | Starting demonstration |
| --- | --- | --- |
| Student | amina@demo.eduai.test | Mathematics notes, quiz, tutor, approved biology pathway |
| Teacher | neema@demo.eduai.test | Mathematics/biology, review queue, assignment grading and premium lesson drafts |
| Parent | parent@demo.eduai.test | Approved link to Amina, reports, alerts and teacher messages |
| School administrator | admin@demo.eduai.test | School accounts, assignments, parent links, reports and payments |
| Second student | juma@demo.eduai.test | Separate student records and fresh quiz attempts |
| Other teacher | hamisi@demo.eduai.test | Physics only; useful for access-denial demonstrations |
| Other school student | isolated@demo.eduai.test | Isolated second-school data |

The seeded teacher has a matching **simulated verified** premium transaction.
New public teacher registrations require administrator activation. Parent link
requests require school verification. New courses need administrator enrollment
before students can access them. Administrator provisioning is out of band.

## Demonstrate the four roles

1. Student: read a material, mark it studied, submit a teacher-created assignment,
   attempt a published quiz, inspect feedback, ask the tutor and view a reviewed
   pathway. Switch navigation/tutor to Kiswahili from the header.
2. Teacher: create an assignment in an assigned course, grade a submitted response,
   inspect scoped student evidence, reject/regenerate/approve a pathway and save
   an edited lesson draft. Quizzes can be manually authored or assembled from the
   small bank; every answer key must be reviewed before publishing.
3. Parent: inspect Amina's report and notifications, send a message to an assigned
   teacher and request another child link. The request grants no access until an
   administrator approves it. Juma's report is initially forbidden.
4. Administrator: activate a newly registered teacher, assign a course, enroll a
   student, verify a parent request, inspect school reports and manage school plans.
   In Payments, verify a pending simulated transaction; suspension immediately
   disables premium entitlement.

For payment failure, select a failed/rejected demo scenario and verify it.
The server reads an internal ledger; a frontend success flag cannot activate
premium access. No real money moves. Renewing an expired plan creates a new
transaction/subscription. Premium applies to teacher draft assistance; basic
learning, reviewed pathways and the retrieval tutor remain available.

## Run the executed checks

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests -q
cd ../frontend
npm test
npm run build
```

For optional browser checks, start both servers, use a fresh fictional seed, then
set `EDUAI_DEMO_PASSWORD` to the chosen demo password in the test terminal and run
`npm run test:e2e`. Chrome is selected locally. To use Playwright's bundled
Chromium instead, install it with `npx playwright install chromium` and set
`PLAYWRIGHT_BROWSER_CHANNEL=chromium`. Browser tests create fictional records,
save screenshots and overwrite their evidence files. No tests touch real data.

See [test evidence and limitations](docs/testing/TESTING_REPORT.md). CI is
configured under `.github/workflows/ci.yml`; no remote CI success is assumed.

## Assistance capabilities

- Recommendations and risk: deterministic, explainable rules using real demo
  grades, explicit recorded activity, preferences and interests. No trained model
  or model accuracy claim. An assigned teacher must approve publication.
- Tutor: lexical retrieval over 11 original English/Kiswahili teaching passages
  in eight subjects, with sources and honest no-match handling. No generative LLM.
- Lesson assistance: retrieved content plus an editable template, saved only by
  the teacher. Quiz assistance assembles existing bank items, which is reported
  as partial generation capability.
- Alerts and communication: in-app only, scoped to approved families and assigned
  teachers. No SMS/email service is connected.

## Deliverables and technical reference

- [Requirements matrix and coverage](docs/requirements/COVERAGE_REPORT.md)
- [Architecture](docs/architecture/ARCHITECTURE.md) and [schema](docs/architecture/SCHEMA.sql)
- [API guide](docs/api/API_GUIDE.md) and [actual route catalogue](docs/api/ROUTES.md)
- [Eight editable draw.io sources](diagrams/drawio), [PNG exports](diagrams/png)
  and [vector PDFs](diagrams/pdf)
- [Diagram validation status](diagrams/EDITOR_VALIDATION.md)
- [Technical proposal PDF](docs/technical-proposal/EduAI_Tanzania_Technical_Proposal.pdf)
  and [editable DOCX](docs/technical-proposal/EduAI_Tanzania_Technical_Proposal.docx)
- [Actual application screenshots](docs/screenshots)
- [Agent contribution report](docs/agent-development-log/AGENT_CONTRIBUTION_REPORT.md)
- [Known limitations](docs/KNOWN_LIMITATIONS.md)

To reproduce diagram/document artifacts, install `scripts/artifact-requirements.txt`
in a separate environment and run `scripts/generate_uml.py` and
`scripts/build_proposal.py`. The source XML is the diagram editing authority.
Run `scripts/build_coverage.py` and `scripts/export_contracts.py` to refresh the
traceability and API/schema documentation. See the artifact validation report
for native-editor opening and Word pagination verification limits.

## Configuration and deployment boundaries

`.env.example` documents **environment variables**; the application does not
automatically load a `.env` file. Set variables in the shell/service environment.
Development creates an ignored random `.local-secret`. Production requires
`APP_ENV=production`, a random `JWT_SECRET` of at least 32 characters, explicit
`FRONTEND_ORIGIN` and a configured `DATABASE_URL`. Demo payments are disabled in
production. Install `backend/requirements-production.txt` for PostgreSQL support;
only SQLite has been exercised. Do not import real student data before security,
governance, migration, recovery and operational review.

Migration command: from backend, `python -m app.migrate` (use the virtual
environment interpreter). Migration 001 establishes the baseline; future schema
changes require explicit revisions. No production hosting, real payment provider,
offline synchronization or full curriculum approval is claimed.

## Git history and target remote

Target: [gloria-mbilinyi/EduAI-Tanzania](https://github.com/gloria-mbilinyi/EduAI-Tanzania).
The original remote README commit is preserved as a parent of the integration
merge. No force push or repository-owner change was performed. The connector
initially used `buriro-ezekia` with no write permission, and local Git Credential
Manager returned Windows access denied when asked to authenticate as
`gloria-mbilinyi`. The final delivery report gives the actual synchronization
result; a public URL alone is not treated as proof that the code was uploaded.

Once authorized Git authentication is available, inspect `git fetch origin`,
confirm the remote is an ancestor (`git merge-base --is-ancestor origin/main main`),
then `git push origin main` and compare `git rev-parse HEAD` with
`git ls-remote origin refs/heads/main`. Never use `--force` for this delivery.
