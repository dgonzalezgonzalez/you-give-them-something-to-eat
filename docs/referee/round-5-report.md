# Fifth-round referee report

**Manuscript:** *You give them something to eat: Dietary Diversity, Coverage, and Catholic Aid in Rwanda*  
**Reviewed tag:** `v0.5.0`  
**Resolved review commit:** `f13190f7e6e668cfd20b9c3c370047286dc85340`  
**Scientific source identified in the hosted run:** `fd958c196d6b68a36430890ca28c30e349031dff`

## Recommendation: **Reject**

This submission contains a genuine advance over the fourth version. The new shared quota-mixture construction is more than a presentation change; its coverage argument appears valid under the stated conditional assignment model. The numerical verification also makes the important distinction between a proposed optimizer output and a defensible upper bound. My execution from the published model receipts reproduces the reported **5.868-group** and **0.503-shortfall-unit** bounds at their upward-rounded display precision. I did not identify a central mathematical or sign error in the new argument or the numerical components I examined.  

Nevertheless, the paper still does not meet the requested leading general-interest economics-journal standard. It has strengthened a conditional uncertainty calculation without yet establishing a sufficiently consequential economic conclusion or a demonstrated methodological contribution of broader importance. The defensible bounds remain large, the relevant organizational objectives and acceptable losses are unestablished, and the methodological performance comparison is mainly against the paper’s own earlier constructions.

The recommendation is therefore not based on failed arithmetic, an insufficient number of checks, or a requirement that every paper identify a statistically significant winner. It is based on what the revised evidence contributes economically. This remains a simulated referee recommendation, not a journal decision.

## Scope of this review and independent execution

I inspected the fourth-report response, quota-inference note, main manuscript text and relevant decision/inference/saving proofs, the four new quota modules, the master script, analytical codebook, compact model documentation and summary, and hosted-reproduction records and workflow.

**The independent execution went materially further than simply reading reported numbers:**

| Work actually performed | What it establishes |
|---|---|
| Reconstructed six model-view JSON files and matched each to its frozen Git blob; likewise authenticated the retrieved arithmetic and moment modules | The executed receipt inputs and those two modules match the retrieved frozen files |
| Recomputed all 18 comparator support bounds using fresh numerical candidates, followed by outward tangent/dual evaluation | Reproduces the two displayed allocation certificates conditional on the published model constants |
| Checked small quota moments by independent 160-digit enumeration, HT/affine inequalities with exact fractions, and all 108 resulting arm-level tangents/duals | Supports the inspected numerical-enclosure implementation on those fixtures and receipts |
| Constructed an exactly rational common-distribution witness and checked its linear constraints and shared exponential sum | Demonstrates that the new production-model outer region still admits equal distributions across all arms |
| Queried GitHub’s hosted-run metadata and inspected its workflow | Corroborates a successful author-initiated run on scientific commit `fd958c1`; does not constitute independent scientific replication |

The recomputation used Python 3.13.5, NumPy 2.3.5 and SciPy 1.17.0, rather than the author’s locked environment. Its main results were:

| Objective | Published certificate | My model-level recomputation | Upward display |
|---|---:|---:|---:|
| Mean HDDS | 5.86712940709943 | 5.867129398437479 | **5.868** |
| Negative normalized six-group shortfall | 0.5025483675290233 | 0.5025483675290228 | **0.503** |

The largest difference across individual comparator bounds was approximately \(7.92\times10^{-8}\). Different fresh tangent candidates can produce slightly different valid upper bounds. I did **not** replay the eighteen original tangent-witness files; I generated new candidates and checked their resulting certificates. The published values are documented in the compact summary. 

The **:chatgpt-content-reference{index="39"}[audit summary](sandbox:/mnt/data/referee_round5/summary.json)** and **:chatgpt-content-reference{index="40"}[code, authenticated model files, and detailed receipts](sandbox:/mnt/data/referee_round5_audit_v0.5.0.zip)** record this scope.

**Important limits:** direct archive/PDF retrieval failed. I did not reconstruct or execute the household or child microdata, regenerate the actual-data quota normalizers or HT model constants, run the full master or Stata, inspect the manuscript PDF, verify its hash, or download and independently hash the hosted artifact ZIP. I also did not repeat the unequal-weight coverage simulation or reconstruct the original corrected source archive. Thus, this is **model/receipt-level recomputation and synthetic numerical verification—not full microdata or PDF replication**.

# Major comments and disposition of the fourth-round concerns

## 1. Economic importance and incremental information

**Disposition of prior M1: the calculation is substantially stronger; the publication obstacle remains.**

The fifth submission reduces the published mean certificate from approximately 7.720305 to 5.867129, a decrease of about **1.853175 groups, or 24.0%**, using the same released data. That is a real improvement in the reported guarantee, conditional on the maintained assumptions and correct construction of the model inputs. It deserves recognition. It is not, however, an estimated dietary improvement, a valuation of experimental information, or a demonstration that the new procedure dominates the earlier one across datasets. The procedures use different standalone confidence constructions.  

The remaining uncertainty is still economically difficult to use. A 5.868-group upper loss bound is broad on a twelve-group score; 0.503 is likewise broad for a shortfall objective with unit range. These numbers do not establish that the actual loss is large. They establish that this procedure has not bounded it tightly enough to support the small-loss interpretation considered in the manuscript.

I also checked something that cannot safely be carried forward merely from the earlier, different region: **does the new region still admit a complete tie?** It does. I constructed one exactly rational score distribution, with mean exactly five, common to all six arms. Exact-fraction checks establish unit mass, bin-floor compliance and all stored logical inequalities. Outward evaluation gives a total exponential sum below **0.0181**, comfortably below the cap of 5,520.

Consequently, every original feasible allocation remains compatible with mean optimality **within the actual production-model outer region used here**. This is not a claim that my probability vector is a sharp, finite-individual potential-outcome realization with the original household weights. Nor is the existence of a tie itself a reason to reject: a decision procedure can be useful without excluding every competitor. Here, the tie and the broad regret certificate jointly underscore the limited decision resolution.

**Scientific priority:** connect the stronger calculation to a consequential economic inference or establish a broadly useful methodological advantage. A further reduction in a bound is not automatically enough. The manuscript should not make the succession of increasingly sophisticated uncertainty constructions its principal economic contribution.

## 2. Assignment assumptions, target population, and baseline-only scale selection

**Disposition of prior M2: the conditional formulation is retained appropriately; the original assignment law remains unverified.**

The codebook clearly distinguishes the assumed conditional mechanism from the realized counts: labels are exchangeable within released blocks given their arm counts, and block assignments are independent. The probability \(k_{ba}/n_b\) follows under that model. It does not follow solely from observing those counts. The fixed weighted released-baseline target is also distinguished from the unsampled eligible frame and deployment populations. 

The new scale-selection rule is compatible with this conditional argument. In the inspected implementation, the candidate exponential grid and selection criterion use baseline weights, block sizes and quotas—not endline diets. Selecting a valid \(\lambda_a\) using those conditioned-on quantities does not require an additional outcome-selection correction. The recorded selected values also have the expected commonality across arms with identical quota structures.   

It is important to distinguish this \(\lambda_a\) from the support-certificate multiplier \(\tau\). The former defines the statistical event and must obey its stated selection restrictions. The latter is used to bound a deterministic optimization problem over the already-defined region; choosing it after observing outcomes does not redefine the event.

**Priority:** preserve this distinction in the code and exposition. A useful regression test would confirm that changing only endline outcomes leaves the selected exponential scales and moment constants unchanged. That is a maintenance safeguard, not a prerequisite missing from the mathematical argument I reviewed.

Recovering the original assignment protocol or investigator confirmation remains important. Without it, the finite result is conditional on the stipulated assignment model—not verified exact coverage under every restriction used in the original experiment.

## 3. Missing outcomes, endpoint tests, and observation consistency

**Disposition of prior M3: the new construction handles the stated missingness problem coherently.**

The quota tests use lower and upper item-informed numerators rather than treating missing diets as observed. At the true arm distribution, the lower-endpoint residual is no larger than the true residual; the upper-endpoint residual is no smaller. With positive \(\lambda_a\), the computable positive- and negative-tail exponential terms are therefore bounded above by their respective true-residual terms. This ordering is the relevant argument—not an assumption that reporting is ignorable. 

The deterministic restrictions also remain legitimate. An actually assigned household with an identified score contributes known fixed-weight mass to that arm’s corresponding score bin. The bin floor cannot exceed the true bin mass under consistency. Other assigned item intervals and unrestricted unassigned counterfactual scores give valid logical restrictions. Intersecting these restrictions with the quota event preserves coverage.

The separation between a fully identified diet and a transformation that happens to be known is still necessary. For the older potential-observation-ratio analyses, knowing a zero shortfall does not automatically make the complete dietary score observed. The manuscript and codebook retain that distinction. 

**Priority:** retain the local target qualifications. The new finite event does not turn selected follow-up regressions into effects on a common fully observed population. It also does not validate source replacements, eliminate reporting error, or establish that household diversity measures the target child’s nutrient intake.

I found no new conceptual defect in the endpoint ordering or deterministic-consistency argument. Actual-data construction of those numerators and bin floors still requires the microdata-to-model verification that I did not independently perform.

## 4. Joint-region optimization and numerical upper-bound certification

**Disposition of prior M4: the implementation now addresses a genuinely different, coupled region; the inspected certification argument is sound.**

The new event should not be confused with the earlier arm-separable boxes. Its shared exponential constraint links the six distributions. Projecting each arm independently and multiplying those projections would generally discard that coupling. The new verifier instead retains the shared constraint through its support-bound calculation. That is the correct approach.

For a comparator direction \(d\), any \(\tau\ge0\) gives

\[
\sup_{\substack{\sum_aF_a(p_a)\le C\\p_a\in\mathcal P_a^{obs}}}d'p
\le
\tau+\sum_a
\sup_{p_a\in\mathcal P_a^{obs}}
\left\{d_a'p_a-\frac{\tau}{C}F_a(p_a)\right\}.
\]

The negative arm objective is convex. An enclosed affine tangent lower bound, followed by a valid lower bound on its minimum, therefore yields a support **upper** bound. The direction of these inequalities matters: a numerical primal minimum by itself would not certify the desired upper bound. 

The feasible-dual construction is also correctly oriented. With \(p\ge f\), \(Ap\le b\), and \(\mathbf1'p=1\), nonpositive inequality multipliers and an appropriately bounded equality multiplier provide

\[
\min g'p
\ge
g'f+\ell'(b-Af)+\zeta(1-\mathbf1'f).
\]

The code does not simply subtract an arbitrary cushion from a floating-point optimizer objective. It encloses the relevant values and gradients, constructs a feasible dual, and evaluates in the conservative direction. Exact rational shares and cost vertices, together with explicit direction-rounding allowances, address another otherwise easy source of small certification errors.  

My checks included independent 160-digit evaluation of the nonlinear tangents and exact-fraction verification of all 108 resulting arm-level duals. The upper bounds survived those checks.

**The remaining qualification is optimality, not validity.** These calculations certify the selected allocations. They do not certify that the allocations minimize worst-case regret over the new region, nor that the remaining optimization gap equals a diagnostic gap reported by the optional search. The submission correctly states this distinction. A globally successful numerical minimizer is not required for a valid certificate, but an exact-minimax interpretation would require additional evidence. 

## 5. Dietary measurement and child-cohort interpretation

**Disposition of prior M5: earlier repairs are maintained; substantive measurement limits remain.**

The codebook continues to distinguish baseline child membership, endline linkage, physical measurement, valid standardized-score availability, and the separate endline-due and fixed-cohort sensitivities. Those distinctions are appropriate. Fixing membership before treatment does not remove selection from missing follow-up scores. 

The paper also correctly avoids interpreting Holm nonrejection as zero full-cohort nutritional effects or as a refutation of the parent study’s richer anthropometric analysis. The new quota event concerns the stated dietary-score distributions; it does not supply a new selection-robust analysis of the child outcomes.  

There remains a substantial gap between the program’s maternal-and-child-nutrition objective and the main decision criterion. A distributionally coherent HDDS analysis is preferable to incoherent threshold regressions, but coherence does not make all food groups nutritionally equivalent or reveal intrahousehold allocation.

**Priority:** keep the dietary decision analysis explicitly about this proxy. More important nutritional claims would require additional measurements or a justified link to the relevant nutritional outcomes. The auxiliary child regressions and saving illustration do not presently supply that link.

## 6. The new coverage derivation and its relation to the old approximation

**Disposition of prior M6: this is a stronger standalone construction, and I find its central conditional coverage argument valid.**

The critical steps are as follows.

For a block with quota \(k\), assignment probability \(p=k/n\), fixed weights \(W_j\), bounded village outcomes \(y_j\) and candidate mean \(u\),

\[
G_A(y,u)=\sum_j\left(\frac{\mathbf1\{j\in A\}}p-1\right)W_j(y_j-u)
\]

is affine jointly in \((y,u)\). The average of \(\exp\{\lambda G_A(y,u)\}\) over quota subsets is therefore convex on the bounding box. Maximizing coordinate by coordinate shows that a maximum occurs at a binary vertex. Allowing \(u\) to range freely over that box relaxes its population-mean relationship; this can be conservative, but does not invalidate the bound.

Complementing both \(y\) and \(u\) reverses \(G_A\). Because the bounding box is invariant under that transformation, the same maximal moment bounds either sign. **This is not an assertion that a fixed population’s positive and negative residual moments are equal.** My independent unequal-weight fixture produced different positive and negative moments while confirming the common bounding argument.

Independent blocks permit multiplication of their moment bounds. At the true global arm mean, the full-population centering cancels, yielding the relevant HT residual. Item-endpoint ordering then gives computable terms satisfying

\[
\mathbb E[e_{az,+}]\le1,\qquad
\mathbb E[e_{az,-}]\le1.
\]

There are 276 terms. Consequently,

\[
\Pr\!\left\{\sum_{a,z,s}e_{az,s}>5520\right\}
\le \frac{276}{5520}=0.05.
\]

No independence across arms or transformations is required for this expectation-and-Markov step. 

The common event also explains why outcome-dependent allocation and support-dual selection are valid: on that event, the true distribution belongs to the region and the deterministic bound holds for every feasible allocation, including the selected one.

The numerical moment implementation appears consistent with the proof. Integer proxy residuals are evaluated exactly before the exponential calculation; the actual-weight discrepancy receives an explicit allowance; and the exponential/logarithmic and positive-sum calculations are bounded outward. Python’s documented rounding behavior for `Decimal.exp` and `Decimal.ln` supports the neighboring-value enclosure used here. My independent small-population moment enumerations and exact HT/affine fixtures found no violation.  :chatgpt-content-reference{index="20"}

**Limits remain important.** The result is conditional on the assignment model and fixed target. It is not obtained by intersecting the old and new 95% regions. Taking an outcome-selected minimum across separately valid procedures would require its own justification. The current submission correctly treats the quota event as standalone.

Finally, the retained 695/800 and 592/800 stress failures concern the different block approximation. They neither validate the quota event nor refute its separate proof. I did not repeat those simulations this round.

## 7. Institutional restrictions and economic opportunity costs

**Disposition of prior M7: the interpretive correction is maintained; the institutional application remains hypothetical.**

The paper now explicitly distinguishes actual dietary opportunity cost at the unknown true means from differences between optimized worst-case bounds. That is the right correction. Its conclusion also states that the institutional sensitivity uses the **earlier coherent region**, not the new quota region. 

This matters because the old common-menu and own-menu values cannot be interpreted as the institutional implications of the new 5.868-group certificate. There is no coding defect in retaining them as an illustrative comparison, provided the separation remains unmistakable.

The fixed-Gikuriro-share identity also remains correct: when Gikuriro’s cost equals the budget, restricting both choice and comparator homothetically scales own-menu regret. It does not establish that the mandate improves outcomes. 

My common-distribution witness supplies a concrete reminder of the distinction: within the new outer region, all arm distributions can be identical. At that point, actual dietary opportunity costs of nonempty menu restrictions are zero, even though worst-case certificate differences can be positive.

**Scientific priority:** either present these institutional calculations as illustrations of decision geometry or establish a documented institutional decision and evaluate its important restrictions under the relevant current region. More hypothetical scenarios are not a substitute for knowing what the organization is deciding, which alternatives are genuinely available, and which losses it would regard as consequential.

## 8. Provider costs, unused resources, and transport

**Disposition of prior M8: the qualifications remain correct; the stronger statistical event does not resolve the economic cost assumptions.**

I checked feasibility of the new proposals using exact rational shares and the stated costs. The mean proposal’s expected cost is approximately **\$84.269627** against the **\$124.487701** budget. Its feasibility does not depend on claiming a tiny negative numerical budget residual. The shortfall proposal costs approximately \$77.877300.  

These are expected-cost statements under the fixed average-cost convention. They are not realized spending guarantees for a finite set of villages, nor evidence that small shares of different packages can actually be supplied at proportional national-program average costs.

The resource-value comparison remains properly separated from diet-only loss. Adding \(\eta(b-c'q)\) changes both chosen and comparator values; it is not a way to make the same dietary criterion appear more precise. The current sensitivity remains based on the older region and unestimated normative values.  

**Priority:** do not interpret the verified allocation’s unused budget as a recommendation to withhold resources. Actual objectives, fixed activation costs, delivery capacity, participation responses and spillovers remain necessary for an operational conclusion. The improved probability bound does not identify those quantities.

## 9. Originality, methodological positioning, and the saving model

**Disposition of prior M9: the technical development is more substantial, but its broader methodological contribution is not yet demonstrated.**

The new combination—quota-specific moment enumeration, incomplete-outcome ordering, a shared constraint over coherent distributions, and verifiable support certificates—is potentially useful. I would not dismiss it simply because its ingredients are classical.

However, the paper now needs a more direct methodological comparison. The expectation-one exponential terms and their averaging/Markov aggregation belong naturally to the e-value literature. Averaging such quantities is an established dependence-robust operation. Likewise, modern work on bounded-mean inference without replacement provides relevant comparators, although adapting those methods to this weighted, blocked, incomplete-outcome setting would require care. :chatgpt-content-reference{index="27"}

The current improvement over the paper’s earlier conservative constructions does not establish an advantage over credible alternative procedures. Nor does it isolate how much tightening comes from quota-specific moment bounds, the shared exponential constraint, additional bin floors, or the changed numerical optimization. These distinctions matter if methodological usefulness becomes the main contribution.

**Scientific priority:** benchmark a clearly defined contribution under representative designs and economically relevant loss criteria. This is not a request to tune a method until selected coverage simulations pass. The coverage proof should remain separate, and performance comparisons should be transparent about assumptions and targets.

The saving illustration remains mathematically acceptable and uncalibrated. The revised wording appropriately explains that bundled assignment cannot isolate the saving channel **irrespective of the saving coefficient’s significance**. Its role should remain illustrative, not a second claim of identified contribution.  

## 10. Reproducibility, hosted execution, and preservation

**Disposition of prior M10: reproducibility evidence is materially stronger; independent full replication and durable preservation remain distinct.**

GitHub independently reports that run `36788039531` completed successfully on scientific commit `fd958c1`. The inspected workflow installs Python and the statistical lock, installs Ubuntu TeX, checks public-part reconstruction, performs cold microdata-to-manuscript execution, and preserves outputs. This is stronger evidence than another reused local-environment run.  

It remains **author-initiated CI**, using the author’s programs and comparison rules. My API check corroborates its existence, source identity and successful status; it does not make me the independent executor of its household analysis.

The comparison scope also needs to remain precise. The hosted receipt distinguishes numerical-tolerance comparisons, exact generated/model checks, and PDF compilation/content checks. It explicitly excludes cross-platform full PDF-text identity and PNG/PDF byte identity. It should not be summarized as ninety-five byte-identical checks or as my inspection of the submitted PDF. 

The default master appropriately recomputes the event/model calculations and verifies the published proposals; a separate optional optimizer search need not be part of every certificate replay. I inspected that separation, but did not execute the master. 

**Priority:** retain the reproducible verifier and provenance records, complete independent microdata-to-output and rendered-PDF review, and preserve the publication package durably. A time-limited CI artifact and a Git tag are not equivalent to durable archival deposition. None of these remaining verification steps is the principal reason for my rejection.

# Minor comments: disposition of m1–m8

1. **Title and Catholic context — maintained appropriately.** The religious affiliation remains contextual rather than a randomized mechanism. The new inference does not identify a Catholic-specific delivery effect.

2. **Assignment, receipt and selection language — improved.** Retain “assignment/offer under the original participation pattern” wherever assistance coverage is discussed. A village allocation probability is not verified receipt by every eligible household. The codebook preserves the relevant distinction. 

3. **Dietary ceiling — no new objection.** The reachable-threshold and twelve-group-ceiling qualifications remain correct in the saving illustration. 

4. **Counts, tables and organization — improved at source level.** Moving historical diagnostics out of the main narrative is helpful. I did not visually verify the reported sixteen-table, one-figure, thirty-one-page document.

5. **Codebook and program labels — earlier repair retained.** Baseline child membership, observation and follow-up inference remain separately described. For the new methods, continue distinguishing statistical scales \(\lambda\), certificate multipliers \(\tau\), proposed allocations, and certified bounds; they play different roles.

6. **Numerical presentation — appropriate.** Upward reporting as 5.868 and 0.503 is correct for the inspected certificates. Continue avoiding language that upgrades a verified feasible allocation to a certified minimax optimum. The compact summary currently states the limitation clearly. 

7. **One remaining local wording inconsistency.** In “Cost accounting and magnitude,” the phrase saying the scenarios use the “same … regions as the main allocations” is now ambiguous because the headline allocation uses the quota event. Replace it with an explicit reference to the **earlier coherent finite and finite-and-consistency regions**. The conclusion already makes that distinction correctly. This is a presentation fix, not evidence of incorrect scenario calculations. 

8. **Exploratory history — appropriately retained.** Preserve the sequence of methods and abandoned claims without treating it as prospective registration. In the scientific narrative, emphasize the final estimand, assumptions and findings rather than the number of review rounds or validation checks.

# Overall judgment and conditions for reconsideration

The fifth submission improves my assessment of the technical work. The shared quota event has a coherent conditional proof, the enclosure strategy addresses the relevant numerical inequality directions, and independent receipt-level execution supports the displayed certificates. The hosted evidence also represents a real improvement in reproducibility.

My assessment of publication importance does not change. The paper still mainly shows that a progressively stronger, carefully verified uncertainty construction produces a broad allocation bound in one existing experiment. It does not yet establish a consequential allocation recommendation, an empirically grounded institutional opportunity cost, or a general methodological advantage demonstrated beyond its own earlier procedures.

There are two plausible substantive directions: an economic application tied to a real decision with justified objectives and tolerances, or a methodological paper establishing when this quota-mixture construction offers useful protection relative to appropriate alternatives. Either can potentially use existing data; a new field experiment is not intrinsically required. But neither contribution follows from an additional decimal place of certification or another successful reproducibility run.

I would therefore **not recommend an R&R conditioned merely on further numerical tightening or completion of the replication checklist**. A substantial economic finding or demonstrated methodological contribution could change the recommendation. The evidence in this fifth submission has not yet supplied it.

**Final recommendation: Reject at the unchanged leading general-interest economics-journal standard.**