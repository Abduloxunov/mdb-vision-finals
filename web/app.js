// CarDoctor whole-car check: several photos per car, two modes (sell/buy and fleet).
let token='',current=null,busy=false,mode='sell';const photos=[];
const $=id=>document.getElementById(id);
const el=(tag,text,cls)=>{const x=document.createElement(tag);if(text!==undefined)x.textContent=text;if(cls)x.className=cls;return x;};
const VIEWS=['front','rear','left','right','interior','other'];
const NICE={dent:'Dent',scratch:'Scratch',crack:'Crack','glass shatter':'Shattered glass','lamp broken':'Broken lamp','tire flat':'Flat tyre'};
const COPY={
  sell:{eyebrow:'USED-CAR MARKETPLACE',headline:'Every scratch, found before the buyer arrives.',
    lede:'Upload photos of the car from all sides. CarDoctor finds visible damage on each photo and builds one condition report a buyer can trust, with sources.',
    query:'Anything the buyer should know? (optional)',placeholder:'e.g. small scratch on rear bumper, new tyres',button:'Check the car',shops:'Where the buyer can get it inspected'},
  fleet:{eyebrow:'FLEET & LOGISTICS',headline:'A truck has a problem. Know what to do in a minute.',
    lede:'The driver sends photos and/or describes the problem in their own words. CarDoctor finds the damage, rates how urgent it is and points to the right technician.',
    query:'What is the problem?',placeholder:'e.g. engine overheating and steam, tyre lost pressure on the highway, brake warning light',button:'Diagnose and route',shops:'Send to a technician'}};
function sourceLink(source,label){if(!source)return el('span','');const u=new URL(source.url);if(!['http:','https:'].includes(u.protocol))return el('span','Source unavailable');const a=el('a',label||source.title);a.href=u.href;a.target='_blank';a.rel='noopener noreferrer';return a;}
function setMode(next){mode=next;for(const b of document.querySelectorAll('.mode')){const on=b.dataset.mode===mode;b.classList.toggle('active',on);b.setAttribute('aria-selected',on);}
  const c=COPY[mode];$('eyebrow').textContent=c.eyebrow;$('headline').textContent=c.headline;$('lede').textContent=c.lede;$('queryLabel').textContent=c.query;$('query').placeholder=c.placeholder;$('submit').firstChild.textContent=c.button+' ';$('workshopTitle').textContent=c.shops;$('fleetCtx').hidden=mode!=='fleet';}
for(const b of document.querySelectorAll('.mode'))b.addEventListener('click',()=>setMode(b.dataset.mode));

// Poll until the server has loaded the models in memory (startup warm-up), so the first check is fast.
function health(){fetch('/api/health').then(r=>r.json()).then(h=>{token=h.token;
  if(h.warm==='loading'){$('status').textContent='Loading the damage model into memory… (first start only)';setTimeout(health,1500);return;}
  $('status').textContent=h.warm==='ready'&&h.checkpoint_available?'Ready. Damage model loaded.':h.checkpoint_available?'Ready.':'Damage model file is missing. Text checks still work.';}).catch(()=>$('status').textContent='Server is unavailable. Restart the app.');}
health();

// Shrink photos in the browser so big phone photos upload fast and stay under limits.
function shrink(file){return new Promise((resolve,reject)=>{const url=URL.createObjectURL(file);const img=new Image();
  img.onload=()=>{const k=Math.min(1,1600/Math.max(img.width,img.height));const c=document.createElement('canvas');c.width=Math.round(img.width*k);c.height=Math.round(img.height*k);c.getContext('2d').drawImage(img,0,0,c.width,c.height);URL.revokeObjectURL(url);resolve(c.toDataURL('image/jpeg',0.85));};
  img.onerror=()=>{URL.revokeObjectURL(url);reject(Error(`${file.name} could not be opened. Use JPEG, PNG or WebP.`));};img.src=url;});}
$('photo').addEventListener('change',async e=>{const files=[...e.target.files];e.target.value='';
  for(const f of files){if(photos.length>=10){$('status').textContent='Up to 10 photos per check.';break;}
    try{const used=new Set(photos.map(p=>p.view));photos.push({image:await shrink(f),view:['front','rear','left','right'].find(v=>!used.has(v))||'other'});}catch(err){$('status').textContent=err.message;}}
  drawThumbs();});
function drawThumbs(){$('thumbs').replaceChildren(...photos.map((p,i)=>{const box=el('div',undefined,'thumb');const img=el('img');img.src=p.image;img.alt=`Photo ${i+1}`;
  const sel=el('select');sel.setAttribute('aria-label',`Side of photo ${i+1}`);for(const v of VIEWS){const o=el('option',v[0].toUpperCase()+v.slice(1));o.value=v;o.selected=v===p.view;sel.append(o);}sel.addEventListener('change',()=>p.view=sel.value);
  const x=el('button','✕','remove');x.type='button';x.setAttribute('aria-label',`Remove photo ${i+1}`);x.addEventListener('click',()=>{photos.splice(i,1);drawThumbs();});box.append(img,sel,x);return box;}));}

$('form').addEventListener('submit',async e=>{e.preventDefault();if(busy)return;
  if(!photos.length&&!$('query').value.trim()){$('status').textContent='Add photos or describe the problem.';return;}
  busy=true;$('submit').disabled=true;$('status').textContent=photos.length?`Checking ${photos.length} photo${photos.length>1?'s':''} for damage…`:'Looking up the problem…';
  try{const context={};for(const n of ['engine_running','parking_brake_released'])if($(n).value)context[n]=$(n).value==='yes';
    const data={mode,photos,query:$('query').value,vehicle:$('vehicle').value,part:$('part').value,propulsion:$('propulsion').value,context,threshold:Number($('threshold').value),use_llm:$('llm').checked};
    const response=await fetch('/api/assess',{method:'POST',headers:{'Content-Type':'application/json','X-CarDoctor-Token':token},body:JSON.stringify(data)});
    let result;try{result=await response.json();}catch{throw Error('The server returned an unexpected answer. Try again.');}
    if(response.status===403){throw Error('Session expired. Reload the page and try again.');}
    if(!response.ok)throw Error(result.error||'The check failed.');
    current=result;await render(result);$('status').textContent='Report ready.';$('results').scrollIntoView({behavior:'smooth',block:'start'});
  }catch(error){$('status').textContent=error.message||'The check failed.';}finally{busy=false;$('submit').disabled=false;}});

function drawPhoto(p){return new Promise(resolve=>{const img=new Image();img.onload=()=>{const c=el('canvas');c.width=img.width;c.height=img.height;const ctx=c.getContext('2d');ctx.drawImage(img,0,0);
  const lw=Math.max(3,img.width/300),fs=Math.max(16,img.width/45);ctx.lineWidth=lw;ctx.font=`bold ${fs}px system-ui`;
  for(const d of p.detections){const [x1,y1,x2,y2]=d.box;ctx.strokeStyle='#e8433a';ctx.strokeRect(x1,y1,x2-x1,y2-y1);const t=`${NICE[d.label]||d.label} ${Math.round(d.score*100)}%`;const y=Math.max(fs+8,y1);ctx.fillStyle='#e8433a';ctx.fillRect(x1,y-fs-8,ctx.measureText(t).width+14,fs+8);ctx.fillStyle='white';ctx.fillText(t,x1+7,y-6);}
  const fig=el('figure');fig.append(c,el('figcaption',`Photo ${p.index+1} · ${p.view} · ${p.detections.length?p.detections.length+' finding'+(p.detections.length>1?'s':''):'no damage found'}`));resolve(fig);};img.onerror=()=>resolve(el('p','Photo could not be shown.'));img.src=p.image;});}

async function render(r){
  const v=r.verdict;const card=$('verdict');card.className='verdict '+v.level;card.replaceChildren(el('p',r.mode==='sell'?'CONDITION REPORT':'FLEET INCIDENT','kicker'),el('h2',v.title),el('p',v.text));
  if(v.first_action)card.append(el('p','First step: '+v.first_action,'step'));if(v.driver_condition)card.append(el('p','Applies when: '+v.driver_condition,'cond'));
  for(const z of document.querySelectorAll('.zone')){const view=z.dataset.view;z.classList.remove('bad','ok');if(r.views_damaged.includes(view))z.classList.add('bad');else if(r.views_checked.includes(view))z.classList.add('ok');}
  const s=$('summary');s.replaceChildren();if(!r.summary.length)s.append(el('li',r.photos.length?'No visible damage detected.':'Text-only check (no photos).'));
  for(const x of r.summary)s.append(el('li',`${x.count} × ${NICE[x.label]||x.label} · ${x.view}`));
  document.querySelector('.carmap').hidden=!r.photos.length;$('timing').textContent=r.photos.length?`${r.timing.photos} photo(s) analysed in ${r.timing.total_seconds}s · ${r.model.name}`:`Text check in ${r.timing.total_seconds}s · sourced knowledge base`;
  $('warnings').textContent=r.warnings.join(' ');$('warnings').hidden=!r.warnings.length;
  const shops=$('workshops');shops.replaceChildren();if(!r.workshops.length)shops.append(el('p','No matching contact in our directory yet.','small'));
  for(const w of r.workshops){const c=el('div',undefined,'shop');c.append(el('b',w.name),el('p',w.address||'Address not published','small'));if(w.matched.length)c.append(el('p','Offers: '+w.matched.join(', '),'small'));
    if(w.phone){const a=el('a','📞 '+w.phone);a.href='tel:'+w.phone.replace(/[^+\d]/g,'');c.append(a);}c.append(el('p','Published contact; confirm before visiting.','tiny'));shops.append(c);}
  drawTechs(r.technicians||[]);
  const g=$('gallery');g.replaceChildren(...await Promise.all(r.photos.map(drawPhoto)));$('gallery').previousElementSibling.hidden=!r.photos.length;
  const sources=Object.fromEntries(r.evidence.sources.map(x=>[x.id,x]));const ans=$('answer');ans.replaceChildren();const ex=r.explanation||{};
  if(ex.answer){ans.append(el('h3','AI explanation (from the sources below)'));for(const c of ex.answer.claims){const p=el('p',c.text+' ','claim');p.append(sourceLink(sources[c.source_id],`[${c.record_id}]`));ans.append(p);}for(const q of ex.answer.follow_up_questions)ans.append(el('p','❓ '+q));}
  else if(ex.status==='deterministic_fallback')ans.append(el('p','AI explanation unavailable right now; the sourced guidance below still applies.','small'));
  const ev=$('evidence');ev.replaceChildren();for(const q of r.evidence.questions)ev.append(el('p','❓ '+q,'notice'));
  if(!r.evidence.evidence.length)ev.append(el('p','No matching guidance yet. Add the car model or describe the problem in more detail.','small'));
  for(const rec of r.evidence.evidence){const b=el('article',undefined,'record');const lvl=rec.urgency.level.replace(/_/g,' ');b.append(el('span',lvl,'pill '+rec.urgency.level),el('h4',rec.title),el('p',rec.source_summary));const ul=el('ul');for(const a of rec.actions)ul.append(el('li',a));b.append(ul,el('p','Repair type: '+rec.repair_type,'small'));
    for(const ref of rec.source_refs){const p=el('p',undefined,'small');p.append('Source: ',sourceLink(sources[ref.source_id]),' · '+ref.locator);b.append(p);}ev.append(b);}
  $('empty').hidden=true;$('results').hidden=false;window.dispatchEvent(new CustomEvent('cardoctor:result',{detail:r}));}
$('download').addEventListener('click',()=>{if(!current)return;const url=URL.createObjectURL(new Blob([current.report],{type:'text/markdown;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=`cardoctor-${current.mode}-report.md`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$('print').addEventListener('click',()=>window.print());

// Technicians: sort by distance from the user (browser geolocation), show on a simple map, link to routes.
const CITY={lat:41.311,lon:69.28};let here=null,techList=[];
function km(a,b){const R=6371,r=Math.PI/180,dl=(b.lat-a.lat)*r,dn=(b.lon-a.lon)*r;const h=Math.sin(dl/2)**2+Math.cos(a.lat*r)*Math.cos(b.lat*r)*Math.sin(dn/2)**2;return 2*R*Math.asin(Math.sqrt(h));}
function routeUrl(t){const dest=`${t.lat},${t.lon}`;return here?`https://www.google.com/maps/dir/?api=1&origin=${here.lat},${here.lon}&destination=${dest}`:`https://www.google.com/maps/search/?api=1&query=${dest}`;}
function svgEl(tag,attrs,text){const x=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const[k,v]of Object.entries(attrs))x.setAttribute(k,v);if(text!==undefined)x.textContent=text;return x;}
function drawTechs(list){techList=list;const box=$('techs'),map=$('techmap');$('techs').closest('.nearby').hidden=!list.length;if(!list.length)return;
  const from=here||CITY;const sorted=[...list].map(t=>({...t,dist:km(from,t)})).sort((a,b)=>a.dist-b.dist);
  const pts=[...sorted,...(here?[{...here,me:true}]:[])];const lats=pts.map(p=>p.lat),lons=pts.map(p=>p.lon);
  const pad=.01,minLa=Math.min(...lats)-pad,maxLa=Math.max(...lats)+pad,minLo=Math.min(...lons)-pad,maxLo=Math.max(...lons)+pad;
  const X=lon=>20+(lon-minLo)/(maxLo-minLo)*360,Y=lat=>155-(lat-minLa)/(maxLa-minLa)*140;
  map.replaceChildren(svgEl('rect',{x:0,y:0,width:400,height:170,rx:12,class:'mapbg'}),svgEl('text',{x:390,y:16,class:'north'},'N ↑ Tashkent'));
  sorted.forEach((t,i)=>{const g=svgEl('a',{href:routeUrl(t),target:'_blank'});g.append(svgEl('circle',{cx:X(t.lon),cy:Y(t.lat),r:i===0?11:8,class:i===0?'pin best':'pin'}),svgEl('text',{x:X(t.lon),y:Y(t.lat)+4,class:'pinlabel'},String(i+1)));map.append(g);});
  if(here){map.append(svgEl('circle',{cx:X(here.lon),cy:Y(here.lat),r:9,class:'me'}),svgEl('text',{x:X(here.lon),y:Y(here.lat)-14,class:'melabel'},'You'));}
  box.replaceChildren(...sorted.slice(0,4).map((t,i)=>{const c=el('div',undefined,'shop'+(i===0?' best':''));c.append(el('b',`${i+1}. ${t.name}`),el('p',`${t.dist.toFixed(1)} km ${here?'from you':'from city centre'} · ${t.district}`,'small'),el('p','Can help with: '+t.matched.join(', '),'small'));
    if(t.mobile)c.append(el('p','🚐 Can come to you','small'));const a=el('a','🧭 Route');a.href=routeUrl(t);a.target='_blank';a.rel='noopener noreferrer';c.append(a,el('p','Demo technician (fictional)','tiny'));return c;}));}
$('locate').addEventListener('click',()=>{if(!navigator.geolocation){$('locate').textContent='Location not available';return;}$('locate').textContent='Locating…';
  navigator.geolocation.getCurrentPosition(p=>{here={lat:p.coords.latitude,lon:p.coords.longitude};$('locate').textContent='📍 Location on';drawTechs(techList);},
  ()=>{$('locate').textContent='Location blocked: showing distance from city centre';},{enableHighAccuracy:true,timeout:8000});});
