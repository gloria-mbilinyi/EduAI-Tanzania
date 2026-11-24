import json
from typing import Literal
from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import principal, require, role
from ..models import *
from ..schemas.common import Input
from ..services.access import *
from ..ai.recommendations import generate

router = APIRouter(prefix='/api', tags=['recommendations'])
class Generate(Input):
    student_id: int = Field(gt=0)
    course_id: int = Field(gt=0)

def scope(db, u, student_id, course_id):
    student_access(db, u, student_id)
    course_access(db, u, course_id, manage=role(db, u) == 'teacher')
    if not enrolled(db, student_id, course_id): raise HTTPException(403, 'Student not enrolled')
    require(db, u, 'teacher', 'student')

@router.post('/recommendations/generate', status_code=201)
def create(data: Generate, u: User = Depends(principal), db: Session = Depends(get_db)):
    scope(db, u, data.student_id, data.course_id)
    content, reasons = generate(db, data.student_id, data.course_id)
    r = Recommendation(student_id=data.student_id, course_id=data.course_id, content=content, reasons=json.dumps(reasons))
    save(db, u, r, 'recommendation.generated_pending_review')
    db.add(RecommendationRevision(recommendation_id=r.id,version=r.version,content=r.content,reasons=r.reasons));db.commit()
    return {'id': r.id, 'status': r.status, 'message': 'Draft sent to assigned teacher; hidden until approval'}

@router.get('/recommendations')
def listing(student_id: int | None = None, u: User = Depends(principal), db: Session = Depends(get_db)):
    if student_id is not None: student_access(db, u, student_id)
    result = []
    for r in db.query(Recommendation).order_by(Recommendation.id.desc()):
        if student_id is not None and r.student_id != student_id: continue
        try:
            student_access(db, u, r.student_id)
            course_access(db, u, r.course_id)
        except HTTPException: continue
        if role(db, u) in {'student', 'parent'} and r.status not in {'published', 'viewed'}: continue
        result.append(record(r) | {'reasons': json.loads(r.reasons), 'student_name': db.get(User, r.student_id).name, 'course_title': db.get(Course, r.course_id).title})
    return result

class Review(Input):
    decision: Literal['approved', 'rejected']
    comment: str = Field(min_length=3, max_length=3000)

@router.post('/recommendations/{recommendation_id}/review')
def review(recommendation_id: int, data: Review, u: User = Depends(principal), db: Session = Depends(get_db)):
    r = get(db, Recommendation, recommendation_id)
    course_access(db, u, r.course_id, manage=True)
    if r.status != 'pending_review': raise HTTPException(409, 'Recommendation is not pending review')
    db.add(RecommendationApproval(recommendation_id=r.id, teacher_id=u.id, decision=data.decision, comment=data.comment, version=r.version))
    r.status = 'published' if data.decision == 'approved' else 'rejected'
    if r.status == 'published': db.add(Notification(user_id=r.student_id, title='Your learning pathway is ready', body='Your teacher has approved a personalized recommendation.'))
    return record(save(db, u, r, 'recommendation.' + data.decision))

@router.post('/recommendations/{recommendation_id}/regenerate')
def regenerate(recommendation_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    r = get(db, Recommendation, recommendation_id)
    scope(db, u, r.student_id, r.course_id)
    if r.status != 'rejected': raise HTTPException(409, 'Only rejected drafts can be regenerated')
    if not db.query(RecommendationRevision).filter_by(recommendation_id=r.id,version=r.version).first():
        db.add(RecommendationRevision(recommendation_id=r.id,version=r.version,content=r.content,reasons=r.reasons))
    r.content, reasons = generate(db, r.student_id, r.course_id)
    r.reasons, r.version, r.status = json.dumps(reasons), r.version + 1, 'pending_review'
    db.add(RecommendationRevision(recommendation_id=r.id,version=r.version,content=r.content,reasons=r.reasons))
    save(db, u, r, 'recommendation.regenerated')
    return {'id': r.id, 'status': r.status, 'version': r.version}

@router.get('/recommendations/{recommendation_id}/history')
def history(recommendation_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    r = get(db, Recommendation, recommendation_id)
    course_access(db, u, r.course_id, manage=True)
    return [record(a) for a in db.query(RecommendationApproval).filter_by(recommendation_id=r.id)]

@router.get('/recommendations/{recommendation_id}/versions')
def versions(recommendation_id:int,u:User=Depends(principal),db:Session=Depends(get_db)):
    r=get(db,Recommendation,recommendation_id);course_access(db,u,r.course_id,manage=True)
    return [record(v)|{'reasons':json.loads(v.reasons)} for v in db.query(RecommendationRevision).filter_by(recommendation_id=r.id).order_by(RecommendationRevision.version)]

@router.post('/recommendations/{recommendation_id}/view')
def viewed(recommendation_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    r = get(db, Recommendation, recommendation_id)
    require(db, u, 'student')
    if r.student_id != u.id or r.status not in {'published', 'viewed'}: raise HTTPException(404, 'Recommendation not found')
    r.status = 'viewed'
    return record(save(db, u, r, 'recommendation.viewed'))

@router.post('/recommendations/{recommendation_id}/archive')
def archive(recommendation_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    r = get(db, Recommendation, recommendation_id)
    course_access(db, u, r.course_id, manage=True)
    if r.status not in {'published', 'viewed', 'rejected'}: raise HTTPException(409, 'Review the draft first')
    r.status = 'archived'
    return record(save(db, u, r, 'recommendation.archived'))
