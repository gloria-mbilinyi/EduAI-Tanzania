from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

class Registration(Input):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$', max_length=254)
    password: str = Field(min_length=10, max_length=128)
    school_id: int = Field(gt=0)
    role: Literal['student', 'teacher', 'parent']
    language: Literal['en', 'sw'] = 'en'

class Login(Input):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)

class ProfileInput(Input):
    name: str = Field(min_length=2, max_length=100)
    language: Literal['en', 'sw'] = 'en'
    interests: str = Field(default='Science', max_length=200)
    preference: Literal['reading', 'video', 'practice'] = 'reading'

class CourseInput(Input):
    title: str = Field(min_length=3, max_length=120)
    subject: str = Field(min_length=2, max_length=60)
    form: str = Field(default='Form 2', min_length=2, max_length=20)
    description: str = Field(default='', max_length=5000)

class TextInput(Input):
    body: str = Field(min_length=1, max_length=10000)
