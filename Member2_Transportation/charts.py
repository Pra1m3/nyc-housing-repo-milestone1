from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pipeline import BOROUGHS, PRIMARY_YEARS

COLORS=['#166c87','#e79742','#7460a6','#458860','#bc5667']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.titleweight':'bold','figure.facecolor':'white','axes.facecolor':'#fafbfc','savefig.facecolor':'white'})

def finish(fig,path):
    fig.savefig(path,dpi=170,bbox_inches='tight');plt.close(fig)

def make_charts(frames, root):
    root=Path(root); (root/'charts').mkdir(exist_ok=True); (root/'reports').mkdir(exist_ok=True)
    m=frames['integrated_borough_year'];m=m.loc[m['analysis_eligible']].copy()
    z=frames['integrated_zip_year'];z=z.loc[z['analysis_eligible']].copy()
    summary={}
                                                                            
    shares=m.groupby('borough')[['observed_counted_units','crash_count','missing_counted_unit_records']].sum(min_count=1).reindex(BOROUGHS)
    shares=shares.rename(columns={'observed_counted_units':'known_counted_units'})
    shares['housing_share_pct']=100*shares['known_counted_units']/shares['known_counted_units'].sum()
    shares['crash_share_pct']=100*shares['crash_count']/shares['crash_count'].sum()
    shares['share_gap_pp']=shares['crash_share_pct']-shares['housing_share_pct']
    shares.to_csv(root/'reports/M2_Q1_borough_shares.csv')
    fig,ax=plt.subplots(figsize=(10,5.3));x=np.arange(5);w=.35
    for offset,col,label,color in [(-w/2,'housing_share_pct','Known HPD counted units','#166c87'),(w/2,'crash_share_pct','SIRTA crash records','#e79742')]:
        bars=ax.bar(x+offset,shares[col].astype(float),w,label=label,color=color)
        ax.bar_label(bars,fmt='%.1f%%',fontsize=9,padding=3)
    ax.set(xticks=x,xticklabels=[b.title() for b in BOROUGHS],ylabel='Share of the five-borough total (%)',ylim=(0,50),title='Where housing activity and investigated crashes concentrate')
    ax.legend(frameon=False,loc='upper right');ax.text(0,-.19,'2022–2025 | Known unit counts only (2 records unknown). Project start year vs. crash year; SIRTA is not all crashes.',transform=ax.transAxes,fontsize=9,color='#555')
    fig.tight_layout();finish(fig,root/'charts/M2_Q1_borough_shares.png')
    biggest=shares['share_gap_pp'].abs().idxmax()
    summary['M2_Q1']={'largest_absolute_gap_borough':biggest,'crash_minus_housing_share_pp':round(float(shares.loc[biggest,'share_gap_pp']),2)}
                                                                          
    a=m.dropna(subset=['new_construction_share','severe_or_fatal_per_crash']).copy()
    a[['borough','year','new_construction_share','severe_or_fatal_per_crash','crash_count']].to_csv(root/'reports/M2_Q2_composition.csv',index=False)
    fig,ax=plt.subplots(figsize=(10,5.8))
    for b,color in zip(BOROUGHS,COLORS):
        g=a[a['borough'].eq(b)]
        ax.scatter(g['new_construction_share'].astype(float)*100,g['severe_or_fatal_per_crash'].astype(float),s=g['crash_count'].astype(float)/7+25,color=color,label=b.title(),alpha=.85,edgecolor='white')
        for _,r in g.iterrows():
            offset=(4,4)
            if b=='BRONX' and int(r['year'])==2022: offset=(4,12)
            if b=='BRONX' and int(r['year'])==2025: offset=(4,-9)
            if b=='MANHATTAN' and int(r['year'])==2025: offset=(-10,-12)
            ax.annotate(str(r['year']), (float(r['new_construction_share'])*100,float(r['severe_or_fatal_per_crash'])),xytext=offset,textcoords='offset points',fontsize=7)
    rho=a['new_construction_share'].rank().corr(a['severe_or_fatal_per_crash'].rank())
    ax.set(xlabel='New-construction share of HPD counted units (%)',ylabel='Recorded severe injuries + fatalities per SIRTA record',title='Does housing composition align with recorded crash severity?')
    ax.legend(frameon=False,loc='upper left',bbox_to_anchor=(1,1));ax.text(0,-.22,f'2022–2025 | n = {len(a)} borough-years | Spearman ρ = {rho:.2f} | Bubble area reflects crash count.\nDescriptive association; this is not a population risk measure or a causal estimate.',transform=ax.transAxes,fontsize=9,color='#555')
    fig.tight_layout();finish(fig,root/'charts/M2_Q2_composition_severity.png')
    summary['M2_Q2']={'n_borough_years':len(a),'spearman_rho':round(float(rho),3)}
                                                                                
    fig,axes=plt.subplots(2,3,figsize=(12,7),sharex=True);indexed=[]
    for ax,b in zip(axes.flat,BOROUGHS):
        g=m[m['borough'].eq(b)].sort_values('year').copy()
        base=g.loc[g['year'].eq(2022)]
        for c,label,color in [('counted_units','HPD counted units','#166c87'),('crash_count','SIRTA records','#e79742')]:
            if base.empty or pd.isna(base.iloc[0][c]) or base.iloc[0][c]==0: continue
            vals=100*g[c].astype(float)/float(base.iloc[0][c]);ax.plot(g['year'].astype(int),vals,'o-',label=label,color=color)
            for y,v in zip(g['year'],vals):indexed.append({'borough':b,'year':int(y),'metric':c,'index_2022_100':v})
        ax.axhline(100,color='#aaa',lw=.7,ls='--');ax.set_title(b.title(),fontsize=11);ax.set_xticks(PRIMARY_YEARS);ax.grid(axis='y',alpha=.2)
    axes.flat[-1].axis('off');handles,labels=axes.flat[0].get_legend_handles_labels();axes.flat[-1].legend(handles,labels,frameon=False,loc='center')
    fig.suptitle('Do housing activity and investigated crashes move together?',fontsize=15,weight='bold')
    fig.supylabel('Index (2022 = 100)');fig.text(.07,.015,'2022–2025 | Project start year versus crash year. Gaps = unknown housing totals. SIRTA reporting may change.',fontsize=9,color='#555')
    fig.tight_layout(rect=[.02,.05,1,.95]);finish(fig,root/'charts/M3_Q1_indexed_trends.png')
    idx=pd.DataFrame(indexed);idx.to_csv(root/'reports/M3_Q1_indexed_trends.csv',index=False)
    latest=m[m['year'].eq(2025)].set_index('borough');base=m[m['year'].eq(2022)].set_index('borough')
    change=((latest[['counted_units','crash_count']]/base[['counted_units','crash_count']])-1)*100
    change.to_csv(root/'reports/M3_Q1_change_2022_2025.csv');summary['M3_Q1']=change.round(2).to_dict('index')
                                                                                
    a=z.dropna(subset=['counted_units','crash_count']).copy()
    fig,ax=plt.subplots(figsize=(10,5.8));correlations=[]
    for b,color in zip(BOROUGHS,COLORS):
        g=a[a['borough'].eq(b)]
        ax.scatter(g['counted_units'].astype(float)+1,g['crash_count'].astype(float)+1,label=f'{b.title()} (n={len(g)})',s=25,alpha=.65,color=color)
        corr=g['counted_units'].rank().corr(g['crash_count'].rank()) if len(g)>2 else np.nan
        correlations.append({'borough':b,'n_zip_years':len(g),'spearman_rho':corr})
    rho=a['counted_units'].rank().corr(a['crash_count'].rank())
    ax.set(xscale='log',yscale='log',xlabel='HPD counted units + 1 (log scale)',ylabel='SIRTA crash records + 1 (log scale)',title='Do higher housing counts coincide with more investigated crashes?')
    ax.legend(frameon=False,loc='upper left',bbox_to_anchor=(1,1));ax.text(0,-.22,f'2023–2025 matched ZIP-years only | n = {len(a)} | Pooled Spearman ρ = {rho:.2f}\nZIP missingness and repeated ZIPs/years limit interpretation; counts are not exposure-adjusted.',transform=ax.transAxes,fontsize=9,color='#555')
    fig.tight_layout();finish(fig,root/'charts/M3_Q2_zip_association.png')
    pd.DataFrame(correlations).to_csv(root/'reports/M3_Q2_within_borough_correlations.csv',index=False)
    a[['zip','borough','year','counted_units','crash_count']].to_csv(root/'reports/M3_Q2_matched_zip_years.csv',index=False)
    summary['M3_Q2']={'n_matched_zip_years':len(a),'pooled_spearman_rho':round(float(rho),3),'borough_correlations':correlations}
    (root/'reports/research_findings.json').write_text(json.dumps(summary,indent=2,default=str))
                                                                                 
    coverage=pd.read_csv(root/'reports/geographic_coverage.csv');fig,axes=plt.subplots(1,2,figsize=(10,4))
    for ax,name in zip(axes,['housing','transport']):
        g=coverage[(coverage['dataset'].eq(name)) & coverage['year'].ge(2022)]
        ax.bar(g['year'].astype(str),g['zip_coverage_pct'],color='#166c87');ax.set(ylim=(0,110),title=name.title(),ylabel='Records with usable ZIP (%)')
        for i,v in enumerate(g['zip_coverage_pct']):ax.text(i,v+2,f'{v:.0f}%',ha='center',fontsize=9)
    fig.suptitle('ZIP completeness explains the primary borough-level join',weight='bold');fig.tight_layout();finish(fig,root/'charts/EDA_zip_completeness.png')
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for ax,name,col,label in [(axes[0],'housing_clean','total_units','Housing: total units per record'),(axes[1],'transport_clean','severe_or_fatal','SIRTA: severe injuries + fatalities')]:
        v=frames[name][col].dropna().astype(float);ax.hist(v,bins=40,color='#166c87');ax.set(title=label,xlabel='Recorded count',ylabel='Records (log scale)',yscale='log')
    fig.suptitle('Heavy tails: flag unusual values and retain valid events',weight='bold');fig.tight_layout();finish(fig,root/'charts/EDA_numeric_distributions.png')
    return summary

if __name__=='__main__':
    from pipeline import run,ROOT
    frames,_=run();print(json.dumps(make_charts(frames,ROOT),indent=2,default=str))
