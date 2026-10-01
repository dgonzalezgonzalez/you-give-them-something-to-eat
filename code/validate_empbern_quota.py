"""Independent high-precision ordered-sampling and missing-endpoint checks."""
from pathlib import Path
from decimal import Decimal,localcontext
import itertools,json,time
from quota_arithmetic import I
from empbern_quota import averaged_block_logs,coefficients,endpoint_dyadic_lower,DYADIC

ROOT=Path(__file__).resolve().parents[1];start=time.perf_counter();checks={};slacks=[];count=0
with localcontext() as ctx:
    ctx.prec=160
    for fixture,weights in enumerate([[1,1,1],[1,2,4],[1,2,3,7]]):
        n=len(weights);maximum=Decimal(max(weights));gamma=Decimal(sum(weights))/(Decimal(2*n)*maximum)
        for k in range(1,n):
            for fraction in [.1,.4,.8]:
                lam=float(fraction*k/(n*float(maximum)));L=Decimal.from_float(lam)
                rho=[-(1-L*Decimal(n)*maximum/Decimal(k)*Decimal(n-k)/Decimal(n-t)).ln()-L*Decimal(n)*maximum/Decimal(k)*Decimal(n-k)/Decimal(n-t) for t in range(1,k+1)]
                orders=list(itertools.permutations(range(n),k))
                for population,bits in enumerate(itertools.product([0,1],repeat=n)):
                    values=[Decimal(w*y) for w,y in zip(weights,bits)];total=sum(values)
                    means={-1:Decimal(0),1:Decimal(0)}
                    for order in orders:
                        G=Decimal(n)*sum(values[j] for j in order)/Decimal(k)-total
                        penalty=sum(rho[t]*(values[j]/maximum-gamma)**2 for t,j in enumerate(order))
                        for sign in [-1,1]:means[sign]+=(Decimal(sign)*L*G-penalty).exp()
                    for sign in [-1,1]:
                        mean=means[sign]/Decimal(len(orders));count+=1
                        checks[f'ordered_moment_{fixture}_{k}_{fraction}_{population}_{sign}']=mean<=1+Decimal('1e-145')
                        slacks.append(float(1-mean))
                # Distinct interior values prevent a vertex-only endpoint
                # check from duplicating the directed implementation.
                values=[Decimal(w)*Decimal(j+1)/Decimal(n+1) for j,w in enumerate(weights)]
                for subset_index,subset in enumerate(itertools.combinations(range(n),k)):
                    selected=[values[j] for j in subset]
                    directed,detail=averaged_block_logs(weights,k,lam,[I(x) for x in selected],[I(x) for x in selected])
                    for sign in [-1,1]:
                        truth=sum((Decimal(sign)*L*Decimal(n)/Decimal(k)*sum(selected)-sum(rho[t]*(selected[j]/maximum-gamma)**2 for t,j in enumerate(order))).exp() for order in itertools.permutations(range(k)))/Decimal(detail['uniform_order_average_terms'])
                        checks[f'order_average_enclosure_{fixture}_{k}_{fraction}_{subset_index}_{sign}']=directed[sign]<=truth.ln()
                    # Every endpoint interval contains its true selected
                    # value; averaging directed minima is pathwise lower.
                    low=[I(Decimal(0)) for j in subset];high=[I(Decimal(weights[j])) for j in subset]
                    relaxed,_=averaged_block_logs(weights,k,lam,low,high)
                    checks[f'missing_box_monotonicity_{fixture}_{k}_{fraction}_{subset_index}']=all(relaxed[sign]<=directed[sign] for sign in [-1,1])
                coeff=coefficients(weights,k,lam)
                for position in range(k):
                    for sign in [-1,1]:
                        score=375;weight=weights[0];x=Decimal(weight)*Decimal(score)/(Decimal(1000)*maximum)
                        truth=Decimal(sign)*L*Decimal(n)*maximum/Decimal(k)*x-rho[position]*(x-gamma)**2
                        lower=Decimal(endpoint_dyadic_lower(weight,score,position,sign,coeff))/Decimal(DYADIC)
                        checks[f'dyadic_endpoint_{fixture}_{k}_{fraction}_{position}_{sign}']=lower<=truth
result={'scope':'Independent 160-digit complete binary populations and all ordered quota samples verify expected empirical-Bernstein tests; interior-valued subsets verify directed complete-data order averages, missing-box monotonicity and dyadic endpoint rounding. These checks support the stated proof, not field coverage, optimized betting performance or independent external replication.',
        'checks':checks,'all_passed':all(checks.values()),'ordered_moment_checks':count,
        'minimum_one_minus_moment':min(slacks),'seconds':time.perf_counter()-start}
(ROOT/'output/empbern-quota-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(sum(checks.values()),'/',len(checks),'empirical-Bernstein checks;',result['seconds'],'seconds',flush=True)
if not result['all_passed']:raise ValueError([k for k,v in checks.items() if not v])
