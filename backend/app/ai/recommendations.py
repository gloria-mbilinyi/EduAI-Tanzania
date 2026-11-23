"""Explainable, deterministic baseline; no trained ML model or accuracy claim."""
from ..models import Student
from ..services.performance import performance

def generate(db, student_id, course_id):
    data = performance(db, student_id)
    course = next(x for x in data['courses'] if x['course_id'] == course_id)
    profile = db.get(Student, student_id)
    mean = course['average']
    weakest = min(course['results'], key=lambda x: x['score'])['title'] if course['results'] else 'introductory concepts'
    target = 'foundation practice' if mean is None or mean < 50 else 'guided revision' if mean < 70 else 'extension exercises'
    content = f'{course["subject"]}: begin with {target}. Focus on {weakest}. '
    content += f'1. Spend 15 minutes reviewing teacher-approved {profile.preference} resources. '
    content += f'2. Complete five practice questions and connect one example to your interest in {profile.interests}. '
    content += '3. Ask your teacher for feedback, then attempt the next available quiz.'
    reasons = [f'Subject average: {mean if mean is not None else "no graded evidence"}.',
               f'{len(course["results"])} graded assessments; weakest recorded assessment: {weakest}.',
               f'{course["activities_30d"]} activities recorded in 30 days.',
               f'Learning preference: {profile.preference}; interests: {profile.interests}.',
               'Explainable rule-based draft. Teacher review required; offline learning is not measured.']
    return content, reasons
