"""Validate actual evidence and deliverables without pretending to rerun tests."""
from pathlib import Path
import ast,hashlib,json,subprocess,xml.etree.ElementTree as ET,zipfile
from PIL import Image
from pypdf import PdfReader
from proposal_content import SECTIONS
ROOT=Path(__file__).resolve().parents[1]
BASE='b45aa529d53d735f9ab74108dd3b50e4dbda0e3f'
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True,encoding='utf-8').strip()
coverage=read('docs/requirements/coverage.json');rows=coverage['requirements']
assert len(rows)==50 and len({r['Requirement ID'] for r in rows})==50
for r in rows:
 for source in r['Source Files'].split('; '):assert (ROOT/source).is_file(),source
 if r['Test Evidence'].startswith('backend/'):
  path,name=r['Test Evidence'].split('::');tree=ast.parse((ROOT/path).read_text());assert any(isinstance(n,ast.FunctionDef) and n.name==name for n in ast.walk(tree)),name
assert coverage['summary']['functional_coverage_percent']==98
counts={}
for name,path in [('backend','docs/testing/pytest-results.xml'),('browser','docs/testing/playwright-results.xml')]:
 tree=ET.parse(ROOT/path);cases=tree.findall('.//testcase')
 assert cases and not tree.findall('.//failure') and not tree.findall('.//error') and not tree.findall('.//skipped')
 counts[name]=len(cases)
ui=read('docs/testing/vitest-results.json');assert ui['numFailedTests']==0;counts['frontend']=ui['numPassedTests']
assert counts=={'backend':95,'browser':12,'frontend':12}
contract=read('docs/api/openapi.json');assert len(contract['paths'])==71
operations=sum(m in {'get','post','patch','put','delete'} for methods in contract['paths'].values() for m in methods)
assert operations==83 and contract['info']['version']=='2.0.0'
diagrams=sorted((ROOT/'diagrams/drawio').glob('*.drawio'));assert len(diagrams)==8
for path in diagrams:
 tree=ET.parse(path);cells=tree.findall('.//mxCell');ids=[c.get('id') for c in cells];assert len(ids)==len(set(ids))
 for c in cells:
  for key in ['source','target']:assert not c.get(key) or c.get(key) in ids
 assert len([c for c in cells if c.get('vertex')=='1'])>10
 with Image.open(ROOT/'diagrams/png'/f'{path.stem}.png') as im:
  assert im.info['mxfile']==path.read_text(encoding='utf-8');im.verify()
 pdf=PdfReader(ROOT/'diagrams/pdf'/f'{path.stem}.pdf');assert len(pdf.pages)==1
 assert not pdf.pages[0]['/Resources'].get('/XObject',{})
layout=read('diagrams/layout-validation.json');assert not layout['overflow_issues'] and layout['text_cells_checked']==737
proposal=ROOT/'docs/technical-proposal/EduAI_Tanzania_Technical_Proposal.pdf';reader=PdfReader(proposal);assert len(reader.pages)==53
text=' '.join((p.extract_text() or '').replace('\n',' ') for p in reader.pages)
for n,(title,_) in enumerate(SECTIONS,2):assert f'{n} {title}' in text,(n,title)
assert '\ufffd' not in text

docx=ROOT/'docs/technical-proposal/EduAI_Tanzania_Technical_Proposal.docx'
with zipfile.ZipFile(docx) as z:
 assert z.testzip() is None
 for name in z.namelist():
  if name.endswith(('.xml','.rels')):ET.fromstring(z.read(name))
 body=ET.fromstring(z.read('word/document.xml'))
 figures=len(body.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline'))
 assert figures==39 and b'PAGE' in z.read('word/footer1.xml')
screens=sorted((ROOT/'docs/screenshots').glob('*.png'));assert len(screens)==20
for p in screens:
 with Image.open(p) as im:im.verify()
tracked=set(git('ls-files').splitlines());baseline_files=set(git('ls-tree','-r','--name-only',BASE).splitlines())
assert baseline_files<=tracked,'A baseline file was removed'
for f in tracked:assert not (f=='.env' or f=='.local-secret' or f.endswith(('.db','.sqlite.backup')) or f.startswith(('.venv/','frontend/node_modules/'))),f
base=set(git('rev-list',BASE).splitlines());current=set(git('rev-list','HEAD').splitlines());assert len(base)==58 and base<=current
assert 'bb68c01b7fbf813701b4cd7dda7a42e6ef1fc6b2' in current
result={'tests':counts,'passing_total':sum(counts.values()),'functional_coverage':coverage['summary'],'api_paths':71,'api_operations':83,
 'diagram_sources':8,'diagram_png_exports':8,'diagram_vector_pdf_exports':8,'editable_xml_and_references_valid':True,'diagram_text_cells_checked':737,
 'native_editor_opening_verified':False,'native_editor_limit':'Online embed initialization timed out before source load.',
 'proposal_pdf_pages':len(reader.pages),'pdf_visual_review':'All 53 rendered pages reviewed in contact sheets; enlarged assignment figure and feature screenshots inspected.',
 'docx_structural_validation':True,'docx_embedded_figures':figures,'proposal_required_sections':31,'docx_pagination_verified':False,
 'docx_renderer_limit':'LibreOffice unavailable; Word COM Access denied; supported desktop launch exposed no Word window.',
 'application_screenshots':len(screens),'frontend_build':'Passed TypeScript/Vite; 805 kB raw / 240 kB gzip chunk warning.',
 'baseline_commits_preserved':len(base),'baseline_file_paths_preserved':len(baseline_files),'source_snapshot_head':git('rev-parse','HEAD'),
 'remote_ci_verified':False,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [proposal,docx]}}
(ROOT/'docs/testing/artifact-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
