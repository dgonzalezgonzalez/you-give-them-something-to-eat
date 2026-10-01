"""Joint cross-stratum and all-cash comparisons after the first JDE report.

All tests are exploratory working approximations among potentially selected
observed diets. No finite event, frontier confidence set, or validated sampling
coverage is inferred from these t tests or Holm adjustments.
"""
from pathlib import Path
from fractions import Fraction
import itertools, json
import numpy as np
import pandas as pd
from scipy.stats import t
from estimate import ARMS, regress, holm
from community_decision import load_population, estimates, menus, exact_weight_sum

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'output'

def inference(value, score, df):
    se=float(np.linalg.norm(score)); critical=float(t.ppf(.975,df))
    return {'estimate':float(value),'se':se,'lo':float(value-critical*se),
            'hi':float(value+critical*se),
            'p':float(2*t.sf(abs(value/se),df)) if se>1e-12 else 1.,
            'df':int(df),'coverage_validated':False}

def comparisons(means, scores, df, estimator, menu, tau):
    cross=[]; cash=[]
    objectives={'eligible':(1.,0.),'ineligible':(0.,1.),
                'baseline_weight_aggregate':(tau,1-tau),
                'ineligible_minus_eligible':(-1.,1.)}
    for cost, model in menu.items():
        vertices={name:np.array([float(x) for x in v])
                  for name,v in zip(model['labels'],model['vertices'])}
        for name, v in vertices.items():
            if name=='Gikuriro':continue
            c=np.eye(6)[1]-v
            u=scores[0]@c-scores[1]@c
            cross.append({'estimator':estimator,'cost_convention':cost,
                          'policy':name,'contrast':'ineligible_minus_eligible',
                          'cross_stratum_covariance':float((scores[0]@c)@(scores[1]@c)),
                          'se_if_covariance_omitted':float(np.hypot(np.linalg.norm(scores[0]@c),np.linalg.norm(scores[1]@c))),
                          **inference(c@(means[0]-means[1]),u,df)})
        alternatives=[name for name in vertices if name!='Gikuriro']
        for left,right in itertools.combinations(alternatives,2):
            c=vertices[left]-vertices[right]
            for population,(we,wn) in objectives.items():
                cash.append({'estimator':estimator,'cost_convention':cost,
                             'population':population,'left':left,'right':right,
                             **inference(c@(we*means[1]+wn*means[0]),
                                         (we*scores[1]+wn*scores[0])@c,df)})
    return cross,cash

def adjust(rows, size):
    if len(rows)!=size:raise ValueError('Declared exploratory family changed')
    for row,p in zip(rows,holm([z['p'] for z in rows])):
        row['p_holm']=float(p);row['family_size']=size

def main():
    full,lo,hi,point,counts,assignment,verified=load_population()
    tau=float(exact_weight_sum(full.loc[full.eligible.eq(1),'samp_wgt'])/
              exact_weight_sum(full.samp_wgt))
    _,mu,I=estimates(full,lo,hi,point,assignment)
    cross,cash=comparisons({g:mu[g,'identified_diets'] for g in [0,1]},
                           {g:I[g,'identified_diets'] for g in [0,1]},
                           len(counts)-1,'assignment_weighted_ratios',menus(),tau)
    adjust(cross,16);adjust(cash,224)
    rcross=[];rcash=[];covariance=[]
    for baseline_control in [False,True]:
        means={};scores={};fits={}
        for g in [0,1]:
            keep=full.eligible.eq(g).to_numpy()&full.endline_panel.eq(1).to_numpy()
            sample=full[keep]
            fit=regress(sample,point[keep],sample.dietarydiversity.to_numpy() if baseline_control else None)
            means[g]=np.r_[0.,fit['beta'][1:6]]
            scores[g]=np.column_stack([np.zeros(248),fit['influence'][:,1:6]])
            fits[g]=fit
        estimator='baseline_ancova' if baseline_control else 'block_wls'
        cr,ca=comparisons(means,scores,min(f['df'] for f in fits.values()),estimator,menus(),tau)
        rcross+=cr;rcash+=ca
        # Common village indexing preserves between-equation covariance even
        # though separate stratum regressions have separate CR1 corrections.
        C=np.column_stack([scores[1],scores[0]]).T@np.column_stack([scores[1],scores[0]])
        for i,j in itertools.product(range(12),repeat=2):
            covariance.append({'estimator':estimator,'row_eligible':int(i<6),
                               'row_arm':ARMS[i%6],'column_eligible':int(j<6),
                               'column_arm':ARMS[j%6],'covariance':float(C[i,j])})
    adjust(rcross,32);adjust(rcash,448)
    pd.DataFrame(cross+rcross).to_csv(OUT/'community_cross_stratum.csv',index=False,lineterminator='\n')
    pd.DataFrame(cash+rcash).to_csv(OUT/'community_cash_pairs.csv',index=False,lineterminator='\n')
    pd.DataFrame(covariance).to_csv(OUT/'community_joint_village_covariance.csv',index=False,lineterminator='\n')
    report={'input_hashes':verified,'baseline_eligible_share':tau,
            'families':{'ratio_cross_stratum':16,'regression_cross_stratum':32,
                        'ratio_cash_pairs':224,'regression_cash_pairs':448},
            'scope':'Exploratory, specified after the ninth report. All eight cash/control vertices, both source cost menus, both strata, baseline aggregate and cross-stratum difference are retained. Cash families contain every unordered vertex pair. Ratio t inference uses common 22 block scores and 21 degrees of freedom; its earlier synthetic nominal-coverage failures remain. Regressions use separate-stratum CR1 corrections with common village scores, cross-equation covariance and minimum stratum G-1 degrees of freedom. No selection correction, original-law recovery, finite coverage or confidence set for switches is claimed.',
            'finite_frontier_scope':'Existing standalone classical and quota boxes each admit all six arm means equal to five in both strata. Every feasible allocation can tie. Neither box certifies a unique cash frontier or switch.',
            'n_cross_stratum':len(cross+rcross),'n_cash_pairs':len(cash+rcash)}
    (OUT/'community-uncertainty.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    selected=pd.DataFrame(cross+rcross)
    print(selected[selected.cost_convention.eq('cost_eligible')&selected.policy.isin(['Lower+Large','Upper'])][['estimator','policy','estimate','se','p','p_holm','cross_stratum_covariance']].to_string(index=False))
    print('All declared contrasts retained:',report['n_cross_stratum'],report['n_cash_pairs'])

if __name__=='__main__':main()
