"""Two outward implementations of the relaxed quota exponential moment.

Integer proxy weights make every centered residual an exact integer/quota.
Decimal exp/ln are correctly rounded; next_plus supplies an upper enclosure.
An IEEE positive-sum error bound encloses the finite averages. A deterministic
Lipschitz correction accounts for the difference from actual fixed weights.
The sorted-threshold recurrence additionally uses directed actual weights.
These certify moment constants, not subsequent floating-point LP solutions.
"""
from decimal import Decimal,localcontext,ROUND_CEILING,ROUND_FLOOR
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


def quota_upper_log_moment_dp(weights,quota,lam):
    """Enclose the same relaxed moment using sorted threshold populations.

    Symmetry and convexity reduce each signed box maximum to the n+1
    populations with the largest m weights active. A positive elementary
    symmetric-mean recurrence evaluates the quota average without listing
    subsets. This is an adaptation of established symmetric-convex range
    computation, not a new concentration theorem. Exact input Decimals,
    directed arithmetic and adjacent exp/ln values supply the enclosure.
    """
    exact=[decimal_weight(x) for x in weights];n=len(exact);k=int(quota)
    if n<1 or k!=quota or not 1<=k<=n or any(not x.is_finite() or x<=0 for x in exact) or not np.isfinite(lam) or lam<0:
        raise ValueError('Positive fixed weights, valid quota and nonnegative lambda required')
    if k==n or lam==0:return 0.,{'full_or_zero':True,'algorithm':'sorted_threshold_symmetric_mean'}
    exact.sort(reverse=True);q=min(k,n-k);best=Decimal(0);best_pattern=None
    # Complementing a k-subset multiplies its residual by -(n-k)/k.
    # Thus lambda/k remains the factor denominator for either quota.
    with localcontext() as ctx:
        ctx.prec=80
        L=Decimal.from_float(float(lam));K=Decimal(k);N=Decimal(n)
        Slo=Decimal(0);Shi=Decimal(0)
        for m in range(n+1):
            if m:
                ctx.rounding=ROUND_FLOOR;Slo+=exact[m-1]
                ctx.rounding=ROUND_CEILING;Shi+=exact[m-1]
            population=exact[:m]+[Decimal(0)]*(n-m)
            for sign in [-1,1]:
                factors=[]
                for x in population:
                    if sign==1:
                        ctx.rounding=ROUND_CEILING;num=N*x-Slo
                    else:
                        ctx.rounding=ROUND_FLOOR;num=(N*x-Shi).copy_negate()
                    ctx.rounding=ROUND_CEILING
                    argument=L*num/K
                    factors.append(argument.exp().next_plus())
                dp=[Decimal(1)]+[Decimal(0)]*q
                for t,a in enumerate(factors,1):
                    T=Decimal(t)
                    for j in range(min(t,q),0,-1):
                        # Both nonnegative rational coefficients and every
                        # product/sum are rounded upward independently.
                        c0=Decimal(t-j)/T;c1=Decimal(j)/T
                        dp[j]=c0*dp[j]+c1*a*dp[j-1]
                bound=dp[q].ln().next_plus()
                if bound>best:best=bound;best_pattern={'active_largest_weights':m,'sign':sign}
        upper_B=float(np.nextafter(float(best),np.inf))
    return upper_B,{'algorithm':'sorted_threshold_symmetric_mean','Decimal_precision':80,
                   'original_quota':k,'evaluated_quota':q,'threshold_populations':2*(n+1),
                   'recurrence_steps':2*(n+1)*sum(min(t,q) for t in range(1,n+1)),
                   'implicit_quota_subsets':math.comb(n,q),'maximizing_threshold':best_pattern,
                   'normalizer_scope':'Directed actual-weight arithmetic; adjacent Decimal exp/ln; positive symmetric-mean recurrence. No integer-weight approximation, subset enumeration or arbitrary numerical cushion.'}


def quota_log_moment_dp_float(weights,quota,lam):
    """Stable diagnostic recurrence for selecting scales from baseline only.

    Vectorization uses more memory than the directed routine. The returned
    floating value is not an enclosure and cannot certify a confidence set.
    """
    w=np.sort(np.asarray(weights,dtype=float))[::-1];n=len(w);k=int(quota)
    if not n or k!=quota or not 1<=k<=n or np.any(~np.isfinite(w)) or np.any(w<=0) or not np.isfinite(lam) or lam<0:
        raise ValueError('Positive fixed weights, valid quota and nonnegative lambda required')
    if k==n or lam==0:return 0.
    q=min(k,n-k)
    populations=np.tri(n+1,n,k=-1)*w
    residual=(n*populations-populations.sum(axis=1)[:,None])*float(lam)/k
    factors=np.r_[residual,-residual];dp=np.full((len(factors),q+1),-np.inf);dp[:,0]=0.
    for t in range(1,n+1):
        j=np.arange(1,min(t,q)+1)
        with np.errstate(divide='ignore'):
            c0=np.log((t-j)/t);c1=np.log(j/t)
        dp[:,j]=np.logaddexp(dp[:,j]+c0,dp[:,j-1]+c1+factors[:,t-1,None])
    return max(0.,float(dp[:,q].max()))
