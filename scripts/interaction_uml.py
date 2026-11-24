"""Two consistent views of four processes; labels live on message links."""
from uml_canvas import Diagram

# a,b,label,kind,phase. Calls, returns and asynchronous notifications are explicit.
SCENARIOS=[
('Student Learning and AI Recommendation', ['Student',':Web App',':Auth',':Hybrid Tutor',':Math / Retrieval',':Performance',':Recommendation','Teacher',':Database'],[
 (0,1,'ask question','call',1),(1,2,'validate current JWT + school','call',1),(2,8,'load active principal','call',1),(8,2,'principal','return',1),
 (1,3,'detect language, topic and intent','call',1),(3,4,'[math] parse, solve and verify','call',1),(4,3,'verified steps or clarification','return',1),
 (3,4,'[topic] retrieve; optional local AI','call',1),(4,3,'cited passage / bounded draft','return',1),(3,8,'save own conversation','call',1),(3,0,'selected-language explanation','return',1),
 (0,1,'request learning pathway','call',2),(1,5,'read official results + progress','call',2),(5,8,'read attempts, grades, activity','call',2),
 (5,6,'generate evidence-based draft','call',2),(6,8,'save pending_review + snapshot','call',2),
 (7,6,'review [assigned teacher]','call',2),(6,7,'draft, evidence and history','return',2),
 (7,6,'[approved] record decision','call',2),(6,8,'save approval + publish atomically','call',2),
 (7,6,'[rejected] request revision','call',2),(6,8,'reject; regenerate version hidden','call',2),
 (0,6,'get [published or viewed]','call',2),(6,0,'approved pathway only','return',2)]),
('Teacher Course and Assignment Management',['Teacher',':Web App',':Auth',':Course Access',':Attempt Service',':Grade Service','Student',':Database'],[
 (0,1,'open assigned course','call',1),(1,2,'validate active teacher','call',1),(1,3,'check assigned-course scope','call',1),(3,7,'read assignment + enrollment','call',1),
 (1,4,'save assignment + policy','call',1),(4,7,'save max attempts / deadline / rule','call',1),
 (6,4,'submit [enrolled student]','call',2),(4,7,'check count, feedback and approval','call',2),(4,7,'append immutable numbered attempt','call',2),(4,6,'attempt history + remaining limit','return',2),
 (6,4,'[blocked] request resubmission','call',2),(0,4,'approve / reopen [assigned]','call',2),(4,7,'authorize one specific next attempt','call',2),
 (0,5,'grade individual attempt','call',2),(5,7,'save grade + feedback revision','call',2),(5,7,'derive first / best / latest / selected','call',2),
 (5,6,'persist student + family alert','async',2),(6,4,'[permitted] submit next attempt','call',2),(4,7,'append; consume approval atomically','call',2)]),
('Parent Monitoring and Notification',['Parent',':Web App',':Auth',':Family Access',':Performance',':Notifications','Teacher',':Database'],[
 (0,1,'open linked student report','call',1),(1,2,'validate active parent','call',1),(1,3,'authorize approved family link','call',1),(3,7,'check same school + approved link','call',1),
 (1,4,'read official linked-student results','call',1),(4,7,'read policy-selected grades only','call',1),(4,0,'private dashboard + CSV report','return',1),
 (6,4,'record grade [assigned teacher]','call',2),(4,5,'create localized in-app alert','async',2),(5,7,'persist verified recipients','call',2),
 (0,5,'read own alerts','call',2),(5,0,'academic notification','return',2),(0,3,'send message [approved pair]','call',2),(3,7,'save scoped parent-teacher message','call',2)]),
('Subscription Payment and Service Activation',['Subscriber',':Web App',':Subscription',':Verification',':Demo Provider',':Database'],[
 (0,1,'select plan [authenticated]','call',1),(1,2,'create pending subscription','call',1),(2,5,'save immutable server price','call',1),(2,4,'simulate outcome; no real money','call',1),(4,5,'record internal provider ledger','call',1),
 (0,3,'request server verification','call',2),(3,5,'compare reference, amount, currency','call',2),(3,2,'[verified] activate + expiry','call',2),(2,5,'save active status and audit','call',2),(2,0,'demonstration receipt','return',2),
 (3,2,'[failed / rejected] deny activation','call',2),(2,5,'save failure; premium disabled','call',2),
 (1,2,'request premium assistance','call',3),(2,5,'require verified, active, unexpired','call',3),(2,0,'[entitled] allow tool','return',3)])]

FRAME_W,FRAME_H=1800,1760
def frame_origin(n):return 30+(n%2)*1840,125+(n//2)*1800
def number(n,i,messages):
 phase=messages[i][4];ordinal=sum(m[4]==phase for m in messages[:i+1]);return f'{n+1}.{phase}.{ordinal}'

def actor(d,name,x,y,w):
 if name.startswith(':'):
  d.node(name,x-w/2,y,w,65,font=20,bold=True,fill='#eaf3ed')
 else:
  d.node('',x-10,y,20,20,shape='ellipse',fill='white');d.line(x,y+20,x,y+50,arrow=False);d.line(x-18,y+31,x+18,y+31,arrow=False)
  d.line(x,y+50,x-17,y+65,arrow=False);d.line(x,y+50,x+17,y+65,arrow=False)
  d.node(name,x-w/2,y+67,w,30,font=20,bold=True,shape='text')

def sequence():
 d=Diagram('01_EduAI_Sequence_Diagram',3700,3750)
 d.title('EduAI Tanzania Sequence Diagram','Four processes. Solid filled arrows: synchronous calls. Dashed: returns. Open solid: asynchronous alerts. Enlarged frames accompany the proposal.')
 for n,(title,actors,messages) in enumerate(SCENARIOS):
  X,Y=frame_origin(n);d.node('',X,Y,FRAME_W,FRAME_H,fill='#fbfdfb')
  d.node('sd '+str(n+1)+'  '+title,X+15,Y+10,FRAME_W-30,45,font=25,bold=True,shape='text',style='align=left;')
  gap=(FRAME_W-100)/len(actors);xs=[X+50+gap*(i+.5) for i in range(len(actors))]
  for x,name in zip(xs,actors):actor(d,name,x,Y+70,gap*.91);d.line(x,Y+170,x,Y+FRAME_H-35,arrow=False,dashed=True)
  dy=min(78,(FRAME_H-270)/len(messages));start=Y+220
  def fragment(first,last,label,split=None):
   top=start+first*dy-57;bottom=start+last*dy+20
   d.node('',X+12,top,FRAME_W-24,bottom-top,fill='none');d.node(label,X+15,top-1,440,26,font=16,bold=True,shape='text',style='align=left;')
   if split is not None:
    sy=start+split*dy-57;d.line(X+12,sy,X+FRAME_W-12,sy,arrow=False,dashed=True)
    d.node(label.split(' / ')[-1],X+15,sy+1,440,25,font=16,shape='text',style='align=left;')
  if n==0:fragment(5,8,'alt [math expression] / [teaching topic]',7);fragment(18,21,'alt [approved] / [rejected]',20)
  if n==1:fragment(6,18,'loop [each authorized attempt]');fragment(10,12,'opt [teacher authorization required]')
  if n==2:fragment(7,9,'opt [new grade]')
  if n==3:fragment(7,11,'alt [payment verified] / [not verified]',10);fragment(12,14,'opt [premium request]')
  for i,(a,b,label,kind,phase) in enumerate(messages):
   y=start+i*dy;d.node('',xs[b]-5,y-9,10,27,fill='#cfe3d5')
   width=min(660,max(240,abs(xs[b]-xs[a])-16))
   d.line(xs[a],y,xs[b],y,number(n,i,messages)+' '+label,dashed=kind=='return',sync=kind=='call',font=19,offset=(0,-30),label_width=width,label_height=48)
 return d

def communication():
 d=Diagram('02_EduAI_Communication_Diagram',3700,3750)
 d.title('EduAI Tanzania Communication Diagram','Objects are linked directly. Nested numbers and guards match Diagram 01. Labels sit on their corresponding directed message links; no separate catalogue is required.')
 for n,(title,actors,messages) in enumerate(SCENARIOS):
  X,Y=frame_origin(n);d.node('',X,Y,FRAME_W,FRAME_H,fill='#fbfdfb')
  d.node(str(n+1)+'  '+title,X+15,Y+10,FRAME_W-30,45,font=25,bold=True,shape='text',style='align=left;')
  half=(len(actors)+1)//2;ids=[]
  for i,name in enumerate(actors):
   row=0 if i<half else 1;col=i%half;space=(FRAME_W-70)/half
   ids.append(d.node(name,X+35+col*space,Y+75+row*(FRAME_H-210),space-20,72,font=20,bold=True,fill='#eaf3ed'))
  groups={}
  for i,m in enumerate(messages):groups.setdefault((m[0],m[1],m[3]),[]).append((number(n,i,messages),m[2]))
  available=FRAME_H-370;weights=[max(2,len(labels))*27+20 for labels in groups.values()];scale=min(1,available/sum(weights));lane=Y+190
  for j,((a,b,kind),labels) in enumerate(groups.items()):
   height=weights[j]*scale;lane+=height/2
   x,y,w,h=d.boxes[ids[a]];xx,yy,ww,hh=d.boxes[ids[b]]
   sx=x+w/2+(j%3-1)*8;tx=xx+ww/2+(j%3-1)*8;sy=y+h if a<half else y;ty=yy+hh if b<half else yy
   # A short loop route preserves messages between adjacent objects on the same row.
   text='\n'.join(f'{num} {label}' for num,label in labels)
   d.line(sx,sy,tx,ty,text,source=ids[a],target=ids[b],points=[(sx,lane),(tx,lane)],
          dashed=kind=='return',sync=kind=='call',font=18,offset=(0,lane-(sy+ty)/2),label_width=min(1300,max(620,abs(tx-sx)-20)),label_height=height-8)
   lane+=height/2
 return d
