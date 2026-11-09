import unittest
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    from pipeline import standard_zip, clean_transport, integrate
except ImportError:
    standard_zip = clean_transport = integrate = None

class PipelineTests(unittest.TestCase):
    def test_zip_does_not_extract_digits_from_garbage(self):
        self.assertIsNotNone(standard_zip, 'ZIP validation has not been implemented')
        actual = standard_zip(pd.Series(['10001.0',' 11201 ','11201-1234','abc11201','10000',None,'99999']))
        self.assertEqual(actual.fillna('NA').tolist(), ['10001','11201','11201','NA','NA','NA','NA'])

    def test_transport_preserves_unknown_severity_and_quarantines_conflicts(self):
        self.assertIsNotNone(clean_transport, 'Transport cleaner has not been implemented')
        rows = [dict(open_data_crash_id='1',crash_date='2023-01-02T00:00:00.000',crash_borough=' brooklyn ',zipcode='11201',total_severe_injuries='1',total_fatalities='0',total_non_severe_injuries='0'),
                dict(open_data_crash_id='2',crash_date='2023-01-02T00:00:00.000',crash_borough='Queens',zipcode=None,total_severe_injuries=None,total_fatalities='0',total_non_severe_injuries='-2')]
        rows += [rows[0].copy(),dict(rows[0],total_fatalities='1')]
        clean, excluded, audit = clean_transport(pd.DataFrame(rows))
        self.assertEqual(len(clean),1)
        self.assertEqual(clean.iloc[0]['borough'],'QUEENS')
        self.assertTrue(pd.isna(clean.iloc[0]['severe_or_fatal']))
        self.assertTrue(pd.isna(clean.iloc[0]['total_non_severe_injuries']))
        self.assertEqual(audit['exact_duplicates_removed'],1)
        self.assertEqual(len(excluded),2)

    def test_unknown_construction_type_does_not_become_zero_new_units(self):
        from pipeline import housing_aggregate
        d = pd.DataFrame({'borough':['BRONX'], 'year':[2023], 'project_id':['1'],
                          'building_id':['2'], 'total_units':pd.Series([10],dtype='Int64'),
                          'all_counted_units':pd.Series([8],dtype='Int64'),
                          'construction_type':['UNKNOWN']})
        result = housing_aggregate(d, ['borough','year'])
        self.assertTrue(pd.isna(result.iloc[0]['new_construction_units']))
        self.assertTrue(pd.isna(result.iloc[0]['new_construction_share']))

    def test_join_keeps_unknown_unmatched_and_rejects_multiplication(self):
        self.assertIsNotNone(integrate, 'Integration has not been implemented')
        h=pd.DataFrame({'zip':['10001','10002'],'year':[2023,2023],'counted_units':[10,20],'borough':['MANHATTAN']*2})
        t=pd.DataFrame({'zip':['10001','10003'],'year':[2023,2023],'crash_count':[2,4],'borough':['MANHATTAN']*2})
        result,audit=integrate(h,t)
        self.assertEqual(len(result),3)
        self.assertTrue(pd.isna(result.loc[result['zip'].eq('10002'),'crash_count']).all())
        self.assertEqual(audit['both'],1)
        with self.assertRaises(ValueError): integrate(pd.concat([h,h]),t)

if __name__=='__main__': unittest.main()
