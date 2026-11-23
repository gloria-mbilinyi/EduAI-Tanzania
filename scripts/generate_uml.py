"""Generate all eight editable diagrams and export from saved native XML.
Usage: python scripts/generate_uml.py [01 ... 08]
"""
from pathlib import Path
import json, sys
from uml_canvas import Diagram, validate, export

ROOT=Path(__file__).resolve().parents[1]
DRAW=ROOT/'diagrams/drawio';PNG=ROOT/'diagrams/png';PDF=ROOT/'diagrams/pdf'
for p in (DRAW,PNG,PDF):p.mkdir(parents=True,exist_ok=True)

SCENARIOS=[
 ('Student Learning and AI Recommendation', ['Student',':Web Application',':Authentication',':Performance',':Recommendation Engine',':Approval Service','Teacher',':Database'],[
 (0,1,'request learning pathway'),(1,2,'validate JWT [authenticated]'),(2,7,'load current user and school'),(7,2,'active principal',True),
 (1,3,'read results [student belongs to school]'),(3,7,'loop: read recorded grades and activities'),(3,4,'generate explainable pathway'),(4,7,'persist pending_review draft'),
 (1,5,'open review queue'),(5,6,'show draft [teacher assigned to course]',True),
 (6,5,'approve with comment [approved]'),(5,7,'persist approval and publish atomically'),
 (6,5,'reject with comment [rejected]'),(5,7,'persist rejected; keep hidden'),
 (1,5,'get pathway [recommendation approved]'),(5,0,'published content and reasons',True),
 ]),
 ('Teacher Course and Assignment Management',['Teacher',':Web Application',':Authentication',':Course Service',':Assignment Service',':Database'],[
 (0,1,'sign in and open assigned course'),(1,2,'validate JWT [authenticated]'),(2,5,'load active teacher'),(1,3,'check [teacher assigned to course]'),
 (3,5,'read course and assignment membership'),(1,3,'create/update notes or video resource'),(3,5,'persist course/material and audit'),
 (1,4,'create assignment [teacher assigned to course]'),(4,5,'persist assignment'),(5,1,'saved assessment',True),
 (0,4,'grade submitted work [assigned teacher]'),(4,5,'save grade and linked-family alerts'),(4,0,'grade confirmation',True),
 ]),
 ('Parent Monitoring and Notification',['Parent',':Web Application',':Authentication',':Performance',':Notification Service','Teacher',':Database'],[
 (0,1,'open linked student report'),(1,2,'validate JWT [authenticated]'),(2,6,'load current parent'),(1,3,'check [parent linked to student]'),
 (3,6,'read approved link and school'),(3,6,'read linked student grades only'),(3,0,'academic dashboard and report',True),
 (5,3,'record grade [assigned teacher]'),(3,4,'create performance alert'),(4,6,'persist recipient notification'),
 (0,4,'read own notifications'),(4,0,'performance alert',True),(0,5,'message via authorized family relationship'),
 ]),
 ('Subscription Payment and Service Activation',['Subscriber',':Web Application',':Subscription Service',':Payment Verification',':Demo Provider',':Database'],[
 (0,1,'select plan [authenticated]'),(1,2,'create pending subscription'),(2,5,'persist immutable payment amount'),
 (2,4,'simulate provider outcome (no real money)'),(4,5,'record internal provider ledger'),(0,3,'request backend verification'),
 (3,5,'read payment and provider ledger'),(3,5,'verify amount/currency [payment verified]'),(3,2,'activate with expiry [payment verified]'),
 (2,5,'persist active subscription and audit'),(2,0,'generate demonstration receipt',True),
 (3,2,'[failed or rejected] deny activation'),(2,5,'persist failed/rejected and audit'),
 (1,2,'request premium tool [subscription active]'),(2,5,'check verified payment and unexpired entitlement'),(2,0,'allow premium assistance',True),
 ])]

def sequence():
 d=Diagram('01_EduAI_Sequence_Diagram',3000,2160)
 d.title('EduAI Tanzania Sequence Diagram','Four interaction frames. Dashed arrows are returns. Approval and verification precede publication and entitlement.')
 for n,(title,actors,messages) in enumerate(SCENARIOS):
  X=30+(n%2)*1490;Y=125+(n//2)*1000;W=1450;H=965
  d.node('',X,Y,W,H,fill='#fbfdfb')
  d.node(f'sd {n+1}  {title}',X+10,Y+8,W-20,35,font=21,bold=True,shape='text',style='align=left;')
  spacing=(W-65)/len(actors);xs=[]
  for i,name in enumerate(actors):
   x=X+35+spacing*i+spacing/2;xs.append(x)
   d.node(name,x-spacing*.46,Y+58,spacing*.92,65,font=16,bold=True,fill='#e8f1eb')
   d.line(x,Y+123,x,Y+H-45,dashed=True,arrow=False)
  dy=min(46,(H-200)/max(1,len(messages)))
  def fragment(start,end,label,split=None):
   top=Y+165+start*dy-22
   d.node('',X+12,top,W-24,(end-start)*dy+42,fill='none')
   d.node(label,X+19,top+1,240,21,font=12,shape='text',style='align=left;')
   if split is not None:
    sy=Y+165+split*dy-22
    d.line(X+12,sy,X+W-12,sy,arrow=False,dashed=True)
    d.node('[rejected]',X+19,sy+1,200,21,font=12,shape='text',style='align=left;')
  if n==0:
   fragment(5,5,'loop [per recorded result]')
   fragment(10,13,'alt [approved]',12)
   fragment(14,15,'opt [recommendation approved]')
  if n==3:
   fragment(7,12,'alt [payment verified]',11)
   fragment(13,15,'opt [subscription active]')
  for i,m in enumerate(messages):
   a,b,label,*ret=m;y=Y+165+i*dy
   d.node('',xs[b]-5,y-8,10,27,fill='#d8e8dc')
   d.line(xs[a],y,xs[b],y,f'{n+1}.{i+1}  {label}',dashed=bool(ret and ret[0]),font=14,offset=(0,-16))
 return d

def communication():
 d=Diagram('02_EduAI_Communication_Diagram',3000,2760)
 d.title('EduAI Tanzania Communication Diagram','The message numbers, participants and guards match Diagram 01. Link labels reference the ordered message catalogue in each frame.')
 for n,(title,actors,messages) in enumerate(SCENARIOS):
  X=30+(n%2)*1490;Y=125+(n//2)*1300;W=1450;H=1270
  d.node('',X,Y,W,H,fill='#fbfdfb');d.node(f'{n+1}  {title}',X+15,Y+8,W-30,40,font=21,bold=True,shape='text',style='align=left;')
  nodes=[]
  for i,name in enumerate(actors):
   col=i%4;row=i//4
   nodes.append(d.node(name,X+45+col*345,Y+80+row*400,270,58,fill='#e8f1eb',font=17,bold=True))
  grouped={}
  for i,m in enumerate(messages):grouped.setdefault((m[0],m[1]),[]).append(f'{n+1}.{i+1}')
  for j,((a,b),nums) in enumerate(grouped.items()):
   x,y,w,h=d.boxes[nodes[a]];xx,yy,ww,hh=d.boxes[nodes[b]]
   sy=y+h if a<4 else y;ty=yy+hh if b<4 else yy
   lane=Y+170+j*19
   d.line(x+w/2,sy,xx+ww/2,ty,', '.join(nums),points=[(x+w/2,lane),(xx+ww/2,lane)],font=13,source=nodes[a],target=nodes[b],offset=(0,lane-(sy+ty)/2-13))
  d.node('Ordered messages and authorization guards',X+25,Y+580,W-50,35,font=18,bold=True,shape='text',style='align=left;')
  for i,m in enumerate(messages):
   a,b,label,*ret=m
   text=f'{n+1}.{i+1}  {actors[a]} -> {actors[b]}: {label}'
   d.node(text,X+25,Y+620+i*32,W-50,30,font=15,shape='text',style='align=left;')
 return d

from state_uml import state_ai, state_subscription

def overview():
 d=Diagram('05_EduAI_Overview_Package_Diagram',1560,1660)
 d.title('EduAI Tanzania Overview Package Diagram','Dashed arrows indicate a package using another package. Responsibilities are logical packages mapped to application modules.')
 specs=[('Student Management','api/auth.py · students profile'),('Teacher Management','api/teacher_tools.py'),('Parent Management','api/families.py · approved links'),('School Administration','api/admin.py'),('Course Management','api/courses.py'),('Assignment and Quiz Management','api/assignments.py · api/quizzes.py'),('AI Learning Engine','ai/recommendations.py · ai/tutor.py'),('Subscription and Payment','api/billing.py · services/billing.py'),('Performance Analytics','services/performance.py'),('Notification and Communication','services/notifications.py · families.py'),('Reporting','api/performance.py · admin/reports'),('Authentication and Authorization','core/security.py · services/access.py'),('Data Access','core/database.py · SQLAlchemy models'),('Shared Services','core/config.py · schemas/common.py')]
 ids=[]
 for i,(name,module) in enumerate(specs):
  col=i%4;row=i//4
  x=35+col*385;y=145+row*235
  ids.append(d.node('',x,y,340,155,shape='package',fill='#f1f7f3'))
  d.node(name,x+12,y+40,316,46,font=18,bold=True,shape='text')
  d.node(module,x+12,y+88,316,52,font=14,shape='text')
 relations=[(0,4,'enrollments'),(1,4,'assigned courses'),(2,8,'linked reports'),(3,5,'school evidence'),(4,11,'access'),(5,8,'grades'),(6,8,'learning evidence'),(7,12,'transactions'),(8,12,'results'),(9,12,'recipients'),(10,8,'aggregates'),(11,13,'configuration'),(11,12,'current principal')]
 for i,(a,b,label) in enumerate(relations):
  x,y,w,h=d.boxes[ids[a]];X,Y,W,H=d.boxes[ids[b]];lane=1045+i*15
  d.transition(ids[a],ids[b],f'P{i+1}',((x+w+17+X+W+25)/2-30,lane-22,60,22),[(x+w+17,y+h/2),(x+w+17,lane),(X+W+25,lane),(X+W+25,Y+H/2)],('R','R'),dashed=True)
  col=i%2;row=i//2
  d.node(f'P{i+1}  {specs[a][0]} uses {specs[b][0]}: {label}',35+col*760,1320+row*38,735,34,font=14,shape='text',style='align=left;')
 d.node('Interfaces: JSON REST /api; bearer JWT; scoped CSV report and material downloads. Data Access and provider adapters are never directly exposed to the browser.',35,1595,1490,45,font=16,shape='text',style='align=left;')
 return d

def class_diagram(name,title,packages,classes,relations):
 d=Diagram(name,1640,1860);d.title(title,'Entity attributes map to SQLAlchemy models; service stereotypes map to modules. Association identifiers correspond to the multiplicity catalogue below.')
 positions={}
 for col,(package,items) in enumerate(packages):
  X=30+col*540;Y=140
  d.node('',X,Y,510,1120,shape='package',fill=['#f2f7f3','#f8f6ef','#f0f4f8'][col])
  d.node(package,X+12,Y+29,486,40,font=21,bold=True,shape='text')
  for row,key in enumerate(items):
   label,attrs,ops=classes[key];x=X+35;y=Y+95+row*200
   ident=d.node('',x,y,440,170,fill='white')
   d.node(label,x+4,y+3,432,34,font=18,bold=True,shape='text')
   d.line(x,y+40,x+440,y+40,arrow=False)
   d.node(attrs,x+8,y+42,424,65,font=15,shape='text',style='align=left;')
   d.line(x,y+110,x+440,y+110,arrow=False)
   d.node(ops,x+8,y+112,424,54,font=15,shape='text',style='align=left;')
   positions[key]=ident
 for i,(a,b,label) in enumerate(relations):
  x,y,w,h=d.boxes[positions[a]];X,Y,W,H=d.boxes[positions[b]];lane=1280+i*18
  sx=x+w+20;tx=X+W+28
  d.transition(positions[a],positions[b],'',None or (0,0,1,1),[(sx,y+h/2),(sx,lane),(tx,lane),(tx,Y+H/2)],('R','R'),dashed='uses' in label)
  d.node(f'R{i+1}',(sx+tx)/2-28,lane-21,56,20,font=13,shape='text')
  col=i%2;row=i//2
  d.node(f'R{i+1}  {a} -> {b}: {label}',35+col*805,1530+row*43,780,40,font=14,shape='text',style='align=left;')
 d.node('School, enrollment, parent-link and assigned-course checks enforce access. Association IDs identify links; the catalogue specifies the endpoint multiplicities.',35,1810,1570,35,font=16,shape='text',style='align=left;')
 return d

def learning():
 classes={
 'user':('User','id, role_id, school_id, language','profile(); authenticate()'),
 'student':('Student','user_id, form, interests, preference','update preferences()'),
 'school':('School','id, name, region, active','register school association()'),
 'teacher':('Teacher','user_id, specialization','review assigned course drafts()'),
 'course':('Course','id, school_id, subject, form','read materials(); assigned access()'),
 'enrollment':('Enrollment','student_id, course_id [unique pair]','enroll [same school]()'),
 'activity':('LearningActivity','student_id, course_id, action, created_at','record learning event()'),
 'submission':('Submission','student_id, assignment_id XOR quiz_id','submit one assessment attempt()'),
 'result':('Grade','submission_id, score, feedback, grader_id','aggregate recorded results()'),
 'rec':('Recommendation','student_id, course_id, status, version','generate(); regenerate(); view()'),
 'approval':('RecommendationApproval','teacher_id, decision, comment, version','record immutable decision()'),
 'engine':('<<module>> RecommendationEngine','ai/recommendations.py','generate(db, student_id, course_id)'),
 'risk':('<<module>> RiskPredictionService','services/performance.py [rule baseline]','risk_assessment(average, activity, count)'),
 'tutor':('<<module>> ChatbotTutor','ai/tutor.py; bilingual teaching corpus','retrieve(); answer(); persist history()')}
 return class_diagram('06_Learning_AI_Detailed_Package','Learning and AI Detailed Package Diagram',[
 ('Identity and School',['user','student','school','teacher']),('Learning Evidence',['course','enrollment','activity','submission','result']),('AI Learning Services',['rec','approval','engine','risk','tutor'])],classes,[
 ('school','user','1 school : 0..* users'),('user','student','1 identity : 0..1 student'),('student','enrollment','1 student : 0..* enrollments'),('course','enrollment','1 course : 0..* enrollments'),('student','activity','1 student : 0..* activities'),('result','engine','<<uses>> evidence'),('engine','rec','creates 0..* drafts'),('rec','approval','1 recommendation : 0..* decisions'),('teacher','approval','1 teacher : 0..* reviews'),('risk','result','<<uses>> mean grades'),('submission','result','1 submission : 0..1 grade')])

def assessment():
 classes={
 'teacher':('Teacher','user_id, specialization','manage assigned course()'),
 'assignmentlink':('TeacherCourseAssignment','teacher_id, course_id [unique pair]','assign(); remove assignment()'),
 'course':('Course','id, school_id, title, subject, form','create(); update(); list roster()'),
 'lesson':('Lesson','course_id, title, outline','save teacher-reviewed outline()'),
 'material':('LearningMaterial','course_id, title, kind, storage_key, url','upload(); authorized download()'),
 'assignment':('Assignment','course_id, title, instructions, due_at','create(); edit(); enforce deadline()'),
 'quiz':('Quiz','course_id, title, status','draft(); teacher publish()'),
 'question':('Question','quiz_id, prompt, options, correct_index','validate options(); hide answer key()'),
 'submission':('Submission','student_id; assignment_id XOR quiz_id','submit once per assessment()'),
 'grade':('Grade','submission_id [unique], score, grader_id','teacher grade(); send family alert()'),
 'autograde':('<<module>> AutoGradingService','api/quizzes.py; objective answer keys','attempt(); score valid answers()'),
 'draft':('<<module>> TeacherDraftService','api/teacher_tools.py; curated corpus','assemble question bank draft()')}
 return class_diagram('07_Course_Assessment_Detailed_Package','Course and Assessment Detailed Package Diagram',[
 ('Teaching and Courses',['teacher','assignmentlink','course','lesson']),('Learning and Assessment',['material','assignment','quiz','question']),('Submission and Grading',['submission','grade','autograde','draft'])],classes,[
 ('teacher','assignmentlink','1 teacher : 0..* assignments'),('assignmentlink','course','0..* assignments : 1 course'),('course','lesson','1 course : 0..* lessons'),('course','material','1 course : 0..* materials'),('course','assignment','1 course : 0..* assignments'),('quiz','question','1 quiz : 1..* questions'),('assignment','submission','1 assignment : 0..* submissions'),('submission','grade','1 submission : 0..1 grade'),('autograde','grade','creates 1 grade per attempt'),('draft','question','<<uses>> teacher-reviewed bank')])

def administration():
 classes={
 'parent':('Parent','user_id','request link(); view approved child()'),
 'link':('ParentStudentLink','parent_id, student_id, status','request(); admin verify/revoke()'),
 'student':('Student','user_id, form, interests','view own learning evidence()'),
 'notification':('Notification','user_id, title, body, read','create alert(); mark own as read()'),
 'message':('Message','sender_id, recipient_id, student_id, body','validate family pair(); send()'),
 'admin':('<<role>> SchoolAdministrator','User.role_id=admin; school_id','manage own school scope()'),
 'school':('School','id, name, region, active','update registered school()'),
 'report':('<<module>> ReportService','services/performance.py; api/admin.py','student performance(); school report()'),
 'audit':('AuditLog','actor_id, action, entity, detail','append important action()'),
 'plan':('SubscriptionPlan','school_id?, price_tzs, days, premium','create school plan(); set availability()'),
 'subscription':('Subscription','user_id, plan_id, status, expires_at','activate(); expire(); suspend(); cancel()'),
 'payment':('Payment','subscription_id, amount_tzs, status','create pending(); verified receipt()'),
 'verification':('<<module>> PaymentVerificationService','api/billing.py; ProviderTransaction','verify ledger amount and currency()')}
 return class_diagram('08_Admin_Parent_Subscription_Detailed_Package','Parent Administration and Subscription Detailed Package Diagram',[
 ('Family and Communication',['parent','link','student','notification','message']),('School Administration',['admin','school','report','audit']),('Subscription and Payment',['plan','subscription','payment','verification'])],classes,[
 ('parent','link','1 parent : 0..* verified links'),('link','student','0..* links : 1 student'),('parent','message','1 parent : 0..* own messages'),('student','notification','student/linked parent alerts'),('admin','school','0..* administrators : 1 school'),('admin','report','<<uses>> school-scoped evidence'),('admin','audit','1 actor : 0..* actions'),('plan','subscription','1 plan : 0..* subscriptions'),('subscription','payment','1 subscription : 1 payment'),('verification','payment','<<uses>> internal provider ledger'),('school','plan','0..1 school : 0..* plans')])

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
