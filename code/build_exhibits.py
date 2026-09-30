"""Generate every manuscript table, figure and numerical macro from estimates."""
from pathlib import Path
import csv, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from estimate import ARMS, policy_vertices

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'; TABLES=OUT/'tables';FIGS=OUT/'figures'
TABLES.mkdir(exist_ok=True);FIGS.mkdir(exist_ok=True)
arm=pd.read_csv(OUT/'arm_effects.csv');pol=pd.read_csv(OUT/'policy_effects.csv')
sec=pd.read_csv(OUT/'secondary.csv');attr=pd.read_csv(OUT/'attrition.csv')
desc=pd.read_csv(OUT/'descriptives.csv');meta=json.loads((OUT/'run_metadata.json').read_text())
policy=json.loads((OUT/'policies.json').read_text());costs=policy['costs'];budget=policy['budget']

def f(x,d=3):return f'{x:.{d}f}'
def pf(x):return r'$<0.001$' if x<.001 else f(x)
def tex_table(filename,headers,rows,align=None):
    n=len(headers);align=align or ('l'+'r'*(n-1))
    text='\\begin{tabular}{'+align+'}\n\\toprule\n'+' & '.join(headers)+' \\\\\n\\midrule\n'
    for row in rows:text+=' & '.join(map(str,row))+' \\\\\n'
    text+='\\bottomrule\n\\end{tabular}\n'
    (TABLES/filename).write_text(text,encoding='utf8')

def regression_table(filename,data,outcomes,columns,key='arm',correction='p_max_t'):
    rows=[]
    for outcome,label in outcomes:
        data_out=data[data.outcome==outcome].set_index(key)
        vals=[];ses=[];ps=[]
        for col in columns:
            r=data_out.loc[col];p=r[correction]
            stars='^{***}' if p<.01 else ('^{**}' if p<.05 else ('^{*}' if p<.1 else ''))
            vals.append('$'+f(r['estimate'])+stars+'$');ses.append('('+f(r.se)+')');ps.append('['+pf(p)+']')
        rows.extend([[label,*vals],['',*ses],['',*ps]])
    rows += [['Households',*[str(int(data.loc[(data.outcome==outcomes[0][0])&(data[key]==c),'N'].iloc[0])) for c in columns]],
             ['Villages',*['248']*len(columns)]]
    headers=['',*[c.replace('Control+Large','Control + large').replace('+',' + ').replace('GK_minus_','').replace('Gikuriro','Gikuriro') for c in columns]]
    tex_table(filename,headers,rows)

rows=[]
for a in ARMS:
    r=attr.set_index('arm').loc[a]
    q=float(policy['vertices'].get('Control+Large',{}).get('Large',0))
    rows.append([a,0 if a=='Control' else f(costs[a],2),str({'Control':74,'Gikuriro':74,'Lower':22,'Middle':22,'Upper':22,'Large':34}[a]),int(r.baseline_n),int(r.diet_observed),f(100*r.retention_weighted,1)])
tex_table('design.tex',['Arm','Cost (USD)','Villages','Baseline eligible','Observed diet',r'Retained (\%)'],rows)
rows=[]
for label,k in [('Baseline diet (groups)','dietarydiversity'),('Consumption (IHS)','consumption_asinh'),('Household members','hhmember'),('Female head (share)','hhfemale')]:
    r=desc[desc.variable==k].set_index('arm')
    rows.extend([[label,*[f(r.loc[a,'mean'],2) for a in ARMS]],['',*['('+f(r.loc[a,'sd'],2)+')' for a in ARMS]]])
tex_table('baseline.tex',['',*ARMS],rows)
regression_table('diet_itt.tex',arm,[('diet_mean','Dietary diversity'),('shortfall_6','Diet-shortfall reduction ($z=6$)'),('shortfall_sq_6','Squared-shortfall reduction'),('diet_atleast_4','At least 4 food groups'),('diet_atleast_6','At least 6 food groups'),('diet_atleast_8','At least 8 food groups')],ARMS[1:])
regression_table('budget_comparisons.tex',pol,[('diet_mean','Dietary diversity'),('shortfall_4','Shortfall reduction ($z=4$)'),('shortfall_6','Shortfall reduction ($z=6$)'),('shortfall_8','Shortfall reduction ($z=8$)'),('shortfall_sq_6','Squared-shortfall reduction'),('diet_atleast_6','At least 6 food groups')],['Control+Large','Lower+Large','Middle+Large','Upper+Large'],key='policy')
regression_table('secondary.tex',sec,[('consumption_asinh','Consumption (IHS)'),('productiveassets_asinh','Productive assets (IHS)'),('savingsstock_asinh','Saving stock (IHS)'),('borrowingstock_asinh','Borrowing stock (IHS)'),('health_knowledge','Health knowledge index'),('sanitation_practices','Sanitation practices index')],ARMS[1:],correction='p_holm')
rows=[]
for label,p in policy['vertices'].items():
    spent=sum(costs[a]*q for a,q in p.items())
    rows.append([label.replace('+',' + '),f(spent,2),f(100*sum(q for a,q in p.items() if a!='Control'),2),f(100*p.get('Large',0),2)])
tex_table('policies.tex',['Cash policy','Expected USD',r'Cash coverage (\%)',r'Large-cash share (\%)'],rows)
rob=pd.read_csv(OUT/'robustness.csv')
rows=[]
for spec,label in [('unadjusted','Block controls only'),('equal_households','Equal household weights'),('equal_villages','Equal village weights'),('source_score','Supplied diet score'),('complete_baseline','Observed baseline diet')]:
    s=rob[(rob.spec==spec)&(rob.outcome=='diet_mean')].set_index('policy')
    rows.extend([[label,*[f(s.loc[p,'estimate']) for p in ['Control+Large','Upper+Large']]],['',*['('+f(s.loc[p,'se'])+')' for p in ['Control+Large','Upper+Large']]]])
tex_table('robustness.tex',['','Control + large','Upper + large'],rows)
bounds=pd.read_csv(OUT/'attrition_bounds.csv')
tex_table('attrition_bounds.tex',['Outcome','Cash comparison','Lower bound','Upper bound'],[[r.outcome.replace('diet_mean','Diet').replace('shortfall_6','Shortfall reduction'),r.policy.replace('+',' + '),f(r.lo),f(r.hi)] for r in bounds.itertuples()])
het=pd.read_csv(OUT/'heterogeneity.csv')
rows=[]
for a in ARMS[1:]:
    s=het[het.arm==a].set_index('split')
    rows.extend([[a,*[f(s.loc[k,'estimate']) for k in ['dietarydiversity','consumption_asinh']]],['',*['('+f(s.loc[k,'se'])+')' for k in ['dietarydiversity','consumption_asinh']]],['Holm $p$',*[f(s.loc[k,'p_holm']) for k in ['dietarydiversity','consumption_asinh']]]])
tex_table('heterogeneity.tex',['Arm','Low baseline diet','Low baseline consumption'],rows)
foods=pd.read_csv(OUT/'food_groups.csv')
tex_table('foods.tex',['Food group','Large-cash ITT','SE','Holm $p$'],[[r.food.replace('m9_','').replace('vitaafruits','Vitamin A fruits').replace('vitaveg','Vitamin A vegetables'),f(r.estimate),f(r.se),pf(r.p_holm)] for r in foods[foods.arm=='Large'].itertuples()])
ret=pd.read_csv(OUT/'attrition_effects.csv')
tex_table('retention.tex',['Arm','Observed-diet effect','SE','Holm $p$'],[[r.arm,f(100*r.estimate,2),f(100*r.se,2),pf(r.p_holm)] for r in ret.itertuples()])

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})
colors=['#1a4673','#ab422f']
fig,axes=plt.subplots(1,2,figsize=(7.0,2.8),sharey=True)
for ax,p,color in zip(axes,['Control+Large','Upper+Large'],colors):
    s=pol[(pol.policy==p)&pol.outcome.str.startswith('diet_atleast_')].copy()
    s['z']=s.outcome.str.split('_').str[-1].astype(int);s=s.sort_values('z')
    ax.axhline(0,color='0.4',lw=.8)
    ax.fill_between(s.z,100*s.sim_lo,100*s.sim_hi,color=color,alpha=.12,label='95% simultaneous band')
    ax.errorbar(s.z,100*s.estimate,yerr=np.array([100*(s.estimate-s.lo),100*(s.hi-s.estimate)]),fmt='o-',ms=3,color=color,lw=1,capsize=2,label='Pointwise 95% CI')
    ax.set_title('Gikuriro minus '+p.replace('+',' + ').lower(),fontsize=9)
    ax.set_xlabel('At least this many food groups');ax.set_xticks([2,4,6,8,10,12]);ax.grid(axis='y',color='.9',lw=.5)
axes[0].set_ylabel('Difference (percentage points)');axes[0].legend(frameon=False,fontsize=7)
fig.tight_layout();fig.savefig(FIGS/'diet_thresholds.pdf');fig.savefig(FIGS/'diet_thresholds.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(6.4,3.3))
s=arm[arm.outcome=='diet_mean'].set_index('arm');mu={'Control':0.,**{a:float(s.loc[a,'estimate']) for a in ARMS[1:]}}
xgrid=np.linspace(0,costs['Large'],220);frontier=[]
for b in xgrid:
    vertices=policy_vertices(costs,b)
    vals=[sum(q*mu[a] for a,q in p.items()) for p in vertices.values()]
    frontier.append(max(vals) if vals else 0.)
ax.plot(xgrid,frontier,color=colors[0],lw=1.5,label='Cash lottery envelope (point estimates)')
for a in ARMS[1:]:
    c=colors[1] if a=='Gikuriro' else colors[0]
    ax.errorbar(costs[a],mu[a],yerr=np.array([[mu[a]-s.loc[a,'lo']],[s.loc[a,'hi']-mu[a]]]),fmt='o',color=c,ms=4,capsize=3)
    ax.annotate(a,(costs[a],mu[a]),xytext=(4,8 if a!='Upper' else -14),textcoords='offset points',fontsize=8)
ax.axvline(budget,color='.4',lw=.8,ls='--');ax.axhline(0,color='.5',lw=.6)
ax.set(xlabel='Expected provider cost per eligible household (USD)',ylabel='Diet gain relative to control (food groups)')
ax.legend(frameon=False,fontsize=8,loc='lower right');ax.grid(axis='y',color='.9',lw=.5)
fig.tight_layout();fig.savefig(FIGS/'budget_frontier.pdf');fig.savefig(FIGS/'budget_frontier.png',dpi=180);plt.close(fig)

macros={
    'BaselineN':str(meta['baseline_eligible']),'EndlineN':str(meta['endline_eligible_panel']),
    'DietN':str(int(arm.N.iloc[0])),'BlockN':str(meta['blocks']),'FamilyN':str(meta['family_size']),
    'GikuriroCost':f(budget,2),'LargeCost':f(costs['Large'],2),'UpperCost':f(costs['Upper'],2),
    'LargeCoverage':f(100*policy['vertices']['Control+Large']['Large'],1),
    'UpperLargeShare':f(100*policy['vertices']['Upper+Large']['Large'],2),
    'JointCrit':f(arm.joint_critical.iloc[0],3),
    'HetMinP':f(het.p_holm.min(),3)}
r=ret[ret.arm=='Upper'].iloc[0]
macros.update({'UpperRetention':f(100*r.estimate,2),'UpperRetentionSE':f(100*r.se,2),'UpperRetentionHolmP':pf(r.p_holm)})
for name,frame,key,label,outcome in [
    ('LargeDiet',arm,'arm','Large','diet_mean'),('GikuriroDiet',arm,'arm','Gikuriro','diet_mean'),
    ('ControlLargeDiet',pol,'policy','Control+Large','diet_mean'),('UpperLargeDiet',pol,'policy','Upper+Large','diet_mean'),
    ('LargeShortfall',arm,'arm','Large','shortfall_6'),('ControlLargeShortfall',pol,'policy','Control+Large','shortfall_6'),
    ('GikuriroSaving',sec,'arm','Gikuriro','savingsstock_asinh'),('LargeAssets',sec,'arm','Large','productiveassets_asinh')]:
    r=frame[(frame[key]==label)&(frame.outcome==outcome)].iloc[0]
    for field,suffix in [('estimate','Estimate'),('se','SE'),('lo','Lo'),('hi','Hi'),('p','P')]:macros[name+suffix]=f(r[field],4 if field=='p' else 3)
    if 'sim_lo' in r:
        for field,suffix in [('sim_lo','SimLo'),('sim_hi','SimHi'),('p_max_t','JointP')]:macros[name+suffix]=f(r[field],4 if field=='p_max_t' else 3)
    if 'p_holm' in r:macros[name+'HolmP']=pf(r.p_holm)
macros['UpperLargeBreakEven']=f(max(-float(pol[(pol.policy=='Upper+Large')&(pol.outcome=='diet_mean')]['estimate'].iloc[0]),0))
macros['LargeDietBudgetGain']=f(policy['vertices']['Control+Large']['Large']*mu['Large'])
macros['ProviderSavingUpper']=f(budget-costs['Upper'],2)
macro_text='% Generated by code/build_exhibits.py; never edit manually.\n'+''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in macros.items())
(ROOT/'paper/results.tex').write_text(macro_text,encoding='utf8')
(OUT/'numbers.json').write_text(json.dumps(macros,indent=2),encoding='utf8')
mapping=[
('Table 1','design.tex','attrition.csv; policies.json'),
('Table 2','diet_itt.tex','arm_effects.csv'),
('Table 3','budget_comparisons.tex','policy_effects.csv'),
('Table 4','secondary.tex','secondary.csv'),
('Table 5','baseline.tex','descriptives.csv'),
('Table 6','policies.tex','policies.json'),
('Table 7','robustness.tex','robustness.csv'),
('Table 8','attrition_bounds.tex','attrition_bounds.csv'),
('Table 9','heterogeneity.tex','heterogeneity.csv'),
('Table 10','foods.tex','food_groups.csv'),
('Table 11','retention.tex','attrition_effects.csv'),
('Figure 1','diet_thresholds.pdf','policy_effects.csv'),
('Figure 2','budget_frontier.pdf','arm_effects.csv; policies.json'),
('In-text estimates','results.tex','numbers.json')]
lines=Path(__file__).read_text(encoding='utf8').splitlines()
(ROOT/'docs').mkdir(exist_ok=True)
with (ROOT/'docs/output-map.csv').open('w',newline='',encoding='utf8') as file:
    writer=csv.writer(file);writer.writerow(['exhibit','generated_file','builder','builder_line','estimator','numerical_source'])
    for label,name,source in mapping:
        number=next(i+1 for i,line in enumerate(lines) if name in line)
        generated=('paper/' if name=='results.tex' else 'output/figures/' if name.endswith('.pdf') else 'output/tables/')+name
        writer.writerow([label,generated,'code/build_exhibits.py',number,'code/estimate.py',source])
print('Generated 11 tables, 2 figures, numerical macros.')
