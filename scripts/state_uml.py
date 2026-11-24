"""Readable lifecycle diagrams with persisted and conceptual states distinguished."""
from uml_canvas import Diagram

def scaffold(name,title,note):
 d=Diagram(name,2000,1580);d.title(title,'Guards precede protected transitions. Persisted statuses are distinguished from conceptual processing steps.')
 d.node(note,35,115,1930,90,font=20,shape='text',style='align=left;')
 return d

def state_ai():
 d=scaffold('03_AI_Recommendation_State_Machine','AI Recommendation State Machine',
 'Stored: pending_review, rejected, published, viewed, archived. Created, Analysis Pending, Generated, Approved, Revision Required and Regenerated are conceptual request steps. Generation failure rolls back. Cancellation abandons an unpersisted request; no cancel API or published bypass is claimed.')
 specs=[('Created',90,250),('Analysis Pending',570,250),('Generated',1050,250),('Pending Teacher Review',1530,250),('Approved',1530,610),('Published',1050,610),('Viewed',570,610),('Archived',90,610),('Rejected',1530,970),('Revision Required',1050,970),('Regenerated',570,970),('Generation Failed',90,970),('Cancelled',90,1250)]
 ids={s:d.node(s,x,y,300,90,shape='round',font=23,bold=True,fill='#e7f1eb' if s in {'Approved','Published'} else 'white') for s,x,y in specs}
 start=d.node('',35,280,28,28,shape='ellipse',fill='#19382e');end=d.node('',1040,1460,36,36,shape='final')
 d.node('',1048,1468,20,20,shape='ellipse',fill='#19382e')
 def e(a,b,label,box,via=(),ports=None):
  a=ids.get(a,a);b=ids.get(b,b)
  ports=ports or (('R','L') if d.boxes[b][0]>d.boxes[a][0] else ('L','R'))
  d.transition(a,b,label,box,via,ports)
 e(start,'Created','request',(20,210,220,35))
 e('Created','Analysis Pending','validate scope / collect evidence',(390,205,180,65))
 e('Analysis Pending','Generated','analysis succeeds / build draft',(870,205,180,65))
 e('Generated','Pending Teacher Review','persist draft + immutable snapshot',(1350,205,180,65))
 e('Pending Teacher Review','Approved','approve [assigned teacher] / save decision',(1840,430,145,100),ports=('B','T'))
 e('Approved','Published','same transaction / publish',(1350,565,180,65))
 e('Published','Viewed','view [own student]',(870,565,180,65))
 e('Viewed','Archived','archive [assigned teacher]',(390,565,180,65))
 e('Pending Teacher Review','Rejected','reject [assigned teacher] / retain comment',(1570,820,350,65),[(1950,295),(1950,1015)],('R','R'))
 e('Rejected','Revision Required','regeneration requested',(1350,925,180,65))
 e('Revision Required','Regenerated','new evidence / increment version',(870,925,180,65))
 e('Regenerated','Pending Teacher Review','new snapshot / require review again',(900,815,520,55),[(720,890),(1450,890),(1450,210),(1680,210)],('T','T'))
 e('Analysis Pending','Generation Failed','exception / rollback; never publish',(120,400,550,55),[(720,470),(45,470),(45,1015)],('B','L'))
 e('Generation Failed','Cancelled','abandon failed request',(400,1140,260,60),ports=('B','T'))
 e('Archived',end,'retain audit evidence / final',(500,1380,450,50),[(480,655),(480,1478)],('R','L'))
 e('Cancelled',end,'no published object',(500,1240,450,50),[(1058,1295)],('R','T'))
 return d

def state_subscription():
 d=scaffold('04_Subscription_State_Machine','Subscription State Machine',
 'Stored: pending_payment, active, expired, payment_failed, payment_rejected, suspended, cancelled. Created and Payment Verification are request steps. Expiring Soon is a derived time condition. Renewed creates a NEW Subscription and Payment; the old object remains expired. Entitlement also checks verified payment and future expiry on every premium request.')
 specs=[('Created',90,250),('Pending Payment',570,250),('Payment Verification',1050,250),('Active',1530,250),('Expiring Soon\n[derived]',1530,610),('Expired',1050,610),('Renewed\n<<new object event>>',570,610),('Payment Failed',1050,970),('Payment Rejected',1530,970),('Suspended',1530,1250),('Cancelled',90,1250)]
 ids={s:d.node(s,x,y,300,90,shape='round',font=23,bold=True,fill='#e7f1eb' if s=='Active' else 'white') for s,x,y in specs}
 initial=d.node('',35,280,28,28,shape='ellipse',fill='#19382e');final=d.node('',580,1460,36,36,shape='final')
 d.node('',588,1468,20,20,shape='ellipse',fill='#19382e')
 def e(a,b,label,box,via=(),ports=None,dashed=False):
  a=ids.get(a,a);b=ids.get(b,b);ports=ports or (('R','L') if d.boxes[b][0]>d.boxes[a][0] else ('L','R'))
  d.transition(a,b,label,box,via,ports,dashed=dashed)
 e(initial,'Created','select plan',(15,210,230,35))
 e('Created','Pending Payment','checkout / save server price',(390,205,180,65))
 e('Pending Payment','Payment Verification','verify / read provider ledger',(870,205,180,65))
 e('Payment Verification','Active','[success + amount + currency match] / expiry',(1350,195,180,90))
 e('Active','Expiring Soon\n[derived]','remaining time <= 7 days / UI condition',(1840,420,145,95),ports=('B','T'))
 e('Expiring Soon\n[derived]','Expired','now >= expiry / deny premium',(1350,565,180,65))
 e('Expired','Renewed\n<<new object event>>','new checkout [active plan]',(870,565,180,65),dashed=True)
 e('Renewed\n<<new object event>>','Pending Payment','<<create>> NEW transaction; verification required',(390,440,250,90),ports=('T','B'),dashed=True)
 e('Payment Verification','Payment Failed','[provider failure] / premium disabled',(1060,800,350,70),[(1200,400),(990,400),(990,1015)],('B','L'))
 e('Payment Verification','Payment Rejected','[rejected / ledger mismatch] / deny premium',(1570,800,350,70),[(1200,430),(1920,430),(1920,1015)],('B','R'))
 e('Active','Suspended','admin suspend / deny premium',(1600,1130,350,60),[(1980,295),(1980,1295)],('R','R'))
 e('Suspended','Active','restore [verified AND unexpired]',(1270,1140,250,70),[(1450,1295),(1450,295)],('L','L'))
 e('Pending Payment','Cancelled','admin cancel / stop activation',(100,800,400,70),[(450,295),(450,1295)],('L','R'))
 e('Active','Cancelled','admin cancel / deny premium',(600,1345,600,50),[(1680,390),(1880,390),(1880,1410),(240,1410)],('B','B'))
 e('Cancelled',final,'retained; no restoration',(390,1450,180,65),[(240,1478)],('B','L'))
 return d
