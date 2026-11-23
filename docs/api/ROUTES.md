# API route catalogue

Generated from the actual FastAPI OpenAPI contract. Bearer JWT is required unless marked public.

| Method | Path | Access |
| --- | --- | --- |
| GET | `/api/admin/audit` | Bearer JWT |
| POST | `/api/admin/enrollments` | Bearer JWT |
| GET | `/api/admin/parent-links` | Bearer JWT |
| PATCH | `/api/admin/parent-links/{link_id}` | Bearer JWT |
| GET | `/api/admin/plans` | Bearer JWT |
| POST | `/api/admin/plans` | Bearer JWT |
| PATCH | `/api/admin/plans/{plan_id}` | Bearer JWT |
| GET | `/api/admin/reports` | Bearer JWT |
| GET | `/api/admin/school` | Bearer JWT |
| PATCH | `/api/admin/school` | Bearer JWT |
| GET | `/api/admin/subscriptions` | Bearer JWT |
| PATCH | `/api/admin/subscriptions/{subscription_id}` | Bearer JWT |
| GET | `/api/admin/teacher-assignments` | Bearer JWT |
| POST | `/api/admin/teacher-assignments` | Bearer JWT |
| DELETE | `/api/admin/teacher-assignments/{assignment_id}` | Bearer JWT |
| GET | `/api/admin/users` | Bearer JWT |
| POST | `/api/admin/users` | Bearer JWT |
| PATCH | `/api/admin/users/{user_id}` | Bearer JWT |
| PATCH | `/api/assignments/{assignment_id}` | Bearer JWT |
| GET | `/api/assignments/{assignment_id}/submissions` | Bearer JWT |
| POST | `/api/assignments/{assignment_id}/submit` | Bearer JWT |
| POST | `/api/auth/login` | Public |
| POST | `/api/auth/register` | Public |
| GET | `/api/billing` | Bearer JWT |
| POST | `/api/billing/checkout` | Bearer JWT |
| GET | `/api/courses` | Bearer JWT |
| POST | `/api/courses` | Bearer JWT |
| PATCH | `/api/courses/{course_id}` | Bearer JWT |
| GET | `/api/courses/{course_id}/assignments` | Bearer JWT |
| POST | `/api/courses/{course_id}/assignments` | Bearer JWT |
| GET | `/api/courses/{course_id}/materials` | Bearer JWT |
| POST | `/api/courses/{course_id}/materials` | Bearer JWT |
| GET | `/api/courses/{course_id}/quizzes` | Bearer JWT |
| POST | `/api/courses/{course_id}/quizzes` | Bearer JWT |
| GET | `/api/courses/{course_id}/students` | Bearer JWT |
| POST | `/api/courses/{course_id}/upload` | Bearer JWT |
| GET | `/api/health` | Public |
| GET | `/api/materials/{material_id}/download` | Bearer JWT |
| POST | `/api/materials/{material_id}/study` | Bearer JWT |
| GET | `/api/me` | Bearer JWT |
| PATCH | `/api/me` | Bearer JWT |
| GET | `/api/message-contacts/{student_id}` | Bearer JWT |
| GET | `/api/messages` | Bearer JWT |
| POST | `/api/messages` | Bearer JWT |
| GET | `/api/notifications` | Bearer JWT |
| POST | `/api/notifications/{notification_id}/read` | Bearer JWT |
| GET | `/api/parent/links` | Bearer JWT |
| POST | `/api/parent/links` | Bearer JWT |
| GET | `/api/payments/{payment_id}/receipt` | Bearer JWT |
| POST | `/api/payments/{payment_id}/verify` | Bearer JWT |
| GET | `/api/plans` | Public |
| GET | `/api/quizzes/{quiz_id}` | Bearer JWT |
| POST | `/api/quizzes/{quiz_id}/attempt` | Bearer JWT |
| GET | `/api/recommendations` | Bearer JWT |
| POST | `/api/recommendations/generate` | Bearer JWT |
| POST | `/api/recommendations/{recommendation_id}/archive` | Bearer JWT |
| GET | `/api/recommendations/{recommendation_id}/history` | Bearer JWT |
| POST | `/api/recommendations/{recommendation_id}/regenerate` | Bearer JWT |
| POST | `/api/recommendations/{recommendation_id}/review` | Bearer JWT |
| POST | `/api/recommendations/{recommendation_id}/view` | Bearer JWT |
| GET | `/api/schools` | Public |
| GET | `/api/students/{student_id}/performance` | Bearer JWT |
| GET | `/api/students/{student_id}/report.csv` | Bearer JWT |
| POST | `/api/submissions/{submission_id}/grade` | Bearer JWT |
| POST | `/api/teacher-tools/lesson-draft` | Bearer JWT |
| POST | `/api/teacher-tools/lessons` | Bearer JWT |
| GET | `/api/teacher-tools/lessons/{course_id}` | Bearer JWT |
| POST | `/api/teacher-tools/quiz-draft` | Bearer JWT |
| POST | `/api/tutor/ask` | Bearer JWT |
| GET | `/api/tutor/history` | Bearer JWT |
