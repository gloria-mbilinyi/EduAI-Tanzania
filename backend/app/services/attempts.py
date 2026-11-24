"""A Submission is a stable per-student assessment record; attempts are append-only."""
from fastapi import HTTPException
from ..models import *
from ..core.database import now
from .access import record

DEFAULT_POLICY = dict(max_attempts=1, allow_resubmission=False, allow_late=False,
                      require_feedback=False, require_approval=False, grading_policy='latest')

def policy(db, assignment_id):
    p = db.query(AssignmentPolicy).filter_by(assignment_id=assignment_id).first()
    return {k: getattr(p, k) for k in DEFAULT_POLICY} if p else dict(DEFAULT_POLICY)

def ensure_first(db, submission):
    first = db.query(SubmissionAttempt).filter_by(submission_id=submission.id, number=1).first()
    if not first:
        first = SubmissionAttempt(submission_id=submission.id, number=1, content=submission.content, created_at=submission.created_at)
        db.add(first)
        db.flush()
        g = db.query(Grade).filter_by(submission_id=submission.id).first()
        if g: db.add(GradeHistory(attempt_id=first.id, score=g.score, feedback=g.feedback, grader_id=g.grader_id, created_at=g.created_at))
    return first

def grade_for(db, attempt):
    if attempt.number == 1:
        return db.query(Grade).filter_by(submission_id=attempt.submission_id).first()
    return db.query(AttemptGrade).filter_by(attempt_id=attempt.id).first()

def history(db, submission):
    rows = db.query(SubmissionAttempt).filter_by(submission_id=submission.id).order_by(SubmissionAttempt.number).all()
    if not rows:
        g = db.query(Grade).filter_by(submission_id=submission.id).first()
        return [dict(id=None, submission_id=submission.id, number=1, content=submission.content,
                     created_at=submission.created_at, grade=record(g) if g else None)]
    return [record(a) | {'grade': record(g) if (g := grade_for(db, a)) else None} for a in rows]

def official(db, submission, p=None):
    rows = history(db, submission)
    p = p or policy(db, submission.assignment_id)
    key = p['grading_policy']
    if key == 'selected':
        selection = db.query(FinalGradeSelection).filter_by(submission_id=submission.id).first()
        chosen = next((r for r in rows if selection and r['id'] == selection.attempt_id), None)
    elif key == 'first': chosen = rows[0]
    elif key == 'best': chosen = max((r for r in rows if r['grade']), key=lambda r: r['grade']['score'], default=None)
    else: chosen = rows[-1]  # latest ungraded attempt makes the official score pending
    return chosen if chosen and chosen['grade'] else None

def eligibility(db, assignment, student_id):
    p = policy(db, assignment.id)
    s = db.query(Submission).filter_by(assignment_id=assignment.id, student_id=student_id).first()
    rows = history(db, s) if s else []
    number = len(rows) + 1
    approval = db.query(ResubmissionApproval).filter_by(assignment_id=assignment.id, student_id=student_id,
                attempt_number=number, status='approved').order_by(ResubmissionApproval.id.desc()).first()
    if approval and approval.reopen_until and approval.reopen_until < now(): approval = None
    limit = max(p['max_attempts'], number if approval else 0)
    reason = None
    if number > limit: reason = 'Maximum attempts reached'
    elif rows and not p['allow_resubmission'] and not approval: reason = 'Resubmission is disabled'
    elif rows and p['require_feedback'] and (not rows[-1]['grade'] or not rows[-1]['grade']['feedback'].strip()): reason = 'Wait for teacher feedback'
    elif rows and p['require_approval'] and not approval: reason = 'Teacher approval is required'
    elif assignment.due_at and assignment.due_at < now() and not p['allow_late'] and not (approval and approval.reopen_until):
        reason = 'Assignment deadline has passed'
    return dict(policy=p, attempts=rows, remaining_attempts=max(0,limit-len(rows)), next_attempt=number,
                can_submit=reason is None, blocked_reason=reason), s, approval

def add_attempt(db, assignment, student, content):
    state, s, approval = eligibility(db, assignment, student.id)
    if not state['can_submit']: raise HTTPException(409, state['blocked_reason'])
    if not s:
        s = Submission(student_id=student.id, assignment_id=assignment.id, content=content)
        db.add(s); db.flush()
    else: ensure_first(db, s)
    a = SubmissionAttempt(submission_id=s.id, number=state['next_attempt'], content=content)
    db.add(a)
    if approval: approval.status = 'used'
    db.add(LearningActivity(student_id=student.id, course_id=assignment.course_id, action='assignment_submitted'))
    return s, a
