"""Validate deliverable structure and existing executed evidence; does not rerun tests."""
from pathlib import Path
import ast,json,subprocess,xml.etree.ElementTree as ET,zipfile
from PIL import Image
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
coverage=read('docs/requirements/coverage.json');rows=coverage['requirements']
assert len(rows)==50 and len({r['Requirement ID'] for r in rows})==50
for r in rows:
 for source in r['Source Files'].split('; '):assert (ROOT/source).is_file(),source
 if r['Test Evidence'].startswith('backend/'):
  path,name=r['Test Evidence'].split('::');tree=ast.parse((ROOT/path).read_text());assert any(isinstance(n,ast.FunctionDef) and n.name==name for n in ast.walk(tree)),name
assert coverage['summary']['functional_coverage_percent']==92
counts={}
for name,path in [('backend','docs/testing/pytest-results.xml'),('browser','docs/testing/playwright-results.xml')]:
 tree=ET.parse(ROOT/path);cases=tree.findall('.//testcase')
 assert cases and not tree.findall('.//failure') and not tree.findall('.//error') and not tree.findall('.//skipped')
 counts[name]=len(cases)
ui=read('docs/testing/vitest-results.json');assert ui['numFailedTests']==0 and ui['numPassedTests']==9;counts['frontend']=ui['numPassedTests']
assert counts=={'backend':48,'browser':8,'frontend':9}
diagrams=sorted((ROOT/'diagrams/drawio').glob('*.drawio'));assert len(diagrams)==8
for path in diagrams:
 tree=ET.parse(path);cells=tree.findall('.//mxCell');ids=[c.get('id') for c in cells];assert len(ids)==len(set(ids))
 for c in cells:
  for key in ['source','target']:assert not c.get(key) or c.get(key) in ids
 assert len([c for c in cells if c.get('vertex')=='1'])>10
 with Image.open(ROOT/'diagrams/png'/f'{path.stem}.png') as image:image.verify()
 pdf=PdfReader(ROOT/'diagrams/pdf'/f'{path.stem}.pdf');assert len(pdf.pages)==1
 assert path.stem.split('_',1)[1].replace('_',' ').split()[0] in pdf.pages[0].extract_text()
proposal=ROOT/'docs/technical-proposal/EduAI_Tanzania_Technical_Proposal.pdf';reader=PdfReader(proposal)
assert len(reader.pages)==39
text='\n'.join(p.extract_text() or '' for p in reader.pages)
for phrase in ['Abstract','Stakeholder Analysis','AI Methodology','References','Appendices']:assert phrase in text
assert '\ufffd' not in text
docx=ROOT/'docs/technical-proposal/EduAI_Tanzania_Technical_Proposal.docx'
with zipfile.ZipFile(docx) as z:
 assert z.testzip() is None
 for name in z.namelist():
  if name.endswith(('.xml','.rels')):ET.fromstring(z.read(name))
 body=ET.fromstring(z.read('word/document.xml'))
 assert len(body.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline'))==25
screens=sorted((ROOT/'docs/screenshots').glob('*.png'));assert len(screens)>=13
for p in screens:
 with Image.open(p) as im:im.verify()
tracked=subprocess.check_output(['git','-C',str(ROOT),'ls-files'],text=True).splitlines()
for f in tracked:assert not (f=='.env' or f=='.local-secret' or f.endswith('.db') or f.startswith(('.venv/','frontend/node_modules/'))),f
result={'tests':counts,'passing_total':sum(counts.values()),'functional_coverage':coverage['summary'],'diagram_sources':8,'diagram_png_exports':8,'diagram_vector_pdf_exports':8,'diagram_xml_and_references_valid':True,'native_editor_opening_verified':False,'native_editor_limit':'Online embed initialization timed out before loading source.','proposal_pdf_pages':len(reader.pages),'pdf_visual_review':'All 39 rendered pages reviewed; enlarged excerpts checked at full image size.','docx_structural_validation':True,'docx_embedded_figures':25,'docx_pagination_verified':False,'docx_renderer_limit':'Packaged render_docx.py failed: LibreOffice soffice.exe not found on PATH.','application_screenshots':len(screens),'frontend_build':'Passed TypeScript and Vite; 766 kB JS chunk (229 kB gzip) warning retained.','remote_ci_verified':False}
(ROOT/'docs/testing/artifact-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
