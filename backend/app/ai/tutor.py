import re
from .corpus import CORPUS
from .topics import classify, output_language
from .math_solver import solve

STOP = {'what', 'is', 'the', 'a', 'an', 'how', 'do', 'i', 'to', 'of', 'and', 'in', 'explain', 'ni', 'nini', 'ya', 'na', 'kwa','need','solve','please','help','me','about'}
def retrieve(question, subject):
    tokens = set(re.findall(r'\w+', question.lower())) - STOP
    ranked = []
    topic=classify(question,subject)['topic']
    for entry in CORPUS:
        if entry['subject'].lower() != subject.lower(): continue
        if topic and entry['topic'].lower()!=topic:continue
        terms = set(re.findall(r'\w+', (' '.join([entry['topic'], entry['keywords'], entry['en'], entry['sw']])).lower())) - STOP
        score = max(0.75 if topic else 0,len(tokens & terms) / max(1, len(tokens)))
        ranked.append((score, entry))
    return max(ranked, key=lambda x: x[0]) if ranked else (0, None)

def answer(question, subject, language, context=None):
    language=output_language(question,language)
    classified=classify(question,subject)
    resolved=question
    if context and not classified['topic'] and re.search(r'\b(?:more|again|that|another example|zaidi|tena|hilo)\b',question,re.I):
        resolved=context[-1]['question']
        classified=classify(resolved,subject)
    computed=solve(resolved,language) if subject in {'Mathematics','Physics','Chemistry'} else None
    if computed:return computed|classified|{'language':language}
    score, entry = retrieve(resolved, subject)
    if not entry or score < 0.15:
        return {'answer': 'Sijapata maelezo yanayofaa katika maktaba ndogo. Uliza kuhusu mada maalumu au wasiliana na mwalimu.' if language == 'sw' else 'I could not find a suitable passage in the small teaching library. Ask about a specific topic or consult your teacher.',
                'source': 'No matching passage', 'match_score': round(score, 2), 'mode': 'topic-aware retrieval; not generative AI'}|classified|{'language':language}
    return {'answer': entry[language], 'source': f'EduAI original teaching passage {entry["id"]}: {entry["topic"]}', 'source_ids':[entry['id']], 'match_score': round(score, 2), 'mode': 'topic-aware retrieval; not generative AI'}|classified|{'language':language}
