"""Existing-data method comparison; does not change the submitted event.

All rows use the same outcome targets, missing-item bounds, score functions,
costs and rational proposals. Classical moments follow Hoeffding, Serfling,
and the unrelaxed forward-martingale sum in Bardenet and Maillard (2015).
Results compare certificates for fixed proposals, not method-wise optima.
"""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal,localcontext,ROUND_CEILING
import json,time,copy
import numpy as np,pandas as pd
from scipy.optimize import linprog,minimize,minimize_scalar
from quota_arithmetic import I,lp_dual_lower
from quota_models import build_models,ARMS
from quota_allocation import verify_proposals,exact_vertices
from weighted_product_moments import product_log_float,product_log_upper

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'

def fraction_interval(x):
    return I(x.numerator)/I(x.denominator)

def range_coefficient(n,k,method):
    """Return exact V/Wmax**2 for log MGF <= lambda**2 V/8."""
    if not 1<=k<=n:raise ValueError('Invalid quota')
    if k==n:return Fraction(0)
    def forward(j):
        if method=='hoeffding':return Fraction(n*n,j)
        if method=='serfling':return Fraction(n*n,j)*(1-Fraction(j-1,n))
        if method=='harmonic_martingale':
            return Fraction(n*n*(n-j)**2,j*j)*sum((Fraction(1,(n-t)**2) for t in range(1,j+1)),Fraction(0))
        raise ValueError('Unknown range moment')
    # G_k = -(n-k)/k G_(n-k), for the complementary subset.
    return min(forward(k),Fraction((n-k)**2,k*k)*forward(n-k))

def baseline_weights():
    d=pd.read_csv(ROOT/'data/input/households.csv')
    b=d[(d['round']==1)&(d.eligible==1)]
    result={}
    with localcontext() as ctx:
        ctx.prec=100
        for (block,vid),part in b.groupby(['block','vid']):
            result.setdefault(int(block),[]).append(sum(Decimal.from_float(float(x)) for x in part.samp_wgt))
    return result

def classical_rows(method,fixed_lambdas=None):
    weights=baseline_weights();design=pd.read_csv(OUT/'assignment_probabilities.csv');rows=[]
    for arm in ARMS:
        variance=I(0)
        for entry in design[design.arm==arm].itertuples():
            n=int(entry.block_villages);k=int(entry.villages)
            variance+=fraction_interval(range_coefficient(n,k,method))*I(max(weights[int(entry.block)]))*I(max(weights[int(entry.block)]))
        # Choice need not be rounded outwards: every nonnegative fixed lambda
        # has its own enclosed moment bound. Only baseline quantities enter.
        lam=float(np.sqrt(8*np.log(5520.)/float(variance.hi))) if fixed_lambdas is None else fixed_lambdas[arm]
        B=(I(lam)*I(lam)*variance/I(8)).upper_float()
        rows.append({'arm':arm,'fixed_lambda_normalized':lam,'certified_upper_log_normalizer':B,
                     'variance_proxy_upper':str(variance.hi),'method':method})
    return rows

def weight_sensitive_rows(hybrid=False):
    """Select each arm's scale from baseline design, then enclose all moments.

    The hybrid takes a minimum of two bounds on the same block moment before
    observing any endpoint. It does not intersect confidence regions.
    """
    weights=baseline_weights();design=pd.read_csv(OUT/'assignment_probabilities.csv');rows=[]
    for arm in ARMS:
        blocks=[(weights[int(r.block)],int(r.villages),range_coefficient(int(r.block_villages),int(r.villages),'harmonic_martingale'))
                for r in design[design.arm==arm].itertuples()]
        V=sum(float(coef)*float(max(w))**2 for w,k,coef in blocks)
        base=float(np.sqrt(8*np.log(5520.)/V));cache={}
        def diagnostic(loglam):
            lam=float(np.exp(loglam))
            B=sum(product_log_float(w,k,lam,coef if hybrid else None) for w,k,coef in blocks)
            value=(B+np.log(5520.))/lam;cache[lam]=value
            return value
        for scale in [.5,.75,1.,1.25,1.5,2.]:diagnostic(np.log(base*scale))
        minimize_scalar(diagnostic,bounds=(np.log(base/1000),np.log(base*100)),method='bounded',options={'xatol':1e-8,'maxiter':64})
        lam=min(cache,key=cache.get)
        B=sum((I(product_log_upper(w,k,lam,coef if hybrid else None)) for w,k,coef in blocks),I(0)).upper_float()
        rows.append({'arm':arm,'fixed_lambda_normalized':lam,'certified_upper_log_normalizer':B,
                     'method':'weight_sensitive_product_harmonic' if hybrid else 'weight_sensitive_product',
                     'baseline_scale_selection':{'bounds_relative_to_harmonic':[.001,100.],
                         'candidate_evaluations':len(cache),'floating_radius_numerator':cache[lam],
                         'scope':'Baseline-only floating search selects a fixed valid lambda; neither global optimality nor a numerical certificate is inferred from its diagnostic.'}})
    return rows

def empirical_bernstein_rows():
    from empbern_quota import select_empbern_scale
    weights=baseline_weights();design=pd.read_csv(OUT/'assignment_probabilities.csv');rows=[]
    for arm in ARMS:
        blocks=[(weights[int(r.block)],int(r.villages)) for r in design[design.arm==arm].itertuples()]
        selection=select_empbern_scale(blocks,5520)
        rows.append({'arm':arm,'fixed_lambda_normalized':selection['lambda'],'certified_upper_log_normalizer':0.,
                     'method':'empirical_bernstein_fixed_forecast','baseline_scale_selection':selection['scale_search'],
                     'normalizer_scope':'No fixed log-normalizer is used. build_models regenerates per-score directed empirical compensation and averages all assigned-village orders; affine coefficients use total fixed population weight rather than the realized HT denominator.'})
    return rows

def label_source_search(proposals):
    """Retain provenance without attributing quota diagnostics to other methods."""
    result=copy.deepcopy(proposals)
    for proposal in result:
        diagnostic={key:proposal.pop(key) for key in ['exploratory_search_upper','exploratory_search_gap'] if key in proposal}
        if diagnostic:proposal['source_quota_proposal_search_diagnostic']={
            'moment_method':'quota','diagnostic':diagnostic,
            'scope':'Historical floating search that supplied the common rational proposal. Not this comparator method\'s search result or a certified optimality gap.'}
    return result

def separate_support(models,proposals):
    policies=json.loads((OUT/'policies.json').read_text());cost=[Fraction(policies['costs'][a]) for a in ARMS]
    labels,vertices=exact_vertices(cost,Fraction(policies['budget']));results=[]
    # e_j <= 5520 is a Bonferroni region for the same 276 e-values. The
    # shared event implies every individual inequality, so this ablation is
    # nested with the shared region when constants and bin floors are fixed.
    with localcontext() as ctx:
        ctx.prec=80
        upper_logcap=Decimal(5520).ln().next_plus()
    for proposal in proposals:
        q=[Fraction(x,proposal['denominator']) for x in proposal['allocation_numerators']]
        raw=[Fraction(s) if proposal['objective']=='mean' else -Fraction(max(6-s,0),6) for s in range(13)]
        comparator_bounds=[]
        for label,v in zip(labels,vertices):
            bound=I(0);rounding=Fraction(0)
            for model,qa,va in zip(models,q,v):
                exact=[(va-qa)*x for x in raw];direction=np.array([float(x) for x in exact])
                rounding+=max(abs(x-Fraction(float(y))) for x,y in zip(exact,direction))
                A=np.r_[model['A'],model['C']]
                # Subtraction is also outward, so this defines an enlarged
                # polytope containing the conceptual Bonferroni event.
                b=np.r_[model['b'],[(I(upper_logcap)-I(x)).upper_float() for x in model['intercept']]]
                fit=linprog(-direction,A_ub=A,b_ub=b,A_eq=[np.ones(13)],b_eq=[1.],bounds=[(x,None) for x in model['floor']],method='highs')
                if not fit.success:raise ValueError(fit.message)
                lower,_=lp_dual_lower(-direction,A,b,model['floor'],fit.ineqlin.marginals)
                bound-=I(lower)
            bound+=fraction_interval(rounding)
            comparator_bounds.append({'comparator':label,'support_upper':bound.upper_float()})
        results.append({'objective':proposal['objective'],'conditional_loss_upper':max(x['support_upper'] for x in comparator_bounds),'comparators':comparator_bounds})
    return results

def select_support_taus(models,proposals):
    """Diagnostic candidates choose deterministic support duals, not events."""
    policies=json.loads((OUT/'policies.json').read_text());cost=[Fraction(policies['costs'][a]) for a in ARMS]
    labels,vertices=exact_vertices(cost,Fraction(policies['budget']));chosen=copy.deepcopy(proposals);diagnostics=[]
    for proposal in chosen:
        q=[Fraction(x,proposal['denominator']) for x in proposal['allocation_numerators']]
        raw=[Fraction(s) if proposal['objective']=='mean' else -Fraction(max(6-s,0),6) for s in range(13)]
        for label,v in zip(labels,vertices):
            directions=[np.array([float((va-qa)*x) for x in raw]) for qa,va in zip(q,v)];cache={}
            def candidate(tau):
                tau=float(tau)
                if tau in cache:return cache[tau]
                bound=tau
                for m,d in zip(models,directions):
                    def obj(point):
                        logF,grad=m['function'](point);F=np.exp(logF)/5520
                        return -d@point+tau*F,-d+tau*F*grad
                    fit=minimize(lambda p:obj(p)[0],m['seed'],jac=lambda p:obj(p)[1],constraints=[
                        {'type':'eq','fun':lambda p:p.sum()-1,'jac':lambda p:np.ones(13)},
                        {'type':'ineq','fun':lambda p,m=m:m['b']-m['A']@p,'jac':lambda p,m=m:-m['A']}],
                        bounds=[(x,1.) for x in m['floor']],method='SLSQP',options={'ftol':1e-10,'maxiter':250})
                    value,gradient=obj(fit.x)
                    lp=linprog(gradient,A_ub=m['A'],b_ub=m['b'],A_eq=[np.ones(13)],b_eq=[1.],bounds=[(x,None) for x in m['floor']],method='highs')
                    if not lp.success:raise ValueError(lp.message)
                    # Used only to choose tau. The subsequent directed
                    # verifier, not this floating diagnostic, reports bounds.
                    bound-=value-gradient@fit.x+lp.fun
                cache[tau]=bound;return bound
            candidate(proposal['support_dual_taus'][label])
            minimize_scalar(candidate,bounds=(.0001,30.),method='bounded',options={'xatol':1e-5,'maxiter':24})
            tau=min(cache,key=cache.get);proposal['support_dual_taus'][label]=tau
            diagnostics.append({'objective':proposal['objective'],'comparator':label,'selected_tau':tau,'candidate_evaluations':len(cache),'floating_upper':cache[tau]})
    return chosen,diagnostics

def main():
    start=time.time();original=json.loads((OUT/'quota-normalizers.json').read_text())['rows']
    proposals=label_source_search(json.loads((ROOT/'code/quota_proposals.json').read_text())['proposals']);rows=[];receipts=[]
    fixed={x['arm']:x['fixed_lambda_normalized'] for x in original}
    settings=[('quota','shared',True,original),('quota','separate',True,original),('quota','shared',False,original)]
    for method in ['hoeffding','serfling','harmonic_martingale']:
        for scales in ['baseline_optimized']:
            settings.append((method+'_'+scales,'shared',True,classical_rows(method,fixed if scales=='quota_fixed' else None)))
    settings.extend([('weight_sensitive_product_baseline_optimized','shared',True,weight_sensitive_rows()),
                     ('weight_sensitive_hybrid_baseline_optimized','shared',True,weight_sensitive_rows(hybrid=True)),
                     ('empirical_bernstein_fixed_forecast','shared',True,empirical_bernstein_rows())])
    for method,event,floors,moments in settings:
        models,_=build_models(moments)
        if not floors:
            # Keeping the same logical scalar restrictions isolates only the
            # extra assigned identified-score mass, not all consistency.
            models=[{**m,'floor':np.zeros(13)} for m in models]
        selected,diagnostics=(select_support_taus(models,proposals) if event=='shared' and (method!='quota' or not floors) else (proposals,[]))
        results=verify_proposals(models,selected) if event=='shared' else separate_support(models,selected)
        for result in results:
            row={'moment_method':method,'event':event,'bin_floors':floors,'objective':result['objective'],
                 'fixed_proposal_loss_upper':result['conditional_loss_upper']}
            rows.append(row);print(json.dumps(row),flush=True)
        receipts.append({'method':method,'event':event,'bin_floors':floors,'moments':moments,'support_scale_selection':diagnostics,'selected_proposals':selected,'scenarios':results})
    report={'scope':'Same existing-data rational proposals, costs, targets, missing-item envelopes and 23 transformations. Baseline-only moment/scale alternatives; independently valid 95% events, never intersected or selected by observed tighter bound. Shared/separate and bin-floor ablations use the same quota constants. Upper certificates are enclosed; no method-specific minimax optima or global superiority asserted.',
            'sources':['https://arxiv.org/pdf/1309.4029','https://doi.org/10.1214/aos/1176346079','https://proceedings.neurips.cc/paper_files/paper/2020/file/e96c7de8f6390b1e6c71556e4e0a4959-Paper.pdf','https://www.alrw.net/e/02.pdf'],
            'rows':rows,'receipts':receipts,'seconds':time.time()-start}
    (OUT/'quota-benchmarks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    displayed=[]
    with localcontext() as ctx:
        ctx.prec=80;ctx.rounding=ROUND_CEILING
        for row in rows:
            displayed.append({k:v for k,v in row.items() if k!='fixed_proposal_loss_upper'}|
                {'reported_conservative_loss_upper':str(Decimal.from_float(row['fixed_proposal_loss_upper']).quantize(Decimal('.001')))})
    pd.DataFrame(displayed).to_csv(OUT/'quota_benchmarks.csv',index=False)
    print('Benchmark seconds',report['seconds'],flush=True)

if __name__=='__main__':main()
