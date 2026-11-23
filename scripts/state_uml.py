"""Lifecycle diagrams with explicit orthogonal routes and editable text labels."""
from uml_canvas import Diagram

def state_ai():
    d=Diagram('03_AI_Recommendation_State_Machine',1800,1210)
    d.title('AI Recommendation State Machine','A recommendation can reach Published only through an authorized teacher approval and its persisted decision record.')
    d.node('Persisted statuses: pending_review, rejected, published, viewed and archived. Other states describe transient steps inside a request or transaction. Failed generation rolls back. Cancellation before persistence leaves no published object.',30,115,1740,70,font=16,shape='text',style='align=left;')
    specs=[('Created',120,230),('Analysis Pending',480,230),('Generated',840,230),('Pending Teacher Review',1240,230),('Approved',1240,485),('Published',840,485),('Viewed by Student',480,485),('Archived',120,485),('Rejected',1240,725),('Revision Required',840,725),('Regenerated',480,725),('Generation Failed',840,965),('Cancelled',120,965)]
    ids={name:d.node(name,x,y,250 if name in {'Pending Teacher Review','Approved','Rejected'} else 220,80,shape='round',fill='#eaf3ed' if name in {'Published','Approved'} else '#fff',font=19,bold=True) for name,x,y in specs}
    initial=d.node('',35,255,28,28,shape='ellipse',fill='#19382e')
    final=d.node('',390,1130,34,34,shape='final')
    d.node('',398,1138,18,18,shape='ellipse',fill='#19382e')
    def e(a,b,label,box,via=(),ports=None):
        source,target=ids.get(a,a),ids.get(b,b)
        ports=ports or (('R','L') if d.boxes[target][0]>d.boxes[source][0] else ('L','R'))
        d.transition(source,target,label,box,via,ports)
    e(initial,'Created','request / validate scope',(15,195,250,35))
    e('Created','Analysis Pending','generate / collect evidence',(300,180,250,40))
    e('Analysis Pending','Generated','analysis succeeds / build draft',(665,180,280,40))
    e('Generated','Pending Teacher Review','persist pending_review draft',(1005,315,300,40))
    e('Pending Teacher Review','Approved','approve [assigned teacher]\n/ record approval',(1460,355,300,60),ports=('B','T'))
    e('Approved','Published','same transaction / publish',(1050,575,260,40))
    e('Published','Viewed by Student','view [own student] / audit',(665,575,260,40))
    e('Viewed by Student','Archived','archive [assigned teacher]',(300,575,260,40))
    e('Pending Teacher Review','Rejected','reject [assigned teacher]\n/ record decision and comment',(1485,620,290,65),[(1680,270),(1680,765)],('R','R'))
    e('Rejected','Revision Required','request regeneration',(1050,815,260,40))
    e('Revision Required','Regenerated','regenerate / increment version',(665,815,280,40))
    e('Regenerated','Pending Teacher Review','new draft / require review again',(760,620,360,40),[(590,665),(1150,665),(1150,200),(1365,200)],('T','T'))
    e('Analysis Pending','Generation Failed','exception / rollback; no publication',(510,355,280,60),[(590,380),(780,380),(780,1005)],('B','L'))
    e('Generation Failed','Analysis Pending','retry [scope valid] / collect evidence',(1100,1070,430,40),[(1760,1005),(1760,195),(590,195)],('R','T'))
    e('Created','Cancelled','invalid scope or withdrawn request\n/ no persisted publication',(10,845,330,60),[(75,270),(75,1005)],('L','L'))
    e('Archived',final,'retained for audit / lifecycle ends',(30,660,300,40),[(350,600),(350,1100),(407,1100)],('B','T'))
    e('Cancelled',final,'no published object',(85,1060,250,35),[(230,1110),(407,1110)],('B','T'))
    return d

def state_subscription():
    d=Diagram('04_Subscription_State_Machine',1800,1210)
    d.title('Subscription State Machine','The server verifies its provider ledger before activation. Every renewal is a new per-user subscription and payment object.')
    d.node('Entitlement = active status + premium flag + future expiry + verified payment. Expiring Soon is a derived view, not a stored status. Failed or rejected transactions require a new checkout. No real money is transferred.',30,115,1740,70,font=16,shape='text',style='align=left;')
    specs=[('Created',120,230),('Pending Payment',480,230),('Payment Verification',840,230),('Active',1240,230),('Expiring Soon',1240,485),('Expired',840,485),('Renewed',480,485),('Payment Failed',840,725),('Payment Rejected',1240,725),('Suspended',1240,965),('Cancelled',120,965)]
    ids={name:d.node(name,x,y,250 if x==1240 else 220,80,shape='round',fill='#eaf3ed' if name=='Active' else '#fff',font=19,bold=True) for name,x,y in specs}
    initial=d.node('',35,255,28,28,shape='ellipse',fill='#19382e')
    final=d.node('',390,1130,34,34,shape='final')
    d.node('',398,1138,18,18,shape='ellipse',fill='#19382e')
    def e(a,b,label,box,via=(),ports=None):
        source,target=ids.get(a,a),ids.get(b,b)
        ports=ports or (('R','L') if d.boxes[target][0]>d.boxes[source][0] else ('L','R'))
        d.transition(source,target,label,box,via,ports)
    e(initial,'Created','select plan',(20,195,230,35))
    e('Created','Pending Payment','checkout / persist transaction',(300,180,280,40))
    e('Pending Payment','Payment Verification','verify / read server ledger',(660,180,290,40))
    e('Payment Verification','Active','[verified amount and currency]\n/ set active status and expiry',(1050,315,320,60))
    e('Active','Expiring Soon','time remaining <= 7 days\n/ derived state',(1480,355,280,60),ports=('B','T'))
    e('Expiring Soon','Expired','now >= expiry / deny premium',(1050,575,300,40))
    e('Expired','Renewed','checkout / create NEW object',(650,575,300,40))
    e('Renewed','Pending Payment','new transaction\n/ require verification again',(295,355,280,60),ports=('T','B'))
    e('Payment Verification','Payment Failed','[provider failure]\n/ keep premium disabled',(865,620,300,60),[(1150,270),(1150,765)],('R','R'))
    e('Payment Verification','Payment Rejected','[rejected or amount/currency mismatch]\n/ keep premium disabled',(1440,625,330,65),[(950,380),(1610,380),(1610,765)],('B','R'))
    e('Active','Suspended','admin suspend / deny premium',(1470,870,300,40),[(1720,270),(1720,1005)],('R','R'))
    e('Suspended','Active','admin restore [verified AND unexpired]',(1000,895,450,45),[(1180,1005),(1180,270)],('L','L'))
    e('Pending Payment','Cancelled','admin cancel / stop activation',(265,840,310,50),[(410,270),(410,1005)],('L','R'))
    e('Active','Cancelled','admin cancel / deny premium',(575,1080,400,40),[(1120,270),(1120,1100),(230,1100)],('L','B'))
    e('Cancelled',final,'no restoration; start a new checkout',(140,1130,240,40),[(230,1147)],('B','L'))
    return d
