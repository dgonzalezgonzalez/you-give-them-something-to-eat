"""Outward bound for the relaxed quota exponential moment.

Integer proxy weights make every centered residual an exact integer/quota.
Decimal exp/ln are correctly rounded; next_plus supplies an upper enclosure.
An IEEE positive-sum error bound encloses the finite averages. A deterministic
Lipschitz correction accounts for the difference from actual fixed weights.
This certifies moment constants, not subsequent floating-point LP solutions.
"""
from decimal import Decimal,localcontext,ROUND_CEILING
import itertools,math
import numpy as np

def decimal_weight(x):
    return x if isinstance(x,Decimal) else Decimal.from_float(float(x))

def quota_upper_log_moment(weights,quota,lam):
    exact=[decimal_weight(x) for x in weights];n=len(exact);k=int(quota)
    if n<1 or k!=quota or not 1<=k<=n or any(x<=0 or not x.is_finite() for x in exact) or lam<0 or not np.isfinite(lam):
        raise ValueError('Positive fixed weights, valid quota and nonnegative lambda required')
    if k==n or lam==0:return 0.,{'full_or_zero':True}
    proxy=np.array([round(x) for x in exact],dtype=np.int64)
    if (n+k)*sum(abs(int(x)) for x in proxy)>=2**62:
        raise ValueError('Integer proxy outside the certified int64 range')
    choices=list(itertools.combinations(range(n),k))
    selectors=np.zeros((len(choices),n),dtype=np.int64)
    for i,subset in enumerate(choices):selectors[i,list(subset)]=1
    # k times centered residual for a binary population and u=0.
    coefficients=(n*selectors-k)*proxy
    patterns=np.array(list(itertools.product([0,1],repeat=n)),dtype=np.int64)
    numerators=patterns@coefficients.T
    all_values=np.unique(np.r_[numerators.ravel(),(numerators-coefficients.sum(axis=1)).ravel()])
    exponent_upper={}
    with localcontext() as ctx:
        ctx.prec=80;ctx.rounding=ROUND_CEILING
        L=Decimal.from_float(float(lam));K=Decimal(k)
        for j in all_values:
            argument=L*Decimal(int(j))/K
            # exp is correctly rounded with HALF_EVEN regardless of context.
            upper=argument.exp().next_plus()
            exponent_upper[int(j)]=np.nextafter(float(upper),np.inf)
        # Subtract the smaller operand from the larger one: rounding a
        # negative difference upward before taking abs could understate it.
        distances=[max(x,Decimal(int(z)))-min(x,Decimal(int(z))) for x,z in zip(exact,proxy)]
        drift=L*(Decimal(n)/K+1)*sum(distances)
        # Twice the usual unit roundoff is intentionally conservative.
        epsilon=2.**-52;terms=len(choices)
        gamma=np.nextafter(terms*epsilon/(1-terms*epsilon),np.inf)
        denominator=np.nextafter(1-gamma,-np.inf)
        maximum=0.
        values=np.array([exponent_upper[int(j)] for j in all_values])
        if not np.all(np.isfinite(values)) or np.any(values<np.finfo(float).tiny) or denominator<=0:
            raise ValueError('Moment enclosure requires finite normal exponentials and a valid summation bound')
        for u in [0,1]:
            index=np.searchsorted(all_values,numerators-u*coefficients.sum(axis=1))
            sums=np.sum(values[index],axis=1)
            if not np.all(np.isfinite(sums)):raise ValueError('Moment sum overflow')
            averages=np.nextafter(np.nextafter(sums/denominator,np.inf)/terms,np.inf)
            maximum=max(maximum,float(averages.max()))
        B=Decimal.from_float(maximum).ln().next_plus()+drift
        upper_B=np.nextafter(float(B),np.inf)
    return float(upper_B),{'integer_proxy_weights':proxy.tolist(),'unique_integer_residuals':len(all_values),
                          'quota_subsets':len(choices),'weight_drift_log_allowance':str(drift),
                          'Decimal_precision':80,'positive_sum_error_factor':float(gamma),
                          'normalizer_scope':'Outward Decimal elementary functions, exact int64 residuals, IEEE positive-sum enclosure and known-weight Lipschitz relaxation.'}
