# Historical sixth-revision method comparisons

The current seventh comparison, including the omitted product/hybrid benchmark, restricted empirical Bernstein and exact regional brackets, is in [quota-methods-round7.md](quota-methods-round7.md). This file preserves the sixth-revision derivation and omissions; its omission statements and 49.23% comparison are historical.

This analysis responds to the fifth report's methodological-positioning concern. It does not change the frozen fifth submission, introduce observations, identify an operational CRS objective, or establish a leading-journal contribution. All results are separately scoped. The empirical table compares valid upper certificates for the **same rational allocation proposals**. It does not compare method-specific minimax optima, and differences between upper certificates need not equal differences in exact worst-case loss.

## Existing methods and their adaptation

The arithmetic average of expectation-bounded nonnegative tests is an established dependence-robust e-value construction, rather than a new aggregation theorem: [Vovk and Wang, E-values: Calibration, combination, and applications](https://www.alrw.net/e/02.pdf). Sampling-without-replacement concentration also predates this application. [Bardenet and Maillard (2015)](https://arxiv.org/pdf/1309.4029), Lemmas 1.1/1.3, Proposition 2.2 and the intermediate forward-martingale calculation in its proof, supply the three range-based moment comparators. [Waudby-Smith and Ramdas (2020)](https://proceedings.neurips.cc/paper_files/paper/2020/file/e96c7de8f6390b1e6c71556e4e0a4959-Paper.pdf), Theorem 3.1, supplies another interpretation of the unrelaxed harmonic calculation through predictable exponential scales. These comparisons do **not** implement their variance-adaptive empirical-Bernstein or betting methods; superiority over those methods is unestablished.

In a block of n villages with quota k, let t_j=W_j(y_j-u), where the normalized potential outcome and candidate mean satisfy 0<=y_j,u<=1. All t_j lie in [-u Wmax,(1-u) Wmax], an interval of length Wmax. The centered block HT residual is

G=(n/k) sum_{j in A} t_j - sum_j t_j.

For uniform subsets A, its mean is zero. The classical moment bounds have the form log E exp(lambda G) <= lambda² V/8. The forward coefficients V/Wmax² are:

- Hoeffding: n²/k.
- Serfling: (n²/k)[1-(k-1)/n].
- Unrelaxed harmonic martingale: (n²/k²)(n-k)² sum_{t=1}^k (n-t)^(-2), for k<n.

The last expression retains the finite reciprocal-square sum before Serfling's integral relaxation. It is already present in the established proof; it is not a new concentration result. Its connection to the modern Hoeffding process follows by choosing predictable scales lambda_t=Lambda(n-k)/(n-t), with Lambda=lambda*n/k. For any sample position j, the coefficient lambda_j + sum_{t>j}lambda_t/(n-t+1) telescopes to Lambda. The exponent's outcome term is therefore Lambda sum_{j in A}(t_j-mean(t)), and its quadratic compensation is the displayed harmonic sum.

The complement identity G_k=-(n-k)G_(n-k)/k supplies a second valid coefficient. Each comparator uses the smaller forward and rescaled complement coefficient, selected using the design alone. At k=n the residual and coefficient are zero. Across independent blocks the coefficients add, using each block's actual maximum fixed weight. This adaptation remains conditional on the same quota-assignment model and fixed released-baseline target as the quota event.

For each alternative, the 23 score functions, missing-item numerator envelopes and identified-bin/logical restrictions are rebuilt exactly as in the quota construction. Every elementary tail term has expectation at most one. Their shared sum has the same cap 5520 and the same 276/5520 conditional failure bound. No separately valid confidence events are intersected or selected according to which reported loss is smallest.

Classical statistical scales minimize the scalar radius (lambda² V/8+log5520)/lambda using baseline quantities alone. The production quota scales retain their original baseline-only four-point selection. These are not identical scale searches: classical quadratic bounds permit a closed-form optimum, while quota enumeration uses a finite grid. Their differing scale rules are disclosed, rather than calling the comparison a pointwise dominance theorem.

## What the empirical comparison holds fixed

`code/quota_benchmarks.py` recomputes the same fixed proposals' mean and six-group shortfall certificates under the three classical moments. It selects nonnegative support multipliers with a diagnostic scalar search and then runs the directed tangent/feasible-dual verifier. These outcome-dependent multipliers optimize a deterministic support bound within an already-defined region; they do not select the statistical event. The canonical proposal file and fifth-submission moment/event outputs are not overwritten. Comparison receipts, selected multipliers and actual execution time are stored in `output/quota-benchmarks.json`; a compact table is in `output/quota_benchmarks.csv`.

Two ablations use the same production quota moments/scales. Requiring each individual tail term to be at most 5520 gives a standalone Bonferroni region. The shared sum constraint implies those individual constraints, so its region is nested within this separable region. Removing the identified-bin floors while keeping scalar logical consistency enlarges the shared region. Directed bounds can vary slightly with tangent candidates; their numerical ordering alone does not establish exact changes in optimized regret. In particular, near-equal mean bounds with and without bin floors should not be described as a large contribution from bin floors.

## Representative designs

`code/benchmark_quota_designs.py` reports the entire deterministic catalogue: n in {6,10,12}; distinct quotas in {1,floor(n/4),floor(n/2),n-1}; equal weights, alternating weights 1/3, or one weight 10 with other weights 1. There are 22 identical independent blocks and the fixed family penalty log5520. Classical quadratic moments use their analytic scale optimum. Quota moments use six baseline-only scales around the harmonic scale. The outcome is a scalar tail radius divided by total fixed weight, not an allocation loss or a field estimate. Radii exceeding the support are reported untruncated so an apparent gain outside the informative range is visible.

These designs vary quota fractions and weight concentration, while holding block count and family penalty fixed. They are selected transparently after the fifth review, not registered prospectively or representative of all applied designs. The catalogue excludes larger blocks, unequal block sizes, variance-adaptive inference and treatment-dependent endpoint patterns. Computation enumerates binary outcomes and quota subsets, with exponential growth in block size; the range-based comparators avoid that enumeration.

The observed pattern is small gains with equal weights and much larger gains when a maximum-weight village is exceptional. For n=12,k=6, the quota radius is 0.132848 with equal weights versus 0.135977 for the harmonic comparator. With one weight 10 it is 0.394492 versus 0.777009. The corresponding improvements are approximately 2.30 and 49.23 percent. This describes this catalogue's baseline moment radii; it does not establish a universal performance advantage, calibrated welfare benefit, or small-loss recommendation in Rwanda.

## Verification and limits

`code/validate_quota_benchmarks.py` checks the exact coefficient hierarchy and directed Fraction-to-Decimal enclosures for every quota with n=2,...,20. It also independently enumerates binary populations, both centering endpoints and all quota subsets for eight small equal/unequal-weight fixtures at five exponential scales. All 7,138 checks pass, including 6,720 high-precision moment inequalities. The analytic moment arguments supply coverage; passing fixtures are not a substitute for those arguments or a field-coverage estimate.

The empirical comparison uses the existing enclosed support verifier on its new constants. Broader external comparison, method-specific optimizer assessment and an independently regenerated microdata chain remain required. A useful methodological pattern in this limited catalogue is progress on the fifth-report concern, not a recommendation of acceptance.


Actual sixth-revision fresh-source audit completed: **102/102** output comparisons pass, including both new tables, both benchmark CSVs, five macro files, output map and 34-page PDF text. Cold scientific master took 498.536787 seconds using the same installed interpreter. Its initial comparison wrapper failed with `AttributeError: 'str' object has no attribute 'relative_to'` because two added paths were strings. Both entries were corrected to Path objects, and the comparison was rerun against the already completed cold outputs; the scientific master was not repeated. The error and recovery are recorded in output/clean-run.json. This remains internal reproduction, not fresh environment provisioning or external scientific replication.

Optional harmonic allocation search completed in 711.336830 seconds. Mean: 30 iterations, floating upper 6.54311824495414, diagnostic gap 0.00041404881027; it exhausted the iteration limit without reaching the 0.0003 stopping target. Shortfall: nine iterations, floating upper 0.5474535432253077, gap 0.00009834471497. Directed verification of exact-rational proposals gives **6.544 groups / 0.548 shortfall units**, respectively 6.543115241696492 and 0.5474520405798181 before upward display rounding. These remain verified proposals, not certified minimax optima or gaps. Optional receipts are separate from the manuscript's fixed-proposal comparison and production quota inputs. No observed minimum across separately valid confidence events is asserted.
