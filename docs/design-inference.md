# Second-review inference repair: derivation and limits

This document records the implemented second-report revision. The frozen second submission and its historical outputs remain recoverable in Git. Block approximations are explicitly exploratory after failed coverage diagnostics; the headline conditional finite result is derived separately. No acceptance or independent full replication is asserted.

## Assignment information and conditioning

The parent paper's assignment section describes computer randomization in 22 district/poverty blocks of 10–13 villages. The release yields the block-by-arm counts used in assignment_probabilities.csv. Neither the released replication scripts nor the inspected assignment section supplies the original randomization program or every restriction on assignment.

The live AEA registry entry AEARCTR-0002559 was retrieved from https://www.socialscienceregistry.org/trials/2559 on 30 September 2026. It describes computer assignment but does not establish the block quotas. It lists 61 smaller-cash villages while retaining the other arm counts; those listed counts sum to 243 despite a stated total of 248. The released data and parent paper have 66 smaller-cash villages. This discrepancy is preserved rather than silently reconciled. The registry does not resolve the probability-generating mechanism.

For the conditional analysis, assume labels are exchangeable within each released block conditional on its realized counts, and assignments are independent across blocks under that conditioning. Then each village's conditional probability is its block's arm count divided by block size. Uniform fixed-quota assignment implies this model; some more restrictive mechanisms would not. It is an explicit maintained design assumption, not proof recovered from the observed frequencies. Household frame expansion and treatment probabilities are separate. Exact conditional assignment statements target the released baseline sample expanded by its fixed weights; representing the entire eligible frame additionally relies on the household sampling/observation assumptions.

## Ratio scores and cross-arm covariance

Let N_ba and D_ba be the weighted outcome and weight totals contributed by assignment block b to arm a, including inverse conditional assignment probability. The arm ratio is sum_b N_ba / sum_b D_ba. Its estimated block score is

    u_ba = (N_ba - muhat_a D_ba) / sum_b D_ba.

These scores sum to zero for each arm. The vector u_b includes all arms in the same block. Its outer product therefore retains the cross-arm covariance that was forced to zero by arm-exclusive village scores. The working covariance is B/(B-1) times sum_b u_b u_b'. All policy contrasts and missingness endpoints must use these shared block vectors. The ratio point estimates and common dietary distributions do not change merely because covariance is grouped correctly.

For the population linearization with nonrandom denominator limits, write independent block scores psi_b with expectations m_b and sum_b m_b=0. The expectation of B/(B-1) times the centered score sum of squares is

    sum_b Var(psi_b) + B/(B-1) sum_b m_b m_b'.

The second term is positive semidefinite. Thus differing fixed-block expected scores can add conservative covariance rather than justify discarding cross-arm dependence. Replacing the population ratios/denominators by their estimates requires a ratio linearization and a sequence with increasing independent blocks, stable positive denominators, and no dominating block. This argument is asymptotic. There are only 22 actual blocks; neither the covariance identity nor resampling proves exact finite-sample coverage.

## Exact counterexample check

code/blocked_inference.py::referee_counterexample enumerates every ordered assignment of two different villages in a block with five scores 4 and five scores 6. It verifies covariance -1/(9B), true difference variance 20/(9B), and the old separate-arm expected estimate 2/B. The latter is 90% of the true variance. The common block covariance retains the missing term. This validates the specific analytical repair; it is not a simulation of Rwanda's actual coverage.

## Monte Carlo and finite-block diagnostics

Block scores have now been integrated into the exploratory ratio/endpoint outputs, using 99,999 draws and a 99% Monte Carlo upper order statistic for the 95% multiplier quantile. Zero estimated variances receive deterministic support ranges rather than structural-zero intervals. These changes repair the covariance omission and Monte Carlo treatment; they do not make the finite-block approximation reliable by assertion.

Synthetic stress tests using the actual quota structure, 800 replications and a smaller 4,999-draw diagnostic multiplier calculation found joint coverage 695/800 in the equal-weight scenario and 592/800 with unequal frame weights. Those results contradict treating the corrected block approximation as a reliable 95% finite-design guarantee here. A sparse positive-effect scenario received full support guards and covered 800/800, which does not rescue the other cases. The observed failures are retained in output/blocked-validation.json; no nominal-coverage test has been passed.

Nested 9,999/29,999/99,999-draw critical values are retained in output/multiplier_quantile_sensitivity.csv. At 99,999 draws, the endpoint-family empirical 95% quantile is 3.190164 and its 99% Monte Carlo upper value is 3.196006. This protects simulation error conditional on scores, not sampling coverage. The historical pure-lower one-group result disappears after the block repair: its current exploratory upper value is 1.019257. Neither that disappearance nor a small Monte Carlo margin validates the bands.

## Finite conditional-assignment outer regions

For a fixed primitive transformation Y in [L,H], observation indicator R and positive baseline weights, define its fixed potential-observation target mu = sum(w R Y)/sum(w R). For full-baseline endpoints R=1. At the true mu, village residuals X_j(mu)=sum_in_j w R (Y-mu) sum to zero over the full fixed sample. Let Wmax_b be the largest baseline village weight in block b. Because mu is inside [L,H], every village residual lies between (L-mu)Wmax_b and (H-mu)Wmax_b, an interval of width (H-L)Wmax_b.

Each arm selects k_ba villages uniformly without replacement under the explicit conditional model; its scaled residuals are X_j/p_ba. Hoeffding (1963), Theorem 4, bounds the convex exponential moment by with-replacement sampling. Independent blocks and the bounded-variable exponential inequality imply

    Pr(|sum_j T_ja X_j(mu)/p_ba| > t)
        <= 2 exp{-2t^2 / [(H-L)^2 V_a]},
    V_a = sum_b k_ba (Wmax_b/p_ba)^2.

Choose t=(H-L) sqrt{V_a log(2M/alpha)/2}. Its residual equals the realized positive denominator times (muhat-mu), so dividing gives the ratio interval centered at muhat with radius t/Dhat, clipped to [L,H]. A zero realized denominator receives full support. This inversion is for the fixed true mu; no grid of hypothesized means requires an extra multiplicity factor. A union bound protects M fixed primitive targets despite cross-arm dependence. Full-baseline endpoint ordering then covers every admissible diet mean and every selected allocation computed from the same region.

The separate full-baseline family has M=276=6 arms x 23 distinct transformations x 2 endpoints. The observed family has M=138. Both use alpha=.05; their union is not asserted to have 95% coverage. The third-submission mean-box loss is 9.440422 groups, compared with 0.570058 for the unvalidated block sensitivity. The fourth revision projects all protected transformations through coherent score distributions and intersects deterministic consistency restrictions, giving 7.720305 groups without a new coverage event. Full construction and support-only/institutional benchmarks are in distribution-inference.md. Neither finite calculation proves no sharper valid procedure could succeed; the smaller block result remains no established small-loss guarantee.

Primary source: Wassily Hoeffding (1963), Probability Inequalities for Sums of Bounded Random Variables, JASA 58(301):13–30, DOI https://doi.org/10.1080/01621459.1963.10500830. The original article was inspected through the university-hosted copy at https://www.cs.rpi.edu/academics/courses/spring06/random/hoefding.pdf; its full text is not redistributed. The manuscript derives the application, not a new concentration theorem.

## Decision optimization and checks

code/policy_allocation.py allows all six allocation shares. For every feasible comparator vertex, it solves the worst mean-vector adversary over a common arm region; the allocation LP minimizes their maximum with a dual vector for each comparator. Independent primal adversaries verify every main certificate. Fitted outcome maximization, observed-region choice, full-baseline-region choice and a statistical minimax-regret sampling rule are distinct; the last is not established here. The original source's national-scale standardized unit costs are maintained assumptions, not mixed-program marginal cost estimates.

All 32 cost settings are recomputed for the headline coherent means and common regions, rebuilding vertices after cost-order or feasibility changes. Effects stay fixed; these are accounting sensitivities. Pre-treatment child cohort membership is fixed by source flags, with observed-follow-up selection still disclosed. Decision validators check bounded-sampling exponential moments, exhaustive small ratio assignments, scaling, zero denominators, primal adversaries, allocation feasibility and cohort partitions. These checks do not certify actual Rwanda sampling coverage or full-frame representativeness. The ANCOVA CR2 diagnostics cannot validate these different estimators.
