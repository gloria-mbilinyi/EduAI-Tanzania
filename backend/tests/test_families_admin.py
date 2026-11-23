from app.models import ParentStudentLink, AuditLog

def test_parent_cannot_view_unlinked_student_or_school(env):
    c,_,users,h=env
    assert c.get(f'/api/students/{users["amina"].id}/performance',headers=h('parent')).status_code==200
    assert c.get(f'/api/students/{users["juma"].id}/performance',headers=h('parent')).status_code==403
    assert c.get(f'/api/students/{users["isolated"].id}/performance',headers=h('parent')).status_code==404
    assert c.get(f'/api/students/{users["juma"].id}/report.csv',headers=h('parent')).status_code==403
    assert c.get('/api/recommendations?student_id='+str(users['juma'].id),headers=h('parent')).status_code==403

def test_pending_link_does_not_grant_access_until_admin_verifies(env):
    c,db,users,h=env
    r=c.post('/api/parent/links',headers=h('parent'),json={'student_id':users['juma'].id})
    assert r.status_code==201 and r.json()['status']=='pending'
    assert 'Juma Salum' not in c.get('/api/parent/links',headers=h('parent')).text
    assert c.get(f'/api/students/{users["juma"].id}/performance',headers=h('parent')).status_code==403
    assert c.patch(f'/api/admin/parent-links/{r.json()["id"]}',headers=h('parent'),json={'status':'approved'}).status_code==403
    assert c.patch(f'/api/admin/parent-links/{r.json()["id"]}',headers=h('admin'),json={'status':'approved'}).status_code==200
    assert c.get(f'/api/students/{users["juma"].id}/performance',headers=h('parent')).status_code==200
    c.patch(f'/api/admin/parent-links/{r.json()["id"]}',headers=h('admin'),json={'status':'rejected'})
    assert c.get(f'/api/students/{users["juma"].id}/performance',headers=h('parent')).status_code==403

def test_teacher_parent_message_relationship_and_private_history(env):
    c,_,users,h=env
    data={'recipient_id':users['neema'].id,'student_id':users['amina'].id,'body':'How can we support algebra practice?'}
    assert c.post('/api/messages',headers=h('parent'),json=data).status_code==201
    assert len(c.get('/api/messages',headers=h('neema')).json())==1
    assert c.get('/api/messages',headers=h('hamisi')).json()==[]
    assert c.post('/api/messages',headers=h('parent'),json={**data,'student_id':users['juma'].id}).status_code==403
    assert c.post('/api/messages',headers=h('amina'),json=data).status_code==403
    assert len(c.get('/api/notifications',headers=h('neema')).json())==1
    n=c.get('/api/notifications',headers=h('neema')).json()[0]['id']
    assert c.post(f'/api/notifications/{n}/read',headers=h('parent')).status_code==404
    assert c.post(f'/api/notifications/{n}/read',headers=h('neema')).json()['read']

def test_admin_scope_school_users_assignments_and_audit(env):
    c,db,users,h=env
    assert users['isolated'].id not in [u['id'] for u in c.get('/api/admin/users',headers=h('admin')).json()]
    assert c.patch(f'/api/admin/users/{users["isolated"].id}',headers=h('admin'),json={'active':False}).status_code==404
    assert c.patch('/api/admin/school',headers=h('admin'),json={'name':'Mwangaza Demo Updated','region':'Dodoma'}).status_code==200
    assert c.post('/api/admin/teacher-assignments',headers=h('admin'),json={'teacher_id':users['neema'].id,'course_id':4}).status_code==404
    r=c.post('/api/admin/teacher-assignments',headers=h('admin'),json={'teacher_id':users['neema'].id,'course_id':3})
    assert r.status_code==201
    assert c.get('/api/courses/3/materials',headers=h('neema')).status_code==200
    assert c.delete(f'/api/admin/teacher-assignments/{r.json()["id"]}',headers=h('admin')).status_code==204
    assert c.get('/api/courses/3/materials',headers=h('neema')).status_code==403
    report=c.get('/api/admin/reports',headers=h('admin')).json()
    assert len(report['students'])==2 and report['school_average'] is not None
    assert users['isolated'].id not in [s['student_id'] for s in report['students']]
    assert any(a['action']=='school.update' for a in c.get('/api/admin/audit',headers=h('admin')).json())

def test_school_plan_management_and_scope(env):
    c,_,_,h=env
    data={'name':'School premium demo','price_tzs':2000,'days':14,'premium':True,'active':True}
    r=c.post('/api/admin/plans',headers=h('admin'),json=data)
    assert r.status_code==201
    pid=r.json()['id']
    assert c.patch(f'/api/admin/plans/{pid}',headers=h('admin'),json={**data,'price_tzs':2500}).status_code==200
    assert c.post('/api/billing/checkout',headers=h('isolated'),json={'plan_id':pid}).status_code==404
    assert c.patch('/api/admin/plans/1',headers=h('admin'),json=data).status_code==403
    assert c.post('/api/admin/plans',headers=h('neema'),json=data).status_code==403

def test_error_handling_and_api_validation(env):
    c,_,_,h=env
    assert c.get('/api/quizzes/999999',headers=h('amina')).status_code==404
    assert c.get('/api/students/not-an-id/performance',headers=h('amina')).status_code==422
    assert c.post('/api/submissions/1/grade',headers=h('neema'),json={'score':120,'feedback':'Invalid score'}).status_code==422
    assert c.post('/api/admin/enrollments',headers=h('admin'),json={'student_id':7,'course_id':1}).status_code==404
