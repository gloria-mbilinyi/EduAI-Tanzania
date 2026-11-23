"""Requirement traceability, conservatively excluding partial capabilities."""
from pathlib import Path
import re, json
ROOT=Path(__file__).resolve().parents[1]
brief=(ROOT/'docs/requirements/MASTER_BRIEF.txt').read_text(encoding='utf-8')
requirements=re.findall(r'^((?:ST|TC|PR|AD|AI)-\d{2}):\s*(.+)$',brief,re.M)
assert len(requirements)==50 and len(dict(requirements))==50
# IDs below refer to executed tests, not unverified acceptance assertions.
mapdata={
'ST':[
('auth','identity::test_registration_school_profile_and_duplicates','Register/login; admin is provisioned out of band'),
('auth','identity::test_profile_language_and_no_role_escalation','Name, language, interests and learning preference'),
('auth','identity::test_registration_school_profile_and_duplicates','Existing active school is required'),
('recommendations','ai::test_pending_hidden_then_teacher_approval_publishes','Persisted rule-based recommendations'),
('tutor','ai::test_bilingual_retrieval_sources_history_and_no_match','Small cited teaching corpus, not a generative LLM'),
('assignments','academics::test_assignment_submission_grading_and_alerts','Text submissions; one per assignment'),
('quizzes','academics::test_objective_quiz_hides_keys_validates_and_grades','One objective attempt per quiz'),
('quizzes','academics::test_objective_quiz_hides_keys_validates_and_grades','Server-side answer keys and persisted grade'),
('performance','academics::test_assignment_submission_grading_and_alerts','Charts use persisted grades'),
('performance','academics::test_assignment_submission_grading_and_alerts','CSV export and printable browser report'),
('recommendations','ai::test_pending_hidden_then_teacher_approval_publishes','Uses weakest assessment, preferences, interests and activity'),
('auth','frontend: switches navigation labels and the document language','Navigation and core labels translated; explanatory and API text still partly English'),
],
'TC':[
('auth','identity::test_teacher_requires_activation','Registration plus administrator activation'),
('courses','e2e: teacher dashboard and lesson assistance persist a reviewed draft','Assigned-course dashboard'),
('courses','academics::test_course_assignment_permissions_and_scope','Creator is assigned automatically'),
('courses','academics::test_course_assignment_permissions_and_scope','Unassigned courses denied on server'),
('courses','academics::test_materials_upload_download_and_validation','Text notes and protected file upload'),
('courses','academics::test_materials_upload_download_and_validation','HTTPS links and capped MP4 upload/download'),
('assignments','academics::test_assignment_submission_grading_and_alerts','Create/edit assignments and grade submissions'),
('performance','academics::test_teacher_performance_excludes_unassigned_subjects','Results restricted to assigned subjects'),
('teacher_tools','ai::test_teacher_tools_are_entitled_drafts_and_persist_reviewed_lesson','Curated question-bank assembly; no novel question generation'),
('teacher_tools','e2e: teacher dashboard and lesson assistance persist a reviewed draft','Retrieved passage plus editable structured lesson template'),
('recommendations','ai::test_rejection_regeneration_keeps_review_history','Assigned teacher approves/rejects; history retained'),
],
'PR':[
('auth','risk::test_parent_self_registration_creates_restricted_account','Registration and login with no automatic child access'),
('families','families_admin::test_pending_link_does_not_grant_access_until_admin_verifies','School-approved family linkage'),
('families','e2e: parent sees approved child and academic report','Parent role dashboard'),
('performance','families_admin::test_parent_cannot_view_unlinked_student_or_school','Linked student reports'),
('families','academics::test_assignment_submission_grading_and_alerts','In-app alerts only; no SMS/email provider'),
('families','families_admin::test_teacher_parent_message_relationship_and_private_history','Validated family/teacher relationship'),
('families','families_admin::test_parent_cannot_view_unlinked_student_or_school','Negative cross-student and school tests'),
],
'AD':[
('auth','activity_roles::test_all_four_roles_login_and_load_protected_identity','Administrator account seeded out of band'),
('admin','families_admin::test_admin_scope_school_users_assignments_and_audit','Create role-assigned accounts, activate/deactivate; changing an existing role is not implemented'),
('admin','families_admin::test_admin_scope_school_users_assignments_and_audit','Update own registered school; school provisioning is out of band'),
('admin','families_admin::test_admin_scope_school_users_assignments_and_audit','Add/remove teacher assignment and enroll students'),
('admin','families_admin::test_admin_scope_school_users_assignments_and_audit','School user, activity and login counts'),
('admin','families_admin::test_admin_scope_school_users_assignments_and_audit','School means computed from persisted student evidence'),
('admin_billing','families_admin::test_school_plan_management_and_scope','Create/edit/disable school plans; shared plans immutable'),
('billing','payments::test_amount_tampering_and_unrelated_verifier_denied','Server verification and school-scoped monitoring'),
('admin_billing','payments::test_expiry_suspension_and_no_manual_activation_bypass','Verified activation, suspension, cancellation and expiry'),
('admin','e2e: school administrator can inspect scoped accounts and reports','Printable academic and usage reports plus audit trail'),
],
'AI':[
('performance','activity_roles::test_reading_materials_is_read_only_and_study_is_explicit','Recorded activity and assessment analysis; offline study unknown'),
('performance','risk::test_explainable_risk_boundaries','Transparent risk rules; no trained ML model or accuracy claim'),
('recommendations','ai::test_pending_hidden_then_teacher_approval_publishes','Three-step rule-based learning pathway'),
('performance','academics::test_assignment_submission_grading_and_alerts','Deterministic evidence summary, not generative narrative'),
('tutor','ai::test_bilingual_retrieval_sources_history_and_no_match','English/Kiswahili passage retrieval and private history'),
('teacher_tools','ai::test_teacher_tools_are_entitled_drafts_and_persist_reviewed_lesson','Structured, editable teacher-reviewed outline'),
('teacher_tools','ai::test_teacher_tools_are_entitled_drafts_and_persist_reviewed_lesson','Question bank selection and assembly only'),
('recommendations','ai::test_pending_hidden_then_teacher_approval_publishes','Visible numeric evidence and understandable reasons'),
('recommendations','ai::test_rejection_regeneration_keeps_review_history','Rejected drafts never publish without a later approval'),
('recommendations','ai::test_rejection_regeneration_keeps_review_history','Review decisions, versions and audited mutations'),
]}
pages={'auth':'Public.tsx; Performance.tsx','courses':'Academics.tsx','assignments':'Academics.tsx','quizzes':'Academics.tsx','performance':'Overview.tsx; Performance.tsx','recommendations':'AI.tsx','tutor':'AI.tsx','teacher_tools':'AI.tsx','families':'Families.tsx','admin':'Admin.tsx','billing':'Billing.tsx; Admin.tsx','admin_billing':'Admin.tsx'}
partial={'ST-12','TC-09','AD-02','AI-07'}
rows=[]
for ident,description in requirements:
 group,num=ident.split('-');module,test,note=mapdata[group][int(num)-1]
 if test.startswith(('frontend:','e2e:')):evidence='frontend/'+('src/tests/ui.test.tsx' if test.startswith('frontend:') else 'e2e/workflows.spec.ts')+' — '+test.split(': ',1)[1]
 else:
  suite,case=test.split('::');evidence=f'backend/tests/test_{suite}.py::{case}'
 source=f'backend/app/api/{module}.py; '+'; '.join('frontend/src/pages/'+p.strip() for p in pages[module].split(';'))
 if module in {'performance','recommendations','tutor'}:source+='; backend/app/'+('services/performance.py' if module=='performance' else 'ai/'+module+'.py')
 rows.append({'Requirement ID':ident,'Description':description.rstrip('.'),'Implementation Status':'Partial' if ident in partial else 'Implemented and tested','Source Files':source,'Test Evidence':evidence,'Notes':note})
total=len(rows);complete=sum(r['Implementation Status']=='Implemented and tested' for r in rows)
summary={'total_functional_requirements':total,'implemented_and_tested':complete,'partial':len(partial),'unimplemented':total-complete-len(partial),'functional_coverage_percent':round(complete/total*100,1),'method':'Complete requirements / all 50 functional requirements; partial items contribute zero.'}
out=ROOT/'docs/requirements';(out/'coverage.json').write_text(json.dumps({'summary':summary,'requirements':rows},indent=2),encoding='utf-8')
columns=list(rows[0]);lines=['# Requirements coverage','',f'**{complete}/{total} complete ({summary["functional_coverage_percent"]}%)**, {len(partial)} partial. Partial items are excluded from the percentage.','',summary['method'],'','AI completion refers to the explicitly permitted rule-based and retrieval baselines; no trained model, validated accuracy or novel generative quiz capability is claimed.','', '| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']
lines += ['| '+' | '.join(str(r[c]).replace('|','/') for c in columns)+' |' for r in rows]
(out/'COVERAGE_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(summary))
