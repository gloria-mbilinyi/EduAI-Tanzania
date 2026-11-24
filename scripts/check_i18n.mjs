import fs from 'node:fs';
import path from 'node:path';
import ts from '../frontend/node_modules/typescript/lib/typescript.js';
const root=path.resolve(import.meta.dirname,'..'),extra=JSON.parse(fs.readFileSync(path.join(root,'frontend/src/i18n/sw.json'),'utf8')),keys=new Set(Object.keys(extra));
const source=ts.createSourceFile('i18n.tsx',fs.readFileSync(path.join(root,'frontend/src/i18n/index.tsx'),'utf8'),99,true,4);
function core(n){if(ts.isVariableDeclaration(n)&&n.name.text==='sw')for(const p of n.initializer.properties)keys.add(p.name.text);ts.forEachChild(n,core);}core(source);
const allow=new Set(['EDUAI TANZANIA','EduAI','EduAI Tanzania Ltd.','TANZANIA','LEARNING PLUS','EDUAI WORKSPACE','AI','TZS','https://…','amina@demo.eduai.test','3x + 9 = 18','v']);
const requested=new Set(),missing=new Set();
function check(value){value=value.trim();if(!/[A-Za-z]/.test(value))return;requested.add(value);if(!keys.has(value)&&!allow.has(value))missing.add(value);}
for(const folder of ['pages','layouts','components'])for(const name of fs.readdirSync(path.join(root,'frontend/src',folder)).filter(f=>f.endsWith('.tsx'))){
 const ast=ts.createSourceFile(name,fs.readFileSync(path.join(root,'frontend/src',folder,name),'utf8'),99,true,4);
 function visit(n){
  if(ts.isJsxText(n)&&/[A-Za-z]/.test(n.text))throw Error('Untranslated JSX text in '+name);
  if(ts.isJsxAttribute(n)&&['value','title','description','label','placeholder','aria-label','alt','note'].includes(n.name.text)&&n.initializer){
   if(ts.isStringLiteral(n.initializer)&&n.name.text!=='value')check(n.initializer.text);
   if(ts.isJsxExpression(n.initializer)&&n.initializer.expression&&ts.isStringLiteral(n.initializer.expression))check(n.initializer.expression.text);
  }
  if(ts.isCallExpression(n)&&['t','tr'].includes(n.expression.text)&&n.arguments[0]&&ts.isStringLiteral(n.arguments[0]))check(n.arguments[0].text);
  ts.forEachChild(n,visit);
 }visit(ast);
}
const report={requested_static_keys:requested.size,dictionary_keys:keys.size,missing:[...missing].sort(),scope:'Static JSX text and named display attributes; excludes user-authored content and dynamic evidence.'};
console.log(JSON.stringify(report,null,2));
if(missing.size)process.exitCode=1;
