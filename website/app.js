import {BOROUGHS,DEFAULTS,parseSearch,buildReport,toCSV} from './core.js';
import {createReportSession} from './report-session.js';
const $=id=>document.getElementById(id),title=s=>s.toLowerCase().replace(/\b\w/g,c=>c.toUpperCase());
const number=v=>v===null||v===undefined?'Unknown':new Intl.NumberFormat('en-US',{maximumFractionDigits:0}).format(v);
const teal='#147e83',coral='#dc795e',colors=['#147e83','#d67a59','#7c75ae','#487ba3','#9c7942'];
const chartIds=['gap-chart','concentration-chart','share-chart','severity-chart','trend-chart','zip-chart'];
let data,searchMode=false;
const config={responsive:true,displaylogo:false,scrollZoom:true,modeBarButtonsToRemove:['select2d','lasso2d','autoScale2d'],toImageButtonOptions:{format:'png',scale:2}};
const axis={gridcolor:'#edf1f2',zerolinecolor:'#dce5e7',tickfont:{size:9,color:'#617680'},automargin:true};
const layout={font:{family:'DM Sans, Arial, sans-serif',size:10,color:'#405e6a'},paper_bgcolor:'transparent',plot_bgcolor:'transparent',margin:{l:42,r:12,t:15,b:50},xaxis:{...axis},yaxis:{...axis},hoverlabel:{font:{family:'Arial',size:12}},legend:{orientation:'h',x:0,y:-.22,font:{size:10}},colorway:colors};
function empty(id,message){if(window.Plotly)Plotly.purge($(id));$(id).replaceChildren(Object.assign(document.createElement('div'),{className:'empty-chart',textContent:message}));}
async function plot(id,traces,extra={}){if(!traces.length){empty(id,'No comparable observations in this view. Try more years or a broader category.');return;}$(id).querySelector('.empty-chart')?.remove();await Plotly.react($(id),traces,{...layout,...extra},config);}
function rank(values){const sorted=values.map((v,i)=>({v,i})).sort((a,b)=>a.v-b.v),out=[];for(let i=0;i<sorted.length;){let end=i+1;while(end<sorted.length&&sorted[end].v===sorted[i].v)end++;for(let k=i;k<end;k++)out[sorted[k].i]=(i+end-1)/2;i=end;}return out;}
function rho(rows,x,y){if(rows.length<3)return null;const a=rank(rows.map(r=>r[x])),b=rank(rows.map(r=>r[y])),ma=a.reduce((s,v)=>s+v,0)/a.length,mb=b.reduce((s,v)=>s+v,0)/b.length;let n=0,da=0,db=0;for(let i=0;i<a.length;i++){n+=(a[i]-ma)*(b[i]-mb);da+=(a[i]-ma)**2;db+=(b[i]-mb)**2;}return da&&db?n/Math.sqrt(da*db):null;}
function describeScope(f){return `${f.borough==='ALL'?'All boroughs':title(f.borough)} · ${f.years.join(', ')} · ${f.housingType==='ALL'?'all housing':title(f.housingType)} · ${f.severity==='ALL'?'all SIRTA':f.severity==='FATAL'?'fatal crashes':'nonfatal severe crashes'}`;}
async function render(r){
 $('scope').textContent=describeScope(r.filters);$('units-stat').textContent=number(r.totals.housing);$('crashes-stat').textContent=number(r.totals.crashes);$('cells-stat').textContent=number(r.totals.matchedCells);
 $('units-note').textContent=r.totals.missingUnits?`${number(r.totals.missingUnits)} contributing ${r.totals.missingUnits===1?'record has':'records have'} unknown unit counts`:'All contributing counted-unit values are known';
 $('cells-note').textContent=`${r.zipPairs.length} complete matched ZIP-year cells`;
 const notices=[];
 if(r.filters.years.includes(2026))notices.push('2026 is partial, through June 30. Do not compare its raw counts with a full year.');
 if(r.filters.housingType!=='ALL'||r.filters.severity!=='ALL')notices.push('Categories filter each domain independently; these are co-located area totals, not crashes linked to housing buildings.');
 if(!r.rows.length)notices.push('No records match this report. Broaden the filters to compare the two sources.');
 $('notice').hidden=!notices.length;$('notice').textContent=notices.join(' ');
 const tasks=[];
 const years=r.filters.years,boros=BOROUGHS.filter(b=>r.filters.borough==='ALL'||r.filters.borough===b);
 const gapRows=boros.map(b=>years.map(y=>r.gaps.find(v=>v.borough===b&&v.year===y)?.gap??null));
 const maxGap=Math.max(5,...r.gaps.map(v=>Math.abs(v.gap??0)));
 tasks.push(plot('gap-chart',r.gaps.some(v=>v.gap!==null)?[{type:'heatmap',x:years.map(String),y:boros.map(title),z:gapRows,zmin:-maxGap,zmax:maxGap,zmid:0,colorscale:[[0,teal],[.5,'#f7f8f4'],[1,coral]],colorbar:{title:{text:'pp',side:'top'},thickness:8,len:.8,tickfont:{size:9}},text:gapRows.map(row=>row.map(v=>v===null?'':`${v>0?'+':''}${v.toFixed(1)}`)),texttemplate:'%{text}',textfont:{size:11},hoverongaps:false,hovertemplate:'%{y} · %{x}<br>SIRTA − known housing share: %{z:.2f} pp<extra></extra>'}]:[],{xaxis:{...axis,type:'category'},yaxis:{...axis,autorange:'reversed'},margin:{l:80,r:25,t:14,b:30}}));
 $('gap-caption').textContent='Coral = larger share of SIRTA than known housing units; teal = the reverse. Denominators cover all five boroughs within each selected year.';
 const c=r.concentration;
 tasks.push(plot('concentration-chart',c.length?[{type:'bar',name:'Housing',x:c.map(v=>title(v.borough)),y:c.map(v=>v.housingEffectiveZips),marker:{color:teal},customdata:c.map(v=>[v.zips,v.housingHHI]),hovertemplate:'%{x}<br>Effective housing ZIPs: %{y:.2f}<br>Observed ZIPs: %{customdata[0]}<br>HHI: %{customdata[1]:.3f}<extra></extra>'},{type:'bar',name:'SIRTA',x:c.map(v=>title(v.borough)),y:c.map(v=>v.transportEffectiveZips),marker:{color:coral},customdata:c.map(v=>[v.zips,v.transportHHI]),hovertemplate:'%{x}<br>Effective SIRTA ZIPs: %{y:.2f}<br>Observed ZIPs: %{customdata[0]}<br>HHI: %{customdata[1]:.3f}<extra></extra>'}]:[],{barmode:'group',yaxis:{...axis,title:{text:'Effective number of ZIPs',font:{size:9}},rangemode:'tozero'},xaxis:{...axis,tickangle:-20}}));
 $('concentration-caption').textContent=`Uses ${r.zipPairs.length} complete matched ZIP-years from selected years within 2023–2025. Units/crashes are pooled by ZIP; effective count = 1 / sum of squared shares. Missing geography limits coverage.`;
 tasks.push(plot('share-chart',r.shares.length?[{type:'bar',name:'Housing',x:r.shares.map(v=>title(v.borough)),y:r.shares.map(v=>v.housingShare===null?null:v.housingShare*100),marker:{color:teal},hovertemplate:'%{x}<br>Known housing-unit share: %{y:.1f}%<extra></extra>'},{type:'bar',name:'SIRTA',x:r.shares.map(v=>title(v.borough)),y:r.shares.map(v=>v.crashShare===null?null:v.crashShare*100),marker:{color:coral},hovertemplate:'%{x}<br>SIRTA record share: %{y:.1f}%<extra></extra>'}]:[],{barmode:'group',yaxis:{...axis,title:{text:'Share of five-borough total (%)',font:{size:9}},rangemode:'tozero'},xaxis:{...axis,tickangle:-20}}));
 const complete=r.rows.filter(v=>v.newShare!==null&&v.severityPerCrash!==null),severityTraces=[];
 for(const [i,b] of BOROUGHS.entries()){const g=complete.filter(v=>v.borough===b);if(g.length)severityTraces.push({type:'scatter',mode:'markers',name:title(b),x:g.map(v=>v.newShare*100),y:g.map(v=>v.severityPerCrash),marker:{size:g.map(v=>Math.sqrt(v.crashes)*.6+6),color:colors[i],opacity:.85,line:{color:'#fff',width:1}},text:g.map(v=>`${title(b)} · ${v.year}`),customdata:g.map(v=>v.crashes),hovertemplate:'%{text}<br>New-construction share: %{x:.1f}%<br>Affected people per record: %{y:.3f}<br>SIRTA records: %{customdata}<extra></extra>'});}
 tasks.push(plot('severity-chart',severityTraces,{xaxis:{...axis,title:{text:'New-construction share (%)',font:{size:9}},range:[-3,103]},yaxis:{...axis,title:{text:'Severe injuries + fatalities / record',font:{size:9}}},legend:{...layout.legend,font:{size:8}}}));
 const sr=rho(complete,'newShare','severityPerCrash');$('severity-caption').textContent=`${complete.length} complete borough-years; rank correlation ${sr===null?'not defined in this view':sr.toFixed(3)}. People per record can exceed one. Small samples, repeat geography and source selection prevent causal interpretation.`;
 const trendTraces=[],trendLayout={grid:{rows:2,columns:3,pattern:'independent'},margin:{l:35,r:15,t:35,b:55},showlegend:true,legend:{orientation:'h',x:0,y:-.15},annotations:[]};
 for(const [i,b] of boros.entries()){
  const cells=r.rows.filter(v=>v.borough===b).sort((a,b)=>a.year-b.year),suffix=i?String(i+1):'',first=cells.find(v=>v.year===Math.min(...years));
  if(!cells.length)continue;
  for(const [metric,name,color,dash] of [['units','Housing',teal,'solid'],['crashes','SIRTA',coral,'dash']]){
   if(first?.[metric]===null||!first?.[metric])continue;
   trendTraces.push({type:'scatter',mode:'lines+markers',name,xaxis:`x${suffix}`,yaxis:`y${suffix}`,showlegend:i===0,legendgroup:name,x:cells.map(v=>v.year),y:cells.map(v=>v[metric]===null?null:v[metric]/first[metric]*100),line:{color,width:2,dash},marker:{size:5},connectgaps:false,text:cells.map(v=>`${title(b)} · ${v.year}<br>${name}: ${number(v[metric])}`),hovertemplate:'%{text}<br>Index: %{y:.1f}<extra></extra>'});
  }
  trendLayout[`xaxis${suffix}`]={...axis,tickmode:'array',tickvals:years,tickfont:{size:8},showgrid:false};trendLayout[`yaxis${suffix}`]={...axis,tickfont:{size:8}};
  trendLayout.annotations.push({text:title(b),xref:`x${suffix} domain`,yref:`y${suffix} domain`,x:.5,y:1.14,showarrow:false,font:{size:10,color:'#405e6a'}});
 }
 tasks.push(plot('trend-chart',trendTraces,trendLayout));
 const zipTraces=[];
 for(const [i,b] of BOROUGHS.entries()){const g=r.zipPairs.filter(v=>v.borough===b);if(g.length)zipTraces.push({type:'scatter',mode:'markers',name:title(b),x:g.map(v=>v.units+1),y:g.map(v=>v.crashes+1),marker:{size:7,opacity:.65,color:colors[i]},text:g.map(v=>`${v.zip} · ${title(b)} · ${v.year}`),customdata:g.map(v=>[v.units,v.crashes]),hovertemplate:'%{text}<br>Counted units: %{customdata[0]}<br>SIRTA records: %{customdata[1]}<extra></extra>'});}
 tasks.push(plot('zip-chart',zipTraces,{xaxis:{...axis,type:'log',title:{text:'Counted units + 1 (log scale)',font:{size:10}}},yaxis:{...axis,type:'log',title:{text:'SIRTA records + 1 (log scale)',font:{size:10}}},legend:{...layout.legend,y:-.24}}));
 const zr=rho(r.zipPairs,'units','crashes');$('zip-caption').textContent=`${r.zipPairs.length} complete matched ZIP-years; pooled rank correlation ${zr===null?'not defined in this view':zr.toFixed(3)}. ZIPs missing from either source are not zero-activity areas. Repeated ZIPs and unmeasured exposure limit interpretation.`;
 const valid=r.shares.filter(v=>v.housingShare!==null&&v.crashShare!==null),biggest=valid.sort((a,b)=>Math.abs(b.crashShare-b.housingShare)-Math.abs(a.crashShare-a.housingShare))[0];
 $('finding').textContent=biggest?`${title(biggest.borough)} has ${(biggest.housingShare*100).toFixed(1)}% of known housing units and ${(biggest.crashShare*100).toFixed(1)}% of SIRTA records in the selected five-borough comparison. A difference in where activity is recorded is a starting point for inquiry, not a measure of residents’ crash risk.`:'This view has insufficient observations to compare both domains. Broaden the selected categories or years.';
 const body=$('data-body');body.replaceChildren();
 for(const row of r.rows){const tr=document.createElement('tr');for(const val of [title(row.borough),row.year,number(row.knownUnits),number(row.units),number(row.missingUnits),number(row.crashes),row.matched?'Both sources':'One source only']){const td=document.createElement('td');td.textContent=val;if(val==='Unknown')td.className='unknown';tr.append(td);}body.append(tr);}
 $('table-count').textContent=`${r.rows.length} borough-year rows`;
 const results=await Promise.allSettled(tasks);const failed=results.find(v=>v.status==='rejected');if(failed)throw failed.reason;

}
function dropdowns(){return {borough:$('borough').value,years:$('year').value.split(',').map(Number),housingType:$('housing-type').value,severity:$('severity').value};}
const session=createReportSession(filters=>buildReport(data,filters),render,state=>{
 for(const control of $('filters').querySelectorAll('button,select,textarea'))control.disabled=state.busy;
 $('download').disabled=state.busy||!state.report?.rows.length;
 $('print').disabled=state.busy||!state.report;
 $('generate').firstChild.textContent=state.busy?'Generating… ':'Generate Report ';
});
async function generate(filters){
 if(session.busy)return;
 $('error').hidden=true;$('status').textContent='Generating all report charts.';
 try{await session.generate(filters);$('pending').textContent='Report is up to date.';$('status').textContent=`Report generated. ${session.report.rows.length} borough-year rows. All six charts updated.`;}
 catch(e){
  $('error').hidden=false;$('error').textContent='The report could not be generated. '+e.message;$('status').textContent='Report generation failed.';
  $('scope').textContent='Report unavailable';for(const id of ['units-stat','crashes-stat','cells-stat'])$(id).textContent='—';
  $('data-body').replaceChildren();$('table-count').textContent='No active report';$('finding').textContent='Generate a report to view the findings.';
  for(const id of chartIds)empty(id,'Report rendering failed. Try Generate Report again.');
 }
}
$('filters').addEventListener('submit',async e=>{e.preventDefault();if(!data)return;try{const filters=searchMode?parseSearch($('query').value):dropdowns();await generate(filters);}catch(error){$('error').textContent=error.message;$('error').hidden=false;$('status').textContent=error.message;}});
function mode(search){searchMode=search;$('dropdown-fields').hidden=search;$('search-fields').hidden=!search;$('search-mode').classList.toggle('selected',search);$('filter-mode').classList.toggle('selected',!search);$('search-mode').setAttribute('aria-pressed',String(search));$('filter-mode').setAttribute('aria-pressed',String(!search));$('error').hidden=true;$('pending').textContent='Generate Report applies the current mode.';}
$('search-mode').addEventListener('click',()=>mode(true));$('filter-mode').addEventListener('click',()=>mode(false));
$('example').addEventListener('click',()=>{$('query').value='Queens 2023–2025';$('query').focus();$('pending').textContent='Search ready. Select Generate Report to apply.';});
$('reset-report').addEventListener('click',async()=>{$('filters').reset();mode(false);await generate({...DEFAULTS,years:[...DEFAULTS.years]});});
$('filters').addEventListener('input',()=>{$('pending').textContent='Changes pending. Select Generate Report.';$('error').hidden=true;});
$('download').addEventListener('click',()=>{const active=session.report;if(!active)return;const csv=toCSV(active.rows),url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download=`cityscope-${active.filters.borough.toLowerCase().replaceAll(' ','-')}-${active.filters.years.join('-')}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
$('print').addEventListener('click',()=>window.print());
window.addEventListener('beforeprint',()=>{for(const id of chartIds)if($(id).data)Plotly.Plots.resize($(id));});
try{
 const response=await fetch('./data/nyc.json');if(!response.ok)throw new Error(`Data request returned ${response.status}`);data=await response.json();
 if(!window.Plotly){await new Promise((resolve,reject)=>{let tries=0;const timer=setInterval(()=>{if(window.Plotly){clearInterval(timer);resolve();}else if(++tries>80){clearInterval(timer);reject(new Error('Chart library could not load. Check your connection and reload.'));}},100);});}
 await generate({...DEFAULTS,years:[...DEFAULTS.years]});
}catch(error){$('error').hidden=false;$('error').textContent=error.message;$('status').textContent='Unable to load report.';$('scope').textContent='Report unavailable';for(const id of chartIds)empty(id,'Unable to load charts. Check your connection and reload this page.');}
