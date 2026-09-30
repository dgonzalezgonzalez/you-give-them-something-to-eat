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
