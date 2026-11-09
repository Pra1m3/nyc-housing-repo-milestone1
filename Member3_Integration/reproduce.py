from pipeline import ROOT,run
from charts import make_charts
from validate import validate
if __name__=='__main__':
    frames,audit=run(ROOT)
    make_charts(frames,ROOT)
    validate(ROOT)
    print('Rebuilt local tables, charts, research evidence and validation report.')
