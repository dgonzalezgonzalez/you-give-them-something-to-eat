"""Directed interval arithmetic and independently feasible LP dual bounds.

Decimal elementary functions are correctly rounded; adjacent Decimal values
enclose their exact values. Directed elementary arithmetic propagates each
enclosure. Solver candidates only select tangents and dual multipliers.
"""
from decimal import Decimal,localcontext,ROUND_FLOOR,ROUND_CEILING
import numpy as np

PREC=80
def D(x):
    if isinstance(x,Decimal):return x
    if isinstance(x,(int,np.integer)):return Decimal(int(x))
    return Decimal.from_float(float(x))
def calc(rounding,fn):
    with localcontext() as ctx:
        ctx.prec=PREC;ctx.rounding=rounding
        return fn()
class I:
    def __init__(self,x,hi=None):self.lo=D(x);self.hi=D(x if hi is None else hi)
    def __add__(self,other):
        other=iv(other)
        return I(calc(ROUND_FLOOR,lambda:self.lo+other.lo),calc(ROUND_CEILING,lambda:self.hi+other.hi))
    __radd__=__add__
    def __neg__(self):return I(self.hi.copy_negate(),self.lo.copy_negate())
    def __sub__(self,other):return self+-iv(other)
    def __rsub__(self,other):return iv(other)+-self
    def __mul__(self,other):
        other=iv(other);pairs=[(a,b) for a in [self.lo,self.hi] for b in [other.lo,other.hi]]
        return I(min(calc(ROUND_FLOOR,lambda:a*b) for a,b in pairs),max(calc(ROUND_CEILING,lambda:a*b) for a,b in pairs))
    __rmul__=__mul__
    def __truediv__(self,other):
        other=iv(other)
        if other.lo<=0<=other.hi:raise ZeroDivisionError('Interval divisor includes zero')
        inverse=I(calc(ROUND_FLOOR,lambda:Decimal(1)/other.hi),calc(ROUND_CEILING,lambda:Decimal(1)/other.lo))
        return self*inverse
    def exp(self):
        return I(calc(ROUND_FLOOR,lambda:self.lo.exp().next_minus()),calc(ROUND_CEILING,lambda:self.hi.exp().next_plus()))
    def upper_float(self):return float(np.nextafter(float(self.hi),np.inf))
    def lower_float(self):return float(np.nextafter(float(self.lo),-np.inf))
def iv(x):return x if isinstance(x,I) else I(x)
def dot(a,b):return sum((iv(x)*iv(y) for x,y in zip(a,b)),I(0))

def lp_dual_lower(g,A,b,floor,multipliers):
    """A feasible dual lower bound for min g'p over p>=floor, Ap<=b, 1'p=1.

    Uses no primal optimum or solver success claim. Upper variable bounds are
    redundant under nonnegative floor and unit mass and are not used.
    """
    A=np.asarray(A);g=np.asarray(g);floor=np.asarray(floor)
    if np.any(floor<0):raise ValueError('Nonnegative bin floors required')
    lam=np.minimum(np.asarray(multipliers),0.)
    if not np.all(np.isfinite(lam)):raise ValueError('Finite dual multipliers required')
    reduced=[(I(g[j])-dot(A[:,j],lam)).lo for j in range(len(g))]
    zeta=min(reduced)
    residual=[I(bb)-dot(row,floor) for row,bb in zip(A,b)]
    mass=I(1)-sum((I(x) for x in floor),I(0))
    value=dot(g,floor)+dot(lam,residual)+I(zeta)*mass
    return value.lo,{'equality_multiplier':str(zeta),'nonpositive_multipliers':lam.tolist(),
                     'feasibility':'Reduced costs nonnegative by directed interval construction.'}

def tangent_support_upper(direction,point,C,intercept,tau,cap,A,b,floor,lp_multipliers):
    """Upper-bound sup[d'p - tau F(p)/cap] using an enclosed convex tangent.

    point and LP multipliers may be approximate. Tangent errors are bounded
    over 0<=p<=1; the directed feasible LP dual replaces a primal LP value.
    """
    point=np.asarray(point);direction=np.asarray(direction);C=np.asarray(C)
    terms=[(dot(row,point)+I(v)).exp() for row,v in zip(C,intercept)]
    F=sum(terms,I(0));factor=I(tau)/I(cap)
    f=-dot(direction,point)+factor*F
    gradients=[-I(direction[j])+factor*dot(C[:,j],terms) for j in range(len(point))]
    g=np.array([float((v.lo+v.hi)/2) for v in gradients])
    error=I(0)
    for p,gg,v in zip(point,g,gradients):
        diff=I(gg)-v
        delta=max(diff.lo.copy_abs(),diff.hi.copy_abs())
        radius=max(D(p).copy_abs(),(I(1)-I(p)).hi.copy_abs(),(I(1)-I(p)).lo.copy_abs())
        error+=I(delta)*I(radius)
    constant=I(f.lo)-dot(g,point)-error
    minimum,receipt=lp_dual_lower(g,A,b,floor,lp_multipliers)
    upper=-(constant+I(minimum))
    return upper.upper_float(),{'tangent_error_upper':str(error.hi),'tangent_gradient':g.tolist(),'F_upper':F.upper_float(),
                                'support_upper':upper.upper_float(),'LP_dual':receipt}

def mixture_upper(models,points):
    return sum((sum(((dot(m['C'][j],p)+I(m['intercept'][j])).exp() for j in range(len(m['C']))),I(0))
                for m,p in zip(models,points)),I(0)).upper_float()


def float_lower(x):return float(np.nextafter(float(x),-np.inf))
def float_upper(x):return float(np.nextafter(float(x),np.inf))

def observed_residual_constants(weights,block_sizes,quotas,lower,upper,zgrid):
    """Enclose HT numerators and denominator using exact stored weights.

    Inputs concern one assigned arm. zgrid is the fixed normalized score
    function on 0,...,12. Its entries are interpreted as their exact stored
    binary floats, so no presumed real-valued identity is substituted.
    """
    weights=list(weights);n=list(block_sizes);k=list(quotas)
    if not weights or not len(weights)==len(n)==len(k)==len(lower)==len(upper):
        raise ValueError('Nonempty aligned assigned observations required')
    z=np.asarray(zgrid,dtype=float)
    if len(z)!=13 or not np.all(np.isfinite(z)) or np.any(np.diff(z)<0) or z.min()<0 or z.max()>1:
        raise ValueError('Increasing normalized thirteen-score objective required')
    receipts=[]
    for rounding in [ROUND_FLOOR,ROUND_CEILING]:
        with localcontext() as ctx:
            ctx.prec=100;ctx.rounding=rounding
            D=Decimal(0);Nlo=Decimal(0);Nhi=Decimal(0)
            for w,nn,kk,l,h in zip(weights,n,k,lower,upper):
                if not np.isfinite(w) or w<=0 or not 0<kk<=nn or int(nn)!=nn or int(kk)!=kk or not 0<=l<=h<=12 or int(l)!=l or int(h)!=h:raise ValueError('Invalid weight, quota or score interval')
                factor=Decimal.from_float(float(w))*Decimal(int(nn))/Decimal(int(kk))
                D+=factor
                Nlo+=factor*Decimal.from_float(float(z[int(l)]))
                Nhi+=factor*Decimal.from_float(float(z[int(h)]))
            receipts.append((D,Nlo,Nhi))
    return {'denominator_lower':float_lower(receipts[0][0]),'denominator_upper':float_upper(receipts[1][0]),
            'lower_numerator_lower':max(0.,float_lower(receipts[0][1])),
            'upper_numerator_upper':float_upper(receipts[1][2]),
            'scope':'100-digit directed Decimal quota arithmetic; outward conversion to stored floats.'}

def outward_affine_tests(constants,zgrid,lam,upper_log_normalizer):
    """Stored affine coefficients are lower than exact normalized log tests.

    This supports conceptual expectation bounds for real-valued linear forms
    of the stored coefficients. Later exp/dot/LP numerical errors require
    their own enclosures; this does not certify those computations.
    """
    z=np.asarray(zgrid,dtype=float);Dlo=constants['denominator_lower'];Dhi=constants['denominator_upper']
    Nlo=constants['lower_numerator_lower'];Nhi=constants['upper_numerator_upper'];B=upper_log_normalizer
    if not np.isfinite(lam) or not np.isfinite(B) or lam<0 or Dlo<=0 or B<0:raise ValueError('Positive denominator and valid moment constants required')
    positive_upper=np.nextafter(lam*Dhi,np.inf)
    positive_lower=np.nextafter(lam*Dlo,-np.inf)
    Cplus=-np.nextafter(positive_upper*z,np.inf)
    Cminus=np.nextafter(positive_lower*z,-np.inf)
    Cplus[z==0]=0.;Cminus[z==0]=0.
    iplus=np.nextafter(np.nextafter(lam*Nlo,-np.inf)-B,-np.inf)
    iminus=np.nextafter(-np.nextafter(lam*Nhi,np.inf)-B,-np.inf)
    return np.stack([Cplus,Cminus]),np.array([iplus,iminus])
