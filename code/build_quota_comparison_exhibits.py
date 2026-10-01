"""Generate the method comparison appendix from actual benchmark outputs."""
from pathlib import Path
from decimal import Decimal,localcontext,ROUND_CEILING,ROUND_FLOOR
import json,re,pandas as pd
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
report=json.loads((OUT/'quota-benchmarks.json').read_text());rows=report['rows']

def upward(x):
    with localcontext() as ctx:
        ctx.prec=80;ctx.rounding=ROUND_CEILING
        return str(Decimal.from_float(x).quantize(Decimal('.001')))
def six_digits(x,rounding):
    with localcontext() as ctx:
        ctx.prec=80;ctx.rounding=rounding
        return str(Decimal.from_float(x).quantize(Decimal('.000001')))

labels={('quota','shared',True):'Quota, shared event',('quota','separate',True):'Quota, individual tests',
        ('quota','shared',False):'Quota, shared, no bin floors',('hoeffding_baseline_optimized','shared',True):'Hoeffding, shared',
        ('serfling_baseline_optimized','shared',True):'Serfling, shared',('harmonic_martingale_baseline_optimized','shared',True):'Harmonic martingale, shared',
        ('weight_sensitive_product_baseline_optimized','shared',True):'Weight-sensitive product, shared',
        ('weight_sensitive_hybrid_baseline_optimized','shared',True):'Product/harmonic hybrid, shared',
        ('empirical_bernstein_fixed_forecast','shared',True):'Empirical Bernstein, fixed forecast'}
brackets=json.loads((OUT/'regional-minimax-brackets.json').read_text())['rows']
def downward(x):
    with localcontext() as ctx:
        ctx.prec=80;ctx.rounding=ROUND_FLOOR
        return str(Decimal.from_float(x).quantize(Decimal('.001')))
table=['\\begin{tabular}{lrrrr}\n\\toprule\n & \\multicolumn{2}{c}{Mean loss} & \\multicolumn{2}{c}{Shortfall loss}\\\\\nMoment/event & Lower & Upper & Lower & Upper\\\\\n\\midrule\n']
values={}
for key,label in labels.items():
    rr={x['objective']:x['fixed_proposal_loss_upper'] for x in rows if (x['moment_method'],x['event'],x['bin_floors'])==key}
    low={x['objective']:x['regional_minimax_lower'] for x in brackets if (x['method'],x['bin_floors'])==(key[0],key[2])} if key[1]=='shared' else {}
    table.append(label+' & '+(downward(low['mean']) if low else '--')+' & '+upward(rr['mean'])+' & '+(downward(low['shortfall_6']) if low else '--')+' & '+upward(rr['shortfall_6'])+'\\\\\n');values[key]=rr
table.append('\\bottomrule\n\\end{tabular}\n')
(OUT/'tables/quota_method_comparison.tex').write_text(''.join(table),encoding='utf8',newline='\n')
design=json.loads((OUT/'quota-design-benchmarks.json').read_text())['rows']
table=['\\begin{tabular}{rlrrr}\n\\toprule\nQuota & Weights & Quota radius & Hybrid radius & Reduction (\\%)\\\\\n\\midrule\n']
for row in design:
    if row['n']!=12:continue
    table.append(f"{row['k']} & {row['weight_shape'].capitalize()} & {row['quota_common_search_radius']:.3f} & {row['weight_sensitive_hybrid_common_search_radius']:.3f} & {100*(1-row['quota_over_hybrid_common_search']):.2f}"+'\\\\\n')
table.append('\\bottomrule\n\\end{tabular}\n')
(OUT/'tables/quota_design_comparison.tex').write_text(''.join(table),encoding='utf8',newline='\n')
macro={'ClassicalMeanCertificate':upward(values[('harmonic_martingale_baseline_optimized','shared',True)]['mean']),
       'ClassicalShortfallCertificate':upward(values[('harmonic_martingale_baseline_optimized','shared',True)]['shortfall_6']),
       'SeparateQuotaMeanCertificate':upward(values[('quota','separate',True)]['mean']),
       'SeparateQuotaShortfallCertificate':upward(values[('quota','separate',True)]['shortfall_6'])}
macro.update({'HybridMeanCertificate':upward(values[('weight_sensitive_hybrid_baseline_optimized','shared',True)]['mean']),
              'HybridShortfallCertificate':upward(values[('weight_sensitive_hybrid_baseline_optimized','shared',True)]['shortfall_6']),
              'EmpBernMeanCertificate':upward(values[('empirical_bernstein_fixed_forecast','shared',True)]['mean']),
              'EmpBernShortfallCertificate':upward(values[('empirical_bernstein_fixed_forecast','shared',True)]['shortfall_6'])})
for objective,prefix in [('mean','Mean'),('shortfall_6','Shortfall')]:
    row=next(x for x in brackets if x['method']=='quota' and x['bin_floors'] and x['objective']==objective)
    macro.update({'QuotaRegional'+prefix+'Lower':six_digits(row['regional_minimax_lower'],ROUND_FLOOR),
                  'QuotaRegional'+prefix+'Upper':six_digits(row['fixed_proposal_loss_upper'],ROUND_CEILING),
                  'QuotaRegional'+prefix+'Gap':six_digits(row['certified_upper_minus_lower'],ROUND_CEILING)})
decisions=json.loads((OUT/'designed-decisions.json').read_text());df=pd.DataFrame(decisions['rows'])
for method,label in [('empirical_best_midpoint','Empirical'),('quota','Quota'),('empirical_bernstein_fixed_forecast','EB')]:
    frame=pd.DataFrame(decisions['benchmark_rows']) if method=='empirical_best_midpoint' else df
    subset=frame[(frame.reporting=='complete')&(frame.method==method)]
    macro['Benchmark'+label+'CompleteRegret']=f'{subset.mean_actual_regret.mean():.4f}'
    for effect,sign in [(-160,'Negative'),(160,'Positive')]:
        subset=frame[(frame.reporting=='assignment_dependent')&(frame.method==method)&(frame.effect_thousandths==effect)]
        macro['Benchmark'+label+'Selected'+sign+'Regret']=f'{subset.mean_actual_regret.mean():.4f}'
(ROOT/'paper/quota-comparison-results.tex').write_text('% Generated by code/build_quota_comparison_exhibits.py.\n'+''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in macro.items()),encoding='utf8',newline='\n')
(OUT/'quota-comparison-numbers.json').write_text(json.dumps(macro,indent=2)+'\n',encoding='utf8')
mapping=pd.read_csv(ROOT/'docs/output-map.csv');records=[]
builder_lines=(ROOT/'code/build_quota_comparison_exhibits.py').read_text(encoding='utf8').splitlines()
for name,leaf in [('Existing-method comparison','quota_method_comparison'),('Representative quota designs','quota_design_comparison')]:
    records.append({'exhibit':name,'generated_file':'output/tables/'+leaf+'.tex','builder':'code/build_quota_comparison_exhibits.py',
                    'builder_line':next(i for i,line in enumerate(builder_lines,1) if "(OUT/'tables/"+leaf+".tex')" in line),
                    'estimator':'code/quota_benchmarks.py' if leaf=='quota_method_comparison' else 'code/benchmark_quota_designs.py',
                    'numerical_source':'quota-benchmarks.json' if leaf=='quota_method_comparison' else 'quota-design-benchmarks.json'})
records.append({'exhibit':'Quota comparison in-text numbers','generated_file':'paper/quota-comparison-results.tex','builder':'code/build_quota_comparison_exhibits.py',
                'builder_line':next(i for i,line in enumerate(builder_lines,1) if "(ROOT/'paper/quota-comparison-results.tex')" in line),
                'estimator':'code/quota_benchmarks.py','numerical_source':'quota-comparison-numbers.json'})
new=pd.DataFrame(records)
mapping=pd.concat([mapping[~mapping.generated_file.isin(new.generated_file)],new],ignore_index=True)
text=(ROOT/'paper/paper.tex').read_text(encoding='utf8')
for i,block in enumerate(re.findall(r'\\begin\{table\}.*?\\end\{table\}',text,flags=re.S),1):
    match=re.search(r'output/tables/([^}]+)',block)
    if match:mapping.loc[mapping.generated_file=='output/tables/'+match[1],'exhibit']='Table '+str(i)
mapping.to_csv(ROOT/'docs/output-map.csv',index=False,lineterminator='\n')
decisions=json.loads((OUT/'designed-decisions.json').read_text());df=pd.DataFrame(decisions['rows'])
method_labels={'quota':'Quota','harmonic_martingale':'Harmonic','weight_sensitive_product':'Product',
               'weight_sensitive_hybrid':'Hybrid','empirical_bernstein_fixed_forecast':'Empirical Bernstein'}
table=['\\begin{tabular}{llrrr}\n\\toprule\nReporting & Method & Actual regret & Certificate & At most 0.10 (\\%)\\\\\n\\midrule\n']
for reporting,label in [('complete','Complete'),('coarse_interval','Coarse interval'),('assignment_dependent','Assignment-dependent')]:
    for method in decisions['methods']:
        subset=df[(df.reporting==reporting)&(df.method==method)]
        table.append(f"{label} & {method_labels[method]} & {subset.mean_actual_regret.mean():.3f} & {subset.mean_certified_loss_upper.mean():.3f} & {100*subset.certificates_at_most_010.sum()/subset.repetitions.sum():.1f}"+'\\\\\n')
table.append('\\bottomrule\n\\end{tabular}\n')
(OUT/'tables/designed_decision_performance.tex').write_text(''.join(table),encoding='utf8',newline='\n')
mapping=pd.read_csv(ROOT/'docs/output-map.csv');leaf='output/tables/designed_decision_performance.tex'
line=next(i for i,source_line in enumerate(Path(__file__).read_text(encoding='utf8').splitlines(),1) if "(OUT/'tables/designed_decision_performance.tex')" in source_line)
record={'exhibit':'Designed decision performance','generated_file':leaf,'builder':'code/build_quota_comparison_exhibits.py','builder_line':line,'estimator':'code/designed_decisions.py','numerical_source':'designed-decisions.json'}
for number,block in enumerate(re.findall(r'\\begin\{table\}.*?\\end\{table\}',text,flags=re.S),1):
    if leaf in block:record['exhibit']='Table '+str(number)
mapping=pd.concat([mapping[mapping.generated_file!=leaf],pd.DataFrame([record])],ignore_index=True)
mapping.to_csv(ROOT/'docs/output-map.csv',index=False,lineterminator='\n')
summaries=[];pair_summaries=[]
all_methods=pd.concat([df,pd.DataFrame(decisions['benchmark_rows'])],ignore_index=True)
for (reporting,effect,method),subset in all_methods.groupby(['reporting','effect_thousandths','method'],sort=True):
    summaries.append({'reporting':reporting,'effect_thousandths':effect,'method':method,'cells':len(subset),
                      'mean_actual_regret':subset.mean_actual_regret.mean(),
                      'mc_standard_error':float((subset.mc_standard_error.pow(2).sum())**.5/len(subset))})
for (reporting,effect,first,second),subset in pd.DataFrame(decisions['paired_rows']).groupby(['reporting','effect_thousandths','first_method','second_method'],sort=True):
    pair_summaries.append({'reporting':reporting,'effect_thousandths':effect,'first_method':first,'second_method':second,'cells':len(subset),
                          'mean_regret_difference':subset.mean_regret_difference.mean(),
                          'paired_mc_standard_error':float(subset.paired_mc_standard_error.pow(2).sum()**.5/len(subset))})
summary=pd.DataFrame(summaries);paired=pd.DataFrame(pair_summaries)
summary.to_csv(OUT/'designed_decision_effect_summary.csv',index=False)
paired.to_csv(OUT/'designed_decision_effect_pairs.csv',index=False)
table=['\\begin{tabular}{lrrrrrr}\n\\toprule\nReporting & Effect & Quota & EB & Empirical & Half & Quota$-$EB\\\\\n & & & & best & & (paired MC SE)\\\\\n\\midrule\n']
for reporting,label in [('complete','Complete'),('coarse_interval','Coarse'),('assignment_dependent','Assignment-dependent')]:
    for effect in decisions['grid']['effect_thousandths']:
        subset=summary[(summary.reporting==reporting)&(summary.effect_thousandths==effect)].set_index('method')
        pair=paired[(paired.reporting==reporting)&(paired.effect_thousandths==effect)&(paired.first_method=='quota')&(paired.second_method=='empirical_bernstein_fixed_forecast')].iloc[0]
        entries=[f"{subset.loc[m,'mean_actual_regret']:.4f}" for m in ['quota','empirical_bernstein_fixed_forecast','empirical_best_midpoint','no_learning_half']]
        table.append(f"{label} & {effect/1000:.2f} & "+' & '.join(entries)+f" & {pair.mean_regret_difference:.6f} ({pair.paired_mc_standard_error:.6f})"+'\\\\\n')
table.append('\\bottomrule\n\\end{tabular}\n')
(OUT/'tables/designed_decision_effects.tex').write_text(''.join(table),encoding='utf8',newline='\n')
leaf='output/tables/designed_decision_effects.tex'
builder_lines=Path(__file__).read_text(encoding='utf8').splitlines()
record={'exhibit':'Effect-specific decision benchmarks','generated_file':leaf,'builder':'code/build_quota_comparison_exhibits.py',
        'builder_line':next(i for i,line in enumerate(builder_lines,1) if "(OUT/'tables/designed_decision_effects.tex')" in line),
        'estimator':'code/designed_decisions.py','numerical_source':'designed_decisions.csv; designed_decision_benchmarks.csv; designed_decision_pairs.csv'}
mapping=pd.concat([mapping[mapping.generated_file!=leaf],pd.DataFrame([record])],ignore_index=True)
for number,block in enumerate(re.findall(r'\\begin\{table\}.*?\\end\{table\}',text,flags=re.S),1):
    match=re.search(r'output/tables/([^}]+)',block)
    if match:mapping.loc[mapping.generated_file=='output/tables/'+match[1],'exhibit']='Table '+str(number)
mapping.to_csv(ROOT/'docs/output-map.csv',index=False,lineterminator='\n')
print('Generated four comparison tables, effect summaries and',len(macro),'macros')
