"""Displays and macros for the referee-driven analyses; all values from outputs."""
from pathlib import Path
import csv,json,re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output';TABLES=OUT/'tables';FIGS=OUT/'figures'
def f(x,n=3):return f'{x:.{n}f}'
def pf(x):return r'$<0.001$' if x<.001 else f(x)
def label(s):return s.replace('+',' + ').replace('_',' ')
def table(name,head,rows):
    text='\\begin{tabular}{l'+'r'*(len(head)-1)+'}\n\\toprule\n'+' & '.join(head)+' \\\\\n\\midrule\n'
    text+=''.join(' & '.join(map(str,r))+' \\\\\n' for r in rows)+'\\bottomrule\n\\end{tabular}\n'
    (TABLES/name).write_text(text,encoding='utf8',newline='\n')

def main():
    meta=json.loads((OUT/'revision_metadata.json').read_text());mac={}
    mac['IdentifiedDietN']=str(meta['identified_diet_N']);mac['PairFamilyN']=str(meta['pair_family_size']);mac['BoundFamilyN']=str(meta['endpoint_family_size'])
    obs=pd.read_csv(OUT/'diet_observation_intervals.csv')
    table('diet_intervals.tex',['Arm','Baseline','Identified','Partial','Unobserved'],[[r.arm,r.baseline_N,r.identified_diets,r.partially_identified,r.unobserved] for r in obs.itertuples()])
    h=pd.read_csv(OUT/'hajek_policy_effects.csv');bound=pd.read_csv(OUT/'population_bounds.csv')
    rows=[]
    for obj in ['mean','shortfall_6']:
        for pol in ['Control+Large','Lower+Large','Upper+Large']:
            r=h[(h.outcome==obj)&(h.policy==pol)].iloc[0]
            b=bound[(bound.outcome==obj)&(bound.left=='Gikuriro')&(bound.right==pol)].set_index('endpoint')
            rows.append(['HDDS' if obj=='mean' else 'Shortfall ($z=6$)',label(pol),f(r['estimate']),f(b.loc['lower','estimate']),f(b.loc['upper','estimate']),f(b.loc['lower','sim_lo']),f(b.loc['upper','sim_hi'])])
    table('population_bounds.tex',['Outcome','Cash policy','Observed','Bound lo.','Bound hi.','Approx. lo.','Approx. hi.'],rows)
    reg=pd.read_csv(OUT/'policy_regret.csv');mean=reg[reg.outcome=='mean'].copy()
    table('regret.tex',['Policy','Fitted HDDS','Fitted regret','Observed approx. upper','Baseline approx. upper'],
          [[label(r.policy),f(r.fitted_value),f(r.fitted_regret),f(r.regret_upper_95),f(r.population_regret_upper_95)] for r in mean.itertuples()])
    for pol,stem in [('Gikuriro','GK'),('Lower+Large','LowerLarge')]:
        r=mean[mean.policy==pol].iloc[0]
        for key,suffix in [('fitted_regret','FittedRegret'),('regret_upper_95','ObservedRegretUpper'),('population_regret_upper_95','PopulationRegretUpper')]:mac[stem+suffix]=f(r[key])
    for pol,stem in [('Control+Large','HajekControlLarge'),('Lower+Large','HajekLowerLarge')]:
        r=h[(h.outcome=='mean')&(h.policy==pol)].iloc[0]
        mac[stem+'Estimate']=f(r['estimate']);mac[stem+'SimLo']=f(r.sim_lo);mac[stem+'SimHi']=f(r.sim_hi)
    c=pd.read_csv(OUT/'original_crosswalk.csv');rows=[]
    for spec,title in [('source_pooled','Original controls, pooled cash'),('source_split','Original controls, split cash'),('lag_only_source','Supplied-score lag only'),('lag_only_integer','Integer outcome, supplied lag')]:
        s=c[c.spec==spec].set_index('arm');rows.append([title,f(s.loc['Gikuriro','estimate']),f(s.loc['Gikuriro','se']),f(s.loc['Large','estimate']),f(s.loc['Large','se']),int(s.N.iloc[0])])
    current=pd.read_csv(OUT/'arm_effects.csv');s=current[current.outcome=='diet_mean'].set_index('arm')
    rows.append(['Integer outcome and baseline',f(s.loc['Gikuriro','estimate']),f(s.loc['Gikuriro','se']),f(s.loc['Large','estimate']),f(s.loc['Large','se']),int(s.N.iloc[0])])
    table('original_crosswalk.tex',['Specification','GK','GK SE','Large','Large SE','N'],rows)
    cr=pd.read_csv(OUT/'cr2_sensitivity.csv');rows=[]
    for comparison in ['Gikuriro','Lower','Middle','Upper','Large','GK_minus_Control+Large','GK_minus_Lower+Large']:
        r=cr[(cr.outcome=='diet_mean')&(cr.comparison==comparison)].iloc[0]
        rows.append([label(comparison).replace('GK minus ','GK vs. '),f(r['estimate']),f(r.se_cr2),f(r.df_satterthwaite,1),pf(r.p_cr2),f(r.effective_score_clusters,1)])
    table('cr2.tex',['Contrast','Effect','CR2 SE','Satt. df','Pointwise $p$','Effective clusters'],rows)
    rows=[]
    for fname,prefix in [('child_effects.csv','Child'),('ineligible_effects.csv','Ineligible')]:
        data=pd.read_csv(OUT/fname)
        for obj in data.outcome.unique():
            s=data[data.outcome==obj].set_index('arm')
            rows.append([prefix+' '+{'haz06':'height-for-age','waz06':'weight-for-age','muacz':'arm circumference','dietarydiversity':'HDDS','consumption_asinh':'consumption (IHS)','savingsstock_asinh':'saving (IHS)'}.get(obj,obj),
                         f(s.loc['Gikuriro','estimate']),f(s.loc['Gikuriro','se']),pf(s.loc['Gikuriro','p_holm']),f(s.loc['Large','estimate']),f(s.loc['Large','se']),pf(s.loc['Large','p_holm']),int(s.N.min())])
    table('additional_populations.tex',['Outcome','GK','SE','Holm $p$','Large','SE','Holm $p$','N'],rows)
    weight=pd.read_csv(OUT/'weight_concentration.csv')
    table('weight_support.tex',['Arm','Villages','Effective weight villages',r'Maximum village weight (\%)'],
          [[r.arm,r.villages,f(r.effective_weight_villages,1),f(100*r.max_village_weight_share,1)] for r in weight.itertuples()])
    loo=pd.read_csv(OUT/'leave_out_sensitivity.csv');rows=[]
    for unit in ['vid','block']:
        for pol in ['Control+Large','Lower+Large','Upper+Large']:
            s=loo[(loo.outcome=='diet_mean')&(loo.drop_unit==unit)&(loo.policy==pol)]
            rows.append(['Village' if unit=='vid' else 'Block',label(pol),f(s.estimate.min()),f(s.estimate.max()),len(s)])
    table('leave_out.tex',['Omitted unit','Cash comparator','Minimum effect','Maximum effect','Fits'],rows)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight'})
    fig,axes=plt.subplots(1,2,figsize=(7,2.9),sharey=True)
    for ax,pol in zip(axes,['Control+Large','Lower+Large']):
        s=h[(h.policy==pol)&h.outcome.str.startswith('survival_')].copy();s['k']=s.outcome.str.split('_').str[-1].astype(int);s=s.sort_values('k')
        b=bound[(bound.left=='Gikuriro')&(bound.right==pol)&bound.outcome.str.startswith('survival_')].copy();b['k']=b.outcome.str.split('_').str[-1].astype(int)
        lo=b[b.endpoint=='lower'].sort_values('k');hi=b[b.endpoint=='upper'].sort_values('k')
        ax.fill_between(lo.k,lo.sim_lo*100,hi.sim_hi*100,color='#1a4673',alpha=.12,label='Exploratory baseline band')
        ax.plot(s.k,s.estimate*100,'o-',color='#ab422f',ms=3,label='Identified-diet point estimate')
        ax.axhline(0,color='.4',lw=.8);ax.set_title('Gikuriro minus '+label(pol).lower(),fontsize=9)
        ax.set_xlabel('At least this many food groups');ax.set_xticks([2,4,6,8,10,12]);ax.grid(axis='y',color='.9',lw=.5)
    axes[0].set_ylabel('Difference (percentage points)');axes[0].legend(frameon=False,fontsize=6.5)
    fig.tight_layout();fig.savefig(FIGS/'coherent_thresholds.pdf');fig.savefig(FIGS/'coherent_thresholds.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(6.5,3.7));y=np.arange(len(mean))
    ax.barh(y,mean.population_regret_upper_95,color='#d9e1e9',label='Exploratory baseline regret bound')
    ax.barh(y,mean.fitted_regret,color='#ab422f',label='Fitted observed-sample regret')
    ax.set_yticks(y,[label(x) for x in mean.policy]);ax.invert_yaxis();ax.set_xlabel('HDDS groups relative to best feasible policy')
    ax.legend(frameon=False,fontsize=7,loc='lower right');ax.grid(axis='x',color='.9',lw=.5)
    fig.tight_layout();fig.savefig(FIGS/'policy_regret.pdf');fig.savefig(FIGS/'policy_regret.png',dpi=180);plt.close(fig)
    text='% Generated referee-revision numbers; never edit manually.\n'+''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in mac.items())
    (ROOT/'paper/revision-results.tex').write_text(text,encoding='utf8',newline='\n')
    (OUT/'revision-numbers.json').write_text(json.dumps(mac,indent=2),encoding='utf8')
    mappings=[('Diet observation','diet_intervals.tex','diet_observation_intervals.csv'),('Population bounds','population_bounds.tex','population_bounds.csv; hajek_policy_effects.csv'),
              ('Policy regret','regret.tex','policy_regret.csv'),('Original-study crosswalk','original_crosswalk.tex','original_crosswalk.csv; arm_effects.csv'),
              ('Small-cluster correction','cr2.tex','cr2_sensitivity.csv'),('Child/ineligible outcomes','additional_populations.tex','child_effects.csv; ineligible_effects.csv'),
              ('Weight support','weight_support.tex','weight_concentration.csv'),('Leave-out sensitivity','leave_out.tex','leave_out_sensitivity.csv'),
              ('Coherent diet thresholds','coherent_thresholds.pdf','population_bounds.csv; hajek_policy_effects.csv'),('Policy-regret figure','policy_regret.pdf','policy_regret.csv'),
              ('Revision in-text numbers','revision-results.tex','revision-numbers.json')]
    lines=Path(__file__).read_text(encoding='utf8').splitlines()
    with (ROOT/'docs/output-map.csv').open('a',newline='',encoding='utf8') as file:
        writer=csv.writer(file)
        for title,name,source in mappings:
            generated=('paper/' if name=='revision-results.tex' else 'output/figures/' if name.endswith('.pdf') else 'output/tables/')+name
            writer.writerow([title,generated,'code/build_revision_exhibits.py',next(i+1 for i,l in enumerate(lines) if name in l),'code/referee_revision.py; code/finite_cluster.py',source])
    # Derive current exhibit numbering from actual manuscript source order.
    mapping=pd.read_csv(ROOT/'docs/output-map.csv')
    source=(ROOT/'paper/paper.tex').read_text(encoding='utf8')
    for kind,env in [('Table','table'),('Figure','figure')]:
        blocks=re.findall(r'\\begin\{'+env+r'\}.*?\\end\{'+env+r'\}',source,flags=re.S)
        for i,block in enumerate(blocks,1):
            match=re.search(r'output/(tables|figures)/([^}]+)',block)
            if match:mapping.loc[mapping.generated_file=='output/'+match[1]+'/'+match[2],'exhibit']=kind+' '+str(i)
    mapping.to_csv(ROOT/'docs/output-map.csv',index=False,lineterminator='\n')
    print('Generated eight revision tables, two revision figures and macros.')

if __name__=='__main__':main()
