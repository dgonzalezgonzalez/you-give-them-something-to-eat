"""Third-submission exhibits: finite conditional regions and exploratory bands.

Never interpret the failed block approximation as a validated coverage claim.
All quantities are read from generated scientific outputs; no manual estimates.
"""
from pathlib import Path
import csv,json,re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from estimate import ARMS
from build_revision_exhibits import table,f,label

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output';FIGS=OUT/'figures'

def main():
    mac={};mappings=[]
    policies=json.loads((OUT/'policies.json').read_text())
    mac['LowerLargeShare']=f(100*policies['vertices']['Lower+Large']['Large'],1)
    finite=pd.read_csv(OUT/'finite_arm_regions.csv')
    endpoints=finite[finite.outcome=='mean'].pivot(index='arm',columns='scope',values='estimate').reindex(ARMS)
    regions=pd.read_csv(OUT/'population_bounds.csv')
    pair=pd.read_csv(OUT/'finite_policy_regions.csv')
    rows=[]
    for left,right in [('Large','Control'),('Gikuriro','Control+Large'),('Gikuriro','Lower+Large'),('Gikuriro','Upper+Large')]:
        if left=='Large':
            lo=endpoints.loc[left,'lower_endpoint']-endpoints.loc[right,'upper_endpoint']
            hi=endpoints.loc[left,'upper_endpoint']-endpoints.loc[right,'lower_endpoint']
            fl=finite[(finite.outcome=='mean')&(finite.arm==left)&(finite.scope=='lower_endpoint')].finite_lower.iloc[0]-finite[(finite.outcome=='mean')&(finite.arm==right)&(finite.scope=='upper_endpoint')].finite_upper.iloc[0]
            fu=finite[(finite.outcome=='mean')&(finite.arm==left)&(finite.scope=='upper_endpoint')].finite_upper.iloc[0]-finite[(finite.outcome=='mean')&(finite.arm==right)&(finite.scope=='lower_endpoint')].finite_lower.iloc[0]
            # Large is not feasible at the fixed budget; no invented all-policy band.
            approx=['--','--'];title='Large vs. control'
            mac.update({'LargeIdentificationLo':f(lo),'LargeIdentificationHi':f(hi),'LargeFiniteLo':f(fl),'LargeFiniteHi':f(fu)})
        else:
            s=regions[(regions.outcome=='mean')&(regions.left==left)&(regions.right==right)].set_index('endpoint')
            lo=s.loc['lower','estimate'];hi=s.loc['upper','estimate'];approx=[f(s.loc['lower','sim_lo']),f(s.loc['upper','sim_hi'])]
            r=pair[(pair.outcome=='mean')&(pair.left==left)&(pair.right==right)&(pair.scope=='weighted_baseline')].iloc[0]
            fl=r.finite_lower;fu=r.finite_upper;title='GK vs. '+label(right)
        rows.append([title,f(lo),f(hi),*approx,f(fl),f(fu)])
    table('decision_bounds.tex',['Comparison','ID lo.','ID hi.','Approx. lo.','Approx. hi.','Finite lo.','Finite hi.'],rows)
    mappings.append(('Baseline diet comparisons','decision_bounds.tex','finite_arm_regions.csv; finite_policy_regions.csv; population_bounds.csv'))
    cert=pd.read_csv(OUT/'allocation_certificates.csv')
    rows=[]
    for obj in ['mean','shortfall_6']:
        for method in ['finite','block_approximation']:
            s=cert[(cert.objective==obj)&(cert.method==method)&(cert.scope=='weighted_baseline')].iloc[0]
            rows.append(['Mean HDDS' if obj=='mean' else 'Shortfall ($z=6$)','Finite conditional' if method=='finite' else 'Block sensitivity',f(s.GK_certificate),f(s.fitted_best_vertex_certificate),f(s.best_vertex_certificate),f(s.optimized_certificate)])
            stem=('Finite' if method=='finite' else 'Approx')+('Mean' if obj=='mean' else 'Shortfall')
            mac[stem+'Allocation']=f(s.optimized_certificate);mac[stem+'Vertex']=f(s.best_vertex_certificate)
            mac[stem+'GK']=f(s.GK_certificate);mac[stem+'Fitted']=f(s.fitted_best_vertex_certificate)
    table('allocation_certificates.tex',['Objective','Region','GK','Fitted cash','Best vertex','Diversified'],rows)
    mappings.append(('Allocation certificates','allocation_certificates.tex','allocation_certificates.csv'))
    rows=[]
    for method in ['finite','block_approximation']:
        s=cert[(cert.objective=='mean')&(cert.method==method)&(cert.scope=='weighted_baseline')].iloc[0]
        rows.append(['Finite conditional' if method=='finite' else 'Block sensitivity',*[f(100*s[a+'_probability'],1) for a in ARMS],f(s.expected_cost,2)])
    table('diversified_allocations.tex',['Region',*ARMS,'USD'],rows)
    mappings.append(('Diversified allocations','diversified_allocations.tex','allocation_certificates.csv'))
    info=json.loads((OUT/'child-cohort-metadata.json').read_text())
    for key,stem in [('baseline_flagged_cohort','BaselineChildCohort'),('all_endline_due','EndlineChildDue'),('baseline_cohort_linked_endline','LinkedChildCohort'),('endline_due_baseline_cohort','DueLinkedChildCohort'),('endline_due_outside_baseline_cohort','DueOutsideChildCohort')]:mac[stem]=str(info[key])
    children=pd.read_csv(OUT/'child_cohort_accounting.csv')
    rows=[[r.arm,r.baseline_flagged_cohort,r.linked_endline_rows,r.baseline_cohort_measured_endline,r.all_endline_due,r.endline_due_outside_baseline_cohort] for r in children.itertuples()]
    table('child_cohorts.tex',['Arm','Baseline cohort','Linked endline','Measured endline','All endline due','Outside cohort'],rows)
    mappings.append(('Child cohort accounting','child_cohorts.tex','child_cohort_accounting.csv'))
    estimates=pd.read_csv(OUT/'baseline_child_effects.csv');rows=[]
    names={'haz06':'Height-for-age','waz06':'Weight-for-age','muacz':'Arm circumference'}
    for obj in names:
        s=estimates[estimates.outcome==obj].set_index('arm')
        rows.extend([[names[obj],*[f(s.loc[a,'estimate']) for a in ARMS[1:]]],['',*['('+f(s.loc[a,'se'])+')' for a in ARMS[1:]]],['Holm $p$',*[f(s.loc[a,'p_holm']) for a in ARMS[1:]]],['N',*[str(int(s.loc[a,'N'])) for a in ARMS[1:]]]])
    table('baseline_child_effects.tex',['Outcome',*ARMS[1:]],rows)
    mappings.append(('Baseline child sensitivity','baseline_child_effects.tex','baseline_child_effects.csv'))
    stress=json.loads((OUT/'blocked-validation.json').read_text())
    for scenario,stem in [('balanced_equal_weights','EqualWeightCoverage'),('unequal_frame_weights','UnequalWeightCoverage')]:
        mac[stem]=f(next(r['joint_coverage'] for r in stress['simulation_cases'] if r['scenario']==scenario))
    rows=[]
    for r in stress['simulation_cases']:
        ci=r['coverage_binomial_95_interval'];rows.append([label(r['scenario']),r['joint_coverage_count'],r['replications'],f(r['joint_coverage']),f(ci[0]),f(ci[1])])
    table('block_stress.tex',['Scenario','Covered','Replications','Joint coverage','MC lo.','MC hi.'],rows)
    mappings.append(('Block stress diagnostics','block_stress.tex','blocked-validation.json'))
    cost=pd.read_csv(OUT/'allocation_cost_sensitivity.csv');rows=[]
    labels=[('relative_g0.75_cash1.0','GK costs $-25\\%$'),('relative_g1.25_cash1.0','GK costs $+25\\%$'),('relative_g1.0_cash0.75','Cash costs $-25\\%$'),('relative_g1.0_cash1.25','Cash costs $+25\\%$')]
    for key,title in labels:
        s=cost[cost.scenario==key].set_index('method');r=s.loc['finite'];a=s.loc['block_approximation']
        rows.append([title,label(r.fitted_observed_best),f(r.upper_cash_margin,2),f(r.optimized_certificate),f(a.optimized_certificate)])
    table('decision_costs.tex',['Accounting scenario','Fitted cash','Upper-cost margin (USD)','Finite loss','Approx. loss'],rows)
    mappings.append(('Aligned cost scenarios','decision_costs.tex','allocation_cost_sensitivity.csv'))
    mac['CostScenarioN']=str(cost.scenario.nunique());mac['GuardedRowN']=str(json.loads((OUT/'revision_metadata.json').read_text())['zero_variance_rows_guarded'])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight'})
    frontier=pd.read_csv(OUT/'allocation_frontier.csv');fig,axes=plt.subplots(1,2,figsize=(7,2.8))
    for ax,method,title in zip(axes,['finite','block_approximation'],['Finite conditional outer region','Exploratory block region']):
        s=frontier[frontier.method==method]
        ax.plot(100*s.GK_share,s.certificate,color='#1a4673',lw=1.5)
        ax.set_title(title,fontsize=9);ax.set_xlabel('Fixed Gikuriro share (%)');ax.grid(axis='y',color='.9',lw=.5)
        ax.set_xticks([0,25,50,75,100])
    axes[0].set_ylabel('Worst-case mean HDDS loss (groups)')
    fig.tight_layout();fig.savefig(FIGS/'allocation_frontier.pdf');fig.savefig(FIGS/'allocation_frontier.png',dpi=180);plt.close(fig)
    mappings.append(('Gikuriro share frontier','allocation_frontier.pdf','allocation_frontier.csv'))
    text='% Generated by code/build_decision_exhibits.py; never edit manually.\n'+''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in mac.items())
    (ROOT/'paper/decision-results.tex').write_text(text,encoding='utf8',newline='\n')
    (OUT/'decision-numbers.json').write_text(json.dumps(mac,indent=2),encoding='utf8')
    mappings.append(('Decision in-text numbers','decision-results.tex','decision-numbers.json'))
    lines=Path(__file__).read_text(encoding='utf8').splitlines()
    with (ROOT/'docs/output-map.csv').open('a',newline='',encoding='utf8') as file:
        writer=csv.writer(file)
        for title,name,src in mappings:
            generated=('paper/' if name=='decision-results.tex' else 'output/figures/' if name.endswith('.pdf') else 'output/tables/')+name
            writer.writerow([title,generated,'code/build_decision_exhibits.py',next(i+1 for i,l in enumerate(lines) if name in l),'code/blocked_inference.py; code/policy_allocation.py; code/child_cohorts.py',src])
    mapping=pd.read_csv(ROOT/'docs/output-map.csv');source=(ROOT/'paper/paper.tex').read_text(encoding='utf8')
    cited=set()
    for kind,env in [('Table','table'),('Figure','figure')]:
        for i,block in enumerate(re.findall(r'\\begin\{'+env+r'\}.*?\\end\{'+env+r'\}',source,flags=re.S),1):
            match=re.search(r'output/(tables|figures)/([^}]+)',block)
            if match:
                path='output/'+match[1]+'/'+match[2];cited.add(path)
                mapping.loc[mapping.generated_file==path,'exhibit']=kind+' '+str(i)
    for i,r in mapping.iterrows():
        if r.generated_file.startswith('output/') and r.generated_file not in cited:mapping.loc[i,'exhibit']='Uncited supplementary output: '+r.exhibit
    mapping.to_csv(ROOT/'docs/output-map.csv',index=False,lineterminator='\n')
    print('Generated seven decision tables, share-frontier figure and decision macros.')

if __name__=='__main__':main()
