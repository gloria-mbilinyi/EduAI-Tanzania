"""Capture authentic history; the snapshot identifies its exact pre-report commit."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[1]
BASE='b45aa529d53d735f9ab74108dd3b50e4dbda0e3f'
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True,encoding='utf-8').strip()
head=git('rev-parse','HEAD');count=int(git('rev-list','--count','HEAD'));base_count=int(git('rev-list','--count',BASE))
rows=[line.split('\t',2) for line in git('log','--reverse','--date=iso-strict','--format=%H%x09%ad%x09%s').splitlines()]
new=set(git('rev-list',BASE+'..HEAD').splitlines());files=git('diff','--name-only',BASE,'HEAD').splitlines()
out=ROOT/'docs/agent-development-log';out.mkdir(exist_ok=True)
log=['# Development activity from actual Git history','',f'Snapshot at `{head}`; {count} reachable commits. The enhancement starts from {base_count} commits at `{BASE}`. Later report and release commits are available in Git and the external final delivery report. The original remote Initial commit is retained and is not attributed to agent implementation.','','| SHA | Recorded commit time | Completed unit |','| --- | --- | --- |']
log += [f'| `{sha}` | {date} | {subject} |' for sha,date,subject in rows]
(out/'DEVELOPMENT_ACTIVITY.md').write_text('\n'.join(log)+'\n',encoding='utf-8')
(out/'commit-snapshot.json').write_text(json.dumps({'snapshot_head':head,'reachable_commits':count,'baseline_head':BASE,'baseline_count':base_count,'enhancement_commits_at_snapshot':len(new),'changed_files_since_baseline':files,'commits':[{'sha':s,'recorded_at':d,'subject':m,'enhancement':s in new} for s,d,m in rows]},indent=2),encoding='utf-8')
report=f'''# Agent contribution report

## Human instructions and preserved baseline

The human developer supplied the original master brief and the enhancement brief retained under docs/requirements. The latest brief required modification of the existing project, hybrid mathematics and tutoring, multi-attempt assignments, reviewed quizzes, bilingual workflows, improved UML, a consistent proposal, additive migrations, actual tests and meaningful commits. It prohibited losing existing records or authentic history.

The human confirmed gloria-mbilinyi/EduAI-Tanzania, main, and preservation of the original remote initial commit. The human authorized GitHub CLI device authentication as gloria-mbilinyi and normal pushes. The agent verified that identity and repository Admin/Write permissions. No stakeholder interviews, meetings, classroom study, educator validation or actual model training are invented.

The enhancement baseline was `{BASE}` with {base_count} reachable commits. The initial remote commit remains an ancestor. The working tree was clean; no database file was found inside this checkout at the start. No existing database was deleted or reset. Browser QA created a separate fictional database retained in ignored work storage.

## Agent architecture decisions and changed modules

The agent retained the modular React/FastAPI application. It added ten extension tables, resulting in 38 ORM tables and a migration ledger. Submission remains the stable student-assessment anchor, preserving old IDs and uniqueness constraints. SubmissionAttempt is append-only. Grade retains first-attempt IDs; AttemptGrade stores later marks. Policies, specific resubmission approval, immutable feedback history and final selection define the official result.

Performance counts at most one official mark per assessment and exposes attempts and improvement. Recommendation drafts use actual scores, weaker feedback, score-derived mastery, activity and preferences; immutable content/evidence snapshots retain each new version. Assigned-teacher approval still gates every publication. Grade changes never auto-publish a pathway.

The tutor separates explicit language handling, subject/topic classification, intent, safe symbolic work, retrieval, optional provider and private history. The parser constructs whitelisted SymPy objects from a bounded AST without evaluating user text. A separate process limits tutor computation. Topic gating fixes calculus-to-algebra mismatches. Twenty-five original bilingual notes cover eight subjects.

Ollama is local, optional and disabled by default. Model availability, bounded requests, limited context, source validation and graceful fallback are implemented. Prompt context is untrusted data; no grade/publication tools exist. No model was downloaded or evaluated. Quiz assistance supports reviewed typed drafts, parameterized numerical variants, secure objective/numeric grading and pending manual short-answer assessment.

The agent added policy and attempt interfaces, review/reopen controls, math formatting, structured quiz editing and persistent language preference. Static text, API errors, notifications and report labels were localized. Teacher-entered content keeps its original language. The source/API/schema reference now lists 71 paths and 83 operations.

## Migration preservation evidence

Versions 2 and 3 add tables only; no legacy table is dropped, altered or rebuilt. Compatibility tests populate frozen actual version-1 DDL, create and integrity-check a SQLite backup, compare every old table row, migrate twice and verify preservation. The PowerShell guide documents backup, upgrade and recovery boundaries. SQLite is exercised; PostgreSQL and operational restoration remain untested.

## Executed checks and corrected failures

Actual results: 95 backend tests, 12 component/client tests and 12 running-browser scenarios pass. TypeScript and Vite production build passes. Original tests are retained. Browser scenarios cover all four roles, three attempts graded 45/80/100, specific extra approval, calculus and equation answers, Kiswahili persistence, reviewed numerical quizzes and 390-pixel layouts. Twenty screenshots come from the application.

Testing caught and corrected a wrongly derived intermediate linear-equation step; map-reading subject ambiguity; a legacy fixture calling the upgraded service too early; Windows backup-journal path limits; a tutor draft-clearing race; untranslated dynamic public feature text; and asynchronous browser assertions reading earlier answers. An older server on default ports was identified and the enhanced QA app isolated on 8011/5181. Earlier failures are not counted as successful runs.

## UML and proposal work

All eight original native drawio filenames remain. Sequence and communication views share 72 direct nested-numbered messages. State views distinguish stored, transient and derived states. Focused class packages reflect attempts, grade storage, approvals and hybrid AI services, with multiplicities at endpoints. Layout checks cover 737 text cells without overflow. Every diagram has a PNG and vector PDF with no raster PDF XObjects.

The 31-section proposal is updated in DOCX and an independently rendered 53-page PDF, with 39 figures and enlarged interaction, lifecycle and package inserts. All PDF pages were visually reviewed. DOCX XML, sections, page fields and figures are structurally checked. The Documents and PDF skills guided artifact revision. Computer Use was attempted for Word validation when COM failed.

Native diagrams.net opening remains unverified because embed initialization timed out before loading a source. Native Word pagination is also unverified: LibreOffice is unavailable, COM returned Access denied and supported desktop launching exposed no Word window. These unavailable checks are explicitly reported, not labeled passed.

## Authentic history and remaining boundaries

At this snapshot `{head}`, {count} commits are reachable, including {len(new)} enhancement commits. The tables and JSON record actual SHAs and changed files. Report/release commits made afterward appear in Git and the external final synchronization report, avoiding a self-referential final SHA inside its own commit.

Original functional coverage is 49/50 (98 percent); existing-role reassignment AD-02 remains partial. No real-model quality evaluation, curriculum certification, production deployment, real payment integration, accessibility certification, independent penetration test or learning-outcome study is claimed. One upstream deprecation warning and a large frontend bundle warning remain. Remote CI success is reported only if actually observed. Final push verification compares local and remote SHAs, complete history sets and artifact blob IDs without force-pushing.
'''
(out/'AGENT_CONTRIBUTION_REPORT.md').write_text(report,encoding='utf-8')
print(json.dumps({'snapshot':head,'commits':count,'enhancement_commits':len(new),'changed_files':len(files)}))
