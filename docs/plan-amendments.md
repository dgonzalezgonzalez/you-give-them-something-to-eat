# Plan amendments and reasons

2026-09-30, before any regression successfully ran: source `dietarydiversity`
contains seven noninteger endline scores equal to 4.46262979507. The underlying
16 food indicators contain 888, 999 and missing codes. A 12-group score rebuilt
from valid binary indicators matches the source exactly for all 5,414 complete
records (all rounds/populations); 92 records have an incomplete food module.
Use the reconstructed integer score, setting incomplete modules missing, for
primary distributional analysis. Retain source score for robustness. Missing
baseline values are imputed only as ANCOVA controls, never as observed outcomes.
No treatment-effect estimate was seen before this measurement decision.

2026-09-30: Numerical implementation uses the explicit WLS/CR1 sandwich in NumPy
and SciPy t-distribution functions rather than adding statsmodels dependencies.
Joint primary family includes all 17 transformations and all 8 feasible cash/control
vertices (including control and feasible pure cash policies), rather than a
selected subset. This protects both threshold and policy selection.

2026-09-30, after the first estimates: extend the joint max-t family to the
85 arm-versus-control comparisons as well as 136 policy contrasts, yielding 221
comparisons. This conservative expansion prevents recipient-level diet claims
from escaping the multiplicity correction. Correct baseline imputation to the
prespecified weighted within-block mean; global imputation in the first code
draft was an implementation error. All estimates regenerated after correction.

2026-09-30, after inspecting observation diagnostics: display all five observed-diet retention effects with a separate five-test Holm family. Upper cash has higher observation. This diagnostic does not change the primary family or establish selection ignorability. Added explicitly to manuscript so the observed-case limitation is concrete.


2026-09-30, after the genuine round-one referee report (17m02s): revise the
scientific framing because the parent paper already covers cost effectiveness
and extensive-margin allocation. Add source-specification crosswalk, explicit
block assignment probabilities, positive-weight Hájek distributions, all twelve
integer survival and shortfall thresholds, item-informed intervals for every
baseline eligible household, endpoint sampling bands, all-policy comparisons,
regret and illustrative tolerances, known-cost/take-up/avertable-share scenarios,
CR2/Satterthwaite working-model sensitivity, village/block omission and score/
weight concentration. Analyze available corrected child and ineligible outcomes
with separate fifteen-test Holm families. These are exploratory referee-driven
extensions; the original plan and initial estimates remain recoverable in Git.

Deduplicate 17 repeated primary Gikuriro/control nulls (204 distinct tests, 221
display rows) and eight secondary repetitions (96 distinct tests, 104 rows).
Revision mean/shortfall-12 and survival-1/shortfall-1 affine repetitions likewise
enter only once: 184 distinct GK/cash comparisons, 828 distinct all-policy
comparisons and 1,656 interval endpoints. Max-t bands retain affine scaling.

Direct verified-ZIP extraction is bound to a frozen independent byte reference;
supplementary source members and derived bytes are pinned before resubmission.
Adversarial tests use isolated fixtures, never altered research inputs. The first
CDF validation draft accidentally aligned different pandas row labels instead
of ordered threshold arrays; the validator was corrected and every identity
then passed. This was a verification-code error, not a revision of estimates.

2026-09-30, after the genuine second referee report: arm-exclusive village Hájek
scores omitted fixed-quota cross-arm covariance. Replace them by shared 22-block
ratio vectors and preserve the exact referee counterexample. Increase exploratory
multipliers to 99,999, add a 99% Monte Carlo upper quantile/nested-draw sensitivity,
and replace zero-variance intervals by deterministic support. Conditional label
exchangeability given released counts is now explicit; original assignment code
and all restrictions are not recovered. Fixed expansion weights do not prove
full-frame sampling representativeness.

Synthetic stress uses actual block quotas, seed 20261001, 800 assignments/scenario
and 4,999 diagnostic draws. Coverage 695/800 (equal weights) and 592/800 (unequal)
fails nominal coverage. Failures remain in the package; reliable one-/half-group
certification claims are withdrawn, without ad hoc critical-value inflation.

Add separately derived finite conditional-assignment outer regions using bounded
sampling without replacement, fixed positive weights and a 276-primitive endpoint
family (138 for a separate observed family). Independent exchangeable quota
assignment and stable potential outcomes are assumptions. Broad outer regions
are not sharp bounds or an impossibility result. These choices follow the observed
inferential flaw/failures; no prospective-registration claim is made.

Optimize region regret over every feasible allocation share, retaining vertices
only for the known-mean adversary. Independent primal verification checks the
dual certificates. Align 32 cost settings to coherent means/regions and disclose
separate national-scale overhead at 56,127 beneficiary households for each cash
amount. Add baseline source-flag child cohort accounting/observed-follow-up
sensitivity with a separate fifteen-test Holm family.

Reorient the main manuscript toward the conditional weighted-baseline decision;
move initial ANCOVA/coarse bounds and saving illustration to appendices. Add
Manski (2007)/Stoye (2007), derive exhibit counts and preserve genuine reports.
Twenty smaller public CSV parts reconstruct existing immutable input bytes for
file-size-limited readers; scientific data and external replication status do
not change.

## Fourth revision after the genuine third rejection

The third referee accepts the finite proof and allocation formulation within its inspected scope, but rejects the economic contribution at the unchanged leading general-interest standard. It independently demonstrates support-only regret 9.6 and a tighter 8.151078 projection using already-protected distributional constraints. No household/child microdata or manuscript PDF execution is attributed to that review.

The fourth revision adds the no-outcome benchmark, deterministic item/outcome-consistency restrictions and discrete score-distribution polytopes using all 25 displayed/23 distinct transformations. Projection inherits the existing conditional event, without a new multiplicity penalty. Their intersection gives mean loss 7.720305, still too wide for a small-loss conclusion. Exact scalar projection of this outer polytope is not joint potential-outcome sharpness. No additional-data necessity or new statistical minimax-regret theorem is claimed.

Six hypothetical assistance/spending classes are evaluated with both own-menu and common original comparators. A minimum Gikuriro share can mechanically scale own-menu regret; the manuscript proves and labels that effect. Six unestimated unused-resource values expose the baseline objective's omission. Thirty-two cost scenarios per current finite method retain fixed outcomes and national-scale average units. These choices are referee-driven exploration, not discovered institutional mandates or calibrated welfare preferences.

The analytical codebook separately documents baseline child membership/inference and explicit assignment assumptions. A compact scope table consolidates targets while positive claims retain local selection qualifiers. The same manuscript file and existing compiler remain in use. Four generated macro sets, actual exhibit numbering and all historical analyses/reports remain recoverable. Internal cold-copy and future separate-source verification are reported with their actual scope; neither is independent full replication or a path guaranteed to simulated acceptance.

## Development after the genuine fourth rejection

The fourth report accepts the principal third-report technical requests within its inspected scope, but rejects on economic contribution. Its requested interpretation repairs distinguish changes in optimized regret bounds from true-mean dietary opportunity costs and incremental finite tightening beyond deterministic consistency. Eleven repetitive auxiliary table displays are removed from the manuscript while every generated analysis remains in the package. No theory embellishment, changed journal standard or manufactured acceptance is used.

A new author-initiated hosted workflow adds a genuinely fresh environment and full cold microdata-to-PDF execution with version-specific receipts. It is not independent scientific replication and does not solve the distinct contribution objection. Further finite-inference refinements are still scratch exploration; they are not substituted for the frozen fourth result or claimed validated merely because an optimization completed.

## Fifth-revision conditional quota procedure

1 October 2026. A new standalone 276-term exponential-mixture event uses convex quota-box moments chosen by a fixed baseline-only four-point grid. Missing-item ordering retains arm-dependent missingness; a common six-distribution probability region preserves its one conditional event. It is not intersected with the previous nominal 95% sets. Outward moment/observable/logical arithmetic, enclosed convex tangents, feasible exact-checked LP duals and rational allocations verify proposal bounds of 5.868 groups and 0.503 shortfall units. Proposals may use outcomes on this event; moment scales do not. A longer exploratory exchange search chose the stored numerical proposals; its approximate gap is not a certified minimax result. No new observations, randomization restrictions, institutional objectives or general theoretical novelty are asserted. Broad bounds and the unchanged contribution objection remain.


## Sixth-revision existing-method comparisons

1 October 2026, after the genuine fifth rejection. Compare existing without-replacement Hoeffding, Serfling and unrelaxed harmonic-martingale moments under the same released target, incomplete-outcome construction, score functions, costs and rational proposals. Baseline-only scale rules and outcome-dependent deterministic support multipliers remain distinct. Separate-tail and bin-floor ablations hold quota constants fixed. Every alternative has its own conditional event; no observed minimum or intersection is treated as jointly 95% valid. Report all 33 designed moment-radius cases and disclose catalogue omissions, enumeration complexity and missing variance-adaptive comparators. A separate optional harmonic allocation search evaluates optimizer sensitivity without replacing production proposals. These are retrospective additions prompted by review, not prospective registration. General-interest contribution and operational objectives remain unresolved.
