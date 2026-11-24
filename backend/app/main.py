from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from .services.i18n import translate
from fastapi.middleware.cors import CORSMiddleware
from .core.config import FRONTEND_ORIGIN
from .migrate import migrate
from .api import auth, courses, assignments, quizzes, performance, billing, recommendations, tutor, teacher_tools, families, admin, admin_billing

@asynccontextmanager
async def lifespan(app):
    migrate()
    yield

app = FastAPI(title='EduAI Tanzania API', version='2.0.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_ORIGIN], allow_methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], allow_headers=['Authorization', 'Content-Type','Accept-Language'])

@app.exception_handler(HTTPException)
async def http_error(request:Request,exc:HTTPException):
    detail=translate(exc.detail,request.headers.get('Accept-Language','en')) if isinstance(exc.detail,str) else exc.detail
    return JSONResponse({'detail':detail,'code':exc.detail},status_code=exc.status_code,headers=exc.headers)

@app.exception_handler(RequestValidationError)
async def validation_error(request:Request,exc:RequestValidationError):
    issues=[]
    for e in exc.errors():
        issue={k:v for k,v in e.items() if k in {'loc','msg','type'}}
        if request.headers.get('Accept-Language','en').startswith('sw'):issue['msg']='Kagua thamani ya sehemu hii; haikidhi masharti.'
        issues.append(issue)
    return JSONResponse({'detail':issues},status_code=422)
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(assignments.router)
app.include_router(quizzes.router)
app.include_router(performance.router)
app.include_router(billing.router)
app.include_router(recommendations.router)
app.include_router(tutor.router)
app.include_router(teacher_tools.router)
app.include_router(families.router)
app.include_router(admin.router)
app.include_router(admin_billing.router)

@app.get('/api/health', tags=['public'])
def health():
    return {'status': 'ok', 'prototype': True, 'ai_mode': 'symbolic mathematics, topic retrieval and optional local AI'}
