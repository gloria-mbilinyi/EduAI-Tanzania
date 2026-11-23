import re
from .corpus import CORPUS

STOP = {'what', 'is', 'the', 'a', 'an', 'how', 'do', 'i', 'to', 'of', 'and', 'in', 'explain', 'ni', 'nini', 'ya', 'na', 'kwa'}
def retrieve(question, subject):
    tokens = set(re.findall(r'\w+', question.lower())) - STOP
    ranked = []
    for entry in CORPUS:
        if entry['subject'].lower() != subject.lower(): continue
        terms = set(re.findall(r'\w+', (' '.join([entry['topic'], entry['keywords'], entry['en'], entry['sw']])).lower())) - STOP
        score = len(tokens & terms) / max(1, len(tokens))
        ranked.append((score, entry))
    return max(ranked, key=lambda x: x[0]) if ranked else (0, None)

def answer(question, subject, language):
    score, entry = retrieve(question, subject)
    if not entry or score < 0.15:
        return {'answer': 'Sijapata maelezo yanayofaa katika maktaba ndogo. Uliza kuhusu mada maalumu au wasiliana na mwalimu.' if language == 'sw' else 'I could not find a suitable passage in the small teaching library. Ask about a specific topic or consult your teacher.',
                'source': 'No matching passage', 'match_score': round(score, 2), 'mode': 'bilingual lexical retrieval; not generative AI'}
    return {'answer': entry[language], 'source': f'EduAI original teaching passage {entry["id"]}: {entry["topic"]}', 'match_score': round(score, 2), 'mode': 'bilingual lexical retrieval; not generative AI'}
