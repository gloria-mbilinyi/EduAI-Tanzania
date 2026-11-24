"""Check saved native sources for text overflow using the exporter's font metrics."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from PIL import ImageFont
from uml_canvas import styles,REGULAR,BOLD,validate
ROOT=Path(__file__).resolve().parents[1]
issues=[];checked=0
for path in sorted((ROOT/'diagrams/drawio').glob('*.drawio')):
    validate(path)
    for cell in ET.parse(path).findall('.//mxCell'):
        value=cell.get('value','');geometry=cell.find('mxGeometry');st=styles(cell.get('style',''))
        if not value or geometry is None:continue
        checked+=1;size=int(st.get('fontSize',17))
        font=ImageFont.truetype(str(BOLD if st.get('fontStyle')=='1' else REGULAR),size)
        vertex=cell.get('vertex')=='1'
        width=float(geometry.get('width',460)) if vertex else float(st.get('labelWidth',460))
        height=float(geometry.get('height',44)) if vertex else float(st.get('eduLabelHeight',44))
        lines=[]
        for original in value.split('\n'):
            line=''
            for word in original.split(' '):
                if font.getlength(word)>width-12:issues.append([path.name,cell.get('id'),'word wider than text box'])
                if line and font.getlength(line+' '+word)>width-12:lines.append(line);line=word
                else:line=(line+' '+word).strip()
            lines.append(line)
        if len(lines)*size*1.28>height+3:issues.append([path.name,cell.get('id'),'wrapped text taller than text box'])
report={'diagrams':8,'text_cells_checked':checked,'overflow_issues':issues,'native_editor_verified':False,
        'native_editor_limit':'Online embed initialization timed out after 45 seconds before loading any source.'}
(ROOT/'diagrams/layout-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
assert not issues
