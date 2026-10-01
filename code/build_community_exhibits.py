"""Population comparisons and fitted frontier; no new welfare identification."""
from pathlib import Path
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction
import json,re
import pandas as pd

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
report=json.loads((OUT/'community-decision.json').read_text())
data=pd.read_csv(OUT/'community_policy_comparisons.csv')
ancova=pd.read_csv(OUT/'community_ancova.csv')
macro={}
def write_table(name,lines):
    (OUT/'tables'/name).write_text(''.join(lines),encoding='utf8',newline='\n')
def outward(value,rounding):
    f=Fraction(value)
    # Exact rational division at ample precision, followed by directional
    # quantization. A guard below verifies the display against the fraction.
    from decimal import localcontext
    with localcontext() as ctx:
        ctx.prec=100
        number=(Decimal(f.numerator)/Decimal(f.denominator)).quantize(Decimal('.001'),rounding=rounding)
    if rounding==ROUND_FLOOR and Fraction(number)>f:raise ValueError('Lower display rounded inward')
    if rounding==ROUND_CEILING and Fraction(number)<f:raise ValueError('Upper display rounded inward')
    return str(number)

macro['CommunityEligibleShare']=f"{100*report['baseline_eligible_weight_share']:.2f}"
labels={'eligible':'Eligible','ineligible':'Baseline ineligible','baseline_weight_aggregate':'Weighted aggregate'}
lines=['\\begin{tabular}{llrrr}\n\\toprule\nPopulation & Cash comparator & Fitted difference & Block SE & Missing-diet endpoints\\\\\n\\midrule\n']
for population in labels:
    for policy in ['Lower+Large','Upper']:
        row=data[data.cost_convention.eq('cost_eligible')&data.population.eq(population)&data.policy.eq(policy)].iloc[0]
        lines.append(f"{labels[population]} & {'Lower/large' if policy=='Lower+Large' else 'Upper'} & {row.gikuriro_minus_policy_identified:.3f} & {row.exploratory_block_se:.3f} & [{row.estimated_missingness_lower:.3f}, {row.estimated_missingness_upper:.3f}]"+'\\\\\n')
        suffix={'eligible':'Eligible','ineligible':'Ineligible','baseline_weight_aggregate':'Aggregate'}[population]
        macro['Community'+suffix+('LowerLarge' if policy=='Lower+Large' else 'Upper')]=f'{row.gikuriro_minus_policy_identified:.3f}'
lines.append('\\bottomrule\n\\end{tabular}\n');write_table('community_comparisons.tex',lines)

names={'assignment_weighted_ratios':'Assignment-weighted ratios','block_wls':'Block WLS','baseline_ancova':'Baseline ANCOVA'}
lines=['\\begin{tabular}{llrr}\n\\toprule\nEstimator & Cost convention & Upper ends at & Upper/large ends at\\\\\n\\midrule\n']
for frontier in report['fitted_frontiers']:
    segments=frontier['segments']
    if [s['policy'] for s in segments]!=['Upper','Upper+Large','Lower+Large']:raise ValueError('Exhibit layout requires revisiting for changed frontier')
    first=segments[0]['theta_upper'];second=segments[1]['theta_upper']
    lines.append(f"{names[frontier['estimator']]} & {'Per eligible' if frontier['cost_convention']=='cost_eligible' else 'Per population'} & {100*first:.1f} & {100*second:.1f}"+'\\\\\n')
    if frontier['estimator']=='assignment_weighted_ratios' and frontier['cost_convention']=='cost_eligible':
        macro.update(CommunityFirstSwitch=f'{100*first:.1f}',CommunitySecondSwitch=f'{100*second:.1f}')
        tau=Fraction(report['baseline_eligible_weight_share_exact'])
        for key,segment in [('CommunityFirstPriority',segments[0]),('CommunitySecondPriority',segments[1])]:
            theta=Fraction(segment['theta_upper_exact'])
            priority=theta*(1-tau)/((1-theta)*tau)
            macro[key]=f'{float(priority):.1f}'
lines.append('\\bottomrule\n\\end{tabular}\n');write_table('community_frontiers.tex',lines)

cases={'eligible':'Eligible only','baseline_weight_aggregate':'Baseline weighted aggregate','unknown_population_weight':'All weights $[0,1]$'}
lines=['\\begin{tabular}{llcc}\n\\toprule\nCost convention & Population weight & Classical mean box & Quota mean box\\\\\n\\midrule\n']
for cost in ['cost_eligible','cost_population']:
    for population in cases:
        brackets=[]
        for method in ['classical_mean_family','quota_mean_only']:
            row=next(z for z in report['decisions'] if z['cost_convention']==cost and z['population']==population and z['method']==method)
            brackets.append('['+outward(row['exact_regional_lower'],ROUND_FLOOR)+', '+outward(row['exact_proposal_upper'],ROUND_CEILING)+']')
            if method=='quota_mean_only' and cost=='cost_eligible':
                macro['Community'+{'eligible':'Eligible','baseline_weight_aggregate':'Aggregate','unknown_population_weight':'Unknown'}[population]+'QuotaUpper']=outward(row['exact_proposal_upper'],ROUND_CEILING)
        lines.append(('Per eligible' if cost=='cost_eligible' else 'Per population')+' & '+cases[population]+' & '+' & '.join(brackets)+'\\\\\n')
lines.append('\\bottomrule\n\\end{tabular}\n');write_table('community_regional_bounds.tex',lines)
row=ancova[ancova.cost_convention.eq('cost_eligible')&ancova.baseline_control.eq(True)&ancova.eligible.eq(0)&ancova.policy.eq('Lower+Large')].iloc[0]
macro['CommunityIneligibleAncovaHolm']=f'{row.p_holm_64:.3f}'
(ROOT/'paper/community-results.tex').write_text('% Generated by code/build_community_exhibits.py.\n'+''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in macro.items()),encoding='utf8',newline='\n')
(OUT/'community-numbers.json').write_text(json.dumps(macro,indent=2)+'\n',encoding='utf8',newline='\n')

mapping=pd.read_csv(ROOT/'docs/output-map.csv')
files=['output/tables/community_comparisons.tex','output/tables/community_frontiers.tex','output/tables/community_regional_bounds.tex','paper/community-results.tex']
source=Path(__file__).read_text().splitlines();records=[]
for file in files:
    leaf=Path(file).name
    line=next(i for i,text in enumerate(source,1) if leaf in text)
    records.append({'exhibit':'Population analysis auxiliary' if 'tables' in file else 'Population in-text numbers','generated_file':file,'builder':'code/build_community_exhibits.py','builder_line':line,'estimator':'code/community_decision.py','numerical_source':'community-decision.json; community_policy_comparisons.csv; community_ancova.csv'})
mapping=pd.concat([mapping[~mapping.generated_file.isin(files)],pd.DataFrame(records)],ignore_index=True)
text=(ROOT/'paper/paper.tex').read_text(encoding='utf8')
for i,block in enumerate(re.findall(r'\\begin\{table\}.*?\\end\{table\}',text,flags=re.S),1):
    match=re.search(r'output/tables/([^}]+)',block)
    if match:mapping.loc[mapping.generated_file=='output/tables/'+match[1],'exhibit']='Table '+str(i)
mapping.to_csv(ROOT/'docs/output-map.csv',index=False,lineterminator='\n')
print('Generated three population tables and',len(macro),'macros')
