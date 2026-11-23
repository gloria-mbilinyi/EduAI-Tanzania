from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import FRONTEND_ORIGIN
from .migrate import migrate
from .api import auth, courses, assignments, quizzes

@asynccontextmanager
async def lifespan(app):
    migrate()
    yield

app = FastAPI(title='EduAI Tanzania API', version='1.0.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND_ORIGIN], allow_methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], allow_headers=['Authorization', 'Content-Type'])
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(assignments.router)
app.include_router(quizzes.router)

@app.get('/api/health', tags=['public'])
def health():
    return {'status': 'ok', 'prototype': True, 'ai_mode': 'explainable rules and bilingual retrieval'}
