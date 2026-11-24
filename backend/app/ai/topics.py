"""Small explicit bilingual taxonomy; topic gates prevent generic word matches."""
import re
from .corpus import CORPUS
TOPICS={
 'calculus':['calculus','differentiate','derivative','integrate','integration','differentiation','integrali','derivativi'],
 'linear equations':['linear equation','linear equations','mlinganyo','milinganyo','algebra','aljebra'],
 'quadratic equations':['quadratic','quadratics','kwadrati'],
 'fractions':['fractions','fraction','sehemu','denominator','numerator'],
 'area of a triangle':['triangle','triangles','pembetatu'],
 'photosynthesis':['photosynthesis','usanisinuru','chlorophyll','klorofili'],
 'cells':['cells','cell','seli','nucleus','kiini'],
 'respiration':['respiration','upumuaji'], 'ecology':['ecology','ecosystem','ikolojia'],
 'force and motion':['force','motion','newton','nguvu','mwendo'],
 'electric circuits':['electric','circuit','current','umeme','mkondo'],
 'energy':['energy','nishati'], 'acids and bases':['acid','acids','bases','base','ph','asidi','besi'],
 'atomic structure':['atom','atomic','atomi'], 'chemical reactions':['reaction','reactions','mmenyuko'],
 'water cycle':['water cycle','evaporation','condensation','uvukizaji','mzunguko wa maji'],
 'map reading':['map','maps','ramani'], 'climate':['climate','hali ya hewa','tabianchi'],
 'historical sources':['historical','sources','source','vyanzo','historia'],
 'trade in east africa':['trade','biashara'], 'colonialism':['colonialism','ukoloni'],
 'subject and verb agreement':['agreement','verb','grammar','kiima'],
 'reading comprehension':['comprehension','reading','ufahamu'],
 'ngeli za nomino':['ngeli','nomino','noun'], 'nyakati za vitenzi':['nyakati','tense','vitenzi'],
}
SUBJECTS=['Mathematics','Biology','Chemistry','Physics','English','Kiswahili','Geography','History']

def classify(question,subject):
    lower=question.lower()
    allowed={e['topic'].lower() for e in CORPUS if e['subject'].lower()==subject.lower()}
    hits=[(max(len(w) for w in words if re.search(r'\b'+re.escape(w)+r'\b',lower)),topic)
          for topic,words in TOPICS.items() if topic in allowed and any(re.search(r'\b'+re.escape(w)+r'\b',lower) for w in words)]
    topic=max(hits,default=(0,None))[1]
    intent='computation' if re.search(r'\d.*[=+*/^]|differentiat|integrat|rahisisha|factor',lower) else 'explanation'
    detected='sw' if re.search(r'\b(?:eleza|nini|kwa|tatua|hesabu|naomba|tafadhali)\b',lower) else 'en'
    normalized=next((s for s in SUBJECTS if s.lower()==subject.lower()),None)
    return dict(subject=normalized,topic=topic,intent=intent,detected_language=detected)

def output_language(question,selected):
    if re.search(r'\b(?:in|kwa)\s+(?:kiswahili|swahili)\b',question,re.I):return 'sw'
    if re.search(r'\b(?:in english|kwa kiingereza)\b',question,re.I):return 'en'
    return selected
