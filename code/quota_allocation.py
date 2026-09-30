"""Verify outcome-selected allocation proposals on one conditional 95% event.

The moment grid uses baseline weights and quotas alone. Directed elementary
arithmetic and feasible LP duals certify the reported support upper bounds.
Stored proposals are approximate exchange-search results; certified minimax
optimality, joint sharpness and unconditional-design coverage are not claimed.
"""
from pathlib import Path
from decimal import Decimal,localcontext,ROUND_CEILING
from fractions import Fraction
import json,time
import numpy as np,pandas as pd
from scipy.optimize import minimize,linprog
from quota_moments import quota_upper_log_moment
from quota_models import build_models,ARMS
from quota_arithmetic import I,tangent_support_upper

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output'
def select_moments():
    begin=time.time();d=pd.read_csv(ROOT/'data/input/households.csv');baseline=d[(d['round']==1)&(d.eligible==1)]
    weights={}
    with localcontext() as ctx:
        ctx.prec=100
        for (block,vid),part in baseline.groupby(['block','vid']):
            weights.setdefault(int(block),[]).append(sum(Decimal.from_float(float(x)) for x in part.samp_wgt))
    village=baseline.groupby(['block','vid']).samp_wgt.sum().reset_index();maximum=village.groupby('block').samp_wgt.max()
    design=pd.read_csv(OUT/'assignment_probabilities.csv');cache={};selected=[];grid=[];kappa=np.log(5520.)
    for arm in ARMS:
        ds=design[design.arm==arm];proxy=sum(float(row.villages)*(maximum.loc[row.block]/row.probability)**2 for row in ds.itertuples())
        base=np.sqrt(8*kappa/proxy);candidates=[]
        for scale in [1.,1.25,1.5,2.]:
            lam=float(scale*base);blocks=[]
            for row in ds.itertuples():
                key=(int(row.block),int(row.villages),lam)
                if key not in cache:cache[key]=quota_upper_log_moment(weights[int(row.block)],int(row.villages),lam)
                bound,detail=cache[key];blocks.append({'block':int(row.block),'upper_log_moment':bound,'detail':detail})
            with localcontext() as ctx:
                ctx.prec=100;ctx.rounding=ROUND_CEILING
                total=sum(Decimal.from_float(row['upper_log_moment']) for row in blocks)
                B=float(np.nextafter(float(total),np.inf))
            record={'arm':arm,'scale':scale,'fixed_lambda_normalized':lam,'certified_upper_log_normalizer':B,
                    'baseline_proxy':float(proxy),'selection_threshold':float((B+kappa)/lam),'blocks':blocks}
            candidates.append(record);grid.append(record)
        chosen=min(candidates,key=lambda row:row['selection_threshold']);selected.append(chosen)
        print(arm,'baseline-selected scale',chosen['scale'],'log normalizer upper',chosen['certified_upper_log_normalizer'],flush=True)
    receipt={'scope':'Fixed four-point grid selected using baseline weights and conditional quotas only. Outward Decimal moment constants, exact integer proxy residuals, positive-sum rounding enclosure and explicit weight drift. No endline outcomes select lambda.',
             'event_terms':276,'event_cap':5520,'rows':selected,'all_grid_receipts':grid,'seconds':time.time()-begin}
    (OUT/'quota-normalizers.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
    return selected

def exact_vertices(cost,budget):
    vertices=[];labels=[]
    for j,c in enumerate(cost):
        if c<=budget:
            labels.append(ARMS[j]);v=[Fraction(0)]*6;v[j]=Fraction(1);vertices.append(v)
    for i,ci in enumerate(cost):
        for j,cj in enumerate(cost):
            if ci<budget<cj:
                mass=(budget-ci)/(cj-ci);v=[Fraction(0)]*6;v[i]=1-mass;v[j]=mass
                labels.append(ARMS[i]+'+'+ARMS[j]);vertices.append(v)
    return labels,vertices

def verify_proposals(models,proposal_rows):
    policies=json.loads((OUT/'policies.json').read_text());cost=[Fraction(policies['costs'][a]) for a in ARMS];budget=Fraction(policies['budget'])
    labels,vertices=exact_vertices(cost,budget);scenarios=[]
    for proposal in proposal_rows:
        name=proposal['objective'];raw=[Fraction(s) if name=='mean' else -Fraction(max(6-s,0),6) for s in range(13)]
        unit=proposal['denominator'];integers=proposal['allocation_numerators'];q=[Fraction(x,unit) for x in integers]
        if min(q)<0 or sum(q)!=1 or sum(c*x for c,x in zip(cost,q))>budget:raise ValueError('Exact rational allocation infeasible')
        receipts=[]
        for label,comparator in zip(labels,vertices):
            tau=float(proposal['support_dual_taus'][label]);upper=I(tau);arm_receipts=[];rounding=Fraction(0)
            if tau<0 or not np.isfinite(tau):raise ValueError('Nonnegative finite dual scale required')
            for arm,m,qa,ra in zip(ARMS,models,q,comparator):
                exact_direction=[(ra-qa)*v for v in raw];direction=np.array([float(v) for v in exact_direction])
                rounding+=max(abs(v-Fraction(float(x))) for v,x in zip(exact_direction,direction))
                def objective(point):
                    logF,grad=m['function'](point);val=np.exp(logF)/5520
                    return -direction@point+tau*val,-direction+tau*val*grad
                constraints=[{'type':'eq','fun':lambda point:point.sum()-1,'jac':lambda point:np.ones(13)},
                             {'type':'ineq','fun':lambda point,m=m:m['b']-m['A']@point,'jac':lambda point,m=m:-m['A']}]
                fit=minimize(lambda point:objective(point)[0],m['seed'],jac=lambda point:objective(point)[1],constraints=constraints,bounds=[(x,1.) for x in m['floor']],method='SLSQP',options={'ftol':1e-12,'maxiter':500})
                _,gradient=objective(fit.x)
                lp=linprog(gradient,A_ub=m['A'],b_ub=m['b'],A_eq=[np.ones(13)],b_eq=[1.],bounds=[(x,None) for x in m['floor']],method='highs')
                if not lp.success:raise ValueError(lp.message)
                bound,receipt=tangent_support_upper(direction,fit.x,m['C'],m['intercept'],tau,5520,m['A'],m['b'],m['floor'],lp.ineqlin.marginals)
                upper+=I(bound);arm_receipts.append({'arm':arm,'SLSQP_success':bool(fit.success),'SLSQP_iterations':int(fit.nit),'candidate':fit.x.tolist(),'direction':direction.tolist(),**receipt})
            round_upper=(I(rounding.numerator)/I(rounding.denominator)).hi;upper+=I(round_upper)
            receipts.append({'comparator':label,'tau':tau,'support_upper':upper.upper_float(),'direction_rounding_upper':str(round_upper),'arms':arm_receipts})
        bound=max(x['support_upper'] for x in receipts)
        # Integer rounding supplies a conservative stable display. No binary
        # float comparison decides which side of the decimal threshold wins.
        with localcontext() as ctx:
            ctx.prec=80;ctx.rounding=ROUND_CEILING
            displayed=Decimal.from_float(bound).quantize(Decimal('.001'))
        scenarios.append({'objective':name,'chosen_allocation_denominator':unit,'chosen_allocation_numerators':dict(zip(ARMS,integers)),
                          'expected_cost_upper':sum((I(float(c))*I(qi.numerator)/I(qi.denominator) for c,qi in zip(cost,q)),I(0)).upper_float(),
                          'conditional_loss_upper':bound,'reported_conservative_loss_upper':str(displayed),'comparators':receipts,
                          'optimization_status':'Proposal selected by exploratory exchange search; a certified minimax optimum or optimization gap is not asserted.'})
        print(name,'conditional loss upper',bound,'conservative display',displayed,flush=True)
    return scenarios

def main():
    start=time.time();moments=select_moments();models,names=build_models(moments)
    proposals=json.loads((ROOT/'code/quota_proposals.json').read_text())['proposals'];scenarios=verify_proposals(models,proposals)
    report={'scope':'Full weighted released baseline, uniform quotas conditional on observed block counts, independent blocks and fixed weights/potential diets. A new standalone 95% exponential-mixture event, not intersection with the earlier 95% finite region. Outward constants and interval convex tangents with feasible LP duals verify data-selected allocations. No sharpness, unconditional design or statistical minimax-regret claim.',
            'event_terms':276,'event_cap':5520,'conditional_failure_probability':'276/5520 = 0.05','transformations':names,
            'scenarios':scenarios,'models':[{'arm':m['arm'],'lambda':m['lambda'],'normalizer_upper':m['normalizer'],'C':m['C'].tolist(),'intercept':m['intercept'].tolist(),'A':m['A'].tolist(),'b':m['b'].tolist(),'bin_floors':m['floor'].tolist()} for m in models],
            'seconds':time.time()-start}
    (OUT/'quota-loss-bound.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    rows=[{'objective':s['objective'],'reported_conservative_loss_upper':s['reported_conservative_loss_upper'],
           'expected_cost_USD':round(s['expected_cost_upper'],6),**{a+'_probability':s['chosen_allocation_numerators'][a]/s['chosen_allocation_denominator'] for a in ARMS}} for s in scenarios]
    pd.DataFrame(rows).to_csv(OUT/'quota_allocations.csv',index=False)
    print('Quota verification seconds',report['seconds'])
if __name__=='__main__':main()
