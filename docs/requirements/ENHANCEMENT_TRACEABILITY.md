# Enhancement traceability

This supplements the original 50-ID matrix. It records implementation evidence and the practical boundary of each requested enhancement; it is not a claim of educational or production validation.

| Brief section | Implemented evidence | Verification and boundary |
| --- | --- | --- |
| Hybrid tutor and math | ai/topics.py, tutor.py, math_solver.py; api/tutor.py | test_math, test_tutor_hybrid; actual equation/calculus browser scenario. Bounded grammar, polynomial calculus, real solutions and five-second worker limit. |
| Optional local generation | ai/ollama.py, quiz_builder.py | test_ollama and test_quiz_types cover success, missing/invalid provider and sources. No installed model was exercised or downloaded. |
| Multiple attempts | models/enhancements.py, services/attempts.py, api/assignments.py, AssignmentWorkflows.tsx | test_attempts and actual three-attempt browser workflow, approval/reopening, feedback and authorization. |
| Progress-sensitive recommendations | performance.py, ai/recommendations.py, recommendation_revisions | test_progress verifies 45, 80 and 100 scores and foundation/intermediate/advanced guidance without auto-publication. Mastery is score-derived, not item-level diagnosis. |
| Reviewed typed quizzes | api/quizzes.py, teacher_tools.py, QuizWorkflows.tsx | test_quiz_types and numerical-draft browser scenario. Short answers await teacher grading. Bank shortfalls are explicit. |
| Bilingual workflows | i18n dictionaries, Trans, account language endpoint, API handlers | 277 checked static display keys, no missing translations; all-role/public browser switching; API/CSV/notification tests. User-authored content retains its original language. |
| Responsive UI | attempt cards, math formatting, forms, role navigation | Desktop and 390-pixel browser checks; 20 actual screenshots. No accessibility certification or slow-network capacity study. |
| Eight editable UML diagrams | diagrams/drawio, png, pdf; source generators | Independent editable cells and endpoint references checked; direct messages and layout bounds validated. Native online editor initialization timed out before loading any source. |
| Proposal | DOCX and 53-page independently rendered PDF, 31 sections, 39 figures | All PDF pages rendered and reviewed; enlarged process and package inserts. DOCX structure checked. Native Word pagination is unverified: converter absent, COM access denied and desktop launch unavailable. |
| Security | current-role, school, enrollment, family, assigned-course and premium checks | Original negative tests retained; attempt, math, key and provider tests added. No independent penetration test. |
| Database preservation | versioned migrations 2 and 3; upgrade helper | Baseline-schema populated fixture, backup integrity, every old table row unchanged and repeated idempotent upgrade. No real database reset. PostgreSQL not integration-tested. |
| Testing and Git | test reports and authentic incremental commits | 95 backend, 12 frontend and 12 browser checks; normal main push verification is recorded in the external final report. |
| Agent evidence | agent-development-log | Human instructions distinguished from agent implementation. SHA snapshots identify their exact capture point. |

The original functional matrix is 49/50 complete (98%). AD-02 remains partial: changing an existing identity's role is outside the implemented administrator controls. This percentage does not score rendering availability, educational quality or deployment readiness.
