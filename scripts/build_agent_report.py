from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()
head=git('rev-parse','HEAD');count=int(git('rev-list','--count','HEAD'));history=git('log','--reverse','--date=iso-strict','--format=%H%x09%ad%x09%s')
out=ROOT/'docs/agent-development-log';out.mkdir(parents=True,exist_ok=True)
rows=[line.split('\t',2) for line in history.splitlines()]
log=['# Development activity from actual Git history','',f'Snapshot at `{head}`; {count} reachable commits. Later delivery commits are available in Git and the final bundle. The original remote Initial commit is retained and is not attributed to agent implementation.','','| SHA | Recorded commit time | Completed unit |','| --- | --- | --- |']
log += [f'| `{sha}` | {date} | {subject} |' for sha,date,subject in rows]
(out/'DEVELOPMENT_ACTIVITY.md').write_text('\n'.join(log)+'\n',encoding='utf-8')
(out/'commit-snapshot.json').write_text(json.dumps({'snapshot_head':head,'reachable_commits':count,'commits':[{'sha':s,'recorded_at':d,'subject':m} for s,d,m in rows]},indent=2))
report=f'''# Agent contribution report

## Human instructions and decisions

The human developer supplied the complete master brief retained in
docs/requirements/MASTER_BRIEF.txt. It specified EduAI Tanzania, four roles,
English/Kiswahili, React/TypeScript, FastAPI, relational storage, teacher-controlled
assistance, simulated verified payments, eight editable draw.io files, a proposal,
tests and incremental version control. It explicitly requested genuine commits
and prohibited claiming unverified test or push success.

The human confirmed gloria-mbilinyi/EduAI-Tanzania as the target, made the
repository public, requested checking authentication as gloria-mbilinyi rather
than the connector's buriro-ezekia identity, and instructed preservation of owner,
existing work and all genuine history. These are human decisions, not agent-
generated organizational requirements. No fictional stakeholder interviews,
meetings, student study or human review approval are asserted.

## Agent analysis and architecture decisions

The agent inspected an empty workspace and established an independent repository
before substantial code development. It retained all 50 functional IDs and 12
business rules. An early planning total was corrected to the actual 50 after
counting the identifiers. Coverage excludes four partial requirements.

The agent chose a modular local React/FastAPI architecture, SQLite for an external-
service-free demo, SQLAlchemy models and a versioned baseline migration. It used
current database-backed role/school checks, explicit parent approvals, assigned
course checks, hidden answer keys, atomic teacher review publication and an
internal simulated provider ledger. New teacher accounts require school activation.
Existing-role reassignment was left partial rather than implemented ambiguously.

## Modules implemented by the agent

Identity and profile management; registered schools; courses and enrollment;
assigned teacher management; notes, HTTPS links and protected capped uploads;
assignments, text submissions, teacher grades and objective quizzes; performance
charts, CSV reports and rule explanations; recommendation generation, review,
rejection, regeneration, version/history and archival; bilingual retrieval tutor
and private history; entitled lesson and question-bank drafts; verified family
links, notifications and teacher-parent messages; plans, simulated payments,
receipts, expiry, suspension and cancellation; administrator school reports,
account activation and audit views; responsive public and four-role interfaces.

The agent also created 28 normalized relational tables, seed/setup/run helpers,
the actual API/schema reference, dependency locks, browser scenarios, screenshots,
CI configuration, traceability and the technical proposal sources and artifacts.

## AI implementation and capability boundaries

Recommendation/risk code uses transparent rules over persisted demonstration
grades, activity, interests and preferences. The tutor performs lexical retrieval
over 11 original bilingual teaching passages. No real student training dataset,
validated accuracy or generative LLM is claimed. Lesson assistance combines
retrieval and a template. Quiz assistance assembles existing question-bank items;
novel generation is partial (TC-09 and AI-07). All recommendations require an
assigned teacher approval before student visibility. Premium tools independently
require a verified active subscription.

## UML and documentation generation

The agent generated native mxGraph XML with separately editable vertices,
connectors, compartment text, states, messages and guards. Sequence and
communication diagrams use the same ordered process definitions. The exporter
reads the saved XML for PNG/vector PDF generation. XML IDs, references, geometry
and export files are checked. Visual review corrected attachment directions,
class text crossings, relationship labels, combined Grade/Submission concepts and
alt/opt/loop frame boundaries. Module stereotypes make conceptual services explicit.

The proposal has all 31 requested sections, all eight diagrams and 17 enlarged
interaction/package extracts. The PDF is independently rendered and reviewed.
An online native-editor initialization attempt timed out before a source was
loaded. The packaged DOCX renderer failed because soffice.exe was unavailable;
editable DOCX content exists, but Word pagination is not claimed as verified.

## Tests and corrections supported by evidence

Executed evidence: 48 real FastAPI/service tests with isolated SQLite databases,
9 React/client tests, 8 Playwright scenarios against running local services and a
successful TypeScript/Vite production build. Negative cases cover unrelated
students, cross-school access, unassigned courses, student grade/review attempts,
unapproved drafts, forged provider results, expired and unverified entitlement.

The first browser run found form controls whose wrapper labels included option
or textarea text. The agent replaced them with stable IDs and htmlFor labels,
made an ambiguous test select a visible heading and reran the same scenarios
successfully. Chart animation was disabled to make captured results stable.
GET materials was changed to be read-only; students now explicitly mark study
activity, preventing duplicated React development fetches from inflating evidence.
The relevant added tests passed. SQL DDL export whitespace was corrected after
git diff --check rejected the initial staging; no failed staging was presented
as a successful commit.

## Git and synchronization evidence

This report's history snapshot is **{count} reachable commits at {head}**.
DEVELOPMENT_ACTIVITY.md and commit-snapshot.json list actual SHAs, recorded times
and subjects. Final delivery commits after this snapshot are preserved in Git and
the supplied bundle; the final external engineering report gives the final count.
Git uses the pre-existing local author configuration; the agent executed the
new development commits under the human's instruction. The retained remote
Initial commit is not an agent contribution.

The original GitHub README commit was fetched and merged with both parent
histories preserved. An add/add README conflict was resolved by retaining the
original description and developed documentation. No force push or owner change
was made. The connected GitHub identity has read access but no push permission.
Git Credential Manager account enumeration and the device-login attempt for
gloria-mbilinyi returned Windows access denied. No successful upload is invented.

## Remaining work and human review

The human developer should review academic wording, verify the editable files on
the submission computer and assess teaching content with educators. Remaining
functional work is complete localization, existing-role reassignment and novel
quiz generation. Later deployment requires PostgreSQL checks, governance,
operational security, capacity/recovery work and real provider integration if
desired. Read docs/KNOWN_LIMITATIONS.md and the final validation report for exact
verification limits. No real-school effectiveness study has been completed.
'''
(out/'AGENT_CONTRIBUTION_REPORT.md').write_text(report,encoding='utf-8')
print(json.dumps({'snapshot_head':head,'reachable_commits':count}))
