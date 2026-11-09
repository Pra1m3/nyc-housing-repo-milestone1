from pathlib import Path
import json
import numpy as np
import pandas as pd

BOROUGHS = ['BRONX', 'BROOKLYN', 'MANHATTAN', 'QUEENS', 'STATEN ISLAND']
PRIMARY_YEARS = [2022, 2023, 2024, 2025]
ZIP_YEARS = [2023, 2024, 2025]
ROOT = Path(__file__).resolve().parent

def text(s):
    return s.astype('string').str.strip().str.replace(r'\s+', ' ', regex=True).replace('', pd.NA)

def standard_zip(s):
    z = text(s).str.replace(r'\.0+$', '', regex=True)
    z = z.where(z.str.fullmatch(r'\d{5}(-\d{4})?', na=False)).str[:5]
    n = pd.to_numeric(z, errors='coerce')
    return z.where(n.between(10001, 11697))

def borough(s):
    return text(s).str.upper().replace({'RICHMOND': 'STATEN ISLAND'}).where(lambda v: v.isin(BOROUGHS))

def nonnegative_integer(s):
    n = pd.to_numeric(s, errors='coerce')
    return n.where(n.ge(0) & n.mod(1).eq(0)).astype('Int64')

def iqr_flags(s):
    q1, q3 = s.quantile([.25, .75])
    if pd.isna(q1) or pd.isna(q3):
        return pd.Series(False, index=s.index), {'q1': None, 'q3': None}
    low, high = float(q1 - 1.5*(q3-q1)), float(q3 + 1.5*(q3-q1))
    return (s.lt(low) | s.gt(high)).fillna(False), {'lower': low, 'upper': high, 'q1': float(q1), 'q3': float(q3)}

def clean_transport(raw):
    audit = {'input_rows': len(raw), 'input_columns': len(raw.columns)}
    d = raw.drop_duplicates().copy()
    audit['exact_duplicates_removed'] = len(raw)-len(d)
    d['source_row'] = d.index + 2                                   
    for c in d.select_dtypes(include=['object','string']).columns:
        d[c] = text(d[c])
    d['collision_id'] = text(d['open_data_crash_id']).str.replace(r'\.0+$','',regex=True)
    d['crash_date'] = pd.to_datetime(d['crash_date'], errors='coerce')
    d['year'] = d['crash_date'].dt.year.astype('Int64')
    d['borough'] = borough(d['crash_borough'])
    d['zip'] = standard_zip(d['zipcode'])
    audit['invalid_numeric_counts'] = {}
    for c in ['total_non_severe_injuries','total_severe_injuries','total_fatalities']:
        orig = d[c].copy()
        d[c] = nonnegative_integer(d[c])
        audit['invalid_numeric_counts'][c] = int((orig.notna() & d[c].isna()).sum())
                                                                                
    d['severe_or_fatal'] = d['total_severe_injuries'] + d['total_fatalities']
    d['severity'] = pd.Series('UNKNOWN', index=d.index, dtype='string')
    d.loc[d['total_fatalities'].gt(0).fillna(False), 'severity'] = 'FATAL'
    known_nonfatal = d['total_fatalities'].eq(0).fillna(False)
    d.loc[(known_nonfatal & d['total_severe_injuries'].gt(0)).fillna(False),'severity'] = 'SEVERE_NONFATAL'
    d.loc[(known_nonfatal & d['total_severe_injuries'].eq(0)).fillna(False),'severity'] = 'NO_RECORDED_SEVERE_OR_FATAL'
    d['severity_outlier'], audit['severity_iqr'] = iqr_flags(d['severe_or_fatal'])
    for c, low, high in [('latitude',40.4,41.0),('longitude',-74.3,-73.65)]:
        if c in d:
            n = pd.to_numeric(d[c],errors='coerce')
            d[c+'_invalid'] = n.notna() & ~n.between(low,high)
            d[c] = n.where(n.between(low,high))
                                                                                   
    conflict = d['collision_id'].notna() & d['collision_id'].duplicated(keep=False)
    reasons = pd.Series('', index=d.index, dtype='string')
    for mask, label in [(conflict,'conflicting_collision_id;'),(d['crash_date'].isna(),'missing_or_invalid_date;'),
                        (d['year'].notna() & ~d['year'].between(2022,2026),'out_of_scope_year;')]:
        reasons.loc[mask] = reasons.loc[mask] + label
    excluded = d.loc[reasons.ne('')].copy()
    excluded['exclusion_reason'] = reasons[reasons.ne('')]
    d = d.loc[reasons.eq('')].copy()
    audit.update(conflicting_id_rows=int(conflict.sum()), excluded_rows=len(excluded), clean_rows=len(d),
                 missing_borough=int(d['borough'].isna().sum()), missing_zip=int(d['zip'].isna().sum()),
                 missing_collision_id=int(d['collision_id'].isna().sum()), severity_outliers=int(d['severity_outlier'].sum()))
    return d, excluded, audit

def clean_housing(raw):
    audit = {'input_rows': len(raw), 'input_columns': len(raw.columns), 'exact_duplicates_removed': int(raw.duplicated().sum())}
    d = raw.drop_duplicates().copy()
    d['source_row'] = d.index+2
    for c in d.select_dtypes(include=['object','string']).columns:
        d[c] = text(d[c])
    for c in ['project_start_date','project_completion_date','building_completion_date']:
        d[c] = pd.to_datetime(d[c], errors='coerce')
    for c in ['project_id','building_id','bin','bbl']:
        d[c] = text(d[c]).str.replace(r'\.0+$','',regex=True)
    d['borough'] = borough(d['borough'])
    d['zip'] = standard_zip(d['postcode'])
    d['year'] = d['project_start_date'].dt.year.astype('Int64')
    unit_cols = [c for c in d if c.endswith('_units')]
    audit['invalid_numeric_counts'] = {}
    for c in unit_cols:
        orig = d[c].copy(); d[c] = nonnegative_integer(d[c])
        audit['invalid_numeric_counts'][c] = int((orig.notna() & d[c].isna()).sum())
    d['construction_type'] = text(d['reporting_construction_type']).str.upper().fillna('UNKNOWN')
    d['units_outlier'],audit['total_units_iqr'] = iqr_flags(d['total_units'])
    d['counted_exceeds_total'] = (d['all_counted_units'] > d['total_units']).fillna(False)
    d['completion_before_start'] = (d['project_completion_date'] < d['project_start_date']).fillna(False)
                                                                                   
                                                                                   
    business_key = ['project_id','building_id']
    possible_conflict = d[business_key].notna().all(axis=1) & d.duplicated(business_key, keep=False)
    d['repeated_project_building_key'] = possible_conflict
    reasons = pd.Series('', index=d.index,dtype='string')
    for mask,label in [(d['project_start_date'].isna(),'missing_or_invalid_start_date;'),
                        (d['year'].notna() & ~d['year'].between(2014,2026),'out_of_scope_year;'),
                        (possible_conflict,'conflicting_project_building_key;')]:
        reasons.loc[mask] = reasons.loc[mask]+label
    excluded=d.loc[reasons.ne('')].copy();excluded['exclusion_reason']=reasons[reasons.ne('')]
    d=d.loc[reasons.eq('')].copy()
    audit.update(clean_rows=len(d),excluded_rows=len(excluded),missing_zip=int(d['zip'].isna().sum()),
                 missing_borough=int(d['borough'].isna().sum()),unit_outliers=int(d['units_outlier'].sum()),
                 counted_exceeds_total=int(d['counted_exceeds_total'].sum()), completion_before_start=int(d['completion_before_start'].sum()))
    return d, excluded, audit

def strict_sum(s):
    return s.sum(min_count=len(s))

def housing_aggregate(d, keys):
    g = d.dropna(subset=keys).groupby(keys,dropna=False,observed=True)
    out = g.agg(housing_records=('project_id','size'), unique_buildings=('building_id','nunique'),
                total_units=('total_units',strict_sum),counted_units=('all_counted_units',strict_sum),
                missing_counted_unit_records=('all_counted_units',lambda s:int(s.isna().sum())),
                observed_counted_units=('all_counted_units',lambda s:s.sum(min_count=1)))
    new_values = d['all_counted_units'].where(d['construction_type'].eq('NEW CONSTRUCTION'),0)
                                                                                
    new_values = new_values.mask(~d['construction_type'].isin(['NEW CONSTRUCTION','PRESERVATION']))
    new = d.assign(_new=new_values)
    out['new_construction_units'] = new.dropna(subset=keys).groupby(keys,observed=True)['_new'].agg(strict_sum)
    out['new_construction_share'] = out['new_construction_units']/out['counted_units'].replace(0,pd.NA)
    return out.reset_index()

def transport_aggregate(d, keys):
    return d.dropna(subset=keys).groupby(keys,dropna=False,observed=True).agg(
        crash_count=('year','size'), severe_injuries=('total_severe_injuries',strict_sum),
        fatalities=('total_fatalities',strict_sum),severe_or_fatal=('severe_or_fatal',strict_sum),
        known_severity_records=('severe_or_fatal','count'),
        observed_severe_or_fatal=('severe_or_fatal',lambda s:s.sum(min_count=1))).reset_index()

def integrate(h, t, keys=None):
    if keys is None: keys=['zip','year'] if 'zip' in h.columns else ['borough','year']
    for name,d in [('housing',h),('transport',t)]:
        if d[keys].isna().any().any() or d.duplicated(keys).any():
            raise ValueError(f'{name}: null or duplicate join keys')
    h,t=h.copy(),t.copy()
    for d in [h,t]:
        d['year']=pd.to_numeric(d['year'],errors='raise').astype('Int64')
        for k in set(keys)-{'year'}:d[k]=d[k].astype('string')
    if 'borough' not in keys:
        h=h.rename(columns={'borough':'housing_borough'});t=t.rename(columns={'borough':'transport_borough'})
    m=h.merge(t,on=keys,how='outer',validate='one_to_one',indicator=True)
    counts=m['_merge'].value_counts()
    audit={k:int(counts.get(k,0)) for k in ['both','left_only','right_only']}
    m['join_status']=m.pop('_merge').astype('string')
    if 'housing_borough' in m:
        m['borough_mismatch']=(m['housing_borough'].notna() & m['transport_borough'].notna() & m['housing_borough'].ne(m['transport_borough'])).fillna(False)
        m['borough']=m['housing_borough'].combine_first(m['transport_borough'])
        audit['borough_mismatches']=int(m['borough_mismatch'].sum())
        m=m.drop(columns=['housing_borough','transport_borough'])
    m['analysis_eligible']=m['join_status'].eq('both') & m['year'].isin(PRIMARY_YEARS)
    if 'borough_mismatch' in m:m['analysis_eligible'] &= ~m['borough_mismatch']
    if 'severe_or_fatal' in m:
        m['severe_or_fatal_per_crash']=m['severe_or_fatal']/m['crash_count'].replace(0,pd.NA)
                                                                                
    for c in m:
        if c.endswith('_count') or c in ['year','housing_records','unique_buildings','total_units','counted_units','new_construction_units','severe_injuries','fatalities','severe_or_fatal','known_severity_records','missing_counted_unit_records','observed_counted_units','observed_severe_or_fatal']:
            m[c]=pd.to_numeric(m[c],errors='raise').astype('Int64')
    return m.sort_values(keys).reset_index(drop=True),audit

def zip_borough(d):
    pairs=d[['zip','borough']].dropna().drop_duplicates()
    counts=pairs.groupby('zip')['borough'].nunique()
    safe=pairs[pairs['zip'].isin(counts[counts.eq(1)].index)]
    return safe, counts[counts.gt(1)].index.tolist()

def profiles(raw, clean):
    return {'shape_raw':list(raw.shape),'shape_clean':list(clean.shape),
            'raw_missing':{k:int(v) for k,v in raw.isna().sum().items()},
            'clean_dtypes':clean.dtypes.astype(str).to_dict(),
            'numeric_summary':clean.select_dtypes('number').describe().round(3).to_dict()}

def run(root=ROOT):
    root=Path(root)
    for p in ['data/processed','reports','charts']:(root/p).mkdir(parents=True,exist_ok=True)
    hraw=pd.read_csv(root/'data/raw/housing_raw.csv',dtype='string')
    traw=pd.read_csv(root/'data/raw/transport_raw.csv',dtype='string')
    h,hx,ha=clean_housing(hraw);t,tx,ta=clean_transport(traw)
    hb=housing_aggregate(h,['borough','year']);tb=transport_aggregate(t,['borough','year'])
    main,ja=integrate(hb,tb,['borough','year'])
    hz=housing_aggregate(h,['zip','year']);tz=transport_aggregate(t,['zip','year'])
    hm,hamb=zip_borough(h);tm,tamb=zip_borough(t)
    hz=hz.merge(hm,on='zip',how='left',validate='many_to_one');tz=tz.merge(tm,on='zip',how='left',validate='many_to_one')
    z,jz=integrate(hz,tz,['zip','year'])
    z['analysis_eligible'] &= z['year'].isin(ZIP_YEARS) & z['borough'].notna() & ~z['zip'].isin(hamb+tamb)
    ht=housing_aggregate(h,['borough','year','construction_type']);ts=transport_aggregate(t,['borough','year','severity'])
    frames={'housing_clean':h,'transport_clean':t,'housing_quarantine':hx,'transport_quarantine':tx,
            'housing_borough_year':hb,'transport_borough_year':tb,'housing_zip_year':hz,'transport_zip_year':tz,
            'integrated_borough_year':main,'integrated_zip_year':z,'housing_borough_year_type':ht,'transport_borough_year_severity':ts}
    for name,d in frames.items():d.to_csv(root/f'data/processed/{name}.csv',index=False)
                                                                                
    coverage=[]
    for name,d in [('housing',h),('transport',t)]:
        for y,g in d.groupby('year'):
            coverage.append(dict(dataset=name,year=int(y),records=len(g),with_borough=int(g['borough'].notna().sum()),with_zip=int(g['zip'].notna().sum()),zip_coverage_pct=round(g['zip'].notna().mean()*100,2)))
    pd.DataFrame(coverage).to_csv(root/'reports/geographic_coverage.csv',index=False)
    audit={'housing':ha,'transport':ta,'borough_join':ja,'zip_join':jz,'ambiguous_housing_zips':hamb,'ambiguous_transport_zips':tamb,
           'primary_analysis_cells':int(main['analysis_eligible'].sum()),'zip_analysis_cells':int(z['analysis_eligible'].sum()),
           'primary_years':PRIMARY_YEARS,'zip_secondary_years':ZIP_YEARS}
    (root/'reports/cleaning_audit.json').write_text(json.dumps(audit,indent=2,default=str))
    (root/'reports/eda_profiles.json').write_text(json.dumps({'housing':profiles(hraw,h),'transport':profiles(traw,t)},indent=2,default=str))
    for name,d,cols in [('housing',h,['total_units','all_counted_units']),('transport',t,['total_non_severe_injuries','total_severe_injuries','total_fatalities'])]:
        d[cols].describe().to_csv(root/f'reports/{name}_numeric_summary.csv')
    return frames,audit

if __name__=='__main__':
    _, audit=run();print(json.dumps(audit,indent=2,default=str))
