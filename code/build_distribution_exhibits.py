"""Fourth-revision information benchmarks and institutional sensitivities."""
from pathlib import Path
import csv,json,re
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from estimate import ARMS
from build_revision_exhibits import table,f

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'

def main():
    cert=pd.read_csv(OUT/'distribution_allocation_certificates.csv')
    selected=cert[cert.scope=='weighted_baseline'].set_index(['method','objective'])
    old=pd.read_csv(OUT/'allocation_certificates.csv');old=old[(old.method=='finite')&(old.scope=='weighted_baseline')].set_index('objective')
    methods=[('support_only','Support and costs only'),('logical_distribution','Outcome consistency'),
             ('primitive_box','Finite primitive box'),('finite_distribution','Finite, coherent distribution'),
             ('finite_consistency_distribution','Finite and consistency')]
    rows=[];values={}
    for method,title in methods:
        values[method]={name:(float(old.loc[name].optimized_certificate) if method=='primitive_box' else float(selected.loc[(method,name)].certificate)) for name in ['mean','shortfall_6']}
        rows.append([title,f(values[method]['mean']),f(values[method]['shortfall_6'])])
    quota=pd.read_csv(OUT/'quota_allocations.csv').set_index('objective')
    values['quota_mixture']={name:float(quota.loc[name].reported_conservative_loss_upper) for name in ['mean','shortfall_6']}
    methods.append(('quota_mixture','Quota mixture, verified proposal'))
    rows.append(['Quota mixture, verified proposal',f(values['quota_mixture']['mean']),f(values['quota_mixture']['shortfall_6'])])
    table('information_benchmarks.tex',['Information region','Mean loss (groups)','Shortfall loss'],rows)
    macro={'SupportMeanLoss':f(values['support_only']['mean']),
           'LogicalMeanLoss':f(values['logical_distribution']['mean']),
           'ProjectedMeanLoss':f(values['finite_distribution']['mean']),
           'TightMeanLoss':f(values['finite_consistency_distribution']['mean']),
           'TightShortfallLoss':f(values['finite_consistency_distribution']['shortfall_6']),
           'NoOutcomeCost':f(selected.loc[('support_only','mean')].expected_cost,2),
           'TightAllocationCost':f(selected.loc[('finite_consistency_distribution','mean')].expected_cost,2),
           'TotalInformationTightening':f(values['support_only']['mean']-values['finite_consistency_distribution']['mean']),
           'TotalInformationPercent':f(100*(1-values['finite_consistency_distribution']['mean']/values['support_only']['mean']),1),
           'ConsistencyTightening':f(values['support_only']['mean']-values['logical_distribution']['mean']),
           'FiniteIncrementOverConsistency':f(values['logical_distribution']['mean']-values['finite_consistency_distribution']['mean']),
           'FiniteIncrementPercent':f(100*(1-values['finite_consistency_distribution']['mean']/values['logical_distribution']['mean']),2)}
    macro.update({'QuotaMeanLoss':f(values['quota_mixture']['mean']),
                  'QuotaShortfallLoss':f(values['quota_mixture']['shortfall_6']),
                  'QuotaAllocationCost':f(quota.loc['mean'].expected_cost_USD,2),
                  'QuotaMeanImprovement':f(values['finite_consistency_distribution']['mean']-values['quota_mixture']['mean']),
                  'QuotaRelativeImprovement':f(100*(1-values['quota_mixture']['mean']/values['finite_consistency_distribution']['mean']),1)})
    rows=[]
    for method in ['support_only','logical_distribution','finite_distribution','finite_consistency_distribution']:
        r=selected.loc[(method,'mean')]
        rows.append([dict(methods)[method],*[f(100*r[a+'_probability'],1) for a in ARMS],f(r.expected_cost,2)])
    q=quota.loc['mean']
    rows.append(['Quota mixture proposal',*[f(100*q[a+'_probability'],1) for a in ARMS],f(q.expected_cost_USD,2)])
    table('distribution_allocations.tex',['Region',*ARMS,'USD'],rows)
    institutions=pd.read_csv(OUT/'institutional_allocation_sensitivity.csv')
    inst=institutions[(institutions.method=='finite_consistency_distribution')&(institutions.objective=='mean')].set_index('class')
    labels=[('expected_cost_ceiling','Expected-cost ceiling'),('at_least_75percent_assisted','At least 75 percent assisted'),
            ('universal_assistance','Universal assistance'),('binding_expected_spending','Binding expected spending'),
            ('universal_assistance_binding_spending','Universal, binding spending'),('at_least_25percent_Gikuriro','At least 25 percent GK')]
    rows=[[title,f(inst.loc[key].certificate),f(inst.loc[key].optimized_loss_against_unrestricted_comparators),f(inst.loc[key].common_comparator_optimum_expected_cost,2)] for key,title in labels]
    table('institutional_rules.tex',['Hypothetical rule','Own-menu loss','Common-menu loss','USD, common-menu optimum'],rows)
    macro['UniversalCommonLoss']=f(inst.loc['universal_assistance'].optimized_loss_against_unrestricted_comparators)
    macro['BindingCommonLoss']=f(inst.loc['binding_expected_spending'].optimized_loss_against_unrestricted_comparators)
    macro['MinimumGKOwnLoss']=f(inst.loc['at_least_25percent_Gikuriro'].certificate)
    resource=pd.read_csv(OUT/'unused_resource_sensitivity.csv')
    table('unused_resource_values.tex',['Groups per unused USD','Augmented-objective loss','Expected USD spent','Unused USD'],
          [[f(r.hypothetical_groups_per_unused_USD),f(r.certificate_in_augmented_objective_units),f(r.expected_cost,2),f(r.unused_expected_budget,2)] for r in resource.itertuples()])
    costs=pd.read_csv(OUT/'distribution_cost_sensitivity.csv');rows=[]
    labels=[('relative_g0.75_cash1.0','GK costs $-25\\%$'),('relative_g1.25_cash1.0','GK costs $+25\\%$'),('relative_g1.0_cash0.75','Cash costs $-25\\%$'),('relative_g1.0_cash1.25','Cash costs $+25\\%$')]
    for key,title in labels:
        s=costs[costs.scenario==key].set_index('method')
        rows.append([title,f(s.iloc[0].upper_cash_margin,2),f(s.loc['finite_distribution'].certificate),f(s.loc['finite_consistency_distribution'].certificate)])
    table('distribution_costs.tex',['Accounting scenario','Upper-cost margin (USD)','Finite coherent loss','With consistency'],rows)
    scope=r'''\begin{tabular}{p{.24\textwidth}p{.28\textwidth}p{.40\textwidth}}
\toprule
Target & Observation and weights & Inference and limits \\
\midrule
Both baseline strata & 1,793 eligible and 995 ineligible households; fixed weights and item intervals & Separate standalone 36-primitive classical and 24-tail quota mean events. Each conditional 95\% event protects all stipulated population weights; neither certifies a unique frontier. \\
Eligible-only baseline & All baseline eligible households; fixed source weights and item intervals & Separate earlier 276-primitive and 276-term quota distribution events. No wider-frame or deployment guarantee. \\
Eligible-only identified diets & Package-specific potential reporting composition; positive weights & Earlier separate 138-primitive event. Outcome observation can select different households by package. \\
Observed regression crosswalk & Selected endline outcomes; baseline controls and source weights & Village CR1/CR2 working approximations. No selection-robust baseline effect. \\
Joint population sensitivity & Both strata; common block or village scores retain cross-equation covariance & Exploratory all-cash and cross-stratum Holm families. Ratio nominal coverage fails retained stress diagnostics; no selection-robust frontier or switch inference. \\
Deployment benchmark & Original packages and within-village saturation & Stable costs, delivery and cross-village spillovers are additional maintained assumptions. \\
\bottomrule
\end{tabular}
'''
    (OUT/'tables/estimand_scope.tex').write_text(scope,encoding='utf8',newline='\n')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight'})
    fig,axes=plt.subplots(1,2,figsize=(7,3.2))
    names=['Support only','Consistency','Finite box','Finite coherent','Finite + consistency','Quota mixture proposal']
    for ax,name,title in zip(axes,['mean','shortfall_6'],['Mean diet: groups','Six-group shortfall: objective units']):
        bars=ax.barh(range(6),[values[m][name] for m,_ in methods],color=['#adb5bd','#6082a4','#bdc8d3','#3a668f','#173f67','#50743d'])
        ax.set_yticks(range(6),names if name=='mean' else ['']*6);ax.invert_yaxis()
        ax.set_title(title,fontsize=9);ax.set_xlabel('Upper loss bound')
        ax.grid(axis='x',color='.9',linewidth=.5);ax.set_axisbelow(True)
        ax.set_xlim(0,10.8 if name=='mean' else .9)
        for bar,(method,_) in zip(bars,methods):ax.text(bar.get_width()+(.10 if name=='mean' else .008),bar.get_y()+bar.get_height()/2,f(values[method][name]),va='center',fontsize=7)
    fig.tight_layout();fig.savefig(OUT/'figures/information_regions.pdf');fig.savefig(OUT/'figures/information_regions.png',dpi=180);plt.close(fig)
    (ROOT/'paper/distribution-results.tex').write_text('% Generated by code/build_distribution_exhibits.py.\n'+''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in macro.items()),encoding='utf8',newline='\n')
    (OUT/'distribution-numbers.json').write_text(json.dumps(macro,indent=2),encoding='utf8')
    entries=[('Information benchmarks','output/tables/information_benchmarks.tex','distribution_allocation_certificates.csv; allocation_certificates.csv; quota_allocations.csv'),
             ('Coherent allocations','output/tables/distribution_allocations.tex','distribution_allocation_certificates.csv; quota_allocations.csv'),
             ('Institutional rules','output/tables/institutional_rules.tex','institutional_allocation_sensitivity.csv'),
             ('Unused resource values','output/tables/unused_resource_values.tex','unused_resource_sensitivity.csv'),
             ('Coherent cost scenarios','output/tables/distribution_costs.tex','distribution_cost_sensitivity.csv'),
             ('Estimand and inference scope','output/tables/estimand_scope.tex','Explicit method definitions'),
             ('Information-region comparison','output/figures/information_regions.pdf','distribution_allocation_certificates.csv; allocation_certificates.csv; quota_allocations.csv'),
             ('Distribution in-text numbers','paper/distribution-results.tex','distribution-numbers.json')]
    lines=Path(__file__).read_text(encoding='utf8').splitlines()
    with (ROOT/'docs/output-map.csv').open('a',newline='',encoding='utf8') as file:
        writer=csv.writer(file)
        for title,path,input_source in entries:
            leaf=Path(path).name
            method_scripts='code/distribution_regions.py; code/institutional_allocations.py'
            if 'quota_allocations.csv' in input_source:method_scripts+='; code/quota_allocation.py'
            writer.writerow([title,path,'code/build_distribution_exhibits.py',next(i+1 for i,l in enumerate(lines) if leaf in l),
                             method_scripts,input_source])
    mapping=pd.read_csv(ROOT/'docs/output-map.csv');source=(ROOT/'paper/paper.tex').read_text(encoding='utf8');cited=set()
    for kind,env in [('Table','table'),('Figure','figure')]:
        for i,block in enumerate(re.findall(r'\\begin\{'+env+r'\}.*?\\end\{'+env+r'\}',source,flags=re.S),1):
            match=re.search(r'output/(tables|figures)/([^}]+)',block)
            if match:
                path='output/'+match[1]+'/'+match[2];cited.add(path)
                mapping.loc[mapping.generated_file==path,'exhibit']=kind+' '+str(i)
    for i,r in mapping.iterrows():
        if r.generated_file.startswith('output/') and r.generated_file not in cited and not r.exhibit.startswith('Uncited supplementary output:'):
            mapping.loc[i,'exhibit']='Uncited supplementary output: '+r.exhibit
    mapping.to_csv(ROOT/'docs/output-map.csv',index=False,lineterminator='\n')
    print('Six fourth-revision tables, information figure, macros and actual source output map generated.')

if __name__=='__main__':main()
