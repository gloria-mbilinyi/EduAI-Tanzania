# Business rules and trust boundaries

| ID | Enforced invariant |
|---|---|
| BR-01 | Student registration requires an existing active school. |
| BR-02 | Parent access requires a persisted, school-scoped approved link. |
| BR-03 | Teacher mutations require an assignment to the course. |
| BR-04 | Only approved recommendations can be read by students or parents. |
| BR-05 | Administrators are scoped to their own school. |
| BR-06 | Bearer JWT required on all non-public API routes. |
| BR-07 | Premium service checks verified payment and unexpired active subscription. |
| BR-08 | Grade and recommendation review endpoints reject students. |
| BR-09 | Passwords use salted PBKDF2 SHA-256; no plaintext credential storage. |
| BR-10 | School, enrollment, ownership and parent-link checks precede private reads. |
| BR-11 | Simulated provider ledger is persisted server-side; clients cannot assert success. |
| BR-12 | Important mutations produce append-only application audit records. |

Public registration allows students, parents and pending teachers. A school
administrator must activate a newly registered teacher. Administrator accounts
are provisioned out of band. No client-supplied role change grants privileges.
Parent link requests are verified by a school administrator; student identifiers
alone do not authorize access. Academic alerts are in-app, not SMS or email.
