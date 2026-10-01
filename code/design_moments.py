"""Common, baseline-only scale search for designed scalar comparisons.

Floating search selects a fixed lambda. Directed moments and divisions report
the radius; no optimum is inferred from the scalar optimizer's termination.
"""
import numpy as np
from scipy.optimize import minimize_scalar
from quota_arithmetic import I
from quota_benchmarks import range_coefficient,fraction_interval
from quota_moments import quota_log_moment_dp_float,quota_upper_log_moment_dp
from weighted_product_moments import product_log_float,product_log_upper,ilog

METHODS=['quota','harmonic_martingale','weight_sensitive_product','weight_sensitive_hybrid']

def select_scalar_moment(weights,k,blocks,cap,method):
    n=len(weights);coef=range_coefficient(n,k,'harmonic_martingale');maximum=max(weights)
    penalty=float(np.log(cap));base=float(np.sqrt(8*penalty/(blocks*float(coef)*float(maximum)**2)))
    cache={}
    def floating_B(lam):
        if method=='quota':return quota_log_moment_dp_float(weights,k,lam)
        if method=='harmonic_martingale':return lam*lam/8*float(coef)*float(maximum)**2
        if method in ['weight_sensitive_product','weight_sensitive_hybrid']:
            return product_log_float(weights,k,lam,coef if method=='weight_sensitive_hybrid' else None)
        raise ValueError('Unknown method')
    def diagnostic(loglam):
        lam=float(np.exp(loglam));value=(blocks*floating_B(lam)+penalty)/lam
        cache[lam]=value;return value
    for scale in [.5,.75,1.,1.25,1.5,2.]:diagnostic(np.log(base*scale))
    minimize_scalar(diagnostic,bounds=(np.log(base/1000),np.log(base*100)),method='bounded',options={'xatol':1e-8,'maxiter':64})
    lam=min(cache,key=cache.get)
    if method=='quota':B,detail=quota_upper_log_moment_dp(weights,k,lam)
    elif method=='harmonic_martingale':
        B=(I(lam)*I(lam)*fraction_interval(coef)*I(maximum)*I(maximum)/I(8)).upper_float();detail={}
    else:
        B=product_log_upper(weights,k,lam,coef if method=='weight_sensitive_hybrid' else None);detail={}
    numerator=(I(blocks)*I(B)+ilog(I(cap)))/I(lam)
    radius=numerator/(I(blocks)*sum((I(w) for w in weights),I(0)))
    return {'method':method,'lambda':lam,'block_log_moment_upper':B,
            'radius_upper':radius.upper_float(),'radius_numerator_upper':str(numerator.hi),
            'scale_search':{'bounds_relative_to_harmonic':[.001,100.],
                'candidate_evaluations':len(cache),'floating_numerator':cache[lam],
                'scope':'Same baseline-only search bounds and six initial scales for every method. Diagnostic candidates, not certified global minimizers.'},
            'moment_receipt':detail}
