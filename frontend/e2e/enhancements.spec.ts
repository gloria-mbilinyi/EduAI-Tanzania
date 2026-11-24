import {test,expect,Page} from '@playwright/test';
const password=process.env.EDUAI_DEMO_PASSWORD;
test.skip(!password,'Set the fictional seed password.');
async function login(page:Page,handle:string){
 const auth=await page.request.post('/api/auth/login',{data:{email:`${handle}@demo.eduai.test`,password}});const {access_token}=await auth.json();
 await page.request.patch('/api/me/language',{headers:{Authorization:`Bearer ${access_token}`},data:{language:'en'}});
 await page.goto('/login');await page.getByLabel('Email address').fill(`${handle}@demo.eduai.test`);await page.getByLabel('Password',{exact:true}).fill(password!);await page.getByRole('button',{name:'Sign in',exact:true}).click();await expect(page).toHaveURL(/app\/overview/);
}
const panel=(page:Page,title:string)=>page.locator('section.panel').filter({has:page.getByRole('heading',{name:title,exact:true})});

test('three assignment attempts preserve feedback and official best score on mobile',async({page,browser})=>{
 await login(page,'neema');await page.goto('/app/assignments?course=1');
 const title='Attempt improvement '+Date.now(),create=panel(page,'Create assignment');
 await create.getByLabel('Title',{exact:true}).fill(title);await create.getByLabel('Instructions').fill('Show every calculation and use feedback to revise.');
 await create.getByLabel('Maximum attempts').fill('3');await create.getByLabel('Allow resubmission',{exact:true}).check();await create.getByLabel('Require feedback before resubmission').check();await create.getByLabel('Official grading policy').selectOption('best');
 await create.getByRole('button',{name:'Create assignment',exact:true}).click();await expect(panel(page,title)).toBeVisible();
 const context=await browser.newContext(),student=await context.newPage();await login(student,'amina');await student.goto('/app/assignments?course=1');
 for(const [i,score] of [45,80,100].entries()){
  const p=panel(student,title);await p.getByLabel('Your response').fill(`Revised calculation attempt ${i+1}`);await p.getByRole('button',{name:i?'Submit another attempt':'Submit',exact:true}).click();
  await expect(p.getByRole('heading',{name:'Attempt history'})).toBeVisible();
  await page.reload();const review=panel(page,title);await review.locator('details').filter({has:page.locator('summary').filter({hasText:'Amina Juma'})}).first().locator('summary').first().click();
  const attempt=review.locator('article.attempt-card').filter({has:page.getByRole('heading',{name:`Attempt ${i+1}`,exact:true})});
  await attempt.getByLabel('Score',{exact:true}).fill(String(score));await attempt.getByLabel('Feedback').fill(`Reviewed calculation with score ${score}`);await attempt.getByRole('button',{name:'Record grade',exact:true}).click();await expect(attempt.getByRole('status')).toBeVisible();
  await student.reload();await expect(panel(student,title).getByText(`Official score: ${score}% (Attempt ${i+1})`,{exact:true})).toBeVisible();
 }
 const p=panel(student,title);await expect(p.getByText('Remaining attempts: 0')).toBeVisible();await expect(p.getByRole('progressbar')).toHaveCount(3);await expect(p.getByRole('button',{name:'Submit another attempt'})).toHaveCount(0);
 await p.getByText('Resubmission requests',{exact:true}).click();await p.getByLabel('Reason').fill('Please allow one extra practice attempt.');await p.getByRole('button',{name:'Request resubmission',exact:true}).click();
 await page.reload();const req=panel(page,title).locator('details').filter({has:page.locator('summary').filter({hasText:'Resubmission requests'})}).first();await req.locator('summary').first().click();await req.getByLabel('Feedback').fill('You may try once more.');await req.getByRole('button',{name:'Review request',exact:true}).click();
 await page.screenshot({path:'../docs/screenshots/14-teacher-attempt-review.png',fullPage:true});
 await student.reload();await student.setViewportSize({width:390,height:844});await expect(panel(student,title).getByRole('button',{name:'Submit another attempt'})).toBeVisible();
 expect(await student.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await student.screenshot({path:'../docs/screenshots/15-mobile-attempt-history.png',fullPage:true});await context.close();
});

test('hybrid tutor solves math routes calculus and persists Kiswahili preference',async({page})=>{
 await login(page,'amina');await page.goto('/app/tutor');
 for(const [question,result] of [['3x + 9 = 18','x = 3'],['Differentiate x^3 + 2x','3 × x'],['Integrate 2x','+ C']]){
  await page.getByLabel('Ask a question',{exact:true}).fill(question);
  const response=page.waitForResponse(r=>r.url().endsWith('/api/tutor/ask')&&r.request().postDataJSON().question===question);
  await page.getByRole('button',{name:'Ask tutor',exact:true}).click();await response;
  await expect(page.locator('.chat-message.question').first()).toContainText(question);
  await expect(page.locator('.math-answer').first()).toContainText(result);
 }
 await page.getByLabel('Ask a question',{exact:true}).fill('I need to solve calculus');await page.getByRole('button',{name:'Ask tutor',exact:true}).click();await expect(page.getByText(/original teaching passage M04/).first()).toBeVisible();
 await page.screenshot({path:'../docs/screenshots/16-hybrid-math-tutor.png',fullPage:true});
 await page.getByRole('button',{name:'Kiswahili',exact:true}).click();await page.getByLabel('Uliza swali',{exact:true}).fill('3x + 9 = 18');await page.getByRole('button',{name:'Uliza msaidizi',exact:true}).click();await expect(page.locator('.math-answer').first()).toContainText('Toa 9');
 await page.reload();await expect(page.getByRole('heading',{name:'Msaidizi wa masomo',exact:true})).toBeVisible();
 const saved=await page.evaluate(async()=>{const r=await fetch('/api/me',{headers:{Authorization:'Bearer '+sessionStorage.getItem('eduai-token')}});return r.json();});expect(saved.language).toBe('sw');
 await page.setViewportSize({width:390,height:844});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.screenshot({path:'../docs/screenshots/17-kiswahili-math-mobile.png',fullPage:true});
});

test('reviewed numerical quiz draft is edited published and securely graded',async({page,browser})=>{
 await login(page,'neema');await page.goto('/app/quizzes?course=1');const editor=panel(page,'Draft assistance');
 await editor.getByLabel('Topic',{exact:true}).fill('Linear equations');await editor.getByLabel('Learning objective').fill('Solve linear equations and verify substitution');await editor.getByLabel('Question type',{exact:true}).selectOption('numerical');await editor.getByLabel('Number of questions').fill('3');
 await editor.getByRole('button',{name:'Generate draft',exact:true}).click();await expect(editor.getByLabel('Numerical answer',{exact:true})).toHaveCount(3);
 const title='Reviewed numerical quiz '+Date.now();await editor.getByLabel('Title',{exact:true}).fill(title);await editor.getByLabel('Publication').selectOption('published');await editor.getByLabel('I reviewed the questions and answer keys.').check();await editor.getByRole('button',{name:'Save reviewed quiz',exact:true}).click();await expect(panel(page,title)).toBeVisible();
 await page.screenshot({path:'../docs/screenshots/18-reviewed-numerical-quiz-builder.png',fullPage:true});
 const context=await browser.newContext(),student=await context.newPage();await login(student,'amina');await student.goto('/app/quizzes?course=1');const p=panel(student,title);await p.getByRole('button',{name:'Start quiz',exact:true}).click();
 for(let i=0;i<3;i++)await p.getByLabel('Numerical answer',{exact:true}).nth(i).fill(String(i+1));
 await p.getByRole('button',{name:'Submit answers',exact:true}).click();await expect(p.getByRole('status').first()).toContainText('100%');await student.screenshot({path:'../docs/screenshots/19-symbolic-quiz-result.png',fullPage:true});await context.close();
});

test('public pages and all four role workspaces switch language',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'Kiswahili',exact:true}).click();await expect(page.getByRole('heading',{name:/Kila mwanafunzi/})).toBeVisible();await expect(page.getByRole('heading',{name:'Jifunze kwa kasi yako',exact:true})).toBeVisible();
 for(const [handle,label] of [['neema','Kozi ulizopangiwa'],['parent','Wanafunzi waliounganishwa'],['admin','Watumiaji'],['amina','Kozi zangu']]){
  await page.context().clearCookies();await page.goto('/login');await page.evaluate(()=>{localStorage.setItem('eduai-language','en');sessionStorage.clear();});await login(page,handle);await page.getByRole('button',{name:'Kiswahili',exact:true}).click();await expect(page.getByRole('link',{name:label,exact:true})).toBeVisible();await page.reload();await expect(page.locator('html')).toHaveAttribute('lang','sw');
 }
 await page.screenshot({path:'../docs/screenshots/20-bilingual-student-workspace.png',fullPage:true});
});
