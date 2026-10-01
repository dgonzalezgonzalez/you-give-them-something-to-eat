"""Corrected-release parent-style population bridge, not historical replication.

Source-selected controls are fixed from the released CovariateLists.xlsx. No
selection is rerun. Historical 2020 population code/control lists are unavailable.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from estimate import ARMS, TX
from community_decision import load_population, estimates, menus, exact_weight_sum
from referee_revision import GROUPS, score_interval
from blocked_inference import hajek_block

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
CONTROLS=['Ldietarydiversity','dietarydiversity_R1','Lhh_wealth_asinh',
          'Lvill_eligible_ratio','Lsavingsstock_asinh3',
          'Lconsumpti_x_Lproductiv','Lconsumpti_x_Lselfcostd']

def wls(d,y,controls,pool=False,cost_linear=None,common=None):
    X=[np.ones(len(d)),d.treat_GK.to_numpy()]
    if cost_linear is not None:
        X += [d[TX].sum(axis=1).to_numpy(),cost_linear]
    elif pool:
        X += [d[TX[1:4]].sum(axis=1).to_numpy(),d[TX[4]].to_numpy()]
    else:X += [d[k].to_numpy() for k in TX[1:]]
    X += [d[k].to_numpy() for k in controls]
    X += [d.eligible.to_numpy()]
    b=pd.get_dummies(d.block,drop_first=True,dtype=float)
    X += [b[k].to_numpy() for k in b]
    X=np.column_stack(X);keep=np.isfinite(y)&np.isfinite(X).all(axis=1)
    if common is not None:keep &= common
    X=X[keep];y=y[keep];w=d.loc[keep,'samp_wgt'].to_numpy()
    # Source lag and R1 columns can be collinear; preserve ordered independent
    # columns, documenting rather than pretending to reestimate lasso selection.
    selected=[]
    for i in range(X.shape[1]):
        if np.linalg.matrix_rank(X[:,selected+[i]])>len(selected):selected.append(i)
    reduced=X[:,selected]; bread=np.linalg.inv(reduced.T@(w[:,None]*reduced))
    fit=bread@(reduced.T@(w*y));beta=np.zeros(X.shape[1]);beta[selected]=fit
    residual=y-reduced@fit;score=np.zeros((248,len(selected)))
    np.add.at(score,d.loc[keep,'vid'].to_numpy(int)-1,reduced*(w*residual)[:,None])
    G=d.loc[keep,'vid'].nunique();N=len(y);K=len(selected)
    influence=np.zeros((248,X.shape[1]))
    influence[:,selected]=(score@bread)*np.sqrt(G/(G-1)*(N-1)/(N-K))
    return beta,influence,keep,K

def main():
    full,lo,hi,point,counts,assignment,verified=load_population()
    core=pd.read_csv(ROOT/'data/input/households.csv')
    aux=pd.read_csv(ROOT/'data/input/revision_households.csv')
    d=core.merge(aux[['hhid','round',*[k for k in aux if k not in core]]],on=['hhid','round'],validate='one_to_one')
    d=d[d['round'].eq(2)&d.sample_panel.eq(1)].copy()
    l,h=score_interval(d);identified=(l+h)/2;identified[l!=h]=np.nan
    source=d.diet_source.to_numpy();complete=d.dietarydiversity.to_numpy()
    common=np.isfinite(source)&np.isfinite(identified)
    stages=[('source_pooled_controls',source,CONTROLS,True,None),
            ('source_split_controls',source,CONTROLS,False,None),
            ('source_split_common',source,CONTROLS,False,common),
            ('item_split_common',identified,CONTROLS,False,common),
            ('item_split_controls',identified,CONTROLS,False,None),
            ('item_split_lag_complete',identified,['dietarydiversity_R1'],False,None),
            ('complete_module_split_lag',complete,['dietarydiversity_R1'],False,None)]
    rows=[];stats=[]
    for name,y,controls,pool,restrict in stages:
        beta,I,keep,K=wls(d,y,controls,pool=pool,common=restrict)
        for a in ARMS[1:]:
            ix=1 if a=='Gikuriro' else (3 if a=='Large' else 2) if pool else ARMS.index(a)
            rows.append({'stage':name,'arm':a,'effect':float(beta[ix]),'village_se':float(np.linalg.norm(I[:,ix])),
                         'N':int(keep.sum()),'rank':K,'pooled_small_cash':pool})
        stats.append({'stage':name,'N':int(keep.sum()),'eligible_N':int(d.loc[keep,'eligible'].sum()),
                      'ineligible_N':int((1-d.loc[keep,'eligible']).sum()),
                      'respondent_eligible_weight_share':float(d.loc[keep&d.eligible.eq(1),'samp_wgt'].sum()/d.loc[keep,'samp_wgt'].sum())})
    # The 2020 text describes village-population cost equivalence. The corrected
    # code defines a TCE regressor but does not execute that historical estimator.
    # This is an explicit reconstruction of the described linear specification.
    model=menus()['cost_population'];delta=np.zeros(len(d))
    for i,a in enumerate(ARMS[1:],1):
        if a!='Gikuriro':delta[d[TX[i-1]].eq(1)]=(float(model['costs'][i])-float(model['budget']))/100
    beta,I,keep,K=wls(d,source,CONTROLS,cost_linear=delta)
    linear={'scope':'Corrected-release reconstruction of described 2020 population cost-linear specification; not historical executable replay. Fixed current source-selected controls, eligibility indicator, blocks, source-score selected panel and village CR1. Cost regressor centered at published Gikuriro population cost.',
            'N':int(keep.sum()),'rank':K,'gikuriro_minus_cost_equivalent_cash':float(beta[1]),
            'village_se':float(np.linalg.norm(I[:,1])),
            'cost_equivalent_cash_effect':float(beta[2]),'cash_slope_per_100_dollars':float(beta[3])}
    _,means,_=estimates(full,lo,hi,point,assignment)
    tau=float(exact_weight_sum(full.loc[full.eligible.eq(1),'samp_wgt'])/exact_weight_sum(full.samp_wgt))
    pooled,_I,_info=hajek_block(full,point,assignment,ARMS)
    aggregate=tau*means[1,'identified_diets']+(1-tau)*means[0,'identified_diets']
    ratios=[{'arm':a,'pooled_respondent_ratio':float(pooled[i]),
             'baseline_share_stratum_ratios':float(aggregate[i]),
             'aggregation_difference':float(aggregate[i]-pooled[i])} for i,a in enumerate(ARMS)]
    costs=pd.read_csv(ROOT/'data/input/costs.csv');costrows=[]
    for r in costs.itertuples():
        eligible=r.cost_beneficiary*(1-r.share_averted+r.share_averted*r.compliance_eligibles)
        population=r.cost_beneficiary*r.compliance_population
        costrows.append({'arm':r.treatment,'eligible_formula':eligible,'source_cost_eligible':r.cost_eligible,
                         'population_formula':population,'source_cost_population':r.cost_population,
                         'eligible_formula_residual':r.cost_eligible-eligible,
                         'population_formula_residual':r.cost_population-population,
                         'baseline_share_times_eligible_cost':tau*r.cost_eligible,
                         'population_to_eligible_cost_ratio':r.cost_population/r.cost_eligible,
                         'implied_ineligible_receipt_rate_if_same_baseline_frame':(r.compliance_population-tau*r.compliance_eligibles)/(1-tau)})
    pd.DataFrame(rows).to_csv(OUT/'population_parent_crosswalk.csv',index=False,lineterminator='\n')
    pd.DataFrame(ratios).to_csv(OUT/'population_aggregation_bridge.csv',index=False,lineterminator='\n')
    pd.DataFrame(costrows).to_csv(OUT/'population_cost_bridge.csv',index=False,lineterminator='\n')
    report={'input_hashes':verified,'stages':stats,'linear_population_cost_reconstruction':linear,
            'source_controls':CONTROLS,'baseline_eligible_share':tau,
            'historical_comparison':{'2020_table_VIII_diet':{'Gikuriro':.12,'Main':0.,'Large':-.28,'N':2718},
              'scope':'Published historical numbers are contextual, not expected validation targets. Current corrected data and selected controls differ; historical population code/control list unavailable in corrected release.'},
            'cost_scope':'Eligible formula reflects nonaverted and participation-dependent components. Cash population columns numerically match beneficiary cost times population participation up to source rounding. Gikuriro differs by about 1.482 dollars: its additional population accounting cannot be recovered from the numeric workbook alone, which contains values rather than formulas. This residual is retained, not attributed to rounding or a verified overhead rule. Implied ineligible receipt rates are conditional accounting, not verified linked receipt. Population column is not baseline share times eligible costs, nor a marginal mixed-rollout cost.'}
    (OUT/'population-crosswalk.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(pd.DataFrame(rows).pivot(index='stage',columns='arm',values='effect').to_string())
    print(json.dumps(linear,indent=2));print(pd.DataFrame(ratios).to_string(index=False))

if __name__=='__main__':main()
