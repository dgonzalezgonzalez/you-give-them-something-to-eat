"""Independent fixtures for quota constants, observable intervals and duals."""
from pathlib import Path
from decimal import Decimal,localcontext
from fractions import Fraction
import itertools,json,random,math
import numpy as np
from scipy.optimize import linprog
from quota_moments import quota_upper_log_moment
from quota_arithmetic import observed_residual_constants,outward_affine_tests
from quota_arithmetic import I,D,dot,lp_dual_lower,tangent_support_upper

root=Path(__file__).resolve().parents[1];checks={};moment_slack=[];rng=random.Random(8103)
def reference_moment(weights,k,lam):
    with localcontext() as ctx:
        ctx.prec=160
        ww=[D(w) for w in weights];L=D(lam);n=len(ww);best=Decimal('-Infinity')
        for y in itertools.product([0,1],repeat=n):
            for u in [0,1]:
                x=[w*(Decimal(v)-u) for w,v in zip(ww,y)];population=sum(x)
                residuals=[Decimal(n)*sum(x[j] for j in ss)/Decimal(k)-population for ss in itertools.combinations(range(n),k)]
                value=(sum((L*r).exp() for r in residuals)/Decimal(len(residuals))).ln()
                best=max(best,value)
        return best
fixtures=[([1.,1.,1.,1.],2,.4),([.7,2.1,1.2,3.4],1,.3),([.7,2.1,1.2,3.4],3,.3),([1.,2.,3.,1.5,4.],2,.15),
          ([1.0000000000001,2.00000000000003,3.00000000000008,4.00000000000013],3,.2),
          ([Decimal('1.00000000000000000000000000000000000000000000000000000000000000000000000000000001'),Decimal('1.99999999999999999999999999999999999999999999999999999999999999999999999999999998'),Decimal('3')],1,.3)]
for i,(w,k,lam) in enumerate(fixtures):
    B,receipt=quota_upper_log_moment(w,k,lam);ref=reference_moment(w,k,lam)
    checks[f'moment_upper_reference_{i}']=D(B)>=ref;moment_slack.append(float(D(B)-ref))
    checks[f'positive_sum_receipt_{i}']=receipt['positive_sum_error_factor']>0
checks['full_quota_exact_zero']=quota_upper_log_moment([.1,2.,3.],3,.5)[0]==0.
checks['zero_lambda_exact_zero']=quota_upper_log_moment([.1,2.,3.],1,0.)[0]==0.
for i,args in enumerate([([0.,2.],1,.2),([1.,2.],.5,.2),([1.,2.],3,.2),([1.,2.],1,float('nan'))]):
    try:quota_upper_log_moment(*args);checks[f'invalid_moment_{i}']=False
    except ValueError:checks[f'invalid_moment_{i}']=True

weights=[.7,2.1,1.2,3.4];nn=[4,5,6,7];kk=[1,2,3,2];lo=[0,2,4,11];hi=[1,8,12,12]
for name,z in [('mean',np.arange(13)/12),('shortfall',1-np.maximum(6-np.arange(13),0)/6),('step',(np.arange(13)>=5).astype(float))]:
    cc=observed_residual_constants(weights,nn,kk,lo,hi,z);C,intercept=outward_affine_tests(cc,z,.3,2.)
    with localcontext() as ctx:
        ctx.prec=160
        factors=[D(w)*n/Decimal(k) for w,n,k in zip(weights,nn,kk)]
        DD=sum(factors);NL=sum(w*D(z[l]) for w,l in zip(factors,lo));NH=sum(w*D(z[h]) for w,h in zip(factors,hi))
        checks[f'observable_denominator_{name}']=D(cc['denominator_lower'])<=DD<=D(cc['denominator_upper'])
        checks[f'observable_numerators_{name}']=D(cc['lower_numerator_lower'])<=NL and D(cc['upper_numerator_upper'])>=NH
        for j in range(30):
            # Exact rational mass vector, independent of float normalization.
            counts=[rng.randrange(1,100) for _ in range(13)];total=sum(counts);p=[Decimal(x)/Decimal(total) for x in counts]
            mu=sum(D(v)*pp for v,pp in zip(z,p))
            exact=[D(.3)*(NL-DD*mu)-2,-D(.3)*(NH-DD*mu)-2]
            computed=[sum(D(c)*pp for c,pp in zip(row,p))+D(ii) for row,ii in zip(C,intercept)]
            checks[f'affine_is_lower_{name}_{j}']=all(x<=y for x,y in zip(computed,exact))

def solve_fraction(matrix,rhs):
    a=[[Fraction(x) for x in row]+[Fraction(y)] for row,y in zip(matrix,rhs)];n=len(rhs)
    for j in range(n):
        pivot=next((i for i in range(j,n) if a[i][j]),None)
        if pivot is None:return None
        a[j],a[pivot]=a[pivot],a[j];v=a[j][j];a[j]=[x/v for x in a[j]]
        for i in range(n):
            if i!=j:
                v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[j])]
    return [a[i][-1] for i in range(n)]
def exact_lp(g,A,b,floor):
    constraints=[[*row] for row in A]+[[-int(i==j) for i in range(len(g))] for j in range(len(g))]
    rhs=[*b,*[-x for x in floor]];vertices=[]
    for indices in itertools.combinations(range(len(rhs)),len(g)-1):
        pp=solve_fraction([[1]*len(g),*[constraints[i] for i in indices]],[1,*[rhs[i] for i in indices]])
        if pp is not None and all(sum(Fraction(x)*p for x,p in zip(row,pp))<=Fraction(bb) for row,bb in zip(constraints,rhs)):
            vertices.append(sum(Fraction(float(x))*p for x,p in zip(g,pp)))
    return min(vertices)
A=np.array([[1.,2.,0.],[0.,0.,1.]]);b=np.array([1.5,.75]);floor=np.array([.125,0.,.125])
for j in range(60):
    g=np.array([rng.uniform(-4,4) for _ in range(3)])
    fit=linprog(g,A_ub=A,b_ub=b,A_eq=[[1]*3],b_eq=[1],bounds=[(x,None) for x in floor],method='highs')
    # Include deliberately distorted and positive suggested multipliers:
    # the construction must remain feasible even when a solver is wrong.
    lam=fit.ineqlin.marginals if j%3 else np.array([rng.uniform(-5,5),rng.uniform(-5,5)])
    lower,receipt=lp_dual_lower(g,A,b,floor,lam);exact=exact_lp(g,A,b,floor)
    checks[f'exact_fraction_dual_{j}']=Fraction(lower)<=exact

# Tangent support direction checked against a dense independent high-precision
# one-dimensional grid, with an intentionally non-optimal tangent point.
C=np.array([[1.2,-.4],[-.6,.9]]);inter=np.array([-.7,-.3]);d=np.array([.8,-.5]);tau=.6;cap=5.
point=np.array([.2,.8]);A2=np.array([[1.,0.]]);b2=np.array([.9]);floor2=np.zeros(2)
z=C@point+inter;fgrad=-d+tau/cap*(np.exp(z)@C)
lp=linprog(fgrad,A_ub=A2,b_ub=b2,A_eq=[[1,1]],b_eq=[1],bounds=[(0,None)]*2,method='highs')
upper,receipt=tangent_support_upper(d,point,C,inter,tau,cap,A2,b2,floor2,lp.ineqlin.marginals)
with localcontext() as ctx:
    ctx.prec=160
    for j in range(901):
        p=[Decimal(j)/Decimal(1000),1-Decimal(j)/Decimal(1000)]
        val=sum(D(x)*y for x,y in zip(d,p))-D(tau)/D(cap)*sum((sum(D(x)*y for x,y in zip(row,p))+D(ii)).exp() for row,ii in zip(C,inter))
        checks[f'convex_tangent_grid_{j}']=D(upper)>=val
checks['tangent_error_finite']=math.isfinite(float(receipt['tangent_error_upper']))
report={'scope':'Independent 160-digit enumerated moments, exact-rational LP vertices, directed observable and affine-envelope checks, and dense independent nonlinear support fixture. Execution checks do not replace the mathematical conditional-coverage proof or establish economic contribution.',
        'checks':checks,'all_passed':all(checks.values()),'moment_upper_slack':moment_slack,'tangent_support_upper':upper}
(root/'output/quota-enclosure-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(sum(checks.values()),'/',len(checks),'checks; minimum moment upper slack',min(moment_slack),'support upper',upper)
if not report['all_passed']:raise AssertionError([k for k,v in checks.items() if not v])
