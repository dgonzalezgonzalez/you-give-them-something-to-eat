"""Established inclusion-indicator product bound with actual fixed weights.

The endpoint reduction and a positive expansion of uniform-subset inclusion
probabilities suffice; negative association is an established interpretation.
No new dependence inequality or uniform advantage over quota inference is
claimed. A baseline-selected minimum with a supplied harmonic coefficient
still bounds the same block moment; it is not event intersection.
"""
import numpy as np
from decimal import Decimal,ROUND_FLOOR,ROUND_CEILING
from quota_arithmetic import I,calc

def ilog(v):
    if v.lo<=0:raise ValueError('Positive moment required')
    return I(calc(ROUND_FLOOR,lambda:v.lo.ln().next_minus()),calc(ROUND_CEILING,lambda:v.hi.ln().next_plus()))

def product_log_upper(weights,quota,lam,harmonic_coefficient=None):
    n=len(weights);k=int(quota)
    if not n or k!=quota or not 1<=k<=n or not np.isfinite(lam) or lam<0:
        raise ValueError('Nonempty weights, valid quota and nonnegative lambda required')
    w=[I(x) for x in weights]
    if any(not x.lo.is_finite() or x.lo<=0 for x in w):raise ValueError('Positive finite weights required')
    if k==n or lam==0:return 0.
    p=I(k)/I(n);notp=I(n-k)/I(n);ratio=I(n-k)/I(k);plus=I(0);minus=I(0)
    for weight in w:
        lw=I(lam)*weight
        plus+=ilog(notp*(-lw).exp()+p*(lw*ratio).exp())
        minus+=ilog(notp*lw.exp()+p*(-lw*ratio).exp())
    value=I(max(Decimal(0),plus.hi,minus.hi)).upper_float()
    if harmonic_coefficient is not None:
        if harmonic_coefficient<0:raise ValueError('Nonnegative harmonic coefficient required')
        coefficient=I(harmonic_coefficient.numerator)/I(harmonic_coefficient.denominator)
        maximum=I(max(x.lo for x in w))
        value=min(value,(I(lam)*I(lam)*coefficient*maximum*maximum/I(8)).upper_float())
    return value

def product_log_float(weights,quota,lam,harmonic_coefficient=None):
    """Baseline scale-selection diagnostic only; never an enclosure."""
    w=np.asarray(weights,dtype=float);n=len(w);k=int(quota)
    if not n or k!=quota or not 1<=k<=n or np.any(~np.isfinite(w)) or np.any(w<=0) or not np.isfinite(lam) or lam<0:
        raise ValueError('Positive fixed weights, valid quota and nonnegative lambda required')
    if k==n or lam==0:return 0.
    p=k/n;lw=lam*w;ratio=(n-k)/k
    value=max(np.logaddexp(np.log1p(-p)-lw,np.log(p)+lw*ratio).sum(),np.logaddexp(np.log1p(-p)+lw,np.log(p)-lw*ratio).sum())
    if harmonic_coefficient is not None:
        if harmonic_coefficient<0:raise ValueError('Nonnegative harmonic coefficient required')
        value=min(value,lam**2/8*float(harmonic_coefficient)*max(w)**2)
    return max(0.,float(value))
