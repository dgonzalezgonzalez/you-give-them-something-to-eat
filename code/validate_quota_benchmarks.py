"""Independent exact-coefficient and high-precision moment checks."""
from pathlib import Path
from fractions import Fraction
from decimal import Decimal,localcontext
import itertools,json
from quota_benchmarks import range_coefficient,fraction_interval

ROOT=Path(__file__).resolve().parents[1]

def main():
    checks=[]
    for n in range(2,21):
        for k in range(1,n+1):
            hh=range_coefficient(n,k,'hoeffding');ss=range_coefficient(n,k,'serfling');mm=range_coefficient(n,k,'harmonic_martingale')
            checks.append(bool(0<=mm<=ss<=hh))
            with localcontext() as ctx:
                ctx.prec=160
                exact=Decimal(mm.numerator)/Decimal(mm.denominator)
                enclosure=fraction_interval(mm)
                checks.append(enclosure.lo<=exact<=enclosure.hi)
    fixtures=[([1,1,1,1],1),([1,1,1,1],2),([1,1,1,1],3),([1,2,3,8],1),([1,2,3,8],2),([1,2,3,8],3),([1,3,1,3,1,3],2),([1,3,1,3,1,3],5)]
    moment_checks=0
    with localcontext() as ctx:
        ctx.prec=160
        for weights,k in fixtures:
            n=len(weights);subsets=list(itertools.combinations(range(n),k))
            for lam in [Fraction(1,100),Fraction(1,10),Fraction(1,2),Fraction(1),Fraction(3)]:
                L=Decimal(lam.numerator)/Decimal(lam.denominator)
                for y in itertools.product([0,1],repeat=n):
                    for u in [0,1]:
                        t=[Fraction(w*(v-u)) for w,v in zip(weights,y)]
                        values=[Fraction(n,k)*sum((t[j] for j in subset),Fraction(0))-sum(t) for subset in subsets]
                        moment=sum((L*(Decimal(g.numerator)/Decimal(g.denominator))).exp() for g in values)/Decimal(len(subsets))
                        for method in ['hoeffding','serfling','harmonic_martingale']:
                            coef=range_coefficient(n,k,method)*max(weights)**2*lam**2/Fraction(8)
                            theoretical=Decimal(coef.numerator)/Decimal(coef.denominator)
                            # High-precision comparison with explicit fixture
                            # tolerance; coverage follows the analytic proof.
                            checks.append(moment.ln()<=theoretical+Decimal('1e-145'));moment_checks+=1
    result={'scope':'Exact rational hierarchy/enclosure of classical coefficients and independent 160-digit complete binary population/centering enumeration. Synthetic moment checks are not field coverage estimates or evidence of methodological dominance.',
            'checks':len(checks),'passed':sum(checks),'independent_moment_inequalities':moment_checks,'all_passed':all(checks)}
    (ROOT/'output/quota-benchmark-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result))
    if not all(checks):raise ValueError('Benchmark moment check failed')

if __name__=='__main__':main()
