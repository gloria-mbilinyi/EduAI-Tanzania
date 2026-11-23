from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import principal
from ..models import User, Lesson
from ..schemas.common import Input
from ..services.access import course_access, save, record
from ..services.billing import premium
from ..ai.corpus import CORPUS
from ..ai.tutor import retrieve

router = APIRouter(prefix='/api/teacher-tools', tags=['teacher draft assistance'])
class Draft(Input):
    course_id: int = Field(gt=0)
    topic: str = Field(min_length=3, max_length=150)

@router.post('/quiz-draft')
def quiz_draft(data: Draft, u: User = Depends(principal), db: Session = Depends(get_db)):
    c = course_access(db, u, data.course_id, manage=True)
    premium(db, u.id)
    entries = [e for e in CORPUS if e['subject'].lower() == c.subject.lower()]
    if not entries: raise HTTPException(422, 'No reviewed question bank for this subject; create questions manually')
    _, best = retrieve(data.topic, c.subject)
    entries.sort(key=lambda x: x['id'] != best['id'] if best else False)
    return {'title': data.topic + ' practice', 'status': 'draft', 'mode': 'question-bank assembly, not generative AI; teacher review required',
            'questions': [{'prompt': e['question'], 'options': e['options'], 'correct_index': e['correct'], 'explanation': e['en']} for e in entries[:3]]}

@router.post('/lesson-draft')
def lesson(data: Draft, u: User = Depends(principal), db: Session = Depends(get_db)):
    c = course_access(db, u, data.course_id, manage=True)
    premium(db, u.id)
    score, entry = retrieve(data.topic, c.subject)
    if not entry or score < 0.15: raise HTTPException(422, 'No suitable teaching passage; refine the topic')
    outline = f'Learning objectives: explain {entry["topic"]}, solve an example, and justify the answer.\n'
    outline += '5 min: ask learners what they know.\n10 min: demonstrate the concept.\n15 min: paired practice using locally available materials.\n10 min: individual exercise and feedback.\n'
    outline += f'Teaching note: {entry["en"]}\nKiswahili support: {entry["sw"]}\nResource: original passage {entry["id"]}.\nAssessment: {entry["question"]}\nAdapt for accessibility and have the teacher verify factual accuracy.'
    return {'title': data.topic, 'outline': outline, 'mode': 'retrieval plus structured template; teacher draft'}

class LessonInput(Draft):
    outline: str = Field(min_length=20, max_length=15000)

@router.post('/lessons', status_code=201)
def save_lesson(data: LessonInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, data.course_id, manage=True)
    return record(save(db, u, Lesson(course_id=data.course_id, title=data.topic, outline=data.outline), 'lesson.teacher_reviewed'))

@router.get('/lessons/{course_id}')
def lessons(course_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, course_id, manage=True)
    return [record(x) for x in db.query(Lesson).filter_by(course_id=course_id)]
