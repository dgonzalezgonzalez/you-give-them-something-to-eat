"""Meaningful finite-bound and decision checks, distinct from failed coverage.

Small exhaustive assignments test the conditional inversion and exponential
comparison. Published LPs are checked against independent primal adversaries.
No Monte Carlo diagnostic is mislabeled an actual Rwanda coverage guarantee.
"""
from pathlib import Path
import itertools,json
import numpy as np
import pandas as pd
from scipy.optimize import linprog
from blocked_inference import bounded_hajek_outer,referee_counterexample
from policy_allocation import region,vector,fitted_arm
from estimate import ARMS

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'

def main():
    checks={};max_mgf_violation=0.
    population=np.array([-3.,-1.,2.,5.])
    # A nontrivial convex-order check, with negative as well as positive lambda.
    for size in [1,2,3,4]:
        sums=np.array([sum(population[list(c)]) for c in itertools.combinations(range(4),size)])
        for lam in [-1.,-.25,0.,.25,1.]:
            without=np.mean(np.exp(lam*sums));withrep=np.mean(np.exp(lam*population))**size
            max_mgf_violation=max(max_mgf_violation,float(without-withrep))
    checks['exhaustive_without_replacement_exponential_comparison']=max_mgf_violation<1e-10
    frame=pd.DataFrame({'block':np.repeat([1,2],4),'vid':np.arange(8),'samp_wgt':[1.,2.,4.,3.,2.,5.,1.,3.]})
    potential=np.array([[0,8],[2,7],[12,3],[4,6],[1,10],[9,2],[3,11],[6,4]],dtype=float)
    observed=np.array([[1,1],[0,1],[1,0],[1,1],[1,0],[1,1],[0,1],[1,1]],dtype=bool)
    assign={a:{1:.5,2:.5} for a in ['A','B']};covered=0;total=0;scale_error=0.
    true=(frame.samp_wgt.to_numpy()[:,None]*observed*potential).sum(axis=0)/(frame.samp_wgt.to_numpy()[:,None]*observed).sum(axis=0)
    selections=list(itertools.combinations(range(4),2))
    for left,right in itertools.product(selections,selections):
        sample=frame.copy();labels=np.ones(8,dtype=int);labels[list(left)+[i+4 for i in right]]=0
        sample['arm']=np.array(['A','B'])[labels]
        values=potential[np.arange(8),labels].copy();values[~observed[np.arange(8),labels]]=np.nan
        point,lo,hi,_=bounded_hajek_outer(sample,values,assign,['A','B'],frame,(0,12),multiplicity=2)
        covered+=int(np.all((true>=lo-1e-12)&(true<=hi+1e-12)));total+=1
        scaled=sample.copy();scaled.samp_wgt*=73.;scaled_frame=frame.copy();scaled_frame.samp_wgt*=73.
        p2,l2,h2,_=bounded_hajek_outer(scaled,values,assign,['A','B'],scaled_frame,(0,12),multiplicity=2)
        scale_error=max(scale_error,float(np.nanmax(np.abs(np.r_[point-p2,lo-l2,hi-h2]))))
    checks['finite_ratio_inversion_exhaustive_36_assignments']=covered==total==36
    checks['finite_intervals_weight_scale_invariant']=scale_error<1e-11
    # Entirely unobserved outcomes produce full support rather than division.
    _,lo,hi,_=bounded_hajek_outer(sample,np.full(8,np.nan),assign,['A','B'],frame,(0,12),multiplicity=2)
    checks['zero_denominator_full_support']=bool(np.array_equal(lo,[0,0]) and np.array_equal(hi,[12,12]))
    checks['exact_cross_arm_referee_counterexample']=np.isclose(referee_counterexample()['independent_to_true_ratio'],.9)
    finite=pd.read_csv(OUT/'finite_arm_regions.csv');checks['finite_endpoint_order']=bool((finite.finite_lower<=finite.finite_upper+1e-12).all())
    p=json.loads((OUT/'policies.json').read_text());base={'Gikuriro':{'Gikuriro':1.},**p['vertices']}
    certificates=pd.read_csv(OUT/'allocation_certificates.csv');maxgap=0.
    for r in certificates.itertuples():
        A,b=region(r.objective,r.method,r.scope,base)
        q=np.array([getattr(r,a+'_probability') for a in ARMS])
        adverse=[]
        for comparator in base.values():
            fit=linprog(-(vector(comparator)-q),A_ub=A,b_ub=b,bounds=[(None,None)]*6,method='highs')
            assert fit.success;adverse.append(-fit.fun)
        maxgap=max(maxgap,abs(max(adverse)-r.optimized_certificate))
    checks['eight_certificates_independent_primal_adversaries']=maxgap<1e-8
    checks['diversification_no_worse_than_best_vertex']=bool((certificates.optimized_certificate<=certificates.best_vertex_certificate+1e-10).all())
    scenarios=pd.read_csv(OUT/'allocation_cost_sensitivity.csv');settings=json.loads((OUT/'cost_inputs.json').read_text())
    checks['32_cost_cases_recomputed_both_methods']=len(scenarios)==64 and scenarios.scenario.nunique()==32
    checks['scenario_feasibility']=all(abs(sum(getattr(r,a+'_probability') for a in ARMS)-1)<1e-9 and sum(getattr(r,a+'_probability')*settings[r.scenario]['costs'][a] for a in ARMS)<=r.budget+1e-8 for r in scenarios.itertuples())
    c=pd.read_csv(OUT/'child_cohort_accounting.csv');info=json.loads((OUT/'child-cohort-metadata.json').read_text())
    checks['child_due_cohort_partition']=int(c.all_endline_due.sum())==info['endline_due_baseline_cohort']+info['endline_due_outside_baseline_cohort']
    checks['child_cohort_membership_precedes_endline']=bool((c.baseline_flagged_cohort>=c.linked_endline_rows).all() and (c.linked_endline_rows>=c.baseline_cohort_measured_endline).all())
    stress=json.loads((OUT/'blocked-validation.json').read_text())
    checks['failed_block_coverage_retained']=stress['coverage_certified'] is False and min(x['joint_coverage'] for x in stress['simulation_cases'])<.8
    source=(ROOT/'paper/paper.tex').read_text(encoding='utf8')
    import re
    defined=set(re.findall(r'\\label\{([^}]+)\}',source));used=set(re.findall(r'\\ref\{([^}]+)\}',source))
    checks['all_manuscript_references_defined']=used<=defined
    report={'checks':{k:bool(v) for k,v in checks.items()},'all_passed':bool(all(checks.values())),
            'exhaustive_assignment_coverage':[covered,total],'max_weight_scale_error':scale_error,
            'max_exponential_moment_violation':max_mgf_violation,'max_primal_certificate_gap':maxgap,
            'scope':'Implementation and finite-bound sanity checks; exhaustive small fixture is not proof of actual sample representativeness. Exploratory multiplier undercoverage is retained, not certified.'}
    (OUT/'decision-validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('Decision validation:',sum(checks.values()),'/',len(checks),'passed')
    if not report['all_passed']:raise AssertionError(report)

if __name__=='__main__':main()
