from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
BOROUGHS=['BRONX','BROOKLYN','MANHATTAN','QUEENS','STATEN ISLAND']
YEARS=[2022,2023,2024,2025]

def research(root=ROOT):
 root=Path(root);out=root/'member4/reports';out.mkdir(parents=True,exist_ok=True)
 d=json.loads((root/'website/data/nyc.json').read_text())
 h=pd.DataFrame(d['housing'],columns=['b','year','type','records','known_units','missing'])
 t=pd.DataFrame(d['transport'],columns=['b','year','severity','crashes','severe','fatalities'])
 h=h[h.year.isin(YEARS)].groupby(['b','year'])[['known_units','missing','records']].sum(min_count=1).reset_index()
 t=t[t.year.isin(YEARS)].groupby(['b','year'])[['crashes','severe','fatalities']].sum(min_count=1).reset_index()
 main=h.merge(t,on=['b','year'],validate='one_to_one');main['borough']=main.b.map(dict(enumerate(BOROUGHS)))
 main['housing_share_pct']=main.known_units/main.groupby('year').known_units.transform('sum')*100
 main['crash_share_pct']=main.crashes/main.groupby('year').crashes.transform('sum')*100
 main['gap_pp']=main.crash_share_pct-main.housing_share_pct
 main.to_csv(out/'M4_Q1_yearly_share_gaps.csv',index=False)
 matrix=main.pivot(index='borough',columns='year',values='gap_pp').reindex(BOROUGHS)
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold'})
 fig,ax=plt.subplots(figsize=(9.5,5.4));limit=float(np.abs(matrix.to_numpy()).max())
 from matplotlib.colors import LinearSegmentedColormap
 cmap=LinearSegmentedColormap.from_list('domain_gap',['#147e83','#f7f8f4','#dc795e'])
 im=ax.imshow(matrix.to_numpy(),cmap=cmap,vmin=-limit,vmax=limit,aspect='auto')
 ax.set_xticks(range(4),YEARS);ax.set_yticks(range(5),[b.title() for b in BOROUGHS]);ax.set_title('Do borough housing / serious-crash share gaps persist?',pad=18)
 for i in range(5):
  for j in range(4):ax.text(j,i,f'{matrix.iloc[i,j]:+.1f}',ha='center',va='center',color='white' if abs(matrix.iloc[i,j])>9.5 else '#142c3b',fontsize=12)
 cb=fig.colorbar(im,ax=ax,shrink=.8);cb.set_label('SIRTA share − known housing share (percentage points)')
 fig.text(.05,.02,'2022–2025 | Citywide denominators per year. Two unknown housing records excluded from known subtotals.\nCoral: larger share of SIRTA; teal: larger share of known HPD units. Descriptive distributions, not resident risk.',fontsize=9,color='#586b75')
 fig.tight_layout(rect=[0,.1,1,1]);fig.savefig(out/'M4_Q1_share_gap_heatmap.png',dpi=170,bbox_inches='tight');plt.close(fig)
 hz=pd.DataFrame(d['housingZip'],columns=['b','year','type','zip','records','known_units','missing']).groupby(['b','year','zip'])[['known_units','missing']].sum(min_count=1).reset_index()
 tz=pd.DataFrame(d['transportZip'],columns=['b','year','severity','zip','crashes','severe','fatalities']).groupby(['b','year','zip'])[['crashes']].sum(min_count=1).reset_index()
 pairs=hz.merge(tz,on=['b','year','zip'],validate='one_to_one');pairs=pairs[pairs.missing.eq(0)&pairs.known_units.notna()]
 pairs.to_csv(out/'M4_Q2_complete_matched_zip_years.csv',index=False)
 pooled=pairs.groupby(['b','zip'])[['known_units','crashes']].sum().reset_index();concentration=[]
 for b,g in pooled.groupby('b'):
  hh=float(((g.known_units/g.known_units.sum())**2).sum());th=float(((g.crashes/g.crashes.sum())**2).sum())
  concentration.append({'borough':BOROUGHS[b],'observed_zips':len(g),'housing_hhi':hh,'sirta_hhi':th,'housing_effective_zips':1/hh,'sirta_effective_zips':1/th})
 concentration=pd.DataFrame(concentration);concentration.to_csv(out/'M4_Q2_zip_concentration.csv',index=False)
 fig,ax=plt.subplots(figsize=(10,5.4));x=np.arange(5);w=.36
 for offset,col,label,color in [(-w/2,'housing_effective_zips','Housing counted units','#147e83'),(w/2,'sirta_effective_zips','SIRTA crash records','#dc795e')]:
  bars=ax.bar(x+offset,concentration[col],w,color=color,label=label);ax.bar_label(bars,fmt='%.1f',padding=3,fontsize=10)
 ax.set_xticks(x,[b.title() for b in BOROUGHS]);ax.set_ylabel('Effective ZIP count (1 / HHI)');ax.set_title('Is housing activity more concentrated within matched ZIPs?');ax.set_ylim(0,35);ax.legend(frameon=False)
 fig.text(.06,.02,'2023–2025 | 306 complete matched ZIP-years, pooled within each ZIP. Lower = more concentrated.\nOnly observed common coverage; missing ZIPs, unequal ZIP sizes and source selection limit inference.',fontsize=9,color='#586b75')
 fig.tight_layout(rect=[0,.1,1,1]);fig.savefig(out/'M4_Q2_effective_zips.png',dpi=170,bbox_inches='tight');plt.close(fig)
 assert main.shape[0]==20 and main.known_units.sum()==103912 and main.crashes.sum()==11921
 assert pairs.shape[0]==306 and (concentration.housing_effective_zips<concentration.sirta_effective_zips).all()
 findings={'M4_Q1':{'queens_gap_pp_by_year':main[main.borough.eq('QUEENS')].set_index('year').gap_pp.round(3).to_dict(),'bronx_gap_pp_by_year':main[main.borough.eq('BRONX')].set_index('year').gap_pp.round(3).to_dict()},'M4_Q2':concentration.round(6).to_dict('records'),'scope':{'main_years':YEARS,'main_cells':20,'zip_years':[2023,2024,2025],'complete_zip_years':306,'known_units':int(main.known_units.sum()),'sirta_records':int(main.crashes.sum())}}
 (out/'research_findings.json').write_text(json.dumps(findings,indent=2))
 return main,concentration,findings

if __name__=='__main__':
 _,_,findings=research();print(json.dumps(findings,indent=2))
