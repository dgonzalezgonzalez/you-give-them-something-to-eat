# Conditional quota-mixture inference and numerical verification

1 October 2026. This fifth-revision procedure uses the same public observations as the fourth submission. It is a new standalone conditional event. It does not intersect two nominal 95% confidence sets and claim their intersection remains 95%. The main target is the fixed weighted released baseline; the potential identified-diet ratio retains a different target and event. No recovered assignment protocol, new observations, sharp potential-outcome region, optimal general inference theorem or statistical minimax-regret rule is claimed.

## Coverage argument

Condition on uniform arm labels given each block's observed quotas, independent blocks, positive fixed baseline weights and stable bounded reported potential diets. For village weight W_j, normalized village score y_j in [0,1], and true overall weighted mean u in [0,1], the centered block residual for a uniform k-subset of n villages is

G_A(y,u) = sum_j (1{j in A}/(k/n) - 1) W_j (y_j-u).

The across-block sum equals the arm's HT residual because the full-population weighted residual sums to zero. For fixed lambda, the quota-average exponential is jointly convex in y and u. Its maximum over their box occurs at binary vertices. Enumerating 2^(n+1) relaxed vertices and all quota subsets bounds the centered block moment for every actual bounded population. The relaxation discards the relationship between u and the village outcomes. Complementing both y and u reverses G; the same maximum protects the negative sign. A particular unequal-weight population need not have a symmetric residual distribution. Independence multiplies block bounds; their log bounds add to B_a.

For each of 23 fixed increasing normalized score functions, missing-diet item intervals give lower and upper assignment-weighted numerators N_lo/N_hi and a full-baseline HT denominator D_hat. The computable terms

e_plus(p_a) = exp[lambda_a (N_lo-D_hat z'p_a)-B_a]

e_minus(p_a) = exp[-lambda_a (N_hi-D_hat z'p_a)-B_a]

are pointwise no larger than the corresponding true-residual terms at the true score distribution. Each therefore has expectation at most one. Their sum has expectation at most 276, despite dependence among packages, score functions and missingness patterns. Markov's inequality gives failure probability at most 276/5520=0.05 for the single event that the sum is no greater than 5520. Unit mass, nonnegativity, assigned identified-score bin floors and deterministic item-consistency restrictions hold for the true distributions for every assignment. Intersecting these restrictions preserves that event.

The four-point exponential grid {1, 1.25, 1.5, 2} times sqrt[8 log(5520)/V_a] is selected by minimizing (B_a+log(5520))/lambda_a using baseline weights and released quotas alone. Neither endline outcomes nor resulting allocation bounds choose the scale. Coverage protects the full probability region, so outcome-dependent allocation and support-dual proposals are allowed on that one event. The score entries are fixed stored bounded functions. Inference projects their common probability region onto the exact raw mean and six-group shortfall objectives; it does not assume an exact floating-point affine identity between normalized and raw scores.

The original randomization code is still unavailable. Released counts do not prove uniform quota assignment or block independence. Those assumptions remain explicit. Fixed released weights do not prove full-frame representativeness, and stable deployment costs and outcomes need additional evidence.

## Outward arithmetic

`quota_moments.py` uses rounded integer proxy village weights. Binary centered residuals then have exact int64 numerators over the integer quota. Directed 80-digit Decimal arguments, correctly rounded Decimal exp/ln with adjacent-value enclosures, and an IEEE positive-sum error bound enclose each proxy quota average upward. Finite normal exponentials and nonoverflowing sums are checked. A deterministic log allowance lambda*(n/k+1)*sum|W-W_proxy| accounts for actual fixed weights. Exact stored household weights are summed at 100 digits; actual inputs fit that precision. Summation and float conversion of block constants are outward.

`quota_arithmetic.py` supplies directed endpoint HT and denominator arithmetic. Its stored affine tests are lower than the conceptual log tests for nonnegative probability vectors. Deterministic logical limits are widened and identified-score floors lowered. This enlarges the event region rather than discarding the true distribution through rounding.

For a direction d, every tau>=0 gives the support upper bound

tau + sum_a sup_{p_a in P_a} [d_a'p_a - tau F_a(p_a)/5520].

The negative arm objective is convex. An interval-enclosed tangent at any candidate is a lower bound everywhere, after subtracting a gradient-error allowance over 0<=p<=1. The candidate need not solve the convex problem. For P={p>=f, Ap<=b, 1'p=1}, suggested inequality multipliers are clamped to nonpositive values. A directed equality multiplier zeta satisfying A'ell+zeta*1<=g gives the LP minimum lower bound g'f+ell'(b-Af)+zeta*(1-1'f). Thus a solver success flag and a primal objective with an arbitrary cushion are not used as proof of the numerical bound. Exact rational shares and ideal cost vertices, enclosed direction rounding, and outward addition produce the final nine-comparator maximum. Display values are rounded upward to three decimals.

## Search and replication scope

`code/quota_proposals.json` contains the outcome-selected allocation numerators and nine nonnegative dual scales. They came from an exploratory exchange search with 30 iterations per objective, 24 tau evaluations per support and 300-iteration arm minimizers. Its floating diagnostic gaps were approximately 0.000114 groups and 0.000047 shortfall units. They are not certified minimax gaps and do not enter the coverage proof or reported upper bounds. The earlier scratch numerical padding is superseded by the production enclosures.

The default master independently recomputes baseline moment selection, all model constants, convex candidates and feasible dual bounds from data, then verifies the stored proposals. It does not need to redo the longer approximate search to verify their scientific claims. `python code/search_quota_allocation.py` offers a new exploratory search on the production region, with a 0.0003 stopping diagnostic. It writes `output/quota-search.json` without changing the canonical proposals. A different approximate proposal is not a coverage failure; any proposed allocation must pass the separate enclosed verifier. Search output is not part of the default manuscript.

Actual production verification gives upper bounds 5.8671294071 groups and 0.5025483675 shortfall units, reported conservatively as **5.868** and **0.503**. The mean proposal spends at most USD84.269627 per eligible household. This improves on the earlier 7.720305 construction but remains broad; no small-loss or operational recommendation is inferred. Institutional, resource-value and cost sensitivity tables remain labeled as calculations on the earlier coherent region.

`validate_quota_enclosures.py` passes 1,076 independent checks: 160-digit quota maxima, observable/affine enclosures, exact-rational LP vertex comparisons including deliberately poor dual proposals, and an independent nonlinear support fixture. `validate_quota_allocation.py` passes 248 checks: optimizer-free support replay, exact rational allocation and LP-dual feasibility, upward displays, and exhaustive 36-assignment arm-dependent missing-diet fixtures. Fixture event coverage is 1.0; that number is not a proof of Rwanda coverage or validation of the failed approximation. The mathematical conditional argument supplies coverage. Further external proof/code review remains required.

Optional production-region exchange search also completed in 387.29 seconds: mean floating upper 5.8671824456 / gap 0.00019747,shortfall upper 0.5025619383 / gap 0.00013635. Actual output/quota-search.json is retained. These are numerical diagnostics; the separately enclosed canonical proposal verification supplies the reported 5.868 / 0.503 bounds. No certified minimax gap is inferred.
