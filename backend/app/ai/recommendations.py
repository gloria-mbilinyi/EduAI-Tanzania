"""Explainable, deterministic baseline; no trained ML model or accuracy claim."""
from ..models import Student, User
from ..services.performance import performance

def generate(db, student_id, course_id):
    data = performance(db, student_id)
    course = next(x for x in data['courses'] if x['course_id'] == course_id)
    profile = db.get(Student, student_id)
    mean = course['average']
    weakest = min(course['results'], key=lambda x: x['score'])['title'] if course['results'] else 'introductory concepts'
    target = 'foundation practice' if mean is None or mean < 50 else 'guided revision' if mean < 70 else 'intermediate practice' if mean < 90 else 'advanced extension exercises'
    content = f'{course["subject"]}: begin with {target}. Focus on {weakest}. '
    content += f'1. Spend 15 minutes reviewing teacher-approved {profile.preference} resources. '
    content += f'2. Complete five practice questions and connect one example to your interest in {profile.interests}. '
    content += '3. Ask your teacher for feedback, then attempt the next available quiz.'
    reasons = [f'Subject average: {mean if mean is not None else "no graded evidence"}.',
               f'{len(course["results"])} graded assessments; weakest recorded assessment: {weakest}.',
               f'{course["activities_30d"]} activities recorded in 30 days.',
               f'Learning preference: {profile.preference}; interests: {profile.interests}.',
               'Explainable rule-based draft. Teacher review required; offline learning is not measured.']
    for result in course['results']:
        if result.get('attempts'):
            scores=[a['grade']['score'] for a in result['attempts'] if a['grade']]
            reasons.append(f'{result["title"]}: attempt scores {scores}; improvement {result["improvement"]} percentage points; official attempt {result["official_attempt"]} under {result["grading_policy"]}; mastery {result["topic_mastery"]}.')
            repeated=[a['grade']['feedback'] for a in result['attempts'] if a['grade'] and a['grade']['score']<65]
            if repeated: reasons.append('Feedback from attempts needing practice: ' + ' | '.join(repeated[-3:]))
    if profile and db.get(User,student_id).language=='sw':
        targets={'foundation practice':'mazoezi ya msingi','guided revision':'marudio yenye mwongozo','intermediate practice':'mazoezi ya kiwango cha kati','advanced extension exercises':'mazoezi ya kiwango cha juu'}
        content=f'{course["subject"]}: anza na {targets[target]}. Lenga {weakest}. 1. Pitia nyenzo zilizoidhinishwa na mwalimu kwa dakika 15. 2. Fanya maswali matano ukihusisha {profile.interests}. 3. Omba mrejesho wa mwalimu kabla ya zoezi linalofuata.'
        reasons=[f'Wastani rasmi: {mean}; tathmini {len(course["results"])}.',f'Shughuli {course["activities_30d"]} katika siku 30; mapendeleo: {profile.preference}.']+[f'{r["title"]}: alama {r["score"]}%; maendeleo {r["improvement"]}; umilisi {r["topic_mastery"]}.' for r in course['results']]+['Rasimu inayotumia kanuni; lazima mwalimu aikague. Masomo nje ya mfumo hayajapimwa.']
    return content, reasons
