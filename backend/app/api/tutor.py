from typing import Literal
from pydantic import Field
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import principal
from ..models import User, TutorMessage
from ..schemas.common import Input
from ..services.access import save, record
from ..ai.tutor import answer

router = APIRouter(prefix='/api/tutor', tags=['tutor'])
class TutorInput(Input):
    question: str = Field(min_length=3, max_length=1500)
    subject: str = Field(min_length=2, max_length=60)
    language: Literal['en', 'sw'] = 'en'

@router.post('/ask')
def ask(data: TutorInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    result = answer(data.question, data.subject, data.language)
    save(db, u, TutorMessage(user_id=u.id, subject=data.subject, language=data.language, question=data.question, answer=result['answer'], source=result['source']), 'tutor.retrieval')
    return result

@router.get('/history')
def history(u: User = Depends(principal), db: Session = Depends(get_db)):
    return [record(m) for m in db.query(TutorMessage).filter_by(user_id=u.id).order_by(TutorMessage.id.desc()).limit(50)]
