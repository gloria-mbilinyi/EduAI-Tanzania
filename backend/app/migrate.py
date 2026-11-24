"""Forward-only migrations. No database or legacy table is rebuilt."""
from sqlalchemy import text
from .core.database import engine, Base
from . import models

def migrate(bind=None):
    with (bind or engine).begin() as conn:
        conn.execute(text('CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, description VARCHAR(200) NOT NULL)'))
        if conn.execute(text('SELECT version FROM schema_migrations WHERE version=1')).first() is None:
            Base.metadata.create_all(conn)
            conn.execute(text("INSERT INTO schema_migrations VALUES (1, 'EduAI normalized baseline')"))
        if conn.execute(text('SELECT version FROM schema_migrations WHERE version=2')).first() is None:
            Base.metadata.create_all(conn)
            conn.execute(text('''INSERT INTO assignment_policies
                (assignment_id, max_attempts, allow_resubmission, allow_late, require_feedback, require_approval, grading_policy, created_at)
                SELECT id, 1, false, false, false, false, 'latest', created_at FROM assignments
                WHERE NOT EXISTS (SELECT 1 FROM assignment_policies p WHERE p.assignment_id=assignments.id)'''))
            conn.execute(text('''INSERT INTO submission_attempts (submission_id, number, content, created_at)
                SELECT id, 1, content, created_at FROM submissions WHERE assignment_id IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM submission_attempts a WHERE a.submission_id=submissions.id)'''))
            conn.execute(text('''INSERT INTO grade_history (attempt_id, score, feedback, grader_id, created_at)
                SELECT a.id, g.score, g.feedback, g.grader_id, g.created_at FROM grades g
                JOIN submission_attempts a ON a.submission_id=g.submission_id AND a.number=1'''))
            conn.execute(text('''INSERT INTO recommendation_revisions (recommendation_id, version, content, reasons, created_at)
                SELECT id, version, content, reasons, created_at FROM ai_recommendations'''))
            conn.execute(text("INSERT INTO schema_migrations VALUES (2, 'Add policies attempts feedback history and recommendation snapshots')"))
        if conn.execute(text('SELECT version FROM schema_migrations WHERE version=3')).first() is None:
            Base.metadata.create_all(conn)
            conn.execute(text("INSERT INTO schema_migrations VALUES (3, 'Typed quiz answers review evidence and pending manual assessment')"))

if __name__ == '__main__':
    migrate()
    print('Versioned migrations applied or already present; legacy rows preserved')
