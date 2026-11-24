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

Teachers POST assignments with an optional policy: max_attempts (1-20), allow_resubmission, allow_late, require_feedback, require_approval and grading_policy first/best/latest/selected. Missing policies retain the original one-attempt behavior. Students POST body to `/assignments/{id}/submit`; the response preserves the stable submission ID and adds attempt_id and attempt_number. New attempts never replace earlier content.

Assigned teachers grade `/attempts/{id}/grade`, inspect `/assignments/{id}/submissions`, and choose `/attempts/{id}/select-final` under selected policy. The original `/submissions/{id}/grade` remains compatible with attempt 1. `/assignments/{id}/history` returns authorized history and the official result; an approved parent can use student_id. Feedback revisions are append-only.

Students request `/assignments/{id}/resubmission-requests`; teachers review `/resubmission-requests/{id}/review` or explicitly `/assignments/{id}/reopen` for an enrolled student and future date. Approval authorizes the specific next attempt and is consumed when used. Backend eligibility checks limits, enrollment, deadlines, feedback and approval; concurrent duplicate attempts return 409.

Quizzes support MCQ, true_false, numerical and short_answer settings. Publication requires reviewed=true or the assigned teacher's `/quizzes/{id}/publish` action. Student question responses omit keys, rubrics and explanations before submission. `/quizzes/{id}/attempt` accepts every question ID mapped to a zero-based integer option or bounded text. Numerical equivalence is checked symbolically. Short answers keep the overall score pending until the assigned teacher posts only the manual component marks to `/quiz-submissions/{id}/grade`. Completed objective grades cannot be overwritten. Quizzes retain one attempt per student.

## Assistance and review

`POST /recommendations/generate` accepts student_id and course_id. It persists a
pending review draft but returns no draft content to a student. Assigned teachers
review with decision approved/rejected and a non-empty comment. Rejected drafts
can regenerate with an incremented version. Students/parents list only published
or viewed records. `/history` and immutable `/versions` snapshots are teacher-scoped. Approval decisions and important
transitions produce history/audit records.

`POST /tutor/ask` accepts question, one of eight supported subjects, language en/sw and optional use_local_ai. It routes bounded symbolic mathematics or topic-gated teaching notes, with explicit verified and mode labels. Explicit requests for English/Kiswahili override the selected output language. Match scores are retrieval signals, not confidence probabilities. Follow-ups use only the current user's recent same-subject context. `/tutor/provider-health` is authenticated and checks optional local model availability.

Lesson and quiz draft endpoints require an assigned teacher and verified premium entitlement. Quiz draft inputs add objective, difficulty, count, language, kind and optional use_local_ai. A missing or invalid provider falls back to the bank. Limited bank counts are stated rather than filled with duplicate questions. Saving and publishing remain separate authorized teacher actions.

Send `Accept-Language: sw` for localized errors and CSV headings; `/me/language` persists a language-only update without changing profile fields. Teacher-entered content and historical messages retain their original language.

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
