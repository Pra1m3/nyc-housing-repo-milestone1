from pathlib import Path
import json,hashlib,urllib.request
from concurrent.futures import ThreadPoolExecutor
root=Path(__file__).resolve().parents[1]
origin='https://cityscope-nyc-housing.vercel.app'
paths=sorted(p for p in (root/'website/dist').rglob('*') if p.is_file())
def verify(p):
 rel=p.relative_to(root/'website/dist').as_posix()
 with urllib.request.urlopen(origin+'/'+rel,timeout=45) as response:
  body=response.read();status=response.status
 assert body==p.read_bytes(),rel
 assert not any(s.encode() in body for s in ['16002100','16007095','16008995','16003895']),rel
 return {'path':rel,'status':status,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}
with ThreadPoolExecutor(max_workers=4) as executor:results=list(executor.map(verify,paths))
report={'url':origin+'/','deployment_id':'dpl_9yMyhSmNZeL9EufyWA9RKdKj2sUL','project_id':'prj_V2EnLP9vDrjAm4WBDCyVDkwHSiO6','state':'READY','environment':'production','hosting':'Vercel','deployment_source':'local static assets, no Git commit or push','base_commit_unchanged':'f2260896a4bd37dadb5f28046de97d77708146e8','public_without_auth':True,'assets':results,'student_ids_in_deployed_assets':False}
(root/'member4/reports/deployment.json').write_text(json.dumps(report,indent=2))
print('Public deployment verified:',len(results),'assets match local SHA-256; no student IDs deployed.')
