# Known limitations and next work

## Partially implemented functional requirements

- ST-12: English/Kiswahili navigation, primary labels and tutor retrieval work.
  Some explanatory copy, server validation messages and teaching-tool drafts
  remain in English. Full localization is not complete.
- TC-09 and AI-07: Quiz assistance selects and assembles reviewed question-bank
  items. Teachers can edit the JSON and publish reviewed quizzes. Novel question
  generation by a language model is not implemented.
- AD-02: Administrators create role-assigned accounts and manage activation.
  Changing the role of an existing identity is not implemented. This avoids
  ambiguous transitions of historical student/teacher records.

These four requirements are excluded from complete functional coverage.

## Academic and operational limits

The tutor has 11 original illustrative teaching passages covering eight subjects.
It is lexical retrieval, not generative AI or a formally certified curriculum.
Risk is a deterministic rule baseline, not a trained model, clinical label or
validated predictor. No accuracy statistic or real student training data is used.
Offline study is not captured; users can explicitly mark a material as studied.

All users, records, school names and payment transactions are fictional. Payments
are simulated; no money moves and no mobile-money provider is integrated.
Subscriptions are per user; a future school-wide billing entitlement is not
implemented. Renewal creates a new subscription object rather than changing an
expired object's history. Alerts and messages are in-app only.

Assignments accept text submissions. File uploads support teaching materials up
to 5 MB, including downloadable MP4 files; there is no streaming/transcoding or
malware scanning. Objective quizzes allow one attempt. New courses require an
administrator to enroll students. Course deletion and global multi-school
administration are deliberately outside this prototype's school-admin scope.

No real-school field study, scalability benchmark, independent penetration test,
accessibility certification, offline synchronization or formal curriculum review
has been completed. PostgreSQL configuration is provided but only SQLite has
been exercised. Migration 001 is a baseline; future schema changes need explicit
versioned migration revisions and backups. Concurrent submission races rely on
database uniqueness constraints and are not yet translated into a friendly 409
in every path. Production needs rate limiting, TLS, secret management, backups,
recovery procedures, monitoring, audit retention and a cookie/session review.

## Delivery verification limits

Local API, component, production-build and headless Chrome browser checks have
been executed; exact results are in docs/testing. GitHub Actions is configured
but has not been observed running remotely. The connected GitHub account has no
write access and local Git Credential Manager cannot enumerate Windows stored
accounts in this environment. No push success is claimed.

Native draw.io XML structure and the local vector/raster exports are validated.
An attempt to load the online native editor through its documented embed API
timed out while waiting for initialization. Native editor opening is therefore
not yet verified. The diagrams contain independent editable cells, not screenshots.

The technical proposal PDF is rendered and checked separately. The packaged
DOCX renderer is attempted; if the host lacks its LibreOffice converter, Word
pagination remains unverified. The final validation report records that result.
