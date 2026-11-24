from datetime import timedelta
from ..models import *
from ..core.database import now
from ..core.security import role
from .access import assigned
from .attempts import official, history, policy

def performance(db, student_id, viewer=None):
    courses = []
    all_scores = []
    for e in db.query(Enrollment).filter_by(student_id=student_id):
        if viewer and role(db, viewer) == 'teacher' and not assigned(db, viewer.id, e.course_id): continue
        c = db.get(Course, e.course_id)
        scores, results = [], []
        for s in db.query(Submission).filter_by(student_id=student_id):
            item = db.get(Assignment, s.assignment_id) if s.assignment_id else db.get(Quiz, s.quiz_id)
            if item.course_id != c.id: continue
            selected = official(db,s) if s.assignment_id else None
            g = selected['grade'] if selected else None
            if not s.assignment_id:
                grade = db.query(Grade).filter_by(submission_id=s.id).first()
                g = {'score':grade.score,'feedback':grade.feedback,'created_at':grade.created_at} if grade else None
            if g:
                scores.append(g['score'])
                attempts = history(db,s) if s.assignment_id else []
                graded = [a for a in attempts if a['grade']]
                improvement = graded[-1]['grade']['score']-graded[0]['grade']['score'] if len(graded)>1 else 0
                date = g['created_at']
                results.append({'title': item.title, 'assessment_id':item.id, 'kind':'assignment' if s.assignment_id else 'quiz',
                    'score':g['score'],'feedback':g['feedback'],'date':date.isoformat() if hasattr(date,'isoformat') else date,
                    'official_attempt':selected['number'] if selected else None,
                    'grading_policy':policy(db,item.id)['grading_policy'] if s.assignment_id else 'objective',
                    'attempts':attempts,'improvement':improvement,
                    'topic_mastery':'mastered' if g['score']>=90 else 'developing' if g['score']>=65 else 'needs_practice'})
        activities = db.query(LearningActivity).filter(LearningActivity.student_id == student_id, LearningActivity.course_id == c.id, LearningActivity.created_at >= now() - timedelta(days=30)).count()
        courses.append({'course_id': c.id, 'title': c.title, 'subject': c.subject, 'average': round(sum(scores)/len(scores), 1) if scores else None, 'results': results, 'activities_30d': activities})
        all_scores.extend(scores)
    average = round(sum(all_scores)/len(all_scores), 1) if all_scores else None
    risk = risk_assessment(average, sum(x['activities_30d'] for x in courses), len(all_scores))
    return {'student_id': student_id, 'courses': courses, 'average': average, 'graded_assessments': len(all_scores), 'risk': risk,
            'summary': f'{len(all_scores)} graded assessments. ' + (f'Average {average}%. ' if average is not None else 'No graded evidence yet. ') + risk['reasons'][0]}

def risk_assessment(average, activities, count):
    if average is None: return {'level': 'insufficient_data', 'reasons': ['Complete an assessment before drawing academic conclusions.'], 'mode': 'explainable rules, not a trained or validated ML model'}
    level = 'high' if average < 50 else 'moderate' if average < 65 or activities < 2 else 'low'
    return {'level': level, 'reasons': [f'Mean recorded score is {average}% across {count} assessments.', f'{activities} recorded learning activities in 30 days; offline study is not captured.'], 'mode': 'explainable rules, not a trained or validated ML model'}
