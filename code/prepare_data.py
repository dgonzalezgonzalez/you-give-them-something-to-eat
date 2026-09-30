"""Extract documented numeric fields from the corrected, CC BY 4.0 panel."""
from pathlib import Path
import hashlib, json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
archive=ROOT/'data/raw/source.zip'
assert hashlib.md5(archive.read_bytes()).hexdigest()=='35fe28d475e1913e993a8305f19b4625', 'Corrected source archive checksum mismatch'
SRC = ROOT / 'data/raw/source/McIntosh and Zeitlin/3-replication/data'
DEST = ROOT / 'data/input'
DEST.mkdir(parents=True, exist_ok=True)
reader = pd.io.stata.StataReader(SRC/'household_panel.dta', convert_categoricals=False)
labels = reader.variable_labels()
data = reader.read()
fields = ['hhid','round','vid','block','eligible','samp_wgt','sample_panel','attrites',
          'treat_GK','treat_GD_lower','treat_GD_mid','treat_GD_upper','treat_GD_huge',
          'dietarydiversity','consumption','consumption_asinh','foodexpenditure',
          'foodownconsumption','productiveassets_asinh','savingsstock_asinh',
          'borrowingstock_asinh','health_knowledge','sanitation_practices',
          'hhmember','hhfemale','hhage','hh_head_schooling','ubudehe']
fields += [k for k in labels if k.startswith('m9_') and k != 'm9_outside']
fields += [k for k in labels if k.endswith('_R1') and k.split('_R1')[0] in fields]
data = data[fields].copy()
groups = [['cereals'],['tubers'],['vitaveg','leafyveg','otherveg'],
          ['vitaafruits','otherfruits'],['organmeat','fleshmeat'],['eggs'],
          ['fish'],['legumes'],['milk'],['oils'],['sweets'],['spices']]
food_fields = [f'm9_{k}' for g in groups for k in g]
data['diet_source'] = data.dietarydiversity
raw_diet = sum(data[[f'm9_{k}' for k in g]].eq(1).any(axis=1).astype(float) for g in groups)
complete = data[food_fields].isin([0,1]).all(axis=1)
raw_diet[~complete] = float('nan')
assert (raw_diet[complete] == data.loc[complete,'dietarydiversity']).all()
data['dietarydiversity'] = raw_diet
# Replace study identifiers with arbitrary sequential keys. No names, contacts,
# geographic identifiers, dates, free text, or administrative recipient lists.
for k in ['hhid','vid','block']:
    keys = sorted(data[k].dropna().unique())
    data[k] = data[k].map({a:i+1 for i,a in enumerate(keys)})
assert not data.duplicated(['hhid','round']).any()
data.to_csv(DEST/'households.csv',index=False,float_format='%.12g',lineterminator='\n')
costs = pd.read_excel(SRC/'CostsAndCompliance.xlsx')
costs.to_csv(DEST/'costs.csv',index=False,float_format='%.12g',lineterminator='\n')
(DEST/'codebook.json').write_text(json.dumps({**{k:labels[k] for k in fields},
    'dietarydiversity':'Reconstructed 12 food-group score; missing if any component is not binary 0/1',
    'diet_source':'Unmodified source dietarydiversity field, retained for sensitivity'},indent=2),encoding='utf8',newline='\n')
manifest = {'source_doi':'10.5281/zenodo.15881329','license':'CC-BY-4.0',
            'source_archive_md5': '35fe28d475e1913e993a8305f19b4625',
            'source_sha256': hashlib.sha256((ROOT/'data/raw/source.zip').read_bytes()).hexdigest(),
            'rows':len(data),'fields':list(data.columns),
            'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                     [DEST/'households.csv',DEST/'costs.csv',DEST/'codebook.json']}}
(DEST/'provenance.json').write_text(json.dumps(manifest,indent=2),encoding='utf8',newline='\n')
print('Prepared deidentified numeric research extract:',len(data),'rows',len(data.columns),'fields')
