"""Native editable mxGraph XML and deterministic vector/raster exports.

The exporter deliberately supports only the small, explicit UML primitive set
used by this project. It reads the saved XML, never a separate screenshot model.
"""
from pathlib import Path
import math
import textwrap
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = Path('C:/Windows/Fonts')
if not FONT_DIR.exists(): FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
REGULAR = FONT_DIR / ('arial.ttf' if (FONT_DIR/'arial.ttf').exists() else 'DejaVuSans.ttf')
BOLD = FONT_DIR / ('arialbd.ttf' if (FONT_DIR/'arialbd.ttf').exists() else 'DejaVuSans-Bold.ttf')
pdfmetrics.registerFont(TTFont('EduArial', str(REGULAR)))
pdfmetrics.registerFont(TTFont('EduArialBold', str(BOLD)))

class Diagram:
    def __init__(self, name, width, height):
        self.name, self.width, self.height = name, width, height
        self.file = ET.Element('mxfile', host='app.diagrams.net', version='24.7.17', type='device')
        page = ET.SubElement(self.file, 'diagram', id=name[:2], name=name)
        model = ET.SubElement(page, 'mxGraphModel', dx='0', dy='0', grid='1', gridSize='10', guides='1', tooltips='1', connect='1', arrows='1', fold='1', page='1', pageScale='1', pageWidth=str(width), pageHeight=str(height), math='0', shadow='0')
        self.root = ET.SubElement(model, 'root')
        ET.SubElement(self.root, 'mxCell', id='0')
        ET.SubElement(self.root, 'mxCell', id='1', parent='0')
        self.counter = 1
        self.boxes = {}

    def node(self, text, x, y, w, h, style='', fill='#ffffff', font=17, bold=False, shape='rect'):
        self.counter += 1
        ident = str(self.counter)
        native = {'rect':'rounded=0;', 'round':'rounded=1;arcSize=16;', 'ellipse':'ellipse;', 'final':'ellipse;shape=doubleEllipse;', 'text':'text;strokeColor=none;fillColor=none;', 'package':'shape=folder;tabWidth=160;tabHeight=26;'}[shape]
        base = f'{native}whiteSpace=wrap;html=0;fillColor={fill};strokeColor=#365b4b;fontColor=#19382e;fontFamily=Arial;fontSize={font};fontStyle={1 if bold else 0};spacing=6;'
        c = ET.SubElement(self.root,'mxCell',id=ident,value=text,style=base+style,vertex='1',parent='1')
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
        self.boxes[ident] = (x,y,w,h)
        return ident

    def line(self, x1,y1,x2,y2,label='',dashed=False,arrow=True,points=None,font=15,source=None,target=None,offset=(0,-10),start=False):
        self.counter+=1
        style=f'edgeStyle=none;rounded=0;html=0;fontFamily=Arial;fontSize={font};fontColor=#19382e;strokeColor=#456353;labelBackgroundColor=#ffffff;endArrow={"open" if arrow else "none"};endFill=0;'
        if dashed: style+='dashed=1;'
        if start: style+='startArrow=open;startFill=0;'
        attrs=dict(id=str(self.counter),value=label,edge='1',parent='1',style=style)
        if source: attrs['source']=source
        if target: attrs['target']=target
        c=ET.SubElement(self.root,'mxCell',**attrs)
        g=ET.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'})
        ET.SubElement(g,'mxPoint',x=str(x1),y=str(y1),**{'as':'sourcePoint'})
        ET.SubElement(g,'mxPoint',x=str(x2),y=str(y2),**{'as':'targetPoint'})
        ET.SubElement(g,'mxPoint',x=str(offset[0]),y=str(offset[1]),**{'as':'offset'})
        if points:
            a=ET.SubElement(g,'Array',**{'as':'points'})
            for x,y in points: ET.SubElement(a,'mxPoint',x=str(x),y=str(y))
        return c

    def connect(self, a,b,label='',**kw):
        x,y,w,h=self.boxes[a];X,Y,W,H=self.boxes[b]
        if abs(X-x)>abs(Y-y):
            x1,y1,x2,y2=(x+w,y+h/2,X,Y+H/2) if X>x else (x,y+h/2,X+W,Y+H/2)
        else:
            x1,y1,x2,y2=(x+w/2,y+h,X+W/2,Y) if Y>y else (x+w/2,y,X+W/2,Y+H)
        return self.line(x1,y1,x2,y2,label,source=a,target=b,**kw)

    def title(self,text,subtitle):
        self.node(text,25,20,self.width-50,45,font=28,bold=True,shape='text')
        self.node(subtitle,25,68,self.width-50,36,font=16,shape='text')

    def save(self, path):
        ET.indent(self.file)
        ET.ElementTree(self.file).write(path,encoding='utf-8',xml_declaration=True)

def styles(text):
    return dict(s.split('=',1) for s in text.split(';') if '=' in s)

def validate(path):
    tree=ET.parse(path);cells=tree.findall('.//mxCell');ids=[c.get('id') for c in cells]
    assert len(ids)==len(set(ids)),f'Duplicate cell IDs: {path}'
    vertices=[c for c in cells if c.get('vertex')=='1'];edges=[c for c in cells if c.get('edge')=='1']
    assert len(vertices)>5 and len(edges)>3
    for c in cells:
        assert c.get('source') is None or c.get('source') in ids
        assert c.get('target') is None or c.get('target') in ids
        if c.get('vertex')=='1':
            g=c.find('mxGeometry');assert g is not None
            assert float(g.get('width'))>0 and float(g.get('height'))>0
    assert not tree.findall('.//image'), 'Raster-only source is forbidden'
    return {'file':path.name,'editable_vertices':len(vertices),'editable_edges':len(edges),'xml_valid':True}

def export(path, png_dir, pdf_dir):
    tree=ET.parse(path);model=tree.find('.//mxGraphModel');W=int(model.get('pageWidth'));H=int(model.get('pageHeight'))
    img=Image.new('RGB',(W,H),'white');draw=ImageDraw.Draw(img)
    out=canvas.Canvas(str(pdf_dir/(path.stem+'.pdf')),pagesize=(W,H))
    out.setTitle(path.stem.replace('_',' '));out.setAuthor('EduAI Tanzania')
    def polyline(points,color='#456353',width=1.5,dash=False):
        out.setStrokeColor(color);out.setLineWidth(width);out.setDash([7,5] if dash else [])
        p=out.beginPath();p.moveTo(points[0][0],H-points[0][1])
        for x,y in points[1:]:p.lineTo(x,H-y)
        out.drawPath(p)
        for (x,y),(X,Y) in zip(points,points[1:]):
            if dash:
                length=math.hypot(X-x,Y-y)
                for d in range(0,int(length),12):
                    e=min(d+7,length)
                    draw.line((x+(X-x)*d/max(length,1),y+(Y-y)*d/max(length,1),x+(X-x)*e/max(length,1),y+(Y-y)*e/max(length,1)),fill=color,width=max(1,int(width)))
            else:draw.line((x,y,X,Y),fill=color,width=max(1,int(width)))
    def text(value,x,y,w,h,size=17,bold=False,align='center',fill='#19382e',background=False):
        font=ImageFont.truetype(str(BOLD if bold else REGULAR),size)
        lines=[]
        for original in value.split('\n'):
            words=original.split(' ');line=''
            for word in words:
                if line and draw.textlength(line+' '+word,font=font)>w-12:lines.append(line);line=word
                else:line=(line+' '+word).strip()
            lines.append(line)
        lineheight=size*1.28;Y=y+(h-len(lines)*lineheight)/2
        if background:
            bw=max([draw.textlength(s,font=font) for s in lines]+[0])+12
            draw.rectangle((x+w/2-bw/2,Y-2,x+w/2+bw/2,Y+lineheight*len(lines)+2),fill='white')
            out.setFillColor('white');out.rect(x+w/2-bw/2,H-Y-lineheight*len(lines)-2,bw,lineheight*len(lines)+4,fill=1,stroke=0)
        for line in lines:
            X=x+6 if align=='left' else x+(w-draw.textlength(line,font=font))/2
            draw.text((X,Y),line,font=font,fill=fill)
            out.setFillColor(fill);out.setFont('EduArialBold' if bold else 'EduArial',size)
            out.drawString(X,H-Y-size*.94,line)
            Y+=lineheight
    for c in tree.findall('.//mxCell'):
        st=styles(c.get('style',''));g=c.find('mxGeometry')
        if g is None:continue
        value=c.get('value','');size=int(st.get('fontSize',17));bold=st.get('fontStyle')=='1'
        if c.get('vertex')=='1':
            x,y,w,h=[float(g.get(k,'0')) for k in ('x','y','width','height')]
            fill=st.get('fillColor','#ffffff');stroke=st.get('strokeColor','#365b4b');shape=st.get('shape','')
            raw=c.get('style','')
            istext=raw.startswith('text;')
            if not istext:
                out.setFillColor(fill if fill!='none' else '#ffffff');out.setStrokeColor(stroke);out.setLineWidth(1.4);out.setDash([])
                if 'ellipse;' in raw:
                    draw.ellipse((x,y,x+w,y+h),fill=fill,outline=stroke,width=2);out.ellipse(x,H-y-h,x+w,H-y,stroke=1,fill=1)
                    if shape=='doubleEllipse':draw.ellipse((x+5,y+5,x+w-5,y+h-5),outline=stroke,width=2);out.ellipse(x+5,H-y-h+5,x+w-5,H-y-5)
                elif shape=='folder':
                    points=[(x,y+26),(x,y),(x+160,y),(x+180,y+26),(x+w,y+26),(x+w,y+h),(x,y+h),(x,y+26)]
                    draw.polygon(points,fill=fill,outline=stroke);p=out.beginPath();p.moveTo(x,H-y-26)
                    for X,Y in points[1:]:p.lineTo(X,H-Y)
                    out.drawPath(p,fill=1,stroke=1)
                elif st.get('rounded')=='1':draw.rounded_rectangle((x,y,x+w,y+h),radius=12,fill=fill,outline=stroke,width=2);out.roundRect(x,H-y-h,w,h,12,stroke=1,fill=1)
                else:draw.rectangle((x,y,x+w,y+h),fill=fill,outline=stroke,width=2);out.rect(x,H-y-h,w,h,stroke=1,fill=1)
            if value:text(value,x,y,w,h,size,bold,st.get('align','center'))
        elif c.get('edge')=='1':
            src=g.find("mxPoint[@as='sourcePoint']");dst=g.find("mxPoint[@as='targetPoint']")
            pts=[(float(src.get('x')),float(src.get('y')))]+[(float(p.get('x')),float(p.get('y'))) for p in g.findall('./Array/mxPoint')]+[(float(dst.get('x')),float(dst.get('y')))]
            polyline(pts,dash=st.get('dashed')=='1')
            def arrow(a,b):
                angle=math.atan2(b[1]-a[1],b[0]-a[0]);arms=[(b[0]-12*math.cos(angle+sgn*.45),b[1]-12*math.sin(angle+sgn*.45)) for sgn in (-1,1)];polyline([arms[0],b,arms[1]])
            if st.get('endArrow')!='none':arrow(pts[-2],pts[-1])
            if st.get('startArrow')=='open':arrow(pts[1],pts[0])
            if value:
                offset=g.find("mxPoint[@as='offset']");ox=float(offset.get('x','0'));oy=float(offset.get('y','-10'))
                X=(pts[0][0]+pts[-1][0])/2+ox;Y=(pts[0][1]+pts[-1][1])/2+oy
                text(value,X-230,Y-22,460,44,size,bold,background=True)
    meta=PngImagePlugin.PngInfo();meta.add_text('mxfile',path.read_text(encoding='utf-8'))
    img.save(png_dir/(path.stem+'.png'),pnginfo=meta)
    out.showPage();out.save()
    return W,H
