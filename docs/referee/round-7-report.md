# Seventh-round referee report

**Manuscript:** *You give them something to eat: Dietary Diversity, Coverage, and Catholic Aid in Rwanda*  
**Reviewed tag:** `v0.7.0`  
**Resolved review commit:** `77c0afa2708814f9d6e83a5a211fd3ed7e5a78d3`  
**Scientific/verification source:** `c8af01aed8725f9ef06fc0974e35ec363ab418de`

## Recommendation: **Reject**

This revision makes substantive progress on the methodological objections in my sixth report. The sorted-threshold algorithm addresses the earlier exponential-enumeration problem. The regional lower-bound construction addresses a different and important weakness: comparing upper certificates alone did not establish an ordering of the methods’ optimized regional decision values. The empirical-Bernstein comparison and known-population exercise also provide useful evidence against a broad quota-dominance interpretation.

**I do not identify a central mathematical error in the new constructions within the scope inspected. Nevertheless, the paper remains insufficiently consequential for a leading general-interest economics journal.** Its strongest advances concern computation and characterization of particular uncertainty regions. The empirical allocation result remains broad, the organizational decision remains hypothetical, and the designed performance exercise does not establish a sufficiently important domain of methodological advantage.

That judgment does not require uniform method dominance, a new experiment, or a uniquely identified best treatment. A substantial computational or methodological contribution could justify publication independently. The present combination of specialization, application, and performance evidence does not yet reach that threshold.

This is a simulated referee recommendation, not an actual journal decision.

## What I retrieved and executed

### Version and source inspection

I resolved the annotated tag and compared the Git trees with the stated hosted source. The **code, data, paper, canonical output, workflow, dependency files, and master script have matching identifiers**. The review freeze changes documentation rather than those scientific objects. This verifies version correspondence, not execution or correctness of the analysis.  

I inspected the manuscript’s main text and new technical appendix; the all-point response; the self-contained methods note; the sorted-moment, benchmark, empirical-Bernstein, model-building, regional-lower-bound, designed-decision and exhibit-building programs; selected model/dual receipts; the comparison summary; and the generated decision-performance table.

### Independent execution

My calculations in this round were deliberately separate from the author’s full replication program:

| Work executed | What was checked |
|---|---|
| Independent 120-digit implementation of sorted-threshold maximization and the positive recurrence | Agreement with exhaustive binary-population/subset calculation in 39 small cases; also evaluated one larger \(n=96\) case without exhaustive verification |
| Independent 100-digit empirical-Bernstein fixtures | Fifty-two finite-population expectations, endpoint domination, and equivalence of averaging over subsets and all sample orders |
| Exact-fraction two-arm calculations | The rectangular-region minimax formula and probability-rounding bound in 225 interval configurations |
| Exact replay of the published quota mean dual’s nonzero terms | Reproduced its exact lower fraction, conditional on the published rational arm means |

The moment calculations agreed to approximately \(10^{-119}\) in the small exhaustive comparisons. The empirical-Bernstein fixtures respected the expectation and endpoint inequalities checked. The quota mean-dual arithmetic reproduced

\[
5.866228120555938,
\]

with a gap of approximately \(0.000900168383\) to the upper value stored in that receipt.

**That last calculation did not verify the underlying probability populations’ membership in the empirical region.** I did not replay all 152 populations, sixteen duals, or the complete lower/upper certificate chain. Likewise, my synthetic programs are independent implementations of the mathematical formulas, not executions of the author’s new validators.

The **:chatgpt-content-reference{index="25"}[audit summary](sandbox:/mnt/data/referee_round7/summary.json)** and **:chatgpt-content-reference{index="26"}[calculation programs and receipts](sandbox:/mnt/data/referee_round7_audit_v0.7.0.zip)** record these distinctions.

### Retrieval and replication limits

Direct archive/PDF retrieval failed. I did **not** reconstruct the twenty public data partitions, execute household or child microdata, regenerate empirical normalizers or model constants, run the master or Stata, rerun the 144-cell decision experiment, inspect or compile the manuscript PDF, or download and independently hash the hosted artifact.

I queried GitHub’s job and artifact metadata. They corroborate a successful hosted job and the stated artifact’s size, source commit and recorded digest. That is metadata verification—not my execution of the hosted analysis or verification of downloaded archive bytes.

# Major comments and disposition of the sixth report

## 1. Economic importance: a stronger methodological application, but the central contribution remains inadequate

**Disposition of prior M1: substantive progress; the leading-journal objection remains.**

The revision now distinguishes three objects more convincingly: a feasible allocation with a verified upper certificate, the optimized decision value within an implemented uncertainty region, and actual regret in a known-population experiment. That distinction is valuable. The new regional lower bounds show that the field quota result is not merely an artifact of a poor allocation search. 

However, the principal empirical conclusion remains essentially unchanged: the selected allocation has a broad conditional dietary-loss guarantee, not a small-loss guarantee, and the paper does not identify the wider welfare ranking. The new computational work clarifies why further optimization of this particular region will not solve that problem. It does not establish that the experiment lacks useful information under other justified analyses.

This matters for the opening question—how much a food-security experiment adds to treatment choice. The paper answers a narrower question: what certain confidence-region constructions and policy classes produce when applied to this experiment. That can support a methodological application, but it is not a general valuation of experimental information or an evaluation of the organization’s actual decision.

The revised evidence has also narrowed the potential methodological claim. The inexpensive hybrid reduces the previously highlighted moment advantage, while empirical Bernstein performs better in important parts of the designed exercise. Those are informative findings, not reasons to suppress the comparison. But they leave the paper without a clearly demonstrated, economically important domain in which its proposed combination changes decisions or materially improves protection.

**Priority:** organize the contribution around a precise, consequential claim supported by these results. Neither a further decimal improvement nor another collection of implementation checks will supply that claim. A method need not dominate everywhere; it does need a compelling account of where its advantages matter.

## 2. Assignment, target population, and outcome-free tuning

**Disposition of prior M2: the formulation remains appropriate; the actual assignment law remains unverified.**

The paper continues to distinguish the maintained conditional model from the historical assignment mechanism: uniform labels given block quotas, independent blocks, fixed released-baseline weights, and stable bounded potential diets. Realized counts do not verify the original law, and the weights do not establish representation of unsampled households or transport to deployment. These limitations are correctly retained. 

The new statistical tuning rules remain compatible with that model. The quota and product/harmonic scales use baseline design information. The empirical-Bernstein forecast and scale heuristic also use weights and quotas rather than follow-up outcomes. The forecast’s working uniform-score assumption affects tuning, not the asserted distribution of the actual outcomes.

The distinction between statistical scales and numerical support multipliers remains essential. Choosing an admissible statistical scale from conditioned-on baseline quantities defines a valid event. Choosing a support multiplier after observing outcomes optimizes a deterministic bound within that event. These are different operations, and the inspected implementation treats them separately. 

**Priority:** retain this conditional scope prominently and seek the original protocol or investigator confirmation of assignment restrictions. That is a documentation requirement, not necessarily new data collection. Until resolved, the finite guarantees should not be described as verified exact statements under every restriction actually used in the original randomization.

## 3. Missingness and the empirical-Bernstein adaptation

**Disposition of prior M3: the accepted selection treatment is maintained, and the new comparator has a defensible endpoint argument.**

The full-baseline target continues to include households with incomplete or absent diets. Knowing one transformation does not automatically identify a complete score, and observation-specific ratios remain distinct from effects on the full baseline population. These distinctions are not lost when the new comparator is introduced. 

For the empirical-Bernstein comparator, the crucial construction is not a zero fixed normalizer. The code replaces the preliminary fixed-normalizer affine rows with rows incorporating realized compensation and the **fixed total population weight**. I verified that branch in `quota_models.py` and `empbern_models.py`. The placeholder zero must not be interpreted as a claim that the uncompensated residual has moment-generating function bounded by one.  

The endpoint step is mathematically sensible. With the forecast fixed, each signed observed contribution has the form

\[
sax-\rho(x-\gamma)^2,\qquad \rho\geq0,
\]

which is concave in \(x\). Its minimum over a reported interval occurs at an endpoint. Replacing the contribution by that minimum gives a pathwise lower test, preserving the relevant expectation bound without reporting ignorability.

Order handling is also important. Uniform sampling of an unordered set does not make the identifier ordering a random sample sequence. Averaging the **positive tests** over all sample orders addresses that issue; averaging log tests would be a different calculation. The inspected field implementation uses the positive average. 

My small-population checks support these steps, but do not regenerate the field compensation terms. The argument is a restricted adaptation of the established without-replacement empirical-Bernstein construction, not an implementation of its full adaptive forecasting or betting family. :chatgpt-content-reference{index="9"}

**Priority:** keep the adaptation’s restrictions explicit. Its relatively poor field certificate is evidence about this comparator specification, not about empirical-Bernstein or betting methods generally.

## 4. Regional lower certificates: an important previous objection is now resolved

**Disposition of prior M4: the upper-bound-only comparison objection is substantially addressed for the implemented regions.**

The new lower-bound argument is correct in structure. Suppose every supplied \(\mu^\ell\) belongs to the implemented region and every associated comparator \(r_\ell\) is budget-feasible. For nonnegative probabilities \(w_\ell\) summing to one and \(\eta\geq0\), every feasible \(q\) satisfies

\[
\max_\ell (r_\ell-q)'\mu^\ell
\geq
\sum_\ell w_\ell r_\ell'\mu^\ell
-\eta b
-\max_j\left\{\sum_\ell w_\ell\mu_j^\ell-\eta c_j\right\}.
\]

The first step averages adversarial losses. The second uses nonnegative shares, unit mass and \(c'q\leq b\). Thus any feasible probabilities and multiplier provide a lower bound; global success of the floating-point LP is unnecessary. Exact normalization and evaluation are appropriate. 

This changes what can be concluded from the comparison. The reported quota upper bound, \(5.8671283\), lies below the hybrid’s reported regional lower bound, \(6.5327927\). Conditional on the certified memberships and upper-bound chains, this establishes a strict ordering of the **optimized values of those implemented regions**. The difference exceeds 0.665 groups. It is no longer merely a comparison of upper bounds for a quota-selected proposal. 

The new results also sharpen the floor-ablation interpretation. Because the region with bin floors is contained in the region without them, their optimized losses satisfy \(V_{\mathrm{no\,floor}}\geq V_{\mathrm{floor}}\). Combining the reported brackets bounds the improvement from the floors by less than **0.000916 groups** and **0.000446 shortfall units**. That is stronger evidence of a small contribution here than equality of three-decimal displays alone.

The scope restrictions are crucial. The lower bound does **not** imply that the actual regret is at least 5.866 groups, that the confidence region is sharp for the original finite household population, or that every valid statistical procedure must have a similarly broad guarantee. It bounds a minimization over one implemented outer relaxation.

**Priority:** make this distinction central. The new bracket convincingly separates optimization error from conservatism of the specified region. It does not separate all sources of statistical conservatism or establish a lower limit on what the data can reveal. My exact dual replay verifies the arithmetic conditional on supplied arm means; complete empirical membership replay remains outside this review’s execution.

## 5. Dietary measurement, child cohorts, and the bundled saving mechanism

**Disposition of prior M5: earlier repairs are retained; the substantive evidence gap remains.**

The manuscript still correctly distinguishes household HDDS from child nutrient adequacy, intrahousehold allocation and broader nutritional welfare. Coherent score distributions repair a statistical consistency problem; they do not make the score a comprehensive welfare measure.

The baseline child-cohort analysis continues to distinguish membership, row linkage, physical measurement and valid-score availability. Fixing membership before treatment does not remove selection from missing follow-up scores. The retained Holm nonrejections therefore cannot establish zero full-cohort nutritional effects or replace the parent study’s anthropometric analysis. 

Likewise, the saving illustration remains compatible with, rather than identified by, the bundled assignment. Its mathematical comparative statics are not the problem. The missing ingredient is variation that isolates the proposed channel from nutrition, agricultural, sanitation and other activities. Stronger statistical significance of the bundled saving coefficient would not supply that variation.

**Priority:** retain these boundaries and avoid using the additional technical results to bridge them rhetorically. Stronger claims about individual nutrition, intertemporal welfare or saving mechanisms require additional measurement or identifying variation. No such requirement is necessary merely to publish a carefully scoped dietary-score analysis, but its narrower contribution must then carry the paper.

## 6. Sorted-threshold computation and the finite-event proof

**Disposition of prior M6: the earlier computational concern is genuinely addressed.**

The sorted-threshold reduction is valid in the inspected argument. Start with a global maximizing binary vertex. If a smaller weight is active while a larger one is inactive, remove the active coordinate and view its replacement value as a scalar argument of the symmetric convex objective. Global maximality implies that the value at the smaller active weight is at least the value at zero; convex secant slopes then imply that using the larger weight cannot reduce the objective. Repeated exchanges yield a maximizer activating the largest \(m\) weights for some \(m\).

The symmetric-mean recurrence then averages subset products without enumerating subsets. The complementary-quota implementation correctly retains the original denominator in the exponent. This gives the stated arithmetic complexity

\[
O\!\left(n^2\min(k,n-k)\right),
\]

rather than exponential enumeration. I independently compared this reduction and recurrence with exhaustive small calculations.  

**I therefore withdraw the exponential-enumeration limitation as a characterization of the current quota implementation.** End-to-end cost is a separate matter: empirical-Bernstein order averaging and support optimization have their own costs, and moment timings should not be presented as total allocation runtimes.

The new algorithm evaluates the same relaxed moment problem more efficiently and at actual weights. It does not remove the relaxation between the candidate population mean and village outcomes. The downstream endpoint ordering, expectation bounds and Markov aggregation remain the source of coverage. The product/harmonic minimum likewise combines two valid bounds on the same moment using baseline information; it is not an outcome-selected intersection of confidence sets.

The self-contained proof is useful. I did not retrieve the full Xiang report and therefore do not independently certify the exact novelty boundary relative to that prior work. That access limit does not undermine the specialization’s proof.

**Priority:** distinguish the proven computational improvement, the retained statistical relaxation and the prior-art attribution. The specialization need not be a new concentration theorem to be useful, but its broader importance must be demonstrated rather than inferred from replacing an inefficient predecessor.

## 7. Institutions and opportunity costs

**Disposition of prior M7: the accepted interpretation is maintained; no new institutional evidence is supplied.**

The institutional exercises remain explicitly hypothetical and tied to the earlier coherent region. Changes in optimized regret bounds are not actual dietary opportunity costs at the unknown true means. Restricting both the chosen allocation and comparator can mechanically reduce an own-menu number, as the fixed-share identity demonstrates. The current manuscript retains these distinctions. 

The new regional lower bounds do not identify organizational preferences, mandates, acceptable losses or the set of allocations a provider can implement. They solve the specified optimization problem more definitively.

**Priority:** either keep these sections as illustrations of decision geometry or ground the relevant menu and objective in an actual documented decision. Another hypothetical restriction is not required. Evidence on a real decision would contribute more than further scenario proliferation.

## 8. Provider costs, resources, and transport

**Disposition of prior M8: the cost qualifications remain correct and unresolved.**

The analysis continues to condition on standardized national-average unit costs and an expected-budget lottery. It does not identify marginal mixed-rollout costs, activation costs, capacity constraints, participation responses or changes in outcomes under different cross-village saturation.

The same applies to unused resources. A diet-only objective assigns them no value; adding a hypothetical resource value changes the criterion on both sides of the comparison. Neither the quota proposal’s feasibility nor the narrow optimization bracket justifies an operational recommendation to leave funds unspent. 

The distinction between expected expenditure and a hard realized cap is maintained appropriately. It should not be treated as a coding deficiency in the problem actually stated, but it limits deployment claims.

**Priority:** preserve the conditional benchmark. Operational conclusions require suitable accounts, objectives and transport evidence. These are substantive information requirements, not problems solved by tighter numerical certification.

## 9. Known-population performance: useful negative evidence, but limited generality

**Disposition of prior M9: the omitted comparator and decision-performance requests are substantially addressed.**

The product bound and baseline-only product/harmonic hybrid are now implemented. The revised catalogue correctly reduces the formerly prominent 49.23% gain against the coarse harmonic envelope to a much smaller gain against the cheap hybrid. The common-search gains of approximately 1.39–6.74% are a more informative description of this catalogue. 

The designed decision exercise also moves beyond scalar radii. Its generated table reports:

| Reporting regime | Quota: average actual regret | Fixed-forecast EB: average actual regret | Quota: mean certificate | EB: mean certificate |
|---|---:|---:|---:|---:|
| Complete | 0.019 | **0.017** | 0.114 | **0.101** |
| Coarse intervals | 0.031 | **0.029** | 0.210 | **0.195** |
| Assignment-dependent | 0.039 | 0.039 | 0.320 | 0.318 |

These are rounded values from the generated table, which I inspected but did not regenerate from all simulation draws. No method obtains a certificate at or below 0.10 under the assignment-dependent regime in that table. 

The negative result is important: better quota-based field certificates do not establish better decision performance generally. The revision acknowledges that rather than claiming dominance.

Several limits should determine the interpretation. Every designed decision uses two equally costly arms, half quotas, one mean objective and rectangular regions. The potential effects are constant shifts of one deterministic outcome pattern. The experiment therefore differs substantially from the field’s six-package, budget-constrained, multi-transformation shared event. Equal weighting of cells is a catalogue summary, not an empirical distribution of policy problems.

Two feasible additions would improve interpretation without expanding the method list indefinitely. First, report paired Monte Carlo uncertainty and effect-specific results for the differences in actual regret. Second, provide simple decision benchmarks. Under the declared equally weighted effect grid, a no-learning 50–50 allocation has average actual regret exactly **0.045**. An empirical-best-arm rule would provide another useful comparison, provided its absence of a comparable certificate is explicit. These would show more clearly what is gained or sacrificed by certificate-driven decisions.

**Priority:** interpret performance by problem class rather than a single average. The current evidence supports a useful restricted comparison. It does not yet establish a consequential domain of advantage broad enough to carry a general-interest methodological contribution.

## 10. Reproducibility, hosted evidence, and the hash correction

**Disposition of prior M10: the execution record is stronger; full independent replication remains distinct.**

GitHub’s job metadata reports successful completion of the dependency, partition-verification and cold-master steps. Its artifact metadata agrees with the stated artifact size, source commit and digest. The published receipt explicitly excludes cross-platform PDF byte/text identity and labels the run as author-initiated CI. Those are appropriate distinctions. 

The first completed-master/failed-comparison record is not, by itself, evidence that the scientific computation failed. A narrowly documented comparison adjustment for a maximum rounding diagnostic can be defensible when an analytic ceiling and exact per-draw certificates remain mandatory. I independently checked the two-arm rounding bound; I did not reproduce the cross-platform drift or audit every comparison-wrapper change.

The LF/CRLF explanation is also plausible as a byte-provenance correction, but I did not independently verify all 535 current aliases or reproduce the diagnosis for every historical file. Parsed-value equality, Git-blob authentication and hashing local line-ending representations are distinct claims. Preserving the frozen history and publishing a separate correction is preferable to silently rewriting earlier manifests.

**Priority:** complete independent microdata-to-exhibit execution, manuscript-PDF inspection and durable archival deposition. A successful CI job and an expiring artifact do not supply those independently. They also do not determine scientific importance.

# Minor comments: disposition of m1–m8

1. **Religious context — retained appropriately.** Catholic affiliation remains a setting characteristic, not an identified treatment channel. Nothing in the new computation changes that.

2. **Assignment versus receipt — retained appropriately.** Continue using assignment or offer under the original participation pattern. The lottery does not establish receipt by every household. In the coverage corollary, “weakly exceeds” would also match the displayed weak inequality more precisely.

3. **Dietary ceiling and saving — no new objection.** The ceiling and reachable-threshold qualifications remain valid. The saving model’s illustrative status should remain explicit.

4. **PDF presentation — not independently verified here.** I cannot endorse the reported absence of clipping or unresolved references without the actual rendered PDF. Source inspection and author-side page screening are not substitutes for that check.

5. **Inherited search diagnostics — corrected.** `label_source_search` now identifies the historical quota-proposal diagnostics rather than presenting them as another method’s search results. This resolves the specific metadata ambiguity raised in the sixth report. 

6. **Exact tolerance counts — a small implementation improvement.** `designed_decisions.py` converts certificate values to floats before counting those at or below 0.05 and 0.10. Compare the exact fractions with \(1/20\) and \(1/10\) before conversion. I have not identified a wrong published count; this avoids a potential boundary-classification discrepancy in an otherwise exact decision calculation. 

7. **A remaining misleading comparison in the main text.** “What changes the guarantee?” still highlights approximately 49.2% without naming the historical harmonic comparator, immediately after discussing the hybrid. Replace it with the current hybrid comparison or explicitly label the historical benchmark. The appendix makes the distinction correctly.  

8. **History, screening and center of gravity.** Preserve the amendment and failure records, but keep prose-screen results and validation counts outside the scientific-merit argument. The abstract and introduction should foreground the genuinely new regional-optimization and performance findings more clearly; they still largely present the earlier empirical narrative.

# Overall assessment and priorities

The seventh revision warrants closing several earlier objections. The quota computation is no longer accurately characterized as requiring exponential enumeration. The omitted weight-sensitive comparator is included. A restricted empirical-Bernstein comparison and actual-regret exercise are present. The regional lower bounds overcome the logical weakness of comparing only upper certificates and establish near-optimality within the implemented quota region.

Those are meaningful advances. They also sharpen the limitation: **the broad field certificate is a property of the chosen outer region, not a failure to search adequately within it**. That is not a lower bound on actual policy loss, on sharp identification, or on the information attainable by all valid analyses.

The most scientifically useful next steps are interpretive and substantive: identify a precise economic or methodological claim, show where it matters, and distinguish gains in numerical protection from gains in actual decisions. Recovering the assignment protocol and completing external replication would strengthen credibility. Better characterization of actual objectives and rollout costs would strengthen an application. None is a guaranteed route to publication at this journal.

My recommendation is not that the work has no value. It is now a considerably stronger technical application than the initial submission. But its combination of an unchanged, unresolved empirical welfare comparison and specialized computational developments still does not establish the importance expected of a leading general-interest economics paper.

**Final recommendation: Reject at the unchanged standard.**