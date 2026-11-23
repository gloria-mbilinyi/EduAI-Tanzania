# Architecture and decisions

React TypeScript/Vite → JSON REST API → scoped application services → SQLAlchemy
repositories → SQLite (demo) or PostgreSQL (deployment). Uploaded material files
remain outside the public frontend and are downloaded through authorized API
requests. External HTTPS resources are allowed; no remote server fetching occurs.

FastAPI dependencies resolve the bearer principal from the database on each
request. Token claims identify a user; the current persisted role, school and
active flag decide authorization. Short token expiry limits exposure. Local
development creates an ignored random signing secret, while production requires
an explicitly configured secret and prohibits demo payments.

Each user has one role. Students, teachers and parents have normalized profile
tables. Course enrollment and teacher assignments are explicit join tables.
Academic reads use enrollment or approved parent links; mutations use teacher
assignments. Administrators are school administrators, never global superusers.

AI modules implement deterministic data-based recommendations and risk rules,
lexical retrieval over bilingual educational passages, and teacher-editable draft
quizzes and lesson outlines. No trained ML model is shipped because no validated
training data was supplied. Premium draft tools check entitlement on the server.

Payments are an academic simulation. A server-side adapter records a deterministic
provider outcome using a demo scenario selected at transaction creation. A
separate verification endpoint reads that ledger, checks amount/currency, and
activates a subscription. No endpoint accepts a client success flag. Verification
is idempotent. Transactions, reviews and administrator changes are audited.

## Tradeoffs

SQLite makes setup independent of external services; production needs PostgreSQL,
managed TLS, backups, migrations, rate limiting and operational review. JWT is held
in browser session storage for the demo; hardened deployment should evaluate
HttpOnly cookies and CSRF controls. Binary uploads are capped and served as
attachments. The prototype has no malware scanner, real money processing,
offline synchronization, SMS delivery or high-availability deployment.
