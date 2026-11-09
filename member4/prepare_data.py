from pathlib import Path
import argparse,json,hashlib
import pandas as pd

parser=argparse.ArgumentParser()
parser.add_argument('--member3',type=Path,required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
source=args.member3/'data/processed'
h=pd.read_csv(source/'housing_clean.csv',dtype={'zip':'string','borough':'string'})
t=pd.read_csv(source/'transport_clean.csv',dtype={'zip':'string','borough':'string'})
boroughs=['BRONX','BROOKLYN','MANHATTAN','QUEENS','STATEN ISLAND']
types=['NEW CONSTRUCTION','PRESERVATION']
severities=['FATAL','SEVERE_NONFATAL']
for d in [h,t]:d['year']=pd.to_numeric(d['year']).astype(int)

def value(v):return None if pd.isna(v) else int(v)
def housing(keys):
 rows=[]
 for key,g in h.dropna(subset=keys).groupby(keys):
  key=dict(zip(keys,key));b=key['borough'];y=int(key['year']);c=key['construction_type']
  if b not in boroughs or c not in types or y<2022:continue
  row=[boroughs.index(b),y,types.index(c)]
  if 'zip' in keys:row.append(str(key['zip']))
  rows.append(row+[len(g),value(g['all_counted_units'].sum(min_count=1)),int(g['all_counted_units'].isna().sum())])
 return rows

def transport(keys):
 rows=[]
 for key,g in t.dropna(subset=keys).groupby(keys):
  key=dict(zip(keys,key));b=key['borough'];y=int(key['year']);s=key['severity']
  if b not in boroughs or s not in severities or y<2022:continue
  row=[boroughs.index(b),y,severities.index(s)]
  if 'zip' in keys:row.append(str(key['zip']))
  rows.append(row+[len(g),value(g['total_severe_injuries'].sum(min_count=len(g))),value(g['total_fatalities'].sum(min_count=len(g)))])
 return rows

safe=pd.read_csv(source/'integrated_zip_year.csv',dtype={'zip':'string'})
safe=safe[safe.analysis_eligible.astype(str).str.lower().eq('true')]
allowed=set(zip(safe.borough,safe.year,safe.zip))
hz=[r for r in housing(['borough','year','construction_type','zip']) if (boroughs[r[0]],r[1],r[3]) in allowed]
tz=[r for r in transport(['borough','year','severity','zip']) if (boroughs[r[0]],r[1],r[3]) in allowed]
data={'meta':{'retrieved':'2026-11-09','housingSource':'https://data.cityofnewyork.us/d/hg8x-zxpr','transportSource':'https://data.cityofnewyork.us/d/xeqp-qz8h','primaryYears':[2022,2023,2024,2025],'partialYear':2026,'partialThrough':'June 30','zipYears':[2023,2024,2025],'boroughs':boroughs,'types':types,'severities':severities,'housingSchema':['borough_index','year','type_index','records','known_counted_units','unknown_unit_records'],'transportSchema':['borough_index','year','severity_index','records','severe_injuries','fatalities'],'zipSchemaNote':'ZIP strings inserted at index 3 in secondary rows; same trailing measures. Only documented eligible ZIP-years included.'},'housing':housing(['borough','year','construction_type']),'transport':transport(['borough','year','severity']),'housingZip':hz,'transportZip':tz}
path=root/'website/data/nyc.json';path.write_text(json.dumps(data,separators=(',',':'),allow_nan=False))
manifest={'website_data_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'housing_clean_sha256':hashlib.sha256((source/'housing_clean.csv').read_bytes()).hexdigest(),'transport_clean_sha256':hashlib.sha256((source/'transport_clean.csv').read_bytes()).hexdigest(),'rows':{k:len(data[k]) for k in ['housing','transport','housingZip','transportZip']},'raw_source_manifest':json.loads((args.member3/'data/raw/source_manifest.json').read_text())}
(root/'member4/reports/data_provenance.json').write_text(json.dumps(manifest,indent=2))
print('Prepared app data:',path.stat().st_size,'bytes',manifest['rows'])
