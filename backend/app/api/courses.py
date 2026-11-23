import secrets
from pathlib import Path
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import Field, HttpUrl
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import principal, role, require
from ..core.config import UPLOADS
from ..models import *
from ..schemas.common import Input, CourseInput
from ..services.access import *

router = APIRouter(prefix='/api', tags=['courses'])

@router.get('/courses')
def list_courses(u: User = Depends(principal), db: Session = Depends(get_db)):
    visible = []
    for c in db.query(Course).filter_by(school_id=u.school_id):
        try: course_access(db, u, c.id)
        except HTTPException: continue
        visible.append(record(c))
    return visible

@router.post('/courses', status_code=201)
def create_course(data: CourseInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    require(db, u, 'teacher')
    c = Course(school_id=u.school_id, **data.model_dump())
    db.add(c)
    db.flush()
    db.add(TeacherCourseAssignment(teacher_id=u.id, course_id=c.id))
    return record(save(db, u, c, 'course.create'))

@router.patch('/courses/{course_id}')
def edit_course(course_id: int, data: CourseInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    c = course_access(db, u, course_id, manage=True)
    for k, v in data.model_dump().items(): setattr(c, k, v)
    return record(save(db, u, c, 'course.update'))

@router.get('/courses/{course_id}/students')
def course_students(course_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, course_id, manage=True)
    return [{'id': s.id, 'name': s.name} for e in db.query(Enrollment).filter_by(course_id=course_id) if (s := db.get(User, e.student_id))]

class MaterialInput(Input):
    title: str = Field(min_length=2, max_length=150)
    kind: Literal['notes', 'video'] = 'notes'
    content: str = Field(default='', max_length=50000)
    url: HttpUrl | None = None

@router.get('/courses/{course_id}/materials')
def materials(course_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, course_id)
    if role(db, u) == 'student':
        db.add(LearningActivity(student_id=u.id, course_id=course_id, action='read_materials'))
        db.commit()
    return [record(m, ['storage_key']) | {'downloadable': bool(m.storage_key)} for m in db.query(LearningMaterial).filter_by(course_id=course_id)]

@router.post('/courses/{course_id}/materials', status_code=201)
def add_material(course_id: int, data: MaterialInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, course_id, manage=True)
    if data.url and data.url.scheme != 'https': raise HTTPException(422, 'Use an HTTPS resource URL')
    return record(save(db, u, LearningMaterial(course_id=course_id, title=data.title, kind=data.kind, content=data.content, url=str(data.url) if data.url else ''), 'material.create'))

@router.post('/courses/{course_id}/upload', status_code=201)
async def upload(course_id: int, title: str = Form(..., min_length=2, max_length=150), file: UploadFile = File(...), u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, course_id, manage=True)
    suffix = Path(file.filename or '').suffix.lower()
    if suffix not in {'.pdf', '.txt', '.png', '.jpg', '.mp4'}: raise HTTPException(422, 'Allowed files: PDF, TXT, PNG, JPG, MP4')
    data = await file.read(5 * 1024 * 1024 + 1)
    if len(data) > 5 * 1024 * 1024: raise HTTPException(413, 'File exceeds 5 MB low-bandwidth limit')
    UPLOADS.mkdir(exist_ok=True)
    key = secrets.token_hex(20) + suffix
    (UPLOADS / key).write_bytes(data)
    return record(save(db, u, LearningMaterial(course_id=course_id, title=title, kind='video' if suffix == '.mp4' else 'notes', storage_key=key), 'material.upload'), ['storage_key'])

@router.get('/materials/{material_id}/download')
def download(material_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    m = get(db, LearningMaterial, material_id)
    course_access(db, u, m.course_id)
    if not m.storage_key or not (UPLOADS / m.storage_key).is_file(): raise HTTPException(404, 'File not found')
    return FileResponse(UPLOADS / m.storage_key, filename='learning-material' + Path(m.storage_key).suffix, media_type='application/octet-stream', headers={'X-Content-Type-Options': 'nosniff'})
