"""Logical package overview and focused class views with endpoint multiplicities."""
from uml_canvas import Diagram

PACKAGE_W,PACKAGE_H=1120,1120

def overview():
 d=Diagram('05_EduAI_Overview_Package_Diagram',1800,1450)
 d.title('EduAI Tanzania Overview Package Diagram','Logical packages use dashed UML dependencies. Common authentication and data dependencies attach at the protected API package boundary.')
 boundary=d.node('',30,140,1740,830,shape='package',font=22,bold=True,fill='#fbfdfb')
 d.node('Protected API packages',60,175,1600,40,font=23,bold=True,shape='text',style='align=left;')
 specs=[('Student Management','auth.py / student profile'),('Teacher Management','teacher_tools.py / assigned roster'),('Parent Management','families.py / verified links'),('School Administration','admin.py / own school'),('Course Management','courses.py / teaching resources'),('Assignment and Quiz Management','assignments.py / quizzes.py'),('AI Learning Engine','ai/* / reviewed assistance'),('Subscription and Payment','billing.py / provider adapter'),('Performance Analytics','performance.py / official grades'),('Reporting','CSV and school aggregates'),('Notifications','notifications.py / approved recipients')]
 ids=[]
 for i,(title,module) in enumerate(specs):
  x=60+(i%4)*435;y=230+(i//4)*245
  ident=d.node('',x,y,390,155,shape='package',fill='#eaf3ed');ids.append(ident)
  d.node(title,x+12,y+32,366,60,font=22,bold=True,shape='text');d.node(module,x+12,y+98,366,45,font=18,shape='text')
 for a,b,label in [(0,4,'study'),(1,5,'assess'),(2,6,'approved pathways'),(3,7,'monitor'),(4,8,'activities'),(5,9,'official results'),(6,10,'published alerts'),(8,9,'aggregates')]:
  x,y,w,h=d.boxes[ids[a]];X,Y,W,H=d.boxes[ids[b]]
  if y==Y:
   d.line(x+w,y+h/2,X,Y+H/2,label,source=ids[a],target=ids[b],dashed=True,font=17,offset=(0,-30),label_width=160)
  else:d.line(x+w/2,y+h,X+W/2,Y,label,source=ids[a],target=ids[b],dashed=True,font=17,offset=(0,0),label_width=180)
 infra=[]
 for i,(title,module) in enumerate([('Authentication','security.py + access.py'),('Data Access','database.py + models/*'),('Shared Services','config.py + schemas + i18n')]):
  x=120+i*565;y=1120
  ident=d.node('',x,y,430,165,shape='package',fill='#f6f3eb');infra.append(ident)
  d.node(title,x+10,y+40,410,45,font=24,bold=True,shape='text');d.node(module,x+10,y+95,410,45,font=19,shape='text')
  d.line(x+215,970,x+215,y,'uses',source=boundary,target=ident,dashed=True,font=19,offset=(0,0),label_width=110)
 d.node('The browser calls REST endpoints. It does not depend directly on ORM storage, answer keys or payment verification. Teacher tools retain assigned-course and premium checks.',40,1340,1720,65,font=21,shape='text',style='align=left;')
 return d

def class_view(name,title,panels):
 d=Diagram(name,2340,2540)
 d.title(title,'Focused logical packages. Associations show multiplicities at endpoints. Repeated classifiers refer to the same implemented model. Service names with <<module>> map to Python functions.')
 for i,(package,classes,relations,note) in enumerate(panels):
  X=30+(i%2)*1160;Y=145+(i//2)*1190
  d.node('',X,Y,PACKAGE_W,PACKAGE_H,shape='package',fill='#f5f8f5')
  d.node(package,X+15,Y+30,PACKAGE_W-30,45,font=26,bold=True,shape='text',style='align=left;')
  ids={}
  for j,(key,title,attrs,ops) in enumerate(classes):
   x=X+50+(j%2)*560;y=Y+110+(j//2)*335
   ident=d.node('',x,y,460,205,fill='white');ids[key]=ident
   d.node(title,x+5,y+3,450,45,font=22,bold=True,shape='text')
   d.line(x,y+51,x+460,y+51,arrow=False);d.node(attrs,x+8,y+57,444,75,font=19,shape='text',style='align=left;')
   d.line(x,y+139,x+460,y+139,arrow=False);d.node(ops,x+8,y+144,444,55,font=19,shape='text',style='align=left;')
  for a,b,label,m1,m2 in relations:
   src,dst=ids[a],ids[b];x,y,w,h=d.boxes[src];xx,yy,ww,hh=d.boxes[dst]
   if y==yy:
    if xx>x:s=(x+w,y+h/2);t=(xx,yy+hh/2)
    else:s=(x,y+h/2);t=(xx+ww,yy+hh/2)
    via=[];cx=(s[0]+t[0])/2;cy=s[1]-40
    d.node(m1,s[0]-55 if xx<x else s[0]+2,s[1]+8,55,28,font=18,shape='text')
    d.node(m2,t[0]+2 if xx<x else t[0]-55,t[1]+8,55,28,font=18,shape='text')
   else:
    down=yy>y;s=(x+w/2,y+h if down else y);t=(xx+ww/2,yy if down else yy+hh)
    mid=(s[1]+t[1])/2;via=[(s[0],mid),(t[0],mid)] if x!=xx else []
    cx=(s[0]+t[0])/2+100;cy=mid
    d.node(m1,s[0]-65,s[1]+3 if down else s[1]-31,55,28,font=18,shape='text')
    d.node(m2,t[0]-65,t[1]-31 if down else t[1]+3,55,28,font=18,shape='text')
   dependency=label.startswith('uses') or label.startswith('creates')
   d.line(*s,*t,label,source=src,target=dst,points=via,dashed=dependency,arrow=dependency,font=18,
          offset=(cx-(s[0]+t[0])/2,cy-(s[1]+t[1])/2),label_width=185,label_height=55)
  d.node(note,X+22,Y+1000,PACKAGE_W-44,94,font=19,shape='text',style='align=left;')
 return d

def learning():
 return class_view('06_Learning_AI_Detailed_Package','Learning and AI Detailed Package Diagram',[
 ('Identity and learning evidence',[
 ('school','School','id, name, region, active','registered school scope'),('teacher','Teacher','user_id, specialization','review assigned courses'),
 ('student','Student','user_id, form, interests, preference','update learning preferences'),('course','Course','id, school_id, subject, form','read materials; list roster'),
 ('enrollment','Enrollment','student_id, course_id [unique]','enroll same-school student'),('activity','LearningActivity','student_id, course_id, action, time','record explicit study event')],
 [('school','student','via User','1','0..*'),('school','teacher','via User','1','0..*'),('student','enrollment','enrolls','1','0..*'),('enrollment','course','for course','0..*','1'),('course','activity','records','1','0..*')],
 'Student and Teacher profiles reference User. School affiliation comes from User.school_id. TeacherCourseAssignment is detailed in Diagram 07.'),
 ('Official assessment evidence',[
 ('submission','Submission','student_id, assignment_id XOR quiz_id','stable legacy assessment record'),('grade','Grade','submission_id unique, score, feedback','first assignment / quiz mark'),
 ('attempt','SubmissionAttempt','submission_id, number unique, content','append immutable attempt'),('perf','<<module>> PerformanceService','services/performance.py','official results and progress'),
 ('attemptgrade','AttemptGrade','attempt_id unique, score, feedback','grade attempts 2 and above'),('risk','<<module>> RiskPredictionService','services/performance.py','explainable risk_assessment()')],
 [('submission','grade','legacy result','1','0..1'),('submission','attempt','attempts','1','0..*'),('attempt','attemptgrade','later result','1','0..1'),('perf','grade','uses official','1','0..*'),('perf','attemptgrade','uses official','1','0..*'),('perf','risk','uses mean','1','1')],
 'One assignment contributes at most one official grade to each student report. First, best, latest and teacher-selected policies are enforced by services/attempts.py.'),
 ('Reviewed recommendation lifecycle',[
 ('engine','<<module>> RecommendationEngine','ai/recommendations.py','generate evidence + reasons'),('teacher','Teacher','user_id, specialization','approve / reject assigned draft'),
 ('rec','Recommendation','student_id, course_id, status, version','generate; regenerate; view'),('approval','RecommendationApproval','teacher_id, decision, version, comment','retain review decision'),
 ('revision','RecommendationRevision','recommendation_id, version unique','retain content + evidence snapshot'),('audit','AuditLog','actor_id, action, entity, detail','append sensitive mutation')],
 [('engine','rec','creates drafts','1','0..*'),('teacher','approval','reviews','1','0..*'),('rec','approval','decisions','1','0..*'),('rec','revision','snapshots','1','1..*'),('approval','audit','audited action','1','1')],
 'Publication and an assigned teacher decision occur in one transaction. Regenerated drafts remain hidden. Old content overwritten before this upgrade is not recoverable.'),
 ('Hybrid tutor service boundaries',[
 ('tutor','<<module>> ChatbotTutor','ai/tutor.py; api/tutor.py','route tools; scoped context'),('classifier','<<module>> TopicClassifier','ai/topics.py','language, subject, topic, intent'),
 ('math','<<module>> MathSolver','ai/math_solver.py','bounded AST; solve; verify'),('retrieval','<<module>> RetrievalService','ai/tutor.py; ai/corpus.py','topic gate; cite original notes'),
 ('message','TutorMessage','user_id, subject, language, Q and A','persist own conversation'),('ollama','<<module>> OllamaProvider','ai/ollama.py; disabled by default','health; bounded JSON generation')],
 [('tutor','classifier','uses routing','1','1'),('tutor','math','uses for math','1','0..1'),('tutor','retrieval','uses notes','1','0..1'),('math','message','verified answer','1','0..*'),('retrieval','ollama','uses optional','1','0..1')],
 'MathSolver returns verified results or clarification; no raw evaluation. Ollama has no grade-writing tools. Retrieved material is untrusted data and source IDs are validated.')])

def assessment():
 return class_view('07_Course_Assessment_Detailed_Package','Course and Assessment Detailed Package Diagram',[
 ('Teaching and course access',[
 ('teacher','Teacher','user_id, specialization','manage assigned course'),('school','School','id, name, region','own-school scope'),
 ('link','TeacherCourseAssignment','teacher_id, course_id unique','assign active teacher'),('course','Course','school_id, title, subject, form','create; update; list roster'),
 ('material','LearningMaterial','course_id, kind, storage_key, URL','protected upload / download'),('lesson','Lesson','course_id, title, outline','save reviewed lesson outline')],
 [('teacher','link','assigned','1','0..*'),('school','course','contains','1','0..*'),('link','course','course','0..*','1'),('course','lesson','lessons','1','0..*'),('course','material','materials','1','0..*')],
 'Enrollment and school membership are checked before student access. Course assignment is checked before every teacher mutation.'),
 ('Assignment policies and attempts',[
 ('assignment','Assignment','course_id, title, instructions, due_at','create; edit; enforce deadline'),('policy','AssignmentPolicy','max_attempts, late, feedback, approval','first / best / latest / selected'),
 ('submission','Submission','student_id + assignment_id unique','stable assessment history anchor'),('approval','ResubmissionApproval','student_id, next number, status, until','request; teacher review; consume'),
 ('attempt','SubmissionAttempt','submission_id + number unique, content','append attempt; never overwrite'),('history','GradeHistory','attempt_id, score, feedback, grader','append each feedback revision')],
 [('assignment','policy','policy','1','0..1'),('assignment','submission','student records','1','0..*'),('policy','approval','one next try','1','0..*'),('submission','attempt','attempts','1','1..*'),('attempt','history','revisions','1','0..*')],
 'Missing legacy policy means one attempt. Existing submissions become attempt 1 without changing IDs. One assignment has many attempts through its per-student Submission record.'),
 ('Separate marks and final selection',[
 ('attempt','SubmissionAttempt','submission_id, number, content','review every attempt'),('teacher','Teacher','user_id, specialization','grade only assigned course'),
 ('grade','Grade','submission_id unique, score, feedback','retain original first-attempt ID'),('later','AttemptGrade','attempt_id unique, score, feedback','mark attempt 2 and above'),
 ('selection','FinalGradeSelection','submission_id unique, attempt_id','assigned teacher selects graded try'),('service','<<module>> AttemptService','services/attempts.py','eligibility; history; official()')],
 [('attempt','grade','number = 1','1','0..1'),('teacher','later','grades','1','0..*'),('attempt','later','number > 1','1','0..1'),('grade','selection','eligible mark','0..1','0..1'),('selection','service','uses selection','0..1','1')],
 'Grade and AttemptGrade are two storage representations of an attempt mark. Legacy Grade points to Submission; the first-attempt mapping is enforced in the service, not a new foreign key.'),
 ('Reviewed quiz and secure grading',[
 ('quiz','Quiz','course_id, title, draft / published','teacher review before publication'),('review','QuizReview','quiz_id, teacher_id, created_at','retain publication review'),
 ('question','Question','quiz_id, prompt, options, key','hide key from student detail'),('settings','QuestionSettings','question_id, kind, answer, language','MCQ / true-false / numeric / short'),
 ('response','QuizResponse','submission_id, parts, manual_marks','retain auto and manual evidence'),('auto','<<module>> AutoGradingService','api/quizzes.py; math_solver.py','objective / symbolic numeric marks')],
 [('quiz','review','reviews','1','0..*'),('quiz','question','questions','1','1..*'),('question','settings','typed key','1','0..1'),('question','response','answered','1..*','0..*'),('settings','auto','uses keys','0..*','1')],
 'QuizResponse belongs to one stable quiz Submission. Short answers wait for assigned-teacher grading. A model can propose a draft but cannot publish questions or overwrite official marks.')])

def administration():
 return class_view('08_Admin_Parent_Subscription_Detailed_Package','Parent Administrator and Subscription Detailed Package Diagram',[
 ('Verified family communication',[
 ('parent','Parent','user_id','request link; read approved child'),('teacher','Teacher','user_id, specialization','message approved family pair'),
 ('link','ParentStudentLink','parent_id, student_id, status','school verifies or revokes link'),('message','Message','sender_id, recipient_id, student_id','persist scoped conversation'),
 ('student','Student','user_id, form, interests','own academic evidence'),('notice','Notification','user_id, title, body, read','localized in-app alert')],
 [('parent','link','family links','1','0..*'),('teacher','message','assigned pair','1','0..*'),('link','student','verified child','0..*','1'),('parent','message','own messages','1','0..*'),('student','notice','result alerts','1','0..*')],
 'Notification.user_id is the recipient User ID; approved parents also receive alerts. The drawn student-alert link represents the result event, not an extra database foreign key.'),
 ('School administration and audit',[
 ('admin','<<role>> SchoolAdministrator','User with persisted role = admin','manage own registered school'),('user','User','id, school_id, role_id, active','current principal; hashed password'),
 ('school','School','id, name, region, active','school provisioning is out of band'),('audit','AuditLog','actor_id, action, entity, detail','append important actions'),
 ('report','<<module>> ReportService','api/performance.py; api/admin.py','scoped reports and safe CSV'),('access','<<module>> AccessService','services/access.py','school / role / family / course checks')],
 [('admin','user','role mapping','1','1'),('admin','school','manages','0..*','1'),('user','audit','actor','1','0..*'),('school','report','uses reports','1','1'),('audit','access','checked writes','0..*','1')],
 'SchoolAdministrator is a role of User, not a separate SQL table. Existing role changes remain outside the implemented administrator UI; activation and assignment controls are supported.'),
 ('Subscription and payment records',[
 ('plan','SubscriptionPlan','school_id optional, price, days, active','shared or school-owned plan'),('user','User','id, school_id','checkout own active plan'),
 ('sub','Subscription','user_id, plan_id, status, expires_at','active only after verified payment'),('verify','<<module>> PaymentVerificationService','api/billing.py; services/billing.py','compare server ledger; entitled()'),
 ('payment','Payment','subscription_id unique, amount, ref','verify; own demonstration receipt'),('provider','ProviderTransaction','reference unique, amount, outcome','internal simulated provider ledger')],
 [('plan','sub','subscribed plan','1','0..*'),('user','verify','own payment','1','1'),('sub','payment','payment','1','1'),('verify','provider','uses ledger','1','0..*'),('payment','provider','reference match','1','1')],
 'No real payment provider is connected. Payment.amount and currency are server-controlled. Renewal makes a new Subscription and Payment; cancelled objects are retained.'),
 ('Protected reporting and entitlements',[
 ('parent','Parent','user_id','view approved linked student only'),('teacher','Teacher','user_id','view assigned subjects only'),
 ('student','Student','user_id','view own marks and pathways'),('access','<<module>> AccessService','services/access.py; security.py','resolve active role and school'),
 ('performance','<<module>> PerformanceService','services/performance.py','one official mark per assessment'),('billing','<<module>> EntitlementService','services/billing.py','active + verified + future expiry')],
 [('parent','student','approved links','0..*','0..*'),('teacher','access','uses scope','1','1'),('student','performance','own evidence','1','1'),('access','billing','uses premium','1','0..1')],
 'Cross-school records are denied before disclosure. Entitlement is checked for premium draft assistance. Core learning, symbolic tutoring and ordinary academic reports do not require premium access.')])
