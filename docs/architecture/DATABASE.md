# Relational design

Identity: roles, schools, users, students, teachers, parents and parent_student_links.
Users reference a school and role; email is unique. Join/profile keys prevent
duplicate identities. Link state defaults to pending and requires admin approval.

Academics: courses, teacher_course_assignments, enrollments, lessons,
learning_materials, assignments, quizzes, questions, submissions, grades and
learning_activities. Each course belongs to one school. Enrollment and assignment
composite unique constraints prevent duplicates. Grades reference a submission;
quizzes have one attempt per student in the demonstration. Quiz answer keys are
never included in student-facing question serialization.

AI: ai_recommendations, recommendation_approvals, tutor_messages. Recommendations
reference a student and course and track pending, rejected, published, viewed and
archived states. Approvals are immutable history records. Regeneration makes a
new reviewable version while retaining prior decisions and audit actions.

Communications: notifications and messages reference sender/recipient/student;
read authorization checks the recipient or a valid teacher-parent relationship.

Billing: subscription_plans, subscriptions, payments and provider_transactions.
Payments have integer TZS amounts, provider references, status and timestamps.
Provider transactions are internal and cannot be mutated via public endpoints.
Auditing: audit_logs record actor, action, entity identifier and metadata without
passwords, JWTs or sensitive request payloads.

All primary keys are integers. Foreign keys are enabled in SQLite. Timestamps use
UTC, rendering uses the browser locale. Indexes cover user email, school-scoped
courses, student records, recommendations and message recipients. Migration 001
creates the baseline schema with a schema version ledger; future revisions must
add explicit migrations rather than relying on create_all to alter tables.
