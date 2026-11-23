# API guide

Base URL during local development: `http://127.0.0.1:8000/api`.
Interactive contract: `/docs`; offline contract: `docs/api/openapi.json`.
The generated `ROUTES.md` lists actual methods, paths and authentication.

## Authentication and scope

`POST /auth/register` accepts name, email, password (10-128 characters), role
student/teacher/parent, existing school_id and language en/sw. Administrators are
provisioned out of band. New teachers await school administrator activation.
`POST /auth/login` accepts JSON email/password and returns access_token and user.
Send `Authorization: Bearer <access_token>` on protected requests. Tokens expire
in two hours; each request checks the current active user, role and school.

No client-supplied role can grant administrator privilege. School membership
cannot be edited through `/me`. Authentication errors return 401; insufficient
permissions return 403; foreign-school and unavailable records generally return
404. Duplicate or invalid state transitions return 409; validation returns 422;
missing premium entitlement returns 402. Demo provider unavailability returns 503.

## Academic workflow

Teachers create `/courses`, which assigns the creator, or edit an already assigned
course. Administrators assign additional teachers and enroll students. Course
materials are available through `/courses/{id}/materials`; uploads use multipart
`title` and `file` at `/courses/{id}/upload`. Downloads remain authenticated.
GET material lists are read-only; students explicitly POST `/materials/{id}/study`.

Teachers POST assignments under a course. Students POST `{ "body": "..." }` to
`/assignments/{id}/submit`. Assigned teachers list submissions and POST score and
feedback to `/submissions/{id}/grade`. Scores must be 0-100. Text submissions are
limited to one per student/assignment and cannot be submitted after the deadline.

Quizzes contain title, status draft/published and questions with prompt, options,
correct_index and explanation. Only assigned teachers create them. Students see
published quizzes without keys. `/quizzes/{id}/attempt` accepts an answers object
mapping every question ID to a valid zero-based option index. The server computes
and persists the grade. A second attempt is rejected; manual quiz-grade override
is not exposed.

## Assistance and review

`POST /recommendations/generate` accepts student_id and course_id. It persists a
pending review draft but returns no draft content to a student. Assigned teachers
review with decision approved/rejected and a non-empty comment. Rejected drafts
can regenerate with an incremented version. Students/parents list only published
or viewed records. `/history` is teacher-scoped. Approval decisions and important
transitions produce history/audit records.

`POST /tutor/ask` accepts question, subject and language en/sw. It returns a
retrieved teaching passage, source, lexical match score and honest mode label.
The score is not predictive confidence. Conversation history is private to the
requesting user. Lesson and quiz draft endpoints require an assigned teacher
and verified premium entitlement. Saving reviewed lessons and quizzes is a
separate teacher action.

## Family and billing workflows

Parents POST student_id to `/parent/links`. A pending link grants no academic
access. A school administrator approves or rejects it. Messages require an
approved parent link and a teacher assigned to a course taken by the student.
Notifications and message history are returned only to their participants.

`POST /billing/checkout` takes plan_id and the clearly labeled demo_scenario
success/failed/rejected. It creates a pending payment and internal simulated
provider transaction. `POST /payments/{id}/verify` takes an empty JSON object;
extra fields such as success are rejected. Verification reads the internal
ledger and compares amount/currency. Only then can the subscription become
active and a demonstration receipt be generated. Verification is idempotent.
School administrators may suspend/cancel access; restoration cannot bypass
verified payment or future expiry. No real payment integration exists.

## Reports and audit

`/students/{id}/performance` applies ownership, link, assigned-course or school
administrator checks. Teacher reports exclude unassigned subjects. Report CSVs
escape free-text formula prefixes. `/admin/reports` returns only the caller's
school and discloses its averaging method. `/admin/audit` returns recent actions
for school actors. Audit records cannot be edited or deleted through the API.
