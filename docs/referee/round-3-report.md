# Third-round referee report

**Manuscript:** *You give them something to eat: Dietary Diversity, Coverage, and Catholic Aid in Rwanda*  
**Reviewed submission:** `8213fbc76411d736806d902613e5b507689f4f04`

## Recommendation: **Reject**

The revision addresses several important objections substantively. The assignment mechanism is now an explicit maintained assumption rather than something purportedly established by realized counts. The finite conditional-assignment argument appears mathematically valid under that assumption. The allocation program correctly allows diversification over all six packages. Most importantly, the paper now reports the failed coverage diagnostics and withdraws the unsupported small-loss guarantees. These are meaningful improvements, not merely additional checks.   

**My rejection is principally about the remaining economic contribution, not a finding that the revised finite-bound proof or allocation LP is wrong.** The empirically defensible result remains a very conservative conditional bound, while the smaller and potentially useful bounds come from an approximation that fails the paper’s own stress tests. Furthermore, independent calculations show that much of the headline diversification improvement is available without observing any outcomes, and that the implementation leaves useful, already-covered distributional information unused.

These findings strengthen the case for a narrower methodological application or replication-oriented paper. They do not establish a contribution sufficient for a leading general-interest economics journal.

## Access, inspection, and execution

I retrieved the response letter, design/inference note, manuscript source—including the decision proofs, saving illustration, and supplementary-method sections—all three empirical macro files, README, self-audit, analytical codebook, output map, principal new inference/allocation/cohort code, validation programs, and selected numerical outputs. I also inspected the public-partition manifest and partitioning program. The first household partition successfully returned its header and an initial row range, so **the smaller data views are readable through the connector**. I did not reconstruct all twenty partitions.   

I performed three distinct kinds of independent execution:

| Executed work | What it establishes |
|---|---|
| An independently implemented allocation LP using published summary intervals and costs | Reproduces the **9.440422** finite mean-loss bound and computes a support-only, no-outcome-data benchmark of **9.600000** |
| Additional LPs imposing distributional consistency across already-covered primitive intervals | Produces a tighter conditional bound of **8.151078**, without new observations or a new coverage assumption |
| The exact retrieved `blocked_inference.py` on synthetic fixtures, plus an independent equal-weight stress implementation | Checks the covariance example, interval formula, scaling and zero-denominator behavior, and reproduces **695/800** coverage in the equal-weight synthetic case |

The retrieved inference module was checked against its Git blob identifier before execution. The calculations used a different installed environment from the author’s locked environment. Their scope and inputs are preserved in the **:chatgpt-content-reference{index="53"}[independent third-round audit bundle](sandbox:/mnt/data/referee_round3_audit_8213fbc.zip)**.

**What I did not do:** I did not execute household or child microdata, reconstruct the original input bytes, run the complete master or Stata, repeat the unequal-frame-weight simulation, or reconstruct the extract from the corrected source archive. Direct download routes failed, and materializing the connector’s CSV reference into the execution environment also failed.

I did **not** retrieve a usable manuscript PDF, inspect its rendered pages, compile it, or verify the reported PDF/ZIP hashes. The author’s 80-comparison audits remain inspected internal evidence, not my independent reproduction of those comparisons. I inspected the external Hoeffding source, including its without-replacement result; that should not be confused with inspecting the manuscript PDF.

# Major comments and disposition of the round-two concerns

## 1. Economic contribution: improved positioning, but the incremental information is still limited

**Disposition of M1: attribution addressed; leading-journal contribution objection remains.**

The introduction now correctly distinguishes the existing cost-effectiveness comparison from the proposed decision analysis. The discussion of Manski and Stoye is also directly relevant. Treatment diversification with missing outcomes and multiple alternatives is established decision theory; the new question must therefore be what this particular experiment adds to the economic understanding or practical application of those ideas.  :chatgpt-content-reference{index="7"}

A useful benchmark is missing from the manuscript: **how much does the finite certificate improve on what could be achieved using only outcome support and costs?**

I independently solved the paper’s allocation problem using the no-outcome-data region

\[
\mathcal C_0=[0,12]^6.
\]

At the reported costs and budget, its optimal worst-case mean loss is **9.600000 groups**. An allocation assigning probability \(0.2\) to each of control, Gikuriro, lower, middle, and upper cash, and zero to large cash, achieves this bound. Its expected cost is approximately **\$79.034**, below the budget.

The lower-bound argument is simple. The five individually feasible pure packages are all available to the comparator. At least one must receive probability no greater than \(0.2\); setting that package’s mean to twelve and the others to zero produces regret of at least \(12(1-0.2)=9.6\). The stated allocation attains that lower bound over the full feasible comparator set.

Against this benchmark, the paper’s finite-box solution improves the certificate only from

\[
9.600000 \quad\text{to}\quad 9.440422,
\]

a tightening of **0.159578 groups**, or approximately **1.66%**. These calculations use the published costs and primitive mean limits; they do not estimate anything from household observations.   

This is not a general valuation of the experiment’s information. It is a comparison of two nested regions under the manuscript’s particular decision criterion. Nevertheless, it materially changes the interpretation of the highlighted reduction from the best vertex’s bound of twelve to the diversified bound of 9.440. **Most of that reduction reflects diversification under broad uncertainty, not learning from the Rwanda outcomes.**

**Revision priority:** report the support-only benchmark and distinguish the gain from expanding the decision class from the gain supplied by empirical information. The paper needs an economically consequential incremental finding beyond illustrating established diversification logic. Merely adding this benchmark would improve the paper, but would not itself meet the leading-journal contribution threshold.

## 2. Conditional assignment and the target population: the definitions are now appropriately honest

**Disposition of M2: addressed as a conditional analysis; the actual assignment law remains unverified.**

The revision no longer treats observed allocation counts as proof of assignment probabilities. It explicitly assumes exchangeable labels within each released block, conditional on its counts, with independent assignments across blocks. Under that model, \(p_{ba}=n_{ba}/n_b\) is justified. It also separates a fixed weighted released-baseline target from representativeness of the unsampled eligible frame. This resolves the conceptual overstatement identified previously.  

That repair is a clarification of assumptions, not recovery of the original design. Additional restrictions—such as restrictions linking allocations across blocks or a nonuniform subset of permitted assignments—could change the relevant distribution. The code’s use of the observed quotas is correct **conditional on** the exchangeability model; it cannot verify that model.

The fixed-sample target is legitimate, but narrower than the operational question motivating the paper. There are three distinct claims:

1. A conditional assignment statement for the released baseline households with their fixed weights.
2. Representation of the wider eligible household frame.
3. Prediction for deployment in comparable villages.

Only the first is covered by the new finite argument, under its maintained design assumptions. The manuscript generally now observes this separation.

**Revision priority:** seek the original randomization protocol, assignment code, or investigator confirmation of the relevant restrictions. This is a documentation task, not necessarily new data collection. Unless that information becomes available, retain the conditional interpretation prominently. Do not present recovery of the frame-weight identity as independent verification of either the assignment law or external representativeness.

## 3. Missing outcomes and affirmative effect claims: substantially addressed

**Disposition of M3: the central implementation and interpretation repairs are satisfactory within inspected scope.**

The item-informed score interval remains correctly constructed. A positive subcategory establishes its combined food group; a group is certainly absent only when all relevant components are observed zero. Entirely unavailable diets receive the full support. Applying increasing transformations to these endpoints gives legitimate bounds without assuming missing outcomes are harmless. 

The revised text also distinguishes the positive observed large-cash response from an established positive effect on the full weighted baseline population. It reports the estimated large-cash-minus-control endpoint region of approximately \([0.171,0.731]\), alongside the much wider finite envelope, rather than promoting the complete-case result into an unrestricted population conclusion. That addresses the affirmative-claim inconsistency raised in round two.  

I also find the use of signed **net** package weights appropriate when forming policy contrasts. Shared package components are cancelled before their endpoint uncertainty enters the contrast. This avoids treating the same unknown arm mean as two independent unknowns.

Two limitations remain substantive rather than coding defects. First, outcome-specific observation can change the population represented by each identified-diet ratio. Its mixture is a well-defined descriptive calculation, but not automatically the distribution of a common baseline population under the proposed policy. Second, the endpoint analysis protects against incomplete reporting within the specified score construction; it does not validate HDDS as a measure of individual nutrition.

**Revision priority:** retain these local qualifications. The withdrawal of an established positive full-baseline effect is appropriate; neither another complete-case specification nor the small proportion of missing diets would remove the underlying selection issue.

## 4. Allocation LP: correct formulation, but the common region discards already-covered information

**Disposition of M4: the vertex-only restriction is repaired; an important correctable inefficiency remains.**

The new robust program is correctly formulated. The chosen allocation \(q\) ranges over all six package probabilities. Only the known-mean comparator is reduced to feasible vertices. The dual equalities

\[
A'\lambda_j=r_j-q,\qquad \lambda_j\ge0,
\]

and constraints \(d'\lambda_j\le t\) correctly represent each comparator’s worst-case advantage over a common polyhedral arm-mean region. I found no sign error in this formulation or in the argument interchanging a finite maximum with a supremum.  

My independent implementation enumerated the 64 corners of the reported mean box and solved the corresponding epigraph LP, rather than using the author’s dual helper. It reproduced the finite weighted-baseline bound:

\[
9.440422172055925
\]

against the reported \(9.440422172055923\), and reproduced its allocation and expected expenditure of approximately \$88.325. That is strong evidence for the **conditional optimization arithmetic**, not for the underlying household estimates. 

However, `policy_allocation.py::region()` filters the primitive output to `outcome == objective`. For mean allocation, it therefore uses only the mean endpoints, discarding survival and shortfall constraints that are already covered by the same simultaneous event.

A feasible improvement requires no new inference theorem. For each arm, introduce probabilities \(p_{ad}\) over scores \(d=0,\ldots,12\), impose

\[
p_{ad}\ge0,\qquad \sum_{d=0}^{12}p_{ad}=1,
\]

and, for every already-protected transformation \(v\),

\[
L_{av}\le \sum_{d=0}^{12}v(d)p_{ad}\le U_{av}.
\]

The true weighted score distribution satisfies all these constraints on the original finite-family coverage event. Projecting this feasible distribution set onto the mean can therefore tighten the mean region **without another multiplicity penalty**. This uses the empirical endpoint CDFs and the finite limits already produced by the program.   

I executed that projection and reoptimized the allocation:

| Region used for mean allocation | Optimized upper loss bound |
|---|---:|
| Support only, without outcome data | 9.600000 |
| Manuscript’s finite mean box | 9.440422 |
| Finite region additionally respecting the already-covered distributional constraints | **8.151078** |

The last calculation inherits the paper’s conditional assignment assumptions and its reported primitive limits. It is not an independently estimated confidence region and is not claimed to be sharp. It remains too broad for a small-loss conclusion.

**Revision priority:** propagate the simultaneous primitive information through a coherent distributional feasible set before optimizing. This is a demonstrated opportunity to improve the implementation, not evidence that the current bound lacks coverage. It also illustrates why the width of one deliberately loose outer box should not become the paper’s central economic finding.

## 5. Measurement and child cohorts: improved, but not an identification of nutritional effects

**Disposition of M5: coherent dietary construction and baseline-cohort accounting addressed; follow-up selection remains.**

The common positive-weight dietary distributions continue to resolve the original incoherence between separately estimated threshold regressions. The missingness endpoints also permit a distributionally coherent analysis, subject to the implementation improvement above.

The new child-cohort program fixes membership using baseline eligibility and the baseline anthropometry flag, links follow-up rows, and carries baseline assignment and weights into the sensitivity analysis. It does not restrict that fixed cohort to children satisfying the endline eligibility/due rule. This is the appropriate direction of repair. 

The published accounting distinguishes the 2,265 baseline-flagged children, 2,213 linked endline rows, and the 3,017 endline-due children. It also distinguishes physical measurement from nonmissing standardized scores. The 806 children outside the baseline cohort are no longer all interpreted as newborns. These distinctions are useful and supported by the inspected code and accounting output, though I did not reproduce them from child records. 

The remaining limitation is not resolved by linking rows. Availability of a follow-up height, weight, or arm-circumference score still selects the regression sample, and the source’s cleaning rules remain inherited. The manuscript correctly avoids interpreting Holm nonrejection as evidence of zero full-cohort nutritional effects.

**Revision priority:** keep cohort membership, row linkage, measurement, and valid-score availability separate throughout. Present this as a composition sensitivity, not an independent confirmation that the program lacked nutritional benefits. Actual child nutrient intake, richer repeated measurements, and causal mediation would require additional information beyond these reconstructed cohorts.

## 6. Inference: the finite proof is acceptable; the smaller approximation remains unvalidated

**Disposition of M6: the covariance omission and unsupported guarantee claims are repaired. The finite argument is valid under its stated assumptions; useful precision remains unresolved.**

### The finite conditional-assignment derivation

I find the new argument mathematically sound under the maintained assignment model.

For a fixed arm and primitive target, the true mean \(\mu\) defines village residuals

\[
X_j(\mu)=\sum_{i\in j}w_iR_i(a)\{Y_i(a)-\mu\}.
\]

Their total is zero. Because \(\mu\in[L,H]\), a village’s residual lies in the stated block-specific interval with width \((H-L)W_b^{\max}\), including villages with smaller weights or missing potential observations.

Under uniform quota assignment, the block contribution is a without-replacement sample of these fixed residuals, scaled by \(1/p_{ba}\). Hoeffding’s convex-order comparison permits bounding its exponential moment by the corresponding with-replacement moment. Independence across blocks then yields the stated tail inequality. I checked the cited without-replacement result in the primary source.  :chatgpt-content-reference{index="25"}

The crucial inversion is also correct:

\[
\sum_j \frac{T_{ja}X_j(\mu)}{p_{b(j),a}}
=
\widehat D_a(\widehat\mu_a-\mu).
\]

The denominator need not be nonrandom. The event is bounded at the **fixed true mean**, after which division by the observed positive denominator gives the reported interval. No union over a grid of hypothesized means is required. Giving full support when the denominator is zero is appropriate.

Finally, the union bound does not require independent arms. The separate 276-primitive baseline family and 138-primitive observed family are correctly distinguished; their conjunction is not automatically a 95% event.  

Thus, **I do not identify a mathematical error in the finite interval construction**. Its conservatism and conditional scope are separate concerns.

### Implementation and synthetic checks

I executed the exact retrieved inference module on synthetic fixtures. The interval formula agreed with a separate scalar calculation over 36 assignments; scaling the weights left the intervals unchanged; and zero denominators produced full-support intervals. These are implementation checks, not a substitute for the proof or evidence of actual Rwanda coverage.

The repaired block scores now retain cross-arm dependence. I independently reproduced the exact 90-assignment covariance example and the old-to-true variance ratio of \(0.9\). I also independently reproduced the equal-weight synthetic stress result of **695/800**, or **86.875%**, using the published quota structure. I did not rerun the unequal-frame-weight case; its reported **592/800** result is supported here by source/output inspection only.  

The manuscript now interprets these failures correctly. The covariance repair, larger multiplier count, Monte Carlo upper quantile, and zero-variance guards do not establish nominal sampling coverage. Nor do the ANCOVA CR2 results validate the different ratio/endpoints procedure.

**Revision priority:** retain the finite result as conditional and the block calculation as exploratory. Use the already-covered distributional constraints first, then investigate sharper justified inference rather than treating the present wide bound as inevitable. Do not tune an inflation factor merely until a selected collection of simulations passes. No new field observations are logically necessary to improve the inferential method.

## 7. Deployment, interference, and expected budgets: appropriately bounded scope

**Disposition of M7: conceptual distinction addressed; transport assumptions remain substantive.**

The paper now consistently separates expected provider cost from a hard realized cap, and original within-village treatment saturation from changes in treatment prevalence across villages. Common village lottery probabilities can preserve expected household-weighted coverage with unequal village sizes. That is not a mistake in the expected-cost formulation.  

Likewise, the within-village package interpretation does not establish invariance of prices, saving networks, implementation capacity, or cross-village spillovers under the proposed allocations. The new finite assignment statement cannot supply that missing transport information.

The ineligible-household regressions are evidence on selected measured outcomes under the original assignment pattern, not a test proving that all spillovers or public-service benefits are absent. The manuscript’s narrower interpretation is appropriate.

**Revision priority:** retain the conditional benchmark but identify more concretely the organization and decision to which it applies. A rule requiring universal assistance, a minimum package, geographic continuity, or a realized spending ceiling changes the feasible set. The paper need not solve every such problem, but should not imply that one hypothetical expected-cost problem exhausts the relevant institutional choice.

Scale-specific costs and interference would require additional evidence or identifying variation. Those limitations cannot be removed by reweighting the existing arms.

## 8. Cost accounting: now aligned with the headline estimands, but not operational cost validation

**Disposition of M8: the estimator mismatch is repaired; economic cost assumptions remain.**

The allocation code now recomputes all scenario allocations using the coherent means and the same common arm regions used in the main decision exercise. It rebuilds the comparator vertices under each cost setting. This resolves the previous mismatch in which the cost analysis used initial ANCOVA effects while the headline decision analysis used different estimands. 

The text also now places the national-scale overhead convention beside the budget constraint. It explicitly states that the source’s separate-package average costs are not observed mixed-program marginal or activation costs. Take-up changes are labeled fixed-outcome accounting scenarios, not causal forecasts. These are important qualifications.  

The remaining issue is decision relevance. The finite-region optimum spends approximately \$88.325 rather than the available \$124.488. This is permissible in the specified program and my independent calculation reproduces it. But it is an uncertainty-dependent hedge under the chosen objective, not evidence that an actual organization should withhold the remaining resources or that this allocation represents an efficient mixed rollout.

**Revision priority:** explain the treatment of unused resources and why the chosen loss criterion is appropriate for the intended organization. Preserve the separation between accounting scenarios and estimated cost uncertainty. Operational conclusions about fixed activation costs, capacity, or redesigned participation require appropriate cost evidence; they cannot be established from the published average-cost workbook alone.

## 9. Theory and saving: the mathematical claims are acceptable, but the mechanism remains illustrative

**Disposition of M9: addressed within the appropriately limited role of the model.**

The known-mean vertex proposition, robust-region diversification proposition, and saving illustration are mathematically acceptable in the inspected source. The dual allocation proof makes the relevant distinction: a comparator maximizing a known linear objective can be restricted to vertices, whereas the chosen allocation minimizing a supremum of regrets need not be a vertex. The manuscript no longer confuses this result with a repeated-sampling statistical minimax theorem. 

Moving the saving model to the appendix improves the paper’s focus. The interior comparative statics and score-ceiling qualification are correct. Nothing in the revision identifies a change in the saving return, estimates the structural parameters, or isolates saving access from the other program components.

The saving coefficient’s pointwise \(p<0.001\) and Holm \(p=0.052\) should be reported as they are. Their location relative to a threshold is not the reason the mechanism remains unidentified; the bundled design and missing mechanism variation are. 

**Revision priority:** keep the illustration subordinate to the decision analysis. A tested saving mechanism would require relevant measurements and variation. The missing-benefit calculation should likewise remain an accounting identity, not a calibrated welfare result.

## 10. Reproducibility: strong architecture, still only partial independent execution

**Disposition of M10: substantial documentation and accessibility improvements; full independent replication and durable archiving remain outstanding.**

The smaller public partitions are a useful response to the earlier access problem. The partitioning program checks repeated headers, row counts, part hashes, reconstructed hashes, and equality to the independently referenced original inputs. That is an appropriate design for exact public views rather than additional observations. I inspected the program, but did not run its complete reconstruction. 

The master keeps implementation checks distinct from coverage failures and includes the new allocation and cohort calculations. The output map distinguishes cited exhibits from unused generated outputs. The self-audit explicitly identifies the reused environment, the tested scientific commit, and the absence of external certification.   

I inspected the retained rights record reporting the corrected deposit’s CC BY 4.0 status and correction statement. I did not independently retrieve the original archive or establish its contents and rights from a fresh archive inspection. The source/derived-data distinction and code-license scope are clearly documented.  

**Revision priority:** complete external execution of the frozen microdata package and rendered-PDF review, and make a durable archival deposit for publication. Neither is established by my summary-output calculations or by the author’s internal audit. These remaining steps concern verification and preservation; their completion would not, by itself, change the economic-contribution recommendation.

# Minor comments: disposition of m1–m8

1. **Title and religious context — addressed.** The manuscript consistently treats Catholic affiliation as setting rather than a randomized attribute. There is no identified Catholic-specific delivery effect. The contextual title should not be made to carry a mechanism claim absent from the analysis. 

2. **Assignment, receipt, and selection language — substantially addressed.** The revised distinction between original assignment effects, observed ratios, and weighted-baseline bounds is much clearer. Continue attaching the relevant qualifier directly to each positive empirical claim rather than relying only on a general limitations section. 

3. **Dietary ceiling — addressed.** The saving illustration retains the reachable-threshold qualification and does not predict a score increase beyond twelve. No further mathematical correction is required on this point. 

4. **Counts and output mapping — addressed at source level.** The current map distinguishes 24 cited tables and one cited figure from the larger set of generated outputs. I did not visually verify their numbering, placement, or readability in the compiled PDF. 

5. **Baseline mapping — implementation addressed; codebook needs updating.** The new cohort code maps actual baseline scores and retains baseline membership. But `analytical-codebook.json` still describes the child “scientific regression” through the earlier endline-due rule and does not separately document the new fixed-cohort sensitivity. Its assignment-probability entry should also reference the explicit conditional-exchangeability assumption rather than only the count formula. Update these entries so the analytical definitions match the current programs.  

6. **Encoding and PDF checks — encoding addressed; visual claim unverified here.** The self-audit’s author field is now correctly encoded. My review does not confirm the absence of overfull boxes, clipping, or unresolved references in the rendered document. Those remain author-side checks until the PDF is independently inspected. 

7. **Organization and variance labels — improved.** Leading with the decision problem and moving initial ANCOVA and saving theory to appendices is effective. The different inference procedures are now distinguished. The main text could still be shortened by consolidating repeated disclaimers into a compact estimand/inference table, while preserving local qualifiers. Historical diagnostic tables need not occupy as much of the reader’s attention as the current economic question.

8. **History and exploratory status — addressed.** The revision preserves abandoned claims and explicitly treats later analyses as referee-driven exploration. That is appropriate. The scientific argument should stand on its assumptions, derivations, and evidence, not on either the number of review rounds or whether a simulated referee has endorsed a particular formulation.  

# Priorities and conditions for reconsideration

The immediate **correctable priorities** are to add the no-outcome-data benchmark, exploit the already-covered distributional constraints in the allocation region, update the codebook, and complete independent microdata/PDF verification. Sharper justified inference can also be pursued without new field observations. None of those tasks should be described as a guaranteed route to acceptance.

The **scientific limitations requiring additional information** concern the original assignment restrictions, operational mixed-program costs, deployment spillovers, sustained outcomes, individual nutritional intake, and the saving mechanism. Some may be resolved through existing documentation or additional released variables; others require genuinely new evidence.

The strongest honest contribution achievable from the present material is a focused, selection-aware decision reanalysis showing how inference and feasible allocations change the interpretation of this cash-benchmarking experiment. It should make clear what is learned from the outcomes, what follows from support and costs alone, and what is an artifact of a conservative region construction.

At present, the manuscript’s valid finite calculation supplies very little additional protection relative to a support-only benchmark, while its smaller bounds lack demonstrated nominal coverage. The demonstrated tightening to 8.151 groups shows that more can be extracted from the current procedure, but it does not establish a practically useful allocation conclusion or a new general method.

**I therefore do not recommend an R&R at the requested journal conditional merely on completing the technical repairs.** I would reconsider if the paper established a substantial new economic implication or a genuinely useful methodological contribution supported by the evidence. A new experiment is not required in principle; a sufficiently important contribution is.

**Final recommendation: Reject at the unchanged leading general-interest economics-journal standard.**