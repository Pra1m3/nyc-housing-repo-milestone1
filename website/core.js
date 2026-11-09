export const BOROUGHS=['BRONX','BROOKLYN','MANHATTAN','QUEENS','STATEN ISLAND'];
export const TYPES=['NEW CONSTRUCTION','PRESERVATION'];
export const SEVERITIES=['FATAL','SEVERE_NONFATAL'];
export const DEFAULTS={borough:'ALL',years:[2022,2023,2024,2025],housingType:'ALL',severity:'ALL'};
const sum=values=>{const known=values.filter(v=>v!==null&&v!==undefined&&Number.isFinite(v));return known.length?known.reduce((a,b)=>a+b,0):null;};
const ratio=(a,b)=>a!==null&&b!==null&&b>0?a/b:null;
export function parseSearch(input){
 let q=input.trim().toLowerCase().replace(/[–—]/g,'-');
 if(!q)throw new Error('Enter a borough, year or category to search.');
 const f={...DEFAULTS,years:[...DEFAULTS.years]};
 const years=[...q.matchAll(/\b(20\d{2})\b/g)].map(m=>Number(m[1]));
 if(years.some(y=>y<2022||y>2026))throw new Error('Available years are 2022–2026; 2026 is partial.');
 const ranges=[...q.matchAll(/\b(202[2-6])\s*(?:-|to)\s*(202[2-6])\b/g)];
 for(const r of ranges){if(+r[1]>+r[2])throw new Error('Put the earlier year first.');for(let y=+r[1];y<=+r[2];y++)years.push(y);}
 if(years.length)f.years=[...new Set(years)].sort();
 q=q.replace(/\b202[2-6]\b/g,' ').replace(/\bto\b|-/g,' ');
 const found=[];
 for(const [pattern,value] of [[/\bstaten\s+island\b|\brichmond\b/g,'STATEN ISLAND'],[/\bbronx\b/g,'BRONX'],[/\bbrooklyn\b|\bkings\b/g,'BROOKLYN'],[/\bmanhattan\b|\bnew\s+york\b/g,'MANHATTAN'],[/\bqueens\b/g,'QUEENS']]){
  if(pattern.test(q)){found.push(value);q=q.replace(pattern,' ');}
 }
 if(found.length>1)throw new Error('Choose one borough, or use all boroughs.');
 if(found.length)f.borough=found[0];
 const newMatch=/\bnew\s+(?:construction|buildings?|housing|developments?)\b/g;
 const preservation=/\bpreservation\b|\bpreserved\b|\bexisting\s+(?:buildings?|housing)\b/g;
 const hasNew=newMatch.test(q),hasPres=preservation.test(q);
 if(hasNew&&hasPres)throw new Error('Choose one housing category or all housing.');
 if(hasNew){f.housingType='NEW CONSTRUCTION';q=q.replace(newMatch,' ');}
 if(hasPres){f.housingType='PRESERVATION';q=q.replace(preservation,' ');}
 const nonfatal=/\bnon[ -]?fatal\b|\bsevere(?:ly)?(?:\s+injur(?:y|ies|ed))?\b/g;
 if(nonfatal.test(q)){f.severity='SEVERE_NONFATAL';q=q.replace(nonfatal,' ');}
 const fatal=/\bfatal(?:ities|ity)?\b|\bfatal\s+crashes?\b/g;
 if(fatal.test(q)){if(f.severity!=='ALL')throw new Error('Choose one crash category or all crashes.');f.severity='FATAL';q=q.replace(fatal,' ');}
 q=q.replace(/\b(?:all|boroughs?|years?|housing|units?|crashes?|crash|records?|show|me|in|and|for|the|with|data|report|investigations?)\b/g,' ').replace(/[,.!?]/g,' ').trim();
 if(q)throw new Error(`Unrecognized search terms: “${q.replace(/\s+/g,' ')}”. Try “Brooklyn 2022 new buildings”.`);
 return f;
}
function aggregate(housing,transport,zip=false){
 const groups=new Map();
 const obtain=(r)=>{const key=zip?`${r[0]}|${r[1]}|${r[3]}`:`${r[0]}|${r[1]}`;if(!groups.has(key))groups.set(key,{borough:BOROUGHS[r[0]],year:r[1],zip:zip?r[3]:undefined,h:[],t:[]});return groups.get(key);};
 for(const r of housing)obtain(r).h.push(r);
 for(const r of transport)obtain(r).t.push(r);
 return [...groups.values()].map(g=>{
  const offset=zip?1:0,hi=4+offset,ki=5+offset,mi=6+offset;
  const hn=3+offset,tn=3+offset,si=4+offset,fi=5+offset;
  const missing=sum(g.h.map(r=>r[mi-1]));
  const known=sum(g.h.map(r=>r[ki-1]));
  const newRows=g.h.filter(r=>r[2]===0);
  const newMissing=sum(newRows.map(r=>r[mi-1]));
  const newKnown=newRows.length?sum(newRows.map(r=>r[ki-1])):(g.h.length?0:null);
  const units=g.h.length&&missing===0?known:null;
  const severe=sum(g.t.map(r=>r[si])),fatalities=sum(g.t.map(r=>r[fi]));
  const crashes=sum(g.t.map(r=>r[tn]));
  return {borough:g.borough,year:g.year,...(zip?{zip:g.zip}:{}),housingRecords:sum(g.h.map(r=>r[hn])),knownUnits:known,missingUnits:missing,units,
   newShare:ratio(newMissing===null||newMissing===0?newKnown:null,units),crashes,severe,fatalities,
   severityPerCrash:ratio(severe===null||fatalities===null?null:severe+fatalities,crashes),matched:!!g.h.length&&!!g.t.length};
 });
}
export function buildReport(data,filters=DEFAULTS){
 const f={...DEFAULTS,...filters};
 const h=r=>f.years.includes(r[1])&&(f.housingType==='ALL'||TYPES[r[2]]===f.housingType);
 const t=r=>f.years.includes(r[1])&&(f.severity==='ALL'||SEVERITIES[r[2]]===f.severity);
 const all=aggregate(data.housing.filter(h),data.transport.filter(t));
 const rows=all.filter(r=>f.borough==='ALL'||r.borough===f.borough).sort((a,b)=>BOROUGHS.indexOf(a.borough)-BOROUGHS.indexOf(b.borough)||a.year-b.year);
 const housingDenominator=sum(all.map(r=>r.knownUnits)),crashDenominator=sum(all.map(r=>r.crashes));
 const shares=BOROUGHS.filter(b=>f.borough==='ALL'||b===f.borough).map(b=>{
  const cells=rows.filter(r=>r.borough===b),knownUnits=sum(cells.map(r=>r.knownUnits)),crashes=sum(cells.map(r=>r.crashes));
  return {borough:b,knownUnits,crashes,housingShare:ratio(knownUnits,housingDenominator),crashShare:ratio(crashes,crashDenominator)};
 }).filter(r=>r.knownUnits!==null||r.crashes!==null);
 const yearTotals=new Map(f.years.map(y=>[y,{housing:sum(all.filter(r=>r.year===y).map(r=>r.knownUnits)),transport:sum(all.filter(r=>r.year===y).map(r=>r.crashes))}]));
 const gaps=rows.map(r=>({...r,housingShare:ratio(r.knownUnits,yearTotals.get(r.year).housing),crashShare:ratio(r.crashes,yearTotals.get(r.year).transport)})).map(r=>({...r,gap:r.housingShare!==null&&r.crashShare!==null?(r.crashShare-r.housingShare)*100:null}));
 const zipPairs=aggregate(data.housingZip.filter(h),data.transportZip.filter(t),true).filter(r=>r.matched&&r.units!==null&&(f.borough==='ALL'||r.borough===f.borough));
 const concentration=[];
 for(const b of BOROUGHS){
  const cells=zipPairs.filter(r=>r.borough===b),byZip=new Map();
  for(const r of cells){if(!byZip.has(r.zip))byZip.set(r.zip,{h:0,t:0});const a=byZip.get(r.zip);a.h+=r.units;a.t+=r.crashes;}
  const hs=[...byZip.values()].map(r=>r.h),ts=[...byZip.values()].map(r=>r.t),hu=sum(hs),tc=sum(ts);
  if(hu>0&&tc>0){const hh=hs.reduce((v,n)=>v+(n/hu)**2,0),th=ts.reduce((v,n)=>v+(n/tc)**2,0);concentration.push({borough:b,zips:byZip.size,housingHHI:hh,transportHHI:th,housingEffectiveZips:1/hh,transportEffectiveZips:1/th,zipYearCells:cells.length});}
 }
 return {filters:f,rows,allRows:all,shares,gaps,zipPairs,concentration,housingDenominator,crashDenominator,
  totals:{housing:sum(rows.map(r=>r.knownUnits)),crashes:sum(rows.map(r=>r.crashes)),missingUnits:sum(rows.map(r=>r.missingUnits)),matchedCells:rows.filter(r=>r.matched).length}};
}
export function toCSV(rows){
 const keys=['borough','year','knownUnits','units','missingUnits','housingRecords','crashes','severe','fatalities','newShare','severityPerCrash','matched'];
 const encode=v=>v===null||v===undefined?'':`"${String(v).replaceAll('"','""')}"`;
 return [keys.join(','),...rows.map(r=>keys.map(k=>encode(r[k])).join(','))].join('\n');
}
