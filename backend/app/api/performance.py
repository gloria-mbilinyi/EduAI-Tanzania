import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import principal
from ..models import User
from ..services.access import student_access
from ..services.performance import performance

router = APIRouter(prefix='/api', tags=['performance'])

@router.get('/students/{student_id}/performance')
def report(student_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    s = student_access(db, u, student_id)
    return performance(db, student_id, u) | {'name': s.name}

@router.get('/students/{student_id}/report.csv')
def export(student_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    data = report(student_id, u, db)
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(['Student ID', 'Subject', 'Assessment', 'Score percent', 'Feedback'])
    # Escape spreadsheet formula prefixes in free text.
    safe = lambda s: "'" + s if s.startswith(('=', '+', '-', '@', '\t', '\r')) else s
    for c in data['courses']:
        for r in c['results']: writer.writerow([student_id, safe(c['subject']), safe(r['title']), r['score'], safe(r['feedback'])])
    return Response(stream.getvalue(), media_type='text/csv', headers={'Content-Disposition': f'attachment; filename=student-{student_id}-progress.csv'})
