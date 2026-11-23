"""Produce matching editable DOCX content and an independently rendered PDF.

Run with artifact-requirements.txt installed. Word pagination must additionally
be verified using the packaged render_docx.py when a converter is available.
"""
from pathlib import Path
import json, re
from xml.sax.saxutils import escape
from PIL import Image as PILImage
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, NextPageTemplate, Image, Table, TableStyle, KeepTogether
from reportlab.lib.pagesizes import A4,A3,landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from uml_canvas import REGULAR,BOLD
from proposal_content import SECTIONS,FIGURES

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/technical-proposal';OUT.mkdir(parents=True,exist_ok=True)
WORK=ROOT/'work/proposal';WORK.mkdir(parents=True,exist_ok=True)
doc=Document();doc.core_properties.title='EduAI Tanzania Technical Software Engineering Proposal'
doc.core_properties.author='EduAI Tanzania project team';doc.core_properties.subject='Academic design and reference prototype'
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3','Caption']:
 st=doc.styles[name];st.font.name='Arial';st.font.color.rgb=RGBColor(0,0,0)
normal=doc.styles['Normal'];normal.font.size=Pt(11);normal.paragraph_format.space_after=Pt(8);normal.paragraph_format.line_spacing=1.15
normal.paragraph_format.widow_control=True
doc.styles['Title'].font.size=Pt(30);doc.styles['Subtitle'].font.size=Pt(18)
doc.styles['Heading 1'].font.size=Pt(17);doc.styles['Heading 2'].font.size=Pt(13)
doc.styles['Caption'].font.size=Pt(10)
def section_size(section, size):
 w,h=size;section.page_width=Pt(w);section.page_height=Pt(h)
 section.orientation=WD_ORIENT.LANDSCAPE if w>h else WD_ORIENT.PORTRAIT
 section.top_margin=section.bottom_margin=Pt(50);section.left_margin=section.right_margin=Pt(52)
section_size(doc.sections[0],A4)
footer=doc.sections[0].footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)

styles={
'body':ParagraphStyle('body',fontName='EduArial',fontSize=10.8,leading=15.7,textColor=colors.HexColor('#26362f'),spaceAfter=9,splitLongWords=True,allowWidows=0,allowOrphans=0),
'h1':ParagraphStyle('heading',fontName='EduArialBold',fontSize=16.5,leading=21,textColor=colors.black,spaceBefore=12,spaceAfter=10,keepWithNext=True),
'caption':ParagraphStyle('caption',fontName='EduArial',fontSize=9.5,leading=13,textColor=colors.black,spaceBefore=7,spaceAfter=5),
'small':ParagraphStyle('small',fontName='EduArial',fontSize=9,leading=12,textColor=colors.black),
'cell':ParagraphStyle('cell',fontName='EduArial',fontSize=9,leading=12,textColor=colors.black),
'headcell':ParagraphStyle('headcell',fontName='EduArialBold',fontSize=9,leading=12,textColor=colors.white),
'title':ParagraphStyle('title',fontName='EduArialBold',fontSize=30,leading=37,textColor=colors.black,spaceAfter=18),
}
story=[];diagram_mode=False
def body_mode():
 global diagram_mode
 if diagram_mode:
  story.extend([NextPageTemplate('body'),PageBreak()]);section_size(doc.add_section(WD_SECTION.NEW_PAGE),A4);diagram_mode=False

def paragraph(text):
 body_mode();doc.add_paragraph(text);story.append(Paragraph(escape(text),styles['body']))

def heading(text,anchor=None):
 body_mode();doc.add_heading(text,level=1)
 p=Paragraph((f'<a name="{anchor}"/>' if anchor else '')+escape(text),styles['h1'])
 p.bookmark=anchor;story.append(p)

def table(headers,rows,widths=None):
 body_mode();t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
 for i,h in enumerate(headers):t.rows[0].cells[i].text=str(h)
 for row in rows:
  for c,v in zip(t.add_row().cells,row):c.text=str(v)
 for ri,row in enumerate(t.rows):
  for ci,cell in enumerate(row.cells):
   if widths:cell.width=Pt(widths[ci])
   tcPr=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
   for side in ['top','left','bottom','right']:
    el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
   tcPr.append(borders);margins=OxmlElement('w:tcMar')
   for side in ['top','left','bottom','right']:
    el=OxmlElement('w:'+side);el.set(qn('w:w'),'90');el.set(qn('w:type'),'dxa');margins.append(el)
   tcPr.append(margins);shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'17384D' if ri==0 else ('F0F4F7' if ri%2==0 else 'FFFFFF'));tcPr.append(shade)
   for p in cell.paragraphs:
    p.paragraph_format.space_after=Pt(3)
    for run in p.runs:run.font.size=Pt(9);run.font.color.rgb=RGBColor(255,255,255) if ri==0 else RGBColor(0,0,0);run.bold=ri==0
  if ri==0:
   repeat=OxmlElement('w:tblHeader');row._tr.get_or_add_trPr().append(repeat)
 doc.add_paragraph()
 data=[[Paragraph(escape(str(x)),styles['headcell' if ri==0 else 'cell']) for x in row] for ri,row in enumerate([headers]+rows)]
 grid=Table(data,colWidths=widths or [491/len(headers)]*len(headers),repeatRows=1,hAlign='LEFT')
 grid.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#17384D')),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#D9D9D9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F0F4F7')])]))
 story.extend([grid,Spacer(1,10)])

def figure(path,title,caption,explanation=None,anchor=None):
 global diagram_mode
 story.extend(([PageBreak()] if diagram_mode else [NextPageTemplate('diagram'),PageBreak()]))
 section_size(doc.add_section(WD_SECTION.NEW_PAGE),landscape(A3));diagram_mode=True
 doc.add_heading(title,level=1)
 title_flow=Paragraph((f'<a name="{anchor}"/>' if anchor else '')+escape(title),styles['h1']);title_flow.bookmark=anchor;story.append(title_flow)
 extra_height=0
 for value in explanation or []:
  doc.add_paragraph(value);flow=Paragraph(escape(value),styles['body']);extra_height+=flow.wrap(1075,10000)[1]+styles['body'].spaceAfter;story.append(flow)
 with PILImage.open(path) as image:w,h=image.size
 scale=min(1075/w,(622-extra_height)/h);width,height=w*scale,h*scale
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.add_run().add_picture(str(path),width=Pt(width),height=Pt(height))
 doc.add_paragraph(caption,style='Caption')
 story.extend([Image(str(path),width=width,height=height),Paragraph(escape(caption),styles['caption'])])

# Cover and navigation
doc.add_paragraph('EduAI Tanzania Ltd',style='Title');doc.add_paragraph('Technical software engineering proposal',style='Subtitle')
doc.add_paragraph('Bilingual learning support and secondary school management')
doc.add_paragraph('Prepared for academic software engineering review\n23 November 2026')
doc.add_paragraph('This proposal presents the design and reference prototype for a teacher-supervised education platform. Educational effectiveness and production readiness remain subjects for future evaluation.')
doc.add_paragraph('Delivery context: local demonstration using fictional schools and users. No real payments or personal student datasets are included.')
story += [Spacer(1,85),Paragraph('EduAI Tanzania Ltd',styles['title']),Paragraph('Technical software engineering proposal',styles['h1']),Spacer(1,18),Paragraph('Bilingual learning support and secondary school management',styles['body']),Spacer(1,32),Paragraph('Prepared for academic software engineering review<br/>23 November 2026',styles['body']),Spacer(1,28),Paragraph('This proposal presents the design and reference prototype for a teacher-supervised education platform. Educational effectiveness and production readiness remain subjects for future evaluation.',styles['body']),Paragraph('Delivery context: local demonstration using fictional schools and users. No real payments or personal student datasets are included.',styles['body'])]
doc.add_page_break();story.append(PageBreak());heading('Contents')
for n,(title,_) in enumerate(SECTIONS,start=2):
 doc.add_paragraph(f'{n} {title}')
 story.append(Paragraph(f'<link href="#section-{n}" color="#000000">{n} {escape(title)}</link>',styles['small']))
 story.append(Spacer(1,3))
doc.add_page_break();story.append(PageBreak())

for n,(title,paragraphs) in enumerate(SECTIONS,start=2):
 if n in FIGURES:
  for i,name in enumerate(FIGURES[n]):
   figure(ROOT/'diagrams/png'/f'{name}.png',f'{n} {title}' if i==0 else 'Diagram '+name[:2]+' '+name.split('_',1)[1].replace('_',' '),f'Actual Diagram {name[:2]} export. Editable source: {name}.drawio. Full-size vector PDF is supplied separately. Enlarged extracts appear in the appendices.',paragraphs if i==0 else None,f'section-{n}' if i==0 else None)
  continue
 heading(f'{n} {title}',f'section-{n}')
 for p in paragraphs:paragraph(p)
 if n==8:
  table(['Stakeholder','Main responsibility','Required protection'],[['Student','Study and submit own work','Own records and enrolled courses'],['Teacher','Teach assigned courses and review drafts','Assigned-course scope'],['Parent','Support a verified linked student','Approved links only'],['Administrator','Manage the registered school','Own-school scope']], [91,185,215])
 if n==9:
  table(['Requirement group','Total','Complete','Partial'],[['Student ST','12','11','1'],['Teacher TC','11','10','1'],['Parent PR','7','7','0'],['Administrator AD','10','9','1'],['AI assistance AI','10','9','1'],['All groups','50','46','4']], [212,93,93,93])
 if n==25:
  table(['Stage','Current evidence','Next acceptance decision'],[['Local reference prototype','Executable source and automated checks','Educator review of workflows'],['Presentation preparation','Diagrams, proposal and role scenarios','Verify artifacts on submission machine'],['Later pilot','Not yet conducted','Governance, consent and field evaluation'],['Production','Not yet undertaken','Operational and deployment readiness']], [113,190,188])
 if n==26:
  table(['Executed check','Result','Practical limit'],[['Pytest API/service checks','48 passed','SQLite only; one upstream deprecation warning'],['Vitest component/client checks','9 passed','Network behavior is mocked in client unit tests'],['Playwright local browser checks','8 passed','Headless Chrome; selected desktop/mobile workflows'],['Frontend production build','Passed','No remote deployment or capacity claim']], [161,89,241])
 for name in FIGURES.get(n,[]):
  title=name.split('_',1)[1].replace('_',' ')
  figure(ROOT/'diagrams/png'/f'{name}.png',f'Diagram {name[:2]} {title}',f'Actual diagram export. Editable source: {name}.drawio. Full-size vector PDF is supplied separately. Enlarged interaction and package extracts follow in the appendices.')

# Enlarged extracts preserve the same source content and make small labels readable.
heading('Appendix A Enlarged interaction frames')
paragraph('These extracts retain the source message numbering and authorization guards. Consult the complete diagram for the relationship between frames.')
for prefix,kind,step,h in [('01','Sequence',1000,965),('02','Communication',1300,1150)]:
 source=next((ROOT/'diagrams/png').glob(prefix+'*.png'))
 with PILImage.open(source) as image:
  for i in range(4):
   x=30+(i%2)*1490;y=125+(i//2)*step;target=WORK/f'{prefix}-scenario-{i+1}.png'
   image.crop((x,y,x+1450,y+h)).save(target)
   figure(target,f'{kind} interaction frame {i+1}',f'Enlarged extract of Diagram {prefix}. Each object, lifeline, message and label remains separately editable in the supplied draw.io source.')
package_titles={6:['Identity and School','Learning Evidence','AI Learning Services'],7:['Teaching and Courses','Learning and Assessment','Submission and Grading'],8:['Family and Communication','School Administration','Subscription and Payment']}
for n in (6,7,8):
 source=next((ROOT/'diagrams/png').glob(f'{n:02}*.png'))
 with PILImage.open(source) as image:
  for col,label in enumerate(package_titles[n]):
   x=30+col*540;target=WORK/f'{n:02}-package-{col+1}.png';image.crop((x,140,x+510,1260)).save(target)
   figure(target,('Appendix B ' if n==6 and col==0 else '')+f'Diagram {n:02} {label}',f'Enlarged actual package compartment from Diagram {n:02}. Module stereotypes describe implemented Python services; associations and endpoint multiplicities appear in the full diagram catalogue.')
heading('Appendix C Reproducible demonstration evidence')
table(['Role','Fictional login','Demonstration path'],[['Student','amina@demo.eduai.test','Courses, quizzes, tutor and approved pathways'],['Teacher','neema@demo.eduai.test','Assignments, student evidence, review and lesson draft'],['Parent','parent@demo.eduai.test','Linked Amina report, alerts and teacher messages'],['Administrator','admin@demo.eduai.test','School users, assignments, links, reports and payments']], [91,180,220])
paragraph('Choose the shared fictional password when running python -m app.seed. The seed script skips an existing populated database instead of overwriting it. The README gives separate backend and frontend terminal commands and the optional PowerShell setup workflow.')
paragraph('Machine-readable evidence: docs/testing/pytest-results.xml, vitest-results.json and playwright-results.xml. Requirements: docs/requirements/coverage.json. Diagram structure: diagrams/validation.json. Development evidence: docs/agent-development-log. The final delivery report records Git count, branch, SHA and remote synchronization without treating a failed push as success.')

class ProposalPDF(BaseDocTemplate):
 def afterFlowable(self,flowable):
  bookmark=getattr(flowable,'bookmark',None)
  if bookmark:self.canv.bookmarkPage(bookmark);self.canv.addOutlineEntry(flowable.getPlainText(),bookmark,level=0,closed=False)

def page_number(c,document):
 c.setFont('EduArial',9);c.setFillColor(colors.HexColor('#62736a'));w,h=c._pagesize;c.drawCentredString(w/2,27,str(document.page))

pdf=ProposalPDF(str(OUT/'EduAI_Tanzania_Technical_Proposal.pdf'),pagesize=A4,title='EduAI Tanzania Technical Software Engineering Proposal',author='EduAI Tanzania project team',leftMargin=52,rightMargin=52,topMargin=50,bottomMargin=50)
pdf.addPageTemplates([PageTemplate(id='body',frames=[Frame(52,50,A4[0]-104,A4[1]-100,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],pagesize=A4,onPage=page_number),PageTemplate(id='diagram',frames=[Frame(50,50,landscape(A3)[0]-100,landscape(A3)[1]-100,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],pagesize=landscape(A3),onPage=page_number)])
pdf.build(story)
doc.save(OUT/'EduAI_Tanzania_Technical_Proposal.docx')
from pypdf import PdfReader
reader=PdfReader(OUT/'EduAI_Tanzania_Technical_Proposal.pdf')
assert len(reader.pages)>20
assert all(len((p.extract_text() or '').strip())>5 for p in reader.pages)
print(json.dumps({'pdf_pages':len(reader.pages),'docx_sections':len(doc.sections),'sections':len(SECTIONS)+1,'embedded_figures':8+8+9,'pdf_exists':True,'docx_exists':True}))
