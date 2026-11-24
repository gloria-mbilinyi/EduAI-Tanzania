"""Generate all eight editable diagrams and export from saved native XML.
Usage: python scripts/generate_uml.py [01 ... 08]
"""
from pathlib import Path
import json, sys
from uml_canvas import Diagram, validate, export

ROOT=Path(__file__).resolve().parents[1]
DRAW=ROOT/'diagrams/drawio';PNG=ROOT/'diagrams/png';PDF=ROOT/'diagrams/pdf'
for p in (DRAW,PNG,PDF):p.mkdir(parents=True,exist_ok=True)

from interaction_uml import SCENARIOS, sequence, communication

from state_uml import state_ai, state_subscription

from package_uml import overview, learning, assessment, administration

GENERATORS={'01':sequence,'02':communication,'03':state_ai,'04':state_subscription,'05':overview,'06':learning,'07':assessment,'08':administration}
def main():
 evidence=[]
 for key in sys.argv[1:] or GENERATORS:
  diagram=GENERATORS[key]();path=DRAW/(diagram.name+'.drawio');diagram.save(path)
  item=validate(path);item['pixels']=export(path,PNG,PDF);evidence.append(item);print(json.dumps(item))
 existing=json.loads((ROOT/'diagrams/validation.json').read_text()) if (ROOT/'diagrams/validation.json').exists() else []
 names={e['file'] for e in evidence};existing=[e for e in existing if e['file'] not in names]+evidence
 (ROOT/'diagrams/validation.json').write_text(json.dumps(sorted(existing,key=lambda e:e['file']),indent=2))
if __name__=='__main__':main()
