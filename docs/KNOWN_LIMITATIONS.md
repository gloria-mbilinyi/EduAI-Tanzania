# Known limitations and further validation

The enhanced original functional coverage is 49/50 (98%). AD-02 remains partial: existing identity roles cannot be reassigned. Administrators can create role-assigned users, activate/deactivate them, and manage course assignments. Historical profile transitions require a deliberate migration design.

The 25 original teaching passages are illustrative, not a certified national curriculum. Topic-aware retrieval and verified bounded mathematics work without a model. Ollama is optional and disabled by default. Its adapter and draft schemas are tested with mocked success/failure responses; no installed model, real inference quality, latency, memory use or hardware suitability was evaluated. The application never downloads a model.

Mathematics is limited to short whitelisted expressions, real solutions, practical linear systems, polynomial calculus and basic trigonometric forms. Symbolic checks do not constitute general proof verification. Arbitrary generated prose may be inaccurate even with a valid source ID. Teacher review remains necessary. Score-based mastery and risk are explainable rules, not trained predictions or item-level diagnoses.

Assignment attempts accept text. First-attempt grades retain their old IDs; later grades use an additive table. Earlier recommendation versions overwritten before the enhancement cannot be recovered; current and future versions are snapshotted. Quizzes retain one student attempt; written responses require teacher grading. If a topic bank cannot meet the requested count, the UI states the shortage and permits manual additions.

Machine-controlled interface text, API errors, new notifications and report headings have structured English/Kiswahili support and saved preferences. Teacher-authored content, historical messages and feedback retain their original language.

Native draw.io opening is unverified: the online embed initialization timed out before any file loaded. Native XML structure, editable cells, endpoint references, text bounds and local PNG/vector PDF exports are checked. Open the eight sources in diagrams.net on the presentation computer.

The 53-page PDF proposal was rendered and visually reviewed. DOCX structure, sections, page fields and 39 embedded figures were checked, but native Word pagination remains unverified. The bundled renderer lacks LibreOffice; installed Word COM activation returned Access denied, and supported desktop launching exposed no targetable Word window. The PDF is an independently rendered counterpart of the same content, not a claimed Word conversion.

Only SQLite has been exercised. PostgreSQL deployment, backup restoration drills, production load, independent penetration testing, accessibility certification, low-bandwidth studies, offline synchronization, real-school evaluation and formal privacy compliance review remain future work. The frontend bundle is about 805 kB raw (240 kB gzip), and one upstream Starlette/httpx deprecation warning remains.

Payments are fictional and per-user. No mobile-money/banking integration, pooled school billing, SMS or email delivery exists. No real student dataset or training is used. The final local/remote synchronization report is recorded separately; authentication is verified as gloria-mbilinyi, and no force push is used. Remote CI success is not assumed from local checks.
