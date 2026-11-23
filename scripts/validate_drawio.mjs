// Native editor round-trip validation through the documented draw.io embed API.
// Requires npm ci in frontend/. Internet is required; no application credentials
// or personal school records are sent. Only the supplied UML source is loaded.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {chromium}=await import(pathToFileURL(path.join(root,'frontend/node_modules/playwright/index.mjs')).href);
const browser=await chromium.launch({channel:'chrome',headless:true});
const evidence=[];
try{
 const page=await browser.newPage({viewport:{width:1500,height:1000}});
 await page.goto('http://127.0.0.1:5173/',{waitUntil:'domcontentloaded'});
 await page.evaluate(()=>{
  window.diagramEvents=[];
  window.addEventListener('message',e=>{if(e.origin!=='https://embed.diagrams.net')return;try{window.diagramEvents.push(JSON.parse(e.data))}catch{}});
  document.body.innerHTML='<iframe id="native-editor" title="Native draw.io validation" style="position:fixed;inset:0;width:100%;height:100%;border:0" src="https://embed.diagrams.net/?embed=1&proto=json&spin=1&ui=min&noSaveBtn=1&noExitBtn=1"></iframe>';
 });
 await page.waitForFunction(()=>window.diagramEvents.some(e=>e.event==='init'),{},{timeout:45000});
 async function send(message){await page.evaluate(m=>{window.diagramEvents=[];document.getElementById('native-editor').contentWindow.postMessage(JSON.stringify(m),'https://embed.diagrams.net')},message)}
 async function receive(event){await page.waitForFunction(type=>window.diagramEvents.some(e=>e.event===type),event,{timeout:25000});return page.evaluate(type=>window.diagramEvents.find(e=>e.event===type),event)}
 const files=(await fs.readdir(path.join(root,'diagrams/drawio'))).filter(f=>f.endsWith('.drawio')).sort();
 for(const file of files){
  const xml=await fs.readFile(path.join(root,'diagrams/drawio',file),'utf8');
  await send({action:'load',xml,title:file,readOnly:false,fit:1,background:'#ffffff'});
  const loaded=await receive('load');if(loaded.error)throw new Error(`${file}: ${loaded.error}`);
  await send({action:'export',format:'svg',border:20});const result=await receive('export');
  if(result.error||!result.data?.startsWith('data:image/svg+xml'))throw new Error(`${file}: SVG export failed`);
  const comma=result.data.indexOf(',');const svg=result.data.slice(0,comma).includes(';base64')?Buffer.from(result.data.slice(comma+1),'base64').toString():decodeURIComponent(result.data.slice(comma+1));
  if(!svg.includes('<svg')||svg.length<4000)throw new Error(`${file}: empty SVG`);
  await fs.mkdir(path.join(root,'diagrams/svg'),{recursive:true});await fs.writeFile(path.join(root,'diagrams/svg',file.replace('.drawio','.svg')),svg);
  await send({action:'export',format:'xmlpng',border:20,scale:1});const png=await receive('export');
  if(!png.data?.startsWith('data:image/png;base64,'))throw new Error(`${file}: PNG export failed`);
  await fs.writeFile(path.join(root,'diagrams/png',file.replace('.drawio','.png')),Buffer.from(png.data.split(',')[1],'base64'));
  const print=await browser.newPage();await print.setContent(`<html><head><style>html,body{margin:0;padding:0;background:white}svg{display:block}</style></head><body>${svg}</body></html>`);
  const size=await print.locator('svg').evaluate(svg=>({width:svg.getAttribute('width'),height:svg.getAttribute('height')}));
  await print.pdf({path:path.join(root,'diagrams/pdf',file.replace('.drawio','.pdf')),width:size.width,height:size.height,printBackground:true,margin:{top:0,bottom:0,left:0,right:0}});await print.close();
  evidence.push({file,native_editor_loaded:true,editable_mode:true,native_svg_export:true,native_png_export:true,pdf_from_native_svg:true,bounds:loaded.modelBounds||loaded.bounds});
  console.log(JSON.stringify(evidence.at(-1)));
 }
 await fs.writeFile(path.join(root,'diagrams/native-validation.json'),JSON.stringify(evidence,null,2));
}finally{await browser.close()}
