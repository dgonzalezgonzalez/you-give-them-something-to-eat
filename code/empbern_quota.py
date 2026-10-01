"""Fixed-forecast empirical-Bernstein adaptation of established WoR tests.

Source: Waudby-Smith and Ramdas (2020), Theorem 3.2 / Appendix B.3.
Scales are baseline-only; compensation uses realized bounded observations.
Uniform sample ordering is essential. Field code averages every observed
order; designed experiments explicitly randomize it. No full betting-family
optimality or new concentration theorem is claimed.
"""
from decimal import Decimal,ROUND_FLOOR
from fractions import Fraction
import itertools
import numpy as np
from scipy.optimize import minimize_scalar
from quota_arithmetic import I,calc
from weighted_product_moments import ilog
from quota_benchmarks import range_coefficient,fraction_interval

DYADIC=2**50

def select_empbern_scale(blocks,cap):
    """An explicitly heuristic, outcome-free variance proxy selects lambda.

    The proxy assumes a unit-range uniform score for scale selection only.
    Every permitted fixed lambda is valid even when that heuristic is wrong.
    """
    V=sum(float(range_coefficient(len(w),k,'harmonic_martingale'))*float(max(w))**2 for w,k in blocks)
    base=np.sqrt(8*np.log(cap)/V);limit=min(k/(len(w)*float(max(w))) for w,k in blocks)
    cache={}
    def diagnostic(loglam):
        lam=float(np.exp(loglam));penalty=0.
        for w,k in blocks:
            w=np.asarray(w,dtype=float);n=len(w);maximum=max(w)
            gamma=w.mean()/(2*maximum)
            variance=np.mean((w/(2*maximum)-gamma)**2)+np.mean((w/maximum)**2)/12
            theta=lam*n/k*maximum*(n-k)/(n-np.arange(1,k+1))
            penalty+=float(np.sum(-np.log1p(-theta)-theta))*variance
        result=(penalty+np.log(cap))/lam;cache[lam]=result;return result
    lower=min(base/1000,limit/1000);upper=.95*limit
    for scale in [.5,.75,1.,1.25,1.5,2.]:diagnostic(np.log(min(base*scale,upper)))
    minimize_scalar(diagnostic,bounds=(np.log(lower),np.log(upper)),method='bounded',options={'xatol':1e-8,'maxiter':64})
    lam=min(cache,key=cache.get)
    return {'method':'empirical_bernstein_fixed_forecast','lambda':lam,
        'scale_search':{'lambda_upper_fraction_of_validity_limit':.95,'candidate_evaluations':len(cache),
            'floating_variance_proxy_numerator':cache[lam],
            'scope':'Baseline weights only. Heuristic uniform-score variance proxy selects a valid fixed scale; it is not a moment bound, optimality certificate or estimated field outcome variance.'}}

def coefficients(weights,k,lam):
    if len(weights)==0 or not 1<=k<len(weights) or any(not np.isfinite(float(w)) or w<=0 for w in weights) or not np.isfinite(lam) or lam<=0:raise ValueError('Positive weights/scale and strict nonempty quota required')
    n=len(weights);maximum=I(max(weights));gamma=sum((I(w) for w in weights),I(0))/(I(2*n)*maximum)
    linear=I(lam)*I(n)*maximum/I(k);rho=[]
    for t in range(1,k+1):
        theta=linear*I(n-k)/I(n-t)
        if theta.lo<0 or theta.hi>=1:raise ValueError('Empirical-Bernstein scale outside [0,1)')
        rho.append(I(max(Decimal(0),(-ilog(I(1)-theta)-theta).hi)))
    return {'maximum':maximum,'gamma':gamma,'linear':linear,'rho':rho}

def endpoint_log_lower(x,position,sign,coeff):
    residual=x-coeff['gamma']
    return (I(sign)*coeff['linear']*x-coeff['rho'][position]*residual*residual).lo

def endpoint_dyadic_lower(weight,score_thousandths,position,sign,coeff):
    x=I(int(weight))*I(int(score_thousandths))/(I(1000)*coeff['maximum'])
    lower=endpoint_log_lower(x,position,sign,coeff)
    return int(calc(ROUND_FLOOR,lambda:(lower*Decimal(DYADIC)).to_integral_value(rounding=ROUND_FLOOR)))

def averaged_block_logs(weights,k,lam,lower,upper):
    """Directed positive average over every k! assigned-village order.

    lower/upper are weighted score totals for the k observed villages. Their
    box minima are separable because the forecast is fixed before assignment.
    """
    if len(lower)!=k or len(upper)!=k:raise ValueError('Aligned quota observations required')
    coeff=coefficients(weights,k,lam);logs={}
    orders=list(itertools.permutations(range(k)))
    for sign in [-1,1]:
        total=I(0)
        for order in orders:
            lower_log=Decimal(0)
            for position,j in enumerate(order):
                if lower[j].lo<0 or lower[j].lo>upper[j].hi:raise ValueError('Invalid score interval')
                value=min(endpoint_log_lower(lower[j]/coeff['maximum'],position,sign,coeff),
                          endpoint_log_lower(upper[j]/coeff['maximum'],position,sign,coeff))
                lower_log=calc(ROUND_FLOOR,lambda:lower_log+value)
            total+=I(lower_log).exp()
        logs[sign]=ilog(total/I(len(orders))).lo
    return logs,{'uniform_order_average_terms':len(orders),'fixed_forecast_lower':str(coeff['gamma'].lo),
                 'fixed_forecast_upper':str(coeff['gamma'].hi),'rho_upper':[str(x.hi) for x in coeff['rho']]}
