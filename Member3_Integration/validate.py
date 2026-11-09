from pathlib import Path
import hashlib,json
import pandas as pd
from pipeline import run,ROOT,PRIMARY_YEARS

def validate(root=ROOT):
    root=Path(root);frames,audit=run(root)
    for name in ['housing','transport']:
        assert audit[name]['input_columns']>=9
        manifest=json.loads((root/'data/raw/source_manifest.json').read_text())[name]
        path=root/'data/raw'/f'{name}_raw.csv'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['sha256']
        assert audit[name]['input_rows']==manifest['verified_api_row_count']
    h,t=frames['housing_clean'],frames['transport_clean']
    assert len(t)+audit['transport']['excluded_rows']+audit['transport']['exact_duplicates_removed']==audit['transport']['input_rows']
    assert len(h)+audit['housing']['excluded_rows']+audit['housing']['exact_duplicates_removed']==audit['housing']['input_rows']
    for name in ['housing','transport']:
        for geo in ['borough','zip']:
            a=frames[f'{name}_{geo}_year']; keys=[geo,'year']
            assert not a.duplicated(keys).any()
            count='housing_records' if name=='housing' else 'crash_count'
            clean=frames[f'{name}_clean']
            assert a[count].sum()==clean[geo].notna().sum()
    m=frames['integrated_borough_year'];a=m[m['analysis_eligible']]
    assert len(a)==20 and set(a['year'])==set(PRIMARY_YEARS)
    assert not m[['borough','year']].isna().any().any()
    assert not m.duplicated(['borough','year']).any()
    assert m.loc[m['join_status'].eq('left_only'),'crash_count'].isna().all()
    assert not m['year'].eq(2026).where(m['analysis_eligible'],False).any()
    pd.testing.assert_series_equal(frames['housing_borough_year']['counted_units'].reset_index(drop=True),m['counted_units'].reset_index(drop=True),check_names=False)
    assert t['collision_id'].dropna().is_unique
    for name,cols in [('housing_clean',['total_units','all_counted_units']),('transport_clean',['total_severe_injuries','total_fatalities'])]:
        for c in cols: assert frames[name][c].dropna().ge(0).all()
    assert all(c not in m for c in ['borough_x','borough_y','year_x','year_y','_merge'])
    report={'status':'PASS','source_hashes_verified':True,'aggregation_conservation':True,
            'one_to_one_joins':True,'no_join_null_zero_imputation':True,'full_year_analysis_cells':len(a),
            'primary_years':PRIMARY_YEARS,'transport_clean_rows':len(t),'housing_clean_rows':len(h)}
    (root/'reports/validation_results.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return report

if __name__=='__main__':validate()
