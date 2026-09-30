# Analysis plan frozen before inspection of treatment effects

Date: 2026-09-30. Secondary analysis; not an original trial registration.
The original publication and its published results are known. No claim of blinded
or prospective trial preregistration is made. Decisions here precede computation
of this project's estimates; later revisions will be logged explicitly.

## Question and contribution to investigate

At a fixed aid budget, does universal Catholic Relief Services Gikuriro improve
the distribution of household dietary diversity relative to feasible lotteries
over the experimentally observed cash-transfer packages? The original paper
estimates mean impacts and uses interpolation in transfer size. This project
instead compares budget-feasible policy mixtures, for which outcomes are mixtures
of observed distributions. It does not estimate responses at unobserved transfer
amounts. Establish novelty by searching the literature before making novelty claims.

## Population and identification

IPA-defined eligible households at baseline in the 248-village Rwanda trial.
Village-level randomized assignment, original randomization block fixed effects,
baseline sampling weights, and inference clustered by village. ITT is primary.
Use documented sample-panel and baseline/endline flags; verify attrition and
weight meanings before final estimation. Avoid conditioning on program receipt.

Policy lotteries operate over whole villages at the original within-village
eligibility/saturation. This preserves within-village spillovers embodied in the
trial. Transport of this policy comparison requires no cross-village spillovers,
stable implementation costs and treatment delivery, and policy lotteries independent
of potential outcomes conditional on the original blocks. Average budget is fixed;
an exact finite-sample spending cap and individual-level selective targeting are
not identified. Costs are provider costs per eligible household, from the source
cost workbook; distinguish treatment cost, transfer received and USD vintage.

## Primary outcomes and inference

Household dietary diversity (HDDS): prespecified primary domain, a proxy for food
access, not a validated hunger measure or child-level nutrient adequacy. Compare
all integer thresholds supported by the documented 12-group construction. Joint
inference protects threshold searches. Summary welfare outcomes: HDDS mean and
normalized diet shortfall max(z-HDDS,0)/z for illustrative z=4,6,8. No claim that
these thresholds are official food-security cutoffs. At z=6 also report squared
shortfall to show sensitivity to priority given to the worst diets.

Baseline-adjusted ANCOVA for every transformation (baseline transformation,
block FE, original weights). Retain a missing-baseline indicator and within-block
baseline mean imputation where needed. Report complete-case robustness. Estimate
each original cash arm separately if assignments are preserved. Contrast universal
Gikuriro against (i) each adjacent cash/control mixture bracketing its cost and
(ii) coverage lotteries between control and each cash arm with sufficient cost.
If a cash arm costs less than Gikuriro, leave budget unspent rather than invent a
larger transfer. Report all feasible pairwise mixtures; the frontier is an explicitly
exploratory optimum, with simultaneous uncertainty rather than selected t tests.

Two-sided 5% tests, 95% confidence intervals, clustered finite-sample adjustment.
Joint max-t multiplier bootstrap over village score contributions, seed 20260930,
9,999 draws, plus Holm adjustment. Validate against cluster-robust sandwich formulas.
No significant result is required. Published outcomes are prior information.

## Secondary outcomes and robustness

Monthly total consumption (source asinh and real levels if documented), purchased
food and own-produced food values, diet-group indicators (descriptive mechanism
evidence with multiplicity correction), productive assets, savings, borrowing,
nutrition knowledge and sanitation practices where available. Baseline diet below
versus above median and baseline consumption below versus above median are the
only prespecified heterogeneity splits. No causal mediation claim.

Unadjusted arm estimates, ANCOVA, equal village weighting, original survey weighting,
balance, attrition by arm, missing outcomes, and bounded [0,12] worst-case attrition
bounds for diet. Check labels, original code, duplicate IDs, constant assignment
within villages and timing before modeling. Report limitations if complete baseline
sample cannot be reconstructed. Include ineligible spillover evidence if supported.

## Theory and calibration

Develop a charity allocation model with concave or shortfall-sensitive nutritional
welfare, overhead and budgeted coverage. Prove attainable policy outcomes form a
convex hull under village lotteries. Derive the budget frontier and sufficient
conditions for universal packages versus concentrated cash. Discuss whether
dominance is uniform over monotone/concave diet-welfare functions. Calibrate coverage,
welfare contrasts and break-even unmeasured Gikuriro benefit from verified program
costs and estimated outcomes; label these policy accounting exercises rather than
identified total welfare or structural parameter estimates.

## Transparency

Record corrected source DOI and archive hash. Never republish withdrawn data.
Keep raw archive out of GitHub; use an automated downloader and inspect an anonymized
minimal analysis file before any public redistribution. All table/figure/in-text
numbers generated by one master command; document software, seeds, rights, runtime,
memory, codebook, output map, limitations and full clean-run results. Preserve
ChatGPT referee prompts/reports verbatim; simulated referee acceptance is not real
journal acceptance. Writing must be original, sourced and scientifically honest;
detector scores do not establish authorship and cannot be guaranteed.
