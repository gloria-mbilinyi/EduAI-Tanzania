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
from ..ai import ollama
from ..ai.tutor import retrieve

router = APIRouter(prefix='/api/tutor', tags=['tutor'])
class TutorInput(Input):
    question: str = Field(min_length=3, max_length=1500)
    subject: str = Field(min_length=2, max_length=60)
    language: Literal['en', 'sw'] = 'en'
    use_local_ai: bool = False

@router.post('/ask')
def ask(data: TutorInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    prior=db.query(TutorMessage).filter_by(user_id=u.id,subject=data.subject).order_by(TutorMessage.id.desc()).limit(4).all()
    result = answer(data.question, data.subject, data.language,context=[record(m) for m in reversed(prior)])
    if data.use_local_ai and result['mode'].startswith('topic-aware'):
        score,entry=retrieve(data.question,data.subject)
        if entry and score>=0.15:
            try:result.update(ollama.tutor(data.question,result['language'],[entry],[record(m) for m in reversed(prior)]))
            except (ollama.ProviderUnavailable,ValueError,KeyError,TypeError,ollama.httpx.HTTPError):result['provider_status']='Local AI unavailable or invalid; teaching passage retained'
        else:result['provider_status']='No suitable source; local generation was skipped'
    save(db, u, TutorMessage(user_id=u.id, subject=data.subject, language=result['language'], question=data.question, answer=result['answer'], source=result['source']), 'tutor.'+result['mode'].split(';')[0])
    return result

@router.get('/history')
def history(u: User = Depends(principal), db: Session = Depends(get_db)):
    return [record(m) for m in db.query(TutorMessage).filter_by(user_id=u.id).order_by(TutorMessage.id.desc()).limit(50)]

@router.get('/provider-health')
def provider_health(u:User=Depends(principal)):
    return ollama.health()
