"""Check both views contain each actual message and nested number exactly once."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from interaction_uml import SCENARIOS,number
root=Path(__file__).resolve().parents[1]
for prefix in ['01','02']:
    tree=ET.parse(next((root/'diagrams/drawio').glob(prefix+'*.drawio')))
    text='\n'.join(c.get('value','') for c in tree.findall('.//mxCell'))
    for n,(_,_,messages) in enumerate(SCENARIOS):
        for i,message in enumerate(messages):
            ident=number(n,i,messages)
            assert len(re.findall(r'(?<![\d.])'+re.escape(ident)+r'(?![\d.])',text))==1,ident
            assert message[2] in text
    print(prefix, 'all',sum(len(s[2]) for s in SCENARIOS),'direct message labels verified')
