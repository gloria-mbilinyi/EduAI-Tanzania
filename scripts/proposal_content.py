"""Academic proposal narrative aligned with executed enhancement evidence."""
SECTIONS = [('Abstract',
  ['EduAI Tanzania Ltd is an academic browser-based platform connecting secondary-school learning, assigned teaching, '
   'verified family access and school administration. The enhancement extends the existing reference prototype in '
   'place. Its original 58 commits, initial GitHub commit and source history are preserved; it does not replace the '
   'application or reset a demonstration database.',
   'The enhanced React and FastAPI system combines verified symbolic mathematics, topic-aware bilingual retrieval and '
   'optional local Ollama generation. Assignment policies support multiple attempts, feedback history and one official '
   'score per assessment. Recommendations explain actual results and progress and remain hidden until an assigned '
   'teacher approves them. Typed quiz drafts require review before publication, with secure objective or symbolic '
   'grading and manual assessment of short answers.',
   'Local evidence comprises 95 backend tests, 12 component tests and 12 browser scenarios passing, with a successful '
   'production build. Coverage of the original 50 functional IDs is 49 complete and one partial, or 98 percent. No '
   'educational outcome study, trained predictive model, installed generative-model evaluation, live payment '
   'integration or production deployment is claimed.']),
 ('Introduction',
  ['A school learning platform should help a student find the next useful activity, allow a teacher to maintain '
   'trustworthy academic records and let an authorized parent understand progress. These functions are often separated '
   'across classroom materials, paper records and informal messages. The proposed system combines them while '
   'preserving the different responsibilities of each role.',
   'This proposal defines the problem, scope, design, implementation approach and evaluation plan for EduAI Tanzania. '
   'The reference prototype is evidence that the architecture can support important workflows; it is not evidence of '
   'school-wide adoption or improved educational attainment. The intended academic submission precedes a later '
   'prototype presentation and any real-school pilot.']),
 ('Background of the Study',
  ['The supplied scenario identifies shortages of qualified subject teachers, uneven access to personalized resources, '
   'delayed family communication and limited use of academic evidence. These concerns motivate a system that can make '
   'existing teaching resources easier to access and give teachers clearer information for follow-up. No survey size, '
   'national shortage percentage or student-outcome dataset is assumed.',
   'Tanzania Institute of Education publishes an ordinary secondary education curriculum and subject syllabuses [9]. '
   'These publications provide an authoritative starting point for later educator-led content mapping. The prototype '
   'uses original illustrative examples in mathematics, biology, physics, chemistry, geography, history, English and '
   'Kiswahili. Their inclusion must not be interpreted as curriculum certification.',
   'Connectivity and device constraints influence the design. Text notes and concise forms receive priority over large '
   'media. Files are capped at 5 MB, videos can be linked through HTTPS and core assistance does not depend on an '
   'external language-model service. Full offline synchronization is outside the current implementation.']),
 ('Problem Statement',
  ['The original tutor could select an algebra passage for a broad calculus request and could not solve a direct '
   'equation such as 3x + 9 = 18. Generic keyword overlap could therefore produce irrelevant assistance. The original '
   'assignment workflow also restricted each student to one submission, limiting practice after feedback.',
   'The enhancement separates classification, symbolic computation, retrieval and optional generation. It introduces '
   'per-assignment policies and immutable attempts while retaining existing submission and grade identifiers. The '
   'academic problem remains wider than software implementation: teachers must validate content, interpret recorded '
   'evidence and supervise recommendations.']),
 ('Project Objectives',
  ['The main objective is to demonstrate a maintainable school learning platform with explicit teacher supervision and '
   'trustworthy academic records.',
   'Implemented enhancement objectives are safe symbolic solving, topic-aware English and Kiswahili tutoring, optional '
   'local generation with graceful fallback, policy-controlled resubmissions, official-score reporting, '
   'progress-sensitive recommendations, reviewed typed quizzes, structured localization, additive migrations and '
   'traceable tests. Educator evaluation of learning quality and operational readiness remains future work.']),
 ('Scope of the System',
  ['Students, teachers, parents and administrators operate within registered schools. The reference system includes '
   'protected resources, text assignments, policy-controlled attempts, feedback history, typed quizzes, reports, '
   'reviewed pathways, in-app communication and simulated subscriptions.',
   'The bounded math engine covers arithmetic, fractions, linear and quadratic equations, practical simultaneous '
   'linear equations, simplification, factorization, substitution, polynomial differentiation and integration, and '
   'basic trigonometric expressions. Unsupported input produces clarification.',
   'Optional Ollama uses an administrator-configured installed model on a local endpoint. No model was downloaded or '
   'exercised here. Real money, SMS/email delivery, video streaming, offline synchronization, formal predictive '
   'modeling, full curriculum ingestion, production operation and changing an existing identity role remain outside '
   'completed scope.']),
 ('Stakeholder Analysis',
  ['Students need understandable instructions, timely feedback and reliable access to their own records. Teachers need '
   'manageable course ownership, useful evidence and the ability to reject unsuitable suggestions. Parents need secure '
   'linkage and clear progress information. School administrators need controlled provisioning, verified links, course '
   'assignments, reports and auditable subscription actions.',
   'The human developer supplies requirements and institutional context, reviews design choices and remains '
   'responsible for academic submission and any deployment decision. The software agent carries out documented '
   'engineering tasks. A future pilot would also involve school leadership, subject specialists, accessibility '
   'reviewers and the people responsible for operating the service.',
   'Student data subjects have interests beyond application convenience. A later pilot should establish an appropriate '
   'consent and governance process, minimize collected data and define retention, correction and incident-handling '
   'procedures before any real records are imported. This proposal makes no legal-compliance certification.']),
 ('Functional Requirements',
  ['The original master brief contains 50 functional IDs: 12 student, 11 teacher, 7 parent, 10 administrator and 10 AI '
   'requirements. The traceability files retain every ID and link it to source and executed evidence.',
   'The enhancement covers structured English and Kiswahili switching and teacher-reviewed quiz assistance, including '
   'parameterized numerical variants and an optional provider whose response schema is tested with a mock. Original '
   'functional coverage is 49/50 complete, or 98 percent. AD-02 remains partial because administrators can provision '
   'role-assigned users and manage activation, but cannot change an existing identity role.',
   'This percentage measures implemented functions in the original brief. It does not measure curriculum quality, '
   'model accuracy, production readiness or native editor availability. The new enhancement requirements are '
   'additionally mapped in docs/requirements/ENHANCEMENT_TRACEABILITY.md.']),
 ('Non Functional Requirements',
  ['Security requires password hashing, expiring bearer tokens, current database-backed authorization and rejection of '
   'cross-school or unrelated-record access. Validation requires bounded strings, valid score ranges, valid quiz '
   'options and explicit allowed input fields. Reliability requires persisted transactions, uniqueness constraints, '
   'idempotent payment verification and useful failure messages.',
   'Usability requires consistent navigation, visible states, associated form labels and layouts that fit a narrow '
   'viewport. Portability requires a local SQLite demonstration and a configurable PostgreSQL connection. '
   'Maintainability requires separated models, API handlers, access helpers, assistance modules and repeatable checks.',
   'Performance targets for a future pilot should be agreed with the host school after measuring actual connectivity '
   'and device constraints. No response-time service-level agreement or concurrency capacity is claimed from the '
   'present tests. Proposed evaluation should include slow-connection trials, keyboard-only navigation and task '
   'completion on affordable phones.']),
 ('Business Rules',
  ['The twelve business rules are implemented at the API trust boundary. Every student must have a registered school. '
   'Parent access requires an approved school-scoped link. Teacher mutations require a course assignment. '
   'Recommendation publication requires an assigned teacher approval. Administrator reports are school-scoped, and '
   'protected services require a valid active principal.',
   'Premium access additionally requires a premium subscription in active state, a future expiry and a verified '
   'payment record. Students cannot write grades or review decisions. Passwords are hashed using salted PBKDF2 '
   'SHA-256. Sensitive records are checked for ownership, school, enrollment or family linkage before being returned.',
   'A client-submitted success flag never verifies a payment. The server reads its internal demonstration provider '
   'ledger and compares reference, amount and currency. Important mutations append audit entries. A production audit '
   'service should add tamper-resistant external retention and operating procedures; the prototype provides '
   'application-level history.',
   'Assignment policies define maximum attempts, permission to resubmit, deadline and late work, feedback and approval '
   'gates, and the official grading rule. A teacher can authorize a specific next attempt or reopen a deadline for an '
   'enrolled student. Each new attempt is appended, each accepted grading revision is retained, and a student cannot '
   'exceed current authorization. First, best, latest and teacher-selected policies contribute at most one official '
   'score per assignment. A latest ungraded attempt has a pending official result.',
   'No grade change automatically publishes or replaces an approved recommendation. Rejected recommendations may be '
   'regenerated with a new immutable content-and-evidence snapshot, and must pass teacher review again. Objective quiz '
   'grades cannot be overwritten by model output or by manual short-answer grading.']),
 ('Feasibility Study',
  ['Technical feasibility is supported by the locally executed React/FastAPI prototype and its automated tests. The '
   'selected open-source stack supports ordinary HTTP browsers and relational storage. SQLAlchemy separates database '
   'access from much of the business logic, although PostgreSQL behavior still needs its own integration test before '
   'deployment [3].',
   'Economic feasibility is evaluated qualitatively. No paid AI API, hosting contract, payment gateway or subscription '
   'service is required to run the demonstration. Hardware, connectivity, support, backups and staff training still '
   'have costs. Demonstration plan prices are illustrative TZS amounts, not a market study or approved business '
   'tariff.',
   'Operational feasibility depends on teacher participation and school processes. Administrators must verify teacher '
   'identities and parent links; teachers must review pathways and teaching drafts. The project should not transfer '
   'these responsibilities to an automated score. A staged pilot is more appropriate than immediate organization-wide '
   'adoption.',
   'Schedule feasibility is managed through incremental deliverables. The remaining work for a presentation should '
   'prioritize educator review, complete translations, artifact opening checks and a reproducible demonstration. A '
   'later deployment schedule must include governance, performance testing and operational readiness.']),
 ('Technology Stack',
  ['The frontend uses React with TypeScript, Vite, React Router, Tailwind CSS, Lucide icons and Recharts. Fetch '
   'provides typed service access and error propagation. Shared form, notice, panel and navigation components keep '
   'role interfaces consistent. React state is separated from persisted server records [4].',
   'The backend uses Python, FastAPI, Pydantic, SQLAlchemy and PyJWT. Passwords are derived through Python '
   'cryptographic primitives. FastAPI provides an inspectable OpenAPI contract and supports bearer authentication '
   'patterns [2]. SQLite is used for executed local tests; an optional psycopg production requirements file prepares '
   'PostgreSQL connectivity.',
   'Pytest exercises real API behavior over isolated relational test databases. Vitest and React Testing Library cover '
   'interface states. Playwright drives headless Chrome against running local services and captures screenshots [7,8]. '
   'Diagram sources use native mxGraph XML and editable cells. Python-docx and ReportLab produce editable document '
   'content and a rendered PDF.',
   'SymPy 1.14 supplies symbolic operations and result verification. A custom bounded syntax-tree parser constructs '
   'only whitelisted mathematical objects; it does not pass raw text to eval, sympify or parse_expr. Tutor computation '
   'runs in a separate process with a five-second limit. The optional Ollama adapter uses httpx, bounded JSON '
   'responses and request limits [10,11].']),
 ('System Architecture',
  ['The architecture follows a browser-to-REST-to-services-to-database flow. The frontend never receives a database '
   'connection, answer-key mutation privilege or provider verification secret. API dependencies resolve the JWT '
   'subject to the current active user. The persisted role and school decide access rather than a client-controlled '
   'role string.',
   'Identity, academic, recommendation, communication and billing handlers are separated into API modules. Shared '
   'access functions validate school equality, teacher assignments, enrollment and parent links. Assistance modules '
   'consume academic evidence and teaching passages. Database models define keys and constraints; the versioned '
   'baseline migration establishes the schema.',
   'Protected uploaded files remain outside the frontend distribution. Downloads traverse an authorized API endpoint '
   'and use attachment responses. A production deployment would add TLS termination, managed configuration, database '
   'backups, monitoring and a hardened upload pipeline. Diagram 05 maps logical packages to actual source modules.',
   'The hybrid tutor pipeline is question, selected-language handling and detection, subject/topic classification, '
   'intent detection, bounded tool choice, symbolic verification or cited retrieval or optional local generation, and '
   'own-user conversation persistence. Topic gates remove the former generic solve-to-algebra mismatch. Follow-up '
   'context is limited to the current user and selected subject.',
   'Generation is isolated from academic writes. The provider sees a small context containing untrusted data, has no '
   'grade or publication tools, and must return validated JSON. Source IDs are checked against supplied passages; '
   'unsupported references cause retrieval fallback. These controls reduce prompt-injection exposure but do not '
   'establish that arbitrary generated prose is factually correct.']),
 ('Database Design',
  ['The enhanced ORM defines 38 entity tables plus the schema_migrations ledger. The original 28 tables remain intact. '
   'Users, password hashes, school records, courses, old submissions and grades, approvals, notifications, '
   'subscriptions and payments are preserved by forward-only migrations.',
   'Version 2 adds AssignmentPolicy, SubmissionAttempt, AttemptGrade, GradeHistory, ResubmissionApproval, '
   'FinalGradeSelection and RecommendationRevision. Submission remains the stable per-student assessment record with '
   'its original ID and uniqueness constraints. Attempt 1 retains its original Grade row. Later attempts have their '
   'own AttemptGrade; the service presents a consistent attempt history and official result.',
   'Version 3 adds QuestionSettings, QuizReview and QuizResponse. Existing multiple-choice questions need no altered '
   'columns. New typed settings hold numerical keys or short-answer rubrics. QuizResponse retains objective evidence '
   'and pending manual marks. Teachers assess short answers without changing objective components.',
   'The PowerShell upgrade helper creates a consistent SQLite backup, checks integrity, snapshots private row digests, '
   'migrates and verifies that every pre-existing row remains unchanged. Tests populate the actual baseline schema and '
   'verify an upgrade followed by a repeated idempotent migration. No database is deleted, recreated or reset. '
   'PostgreSQL migration and restore behavior have not been exercised.']),
 ('UML Sequence Diagram',
  ['Diagram 01 remains one comprehensive sequence view with all four required processes. Its enlarged interaction '
   'extracts show actors, lifelines, activation bars, nested numbering, synchronous calls, asynchronous alerts, '
   'returns and guarded alt, opt and loop fragments.',
   'The learning process includes topic classification, verified math or retrieval, scoped history and recommendation '
   'approval. The assignment process includes policy checks, numbered attempts, resubmission approval, feedback '
   'history and official grading. Parent and subscription processes retain verified relationships and server-side '
   'payment checks.']),
 ('UML Communication Diagram',
  ['Diagram 02 uses the same scenario definitions and all 72 numbered messages as Diagram 01. Message text and guards '
   'appear directly on the directed object links. The automated interaction check verifies that each nested number and '
   'message appears exactly once in both views.',
   'The object network describes collaboration rather than time along a lifeline. Enlarged process extracts accompany '
   'the complete view so the reader can compare participants and guards without depending on a separate message '
   'catalogue.']),
 ('AI Recommendation State Machine',
  ['Diagram 03 models the lifecycle of one recommendation. Analysis produces a pending-review draft. An assigned '
   'teacher can approve or reject it. Approval and publication occur together with a persisted decision; a rejected '
   'draft can be regenerated as a new version and must be reviewed again.',
   'Published records can be marked viewed by their student and archived by an assigned teacher. Generation failure '
   'rolls back the request. Created, analysis, generated, approved and revision labels describe transient conceptual '
   'steps; stored statuses are pending_review, rejected, published, viewed and archived. The diagram explicitly '
   'distinguishes this implementation detail rather than implying separate stored states.']),
 ('Subscription State Machine',
  ['Diagram 04 models creation, pending payment, verification, activation, expiry, suspension and cancellation. A '
   'backend check against the internal provider ledger precedes activation. A verified transaction with a changed or '
   'expired entitlement cannot bypass the premium service check.',
   'Expiring Soon is a derived presentation state. Renewal creates a new subscription and pending transaction, '
   'preserving the history of the expired object. Failed or rejected simulations remain non-entitled. Administrator '
   'restoration requires an existing verified payment and future expiry; cancellation requires a new checkout rather '
   'than silently reviving old access.']),
 ('Overview Package Diagram',
  ['Diagram 05 organizes authentication, profiles, courses, assessment, assistance, performance, communication, '
   'administration, reporting, billing, data access and shared services. Dependencies are directed toward the '
   'capabilities being used. Source module paths are shown so a reviewer can locate the implementation.',
   'The package view is logical rather than a claim that every box is a separately deployed microservice. A modular '
   'monolith is appropriate for this academic prototype because it keeps setup small and makes database transactions '
   'and permission checks easier to inspect.']),
 ('Detailed Package Diagrams',
  ['Diagrams 06, 07 and 08 each contain four focused logical packages with class compartments, short local connectors '
   'and endpoint multiplicities. Services use module stereotypes because implementation boundaries are Python '
   'functions rather than invented persistent classes.',
   'The learning view includes MathSolver, TopicClassifier, RetrievalService, ChatbotTutor and optional '
   'OllamaProvider. The assessment view shows AssignmentPolicy, stable Submission, many SubmissionAttempt rows, '
   'separate first/later grades, approval, final selection and typed quizzes. The family/admin view preserves actual '
   'links, reports, audit, simulated payment verification and entitlement.',
   'SchoolAdministrator is a User role. Where a logical association represents a service mapping rather than an ORM '
   'foreign key, the diagram note states that distinction. Enlarged package inserts preserve readability in the '
   'proposal. Native online draw.io initialization timed out before loading any file; XML editability, references, '
   'layout bounds and local exports are verified, but native editor opening is not claimed.']),
 ('AI Methodology',
  ['The tutor uses explicit bilingual topic aliases and subject-filtered original notes. Its 25 passages cover '
   'Mathematics, Biology, Chemistry, Physics, English, Kiswahili, Geography and History. The corpus is illustrative '
   'original content and has no national certification. A calculus request reaches the calculus note rather than '
   'linear equations. Insufficient matches are rejected instead of returning unrelated teaching content.',
   'The math engine supports bounded input grammar, whitelisted symbols and functions, operation and size limits, and '
   'a separate process time limit. Linear steps are derived from the actual equation. Polynomial roots are substituted '
   'into original equations; integration is checked by differentiating the result; simplifications and numerical quiz '
   'equivalents use symbolic checks. Difficult or unverifiable expressions produce an explicit limitation.',
   'Ollama is disabled by default. When explicitly requested and a suitable source exists, the adapter checks the '
   'exact installed model tag, sends a limited conversation and untrusted source data, applies time and output bounds, '
   'and validates the structured response and source identifiers. Missing, failing or invalid providers retain the '
   'teaching-note fallback. No local model inference quality or hardware performance has been evaluated.',
   'Recommendations use one official result per assessment, attempt improvements, feedback from weaker attempts, '
   'current score-derived mastery, activity, interests and preferences. With one Mathematics assessment improving from '
   '45 to 80 to 100 percent under best-attempt policy, the tested pathway changes from foundation to intermediate to '
   'advanced practice. Mastery and risk labels are transparent rules, not trained predictions or item-level diagnostic '
   'models.',
   'Quiz assistance accepts topic, objective, difficulty, count, language and type. Bank assembly, bounded '
   'parameterized numerical templates and optional validated model drafts all require teacher review. If a bank has '
   'fewer matching items than requested, the system states that limit and permits manual additions. Objective and '
   'true/false questions are graded on the server; numerical answers use symbolic equivalence; short answers remain '
   'pending until an assigned teacher grades them.']),
 ('Security and Privacy',
  ['Access checks are applied on the server. JWTs identify users but do not grant permanent roles; each request reads '
   'current role, school and activation state. Parent linkage and assigned-course relationships constrain academic '
   'reads. Student serializers omit quiz answer keys and unpublished recommendations. Role-restricted endpoints reject '
   'student grade changes and self-approval attempts.',
   'Passwords are salted and derived using PBKDF2 SHA-256 with 600,000 iterations. Tokens expire after two hours. '
   'Development creates an ignored random signing secret; production requires configured secret material and disables '
   'demonstration payments. No secret, virtual environment, dependency folder or local database is included in the '
   'tracked release.',
   'Uploads are capped, extension-checked and served as authorized attachments with nosniff. CSV exports escape '
   'formula prefixes in free text. Application audit entries document important actions without logging credentials. '
   'These controls are a prototype baseline, not an independent security certification.',
   'Before a real deployment, the school should approve data collection and retention processes, access reviews, '
   'incident response, secure backups, monitoring, rate limits and transport security. Browser session storage should '
   'be reassessed against HttpOnly-cookie alternatives and the surrounding threat model. The project has not assessed '
   'jurisdiction-specific compliance obligations.',
   'Additional controls enforce numbered-attempt uniqueness, policy caps, specific approval consumption, deadlines and '
   'school-scoped review. Math parsing rejects executable syntax, unknown names and excessive expressions. Ollama '
   'permits only configured local endpoints, has no tool permissions, caps context and response size, and rejects '
   'unsupported source IDs. A model response is never an authorized academic mutation.']),
 ('Development Methodology',
  ['Development follows incremental vertical workflows: define a requirement and invariant, implement its relational '
   'representation and API behavior, connect the interface, execute relevant checks and commit the result. Initial '
   'models and service contracts stabilize before final UML exports. This ordering allows the design deliverables to '
   'reflect actual behavior.',
   'The software agent performs source creation, testing, diagram generation and documentation under the '
   'human-supplied brief. Human steering establishes the target GitHub owner and requires preservation of existing '
   'work. An activity report records actual commits, failed checks, corrections and executed tests rather than '
   'inventing meetings or conversations.',
   'The repository preserves the original GitHub README commit by merging it with the independent local development '
   'history. No force push or owner change is used. Remote synchronization depends on authenticated write access and '
   'is reported separately from local engineering completion.',
   'The enhancement begins at the verified b45aa529 baseline with 58 reachable commits. Meaningful tested units extend '
   'that history without amending or force-pushing. GitHub CLI authentication is verified as gloria-mbilinyi with '
   'write permission before synchronization. The final external delivery report records exact local/remote SHAs and '
   'the reachable GitHub commit count.']),
 ('Implementation Plan',
  ['The local enhancement implements the hybrid tutor, additive attempt history, teacher controls, official-score '
   'analytics, recommendation snapshots, typed quiz review and structured localization. Test evidence and screenshots '
   'are generated from the running enhanced application using a separate fictional QA database; existing databases are '
   'not reset.',
   'Delivery updates all eight editable diagrams and the 31-section proposal, verifies exports, records actual commit '
   'history and pushes normally to the authorized main branch. Any unavailable native rendering or external model '
   'check is recorded as a limitation.',
   'A later school pilot requires educator content review, accessibility and low-connectivity studies, representative '
   'evaluation of learning quality, database deployment tests, operational recovery rehearsals and approved privacy '
   'procedures. Those activities have not been replaced by software unit tests.']),
 ('Testing Strategy',
  ['The enhanced suite preserves the original tests and adds migration compatibility, attempt limits and history, '
   'teacher approval and reopening, official grading policies, evidence-based progress, immutable recommendation '
   'versions, symbolic equations and calculus, malformed and unsafe expressions, topic routing, bilingual context, '
   'optional-provider fallback and typed-quiz protections.',
   'Actual local results are 95 pytest checks, 12 component/client checks and 12 Playwright browser scenarios passing, '
   'for 119 automated checks. The TypeScript and Vite production build passes. The original 65-check result is '
   'historical baseline evidence. The current reports under docs/testing are the source of truth.',
   'Browser tests drive actual UI submission, per-attempt grading, 45-to-80-to-100 progress, teacher resubmission '
   'approval, typed numerical quiz publication and grading, selected-language math, persisted language, public and '
   'all-role navigation, and 390-pixel layouts. Twenty screenshots are captured from the application. Earlier runs '
   'exposed use of an older server on the default port and a tutor draft-clearing race; the corrected enhanced build '
   'was rerun successfully on separate ports.',
   'One upstream Starlette/httpx deprecation warning and a frontend bundle-size warning remain. Optional generation '
   'uses mocked-provider success/failure tests; no real installed Ollama model was exercised. Native online draw.io '
   'initialization timed out before loading source. Document rendering results are recorded in the artifact validation '
   'evidence rather than inferred from OOXML structure.']),
 ('Risks and Mitigations',
  ['Teacher review and transparent source notes reduce educational-content risk; they do not establish learning '
   'effectiveness. Verified symbolic results cover only the bounded supported grammar. Arbitrary model prose may be '
   'inaccurate even when its source ID is valid, so generation is optional and clearly labeled.',
   'Preserving old IDs and using additive tables reduce migration risk. The verified backup-and-upgrade helper and '
   'baseline compatibility test support recovery planning. Production recovery, PostgreSQL behavior, capacity, TLS, '
   'rate limiting, monitoring and tamper-resistant audit retention still require operational validation.',
   'Broad diagrams are supplied as full editable sources and vector PDFs, with enlarged process and package inserts in '
   'the proposal. Native editor opening remains unverified because the online embed did not initialize. No real '
   'payment, production deployment, curriculum certification, student-data training or educational field study is '
   'claimed.']),
 ('Expected Outcomes',
  ['The expected academic outcome is a reviewable prototype that demonstrates traceable requirements, normalized '
   'relational design, clear role authorization, objective assessment, teacher-controlled assistance and a credible '
   'simulated billing workflow. The source, diagrams, tests and contribution evidence should allow an examiner to '
   'inspect how the system works.',
   'Expected operational benefits such as faster feedback, clearer family communication and more focused teaching '
   'remain hypotheses for a future pilot. They should be measured through task completion, educator judgments, '
   'usability observations and an agreed study design rather than asserted from synthetic demonstration records.',
   'The completed enhancement demonstrates supported mathematical answers, relevant topic retrieval, preserved '
   'multi-attempt evidence, teacher-controlled final scoring, reviewed typed quizzes and improved bilingual workflows. '
   'These are observed software behaviors. Improvements to attainment, teacher workload or family participation remain '
   'hypotheses for a properly designed pilot.']),
 ('Conclusion',
  ['The enhanced EduAI Tanzania prototype provides an inspectable implementation of school learning workflows with '
   'explicit teacher supervision. Safe symbolic tools address the demonstrated equation and calculus failures; '
   'additive attempts retain evidence of improvement while official-score policies prevent repeated attempts from '
   'inflating assessment counts.',
   'The source, tests, editable diagrams, enlarged proposal figures and authentic commit evidence support academic '
   'review. Educator validation, real-model evaluation, native editor opening, production operation and the declared '
   'existing-role-management gap remain distinct follow-up work. The final synchronization report gives the verified '
   'repository state.']),
 ('References',
  ['[1] Human developer. Master development prompt for EduAI Tanzania Ltd. Supplied project brief, retained in '
   'docs/requirements/MASTER_BRIEF.txt.',
   '[2] FastAPI. OAuth2 with Password and Bearer with JWT tokens. '
   'https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ (accessed 23 November 2026).',
   '[3] SQLAlchemy. Unified Tutorial. https://docs.sqlalchemy.org/en/20/tutorial/index.html (accessed 23 November '
   '2026).',
   '[4] React. Managing State. https://react.dev/learn/managing-state (accessed 23 November 2026).',
   '[5] Pydantic. Models. https://pydantic.dev/docs/validation/latest/concepts/models/ (accessed 23 November 2026).',
   '[6] draw.io. Embed mode and diagram export documentation. https://www.drawio.com/docs/reference/embed-mode/ and '
   'https://www.drawio.com/docs/manual/export/ (accessed 23 November 2026).',
   '[7] pytest. How to use fixtures. https://www.pytest.org/en/latest/how-to/fixtures.html (accessed 23 November '
   '2026).',
   '[8] Playwright. Installation and Writing tests. https://playwright.dev/docs/intro and '
   'https://playwright.dev/docs/writing-tests (accessed 23 November 2026).',
   '[9] Tanzania Institute of Education. Curriculum for Ordinary Secondary Education Form I-IV, 2023; lower-secondary '
   'syllabus catalogue. https://www.tie.go.tz/publications/syllabus-for-lower-secondary-academics (accessed 23 '
   'November 2026).',
   '[10] SymPy. Parsing documentation and calculus modules. https://docs.sympy.org/latest/modules/parsing.html and '
   'https://docs.sympy.org/latest/tutorials/intro-tutorial/calculus.html (accessed 24 November 2026). Raw user text is '
   'not passed to the evaluation-based parser.',
   '[11] Ollama. Generate a chat message API. https://docs.ollama.com/api/chat (accessed 24 November 2026).',
   '[12] Human developer. EduAI Tanzania complete system enhancement brief, 24 November 2026. Retained in '
   'docs/requirements/ENHANCEMENT_BRIEF.txt.']),
 ('Appendices',
  ['Appendix A contains enlarged interaction extracts from the same sequence and communication source images. '
   'Continuation views repeat participant headers for orientation. Appendix B supplies focused class packages and '
   'lifecycle details. Complete vector PDFs and editable sources accompany these print inserts.',
   'Appendix C locates executable evidence, fictional demonstration accounts and safe upgrade commands. The original '
   'and enhancement briefs, complete original functional matrix, new traceability map, actual test reports, '
   'screenshots and agent history are retained in the repository. Test records contain no real school dataset or '
   'payment credentials.',
   'All demo passwords are chosen locally and excluded from version control. The principal handles are admin, neema, '
   'amina, juma and parent at demo.eduai.test. Existing populated databases are never reseeded or reset.'])]

FIGURES = {16: ['01_EduAI_Sequence_Diagram'], 17: ['02_EduAI_Communication_Diagram'], 18: ['03_AI_Recommendation_State_Machine'], 19: ['04_Subscription_State_Machine'], 20: ['05_EduAI_Overview_Package_Diagram'], 21: ['06_Learning_AI_Detailed_Package', '07_Course_Assessment_Detailed_Package', '08_Admin_Parent_Subscription_Detailed_Package']}
