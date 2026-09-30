# Referee report: frozen submission `046ce79`

## Scope and verification

**This is a source-based review, not an independently executed replication.** I accessed the frozen commit through the GitHub connector and read the manuscript and appendix text in `paper/paper.tex`, including both proofs. I also inspected `results.tex`, the estimator, data-preparation and exhibit-building programs, validation code, master script, analysis plan and amendments, replication self-audit, licensing statement, and selected numerical outputs.

I could verify the following:

- **Source implementation:** the weighted regression, cluster-sandwich construction, policy contrasts, multiplier procedure, missing-diet construction, and output-generation logic.
- **Recorded numerical consistency:** using a separate calculation, I reproduced all eight mean-diet policy contrasts from the recorded arm estimates and costs, checked their simultaneous-interval arithmetic, and enumerated the feasible policy vertices. The five stored Python estimates and standard errors also match the stored Stata reference to approximately \(1.21\times10^{-13}\) and \(5.05\times10^{-15}\), respectively. **That comparison does not constitute rerunning either estimator.** The calculations are documented in this :chatgpt-content-reference{index="62"}[arithmetic audit receipt](sandbox:/mnt/data/referee_046ce79/arithmetic_audit.json).    
- **External source checks:** I accessed the published McIntosh–Zeitlin article’s abstract and bibliographic record, relevant passages of the authors’ accessible working paper, and current JPE replication guidance. Zenodo’s indexed record corroborates the corrected deposit’s existence, correction description, and advertised archive checksum. :chatgpt-content-reference{index="4"}

**Access limitations:** direct repository downloads failed in this environment. The connector returned no contents for the large household CSV, and I could not obtain the compiled manuscript PDF or corrected source archive. Consequently, I did **not** inspect household observations, reconstruct the extract, rerun regressions or the bootstrap, execute Stata, compile the manuscript, or visually inspect its figures and tables. I also did not obtain the full final published Economic Journal article.

For a definitive full-package assessment, the missing materials are a mounted archive of the frozen tree—especially `data/input/households.csv` and `paper/paper.pdf`—and the corrected original source ZIP for upstream provenance checks. **The recommendation below is therefore provisional, although the accessible manuscript supports a substantive assessment of its contribution.**

## Recommendation

**Reject at the standard of a leading general-interest economics journal.**

The manuscript has real strengths: it identifies an intelligible allocation question, is unusually explicit about the limits of secondary analysis, distinguishes assignment from receipt in its estimation, avoids equating statistical insignificance with equivalence, and acknowledges that the saving mechanism is not identified. The inspected mathematics and central numerical accounting are generally sound. Its transparent reporting deserves credit.  

However, the paper does not currently establish a sufficiently substantial new economic contribution. The headline mean-budget comparison is closely related—indeed, algebraically equivalent under fixed costs—to an existing cost-effectiveness comparison. The genuinely incremental distributional analysis does not yet produce an informative allocation conclusion; population targeting and observation selection require more work; and the theoretical mechanism remains an uncalibrated possibility rather than a tested explanation.

This recommendation is **not** based on the absence of statistically significant policy rankings, nor on the use of AI assistance. It reflects the combination of limited incremental contribution, unresolved identification-to-policy links, and insufficient demonstrated decision value.

# Major comments

## 1. The incremental contribution relative to McIntosh–Zeitlin needs a much sharper accounting

The distinction between universal assistance and concentrated assistance is economically sensible. But for the mean outcome, the control/large-cash comparison is

\[
\Delta_{g,0L}
=\tau_g-\frac{c_g}{c_L}\tau_L
=c_g\left(\frac{\tau_g}{c_g}-\frac{\tau_L}{c_L}\right).
\]

Holding costs fixed, testing whether this contrast is zero is the same hypothesis as testing equality of the two treatment effects per dollar. With the same estimates and covariance matrix, its test statistic is unchanged by this positive rescaling.

The original research already distinguishes cost equivalence from cost effectiveness. This is explicit in Section 3.4 of the accessible working paper; the published article also contains a section on comparative cost effectiveness. The manuscript therefore cannot position the original contribution simply as interpolation at an unobserved transfer size and its own contribution as introducing the budget/coverage question. :chatgpt-content-reference{index="7"}

The more defensible incremental contribution is **distributional cost-effectiveness over a clearly specified class of observed-package lotteries**, potentially combined with decision-making under partial identification. Even there, the paper must explain what is learned beyond applying additional transformations to an existing experiment. Comparing food quantity, dietary diversity, and cost-effectiveness across assistance modalities is already established in the cash/food/voucher literature. Treatment choice under budget or capacity constraints is likewise central to the literature the paper cites. :chatgpt-content-reference{index="8"}

**Feasible revision:** provide a compact contribution crosswalk identifying what the original published study already estimates, which new estimands differ, and which new economic conclusions follow. Reproduce the closest original specifications before showing the effects of changed measurement, covariates, samples, and multiplicity correction. Do not describe a reparameterization as new identification.

**Publication obstacle:** better positioning alone would not resolve this comment. A leading-journal paper needs a substantial new empirical insight, methodological contribution, or decision-relevant result—not merely a more cautious reinterpretation of known findings.

## 2. Establish that the estimator targets the population appearing in the policy problem

The framework defines policy values for the baseline eligible population. The estimator uses pooled weighted ANCOVA with treatment indicators, block fixed effects, and common baseline slopes. The codebook describes `samp_wgt` only as a sampling weight; this is insufficient to establish the connection between the regression coefficient and the stated population average.  

Two issues require separation.

First, **sampling weights do not by themselves resolve treatment-assignment weighting**. With heterogeneous block-specific effects and differing assignment probabilities across blocks, a pooled fixed-effects coefficient need not equal an average using the baseline eligible population’s block shares. In a multi-arm experiment, the implicit weighting can be more complicated than a scalar precision-weighted average. This is a derivation and empirical-audit requirement; without the microdata and assignment schedule, I am not asserting that a particular numerical bias occurs here.

Second, the parent study discusses both survey and intensive-tracking weights. The new paper needs to establish exactly what is contained in `samp_wgt`, whether it changes across rounds, and how it relates to the weights used for retention and missing-outcome bounds. :chatgpt-content-reference{index="11"}

**Feasible revision:** report the arm-by-block assignment counts and probabilities, the construction and distribution of weights, and the target population shares. Compare the primary estimator with a design-aligned estimator that explicitly standardizes arm outcomes to those shares—for example, an appropriate Horvitz–Thompson/Hájek or regression-assisted estimator using known assignment probabilities. Verify that eligibility is baseline-defined and invariant, and that every estimation observation belongs to the intended cohort.

The equal-household and equal-village specifications should be described as **alternative population estimands**, not simply interchangeable robustness checks. Their sign differences may reflect real heterogeneity rather than instability of an estimator for one fixed population.

These checks should be feasible with existing design information and data. If necessary population or assignment information is unavailable, narrow the estimand rather than claiming population representativeness.

## 3. Observation selection must enter the principal results, not remain a caveat beside them

The recorded sample moves from 1,793 baseline eligible households to 1,751 endline-panel households and 1,728 complete reconstructed diets. Upper cash increases observed-diet retention by approximately 3.11 percentage points, with a reported Holm-adjusted \(p=0.026\). This does not itself prove bias in dietary outcomes, but it makes observation selection a substantive issue for a prominently discussed policy comparison.  

The paper correctly acknowledges the issue and correctly labels its worst-case bounds as sample quantities rather than confidence intervals. Nevertheless, complete-case ANCOVA and unadjusted empirical bounds currently address differently adjusted objects. They do not together establish a population causal ranking.  

There is also useful information being discarded by the complete-module rule. For a food group constructed as an “any consumed” indicator, one observed positive subcategory establishes consumption even when another subcategory is missing. More generally, partially answered modules imply household-specific lower and upper HDDS values that can be tighter than \([0,12]\). Requiring all sixteen responses to be binary is transparent but potentially unnecessarily restrictive. 

**Feasible revision:** audit whether incomplete modules nonetheless identify some complete scores; construct item-informed score intervals for the remainder; and estimate block/population-standardized missing-outcome bounds with sampling uncertainty. Add a transparent sensitivity analysis for the mean outcomes of unobserved households, using a common target population throughout.

The recorded bounds contain potentially interesting distinctions. For example, the unadjusted upper/large shortfall comparison has endpoints entirely below zero, whereas its adjusted sampling interval spans zero. That is a reason to separate selection uncertainty from sampling uncertainty carefully—not to claim a significant ranking from the bounds.  

New observations would be necessary to resolve remaining uncertainty without additional assumptions if these improved bounds remain uninformative. Missing outcomes should not be treated as harmless merely because aggregate retention is high.

## 4. The strongest fitted benchmark is lower/large cash, and the decision analysis should confront it directly

The emphasis on control/large and upper/large lotteries is understandable: one varies coverage, while the other preserves universal cash assignment. But upper/large is **not** the best fitted mean-diet cash policy at the Gikuriro budget.

Using the recorded costs and arm estimates, I obtain:

| Policy | Large-cash assignment share | Fitted HDDS gain over control | Gikuriro minus policy | Reported simultaneous 95% interval |
|---|---:|---:|---:|---:|
| Control/large | 24.059% | 0.131 | 0.124 | \([-0.247,\ 0.495]\) |
| Lower/large | 15.287% | 0.382 | −0.127 | \([-0.632,\ 0.379]\) |
| Upper/large | 0.819% | 0.350 | −0.094 | \([-0.625,\ 0.436]\) |

These are arithmetic reconstructions of stored results, not new regressions. Lower/large also assigns cash in every village. The paper includes this comparison in its table, so this is not an allegation of concealment; the issue is that the narrative’s principal universal-cash benchmark does not represent its own fitted optimum.   

The relevant decision question is not simply whether any individual contrast rejects zero. It is what policies can be ruled out, how large a loss a chosen policy might entail, and whether that uncertainty is tolerable.

For example, conditional on the maintained assumptions and the reported simultaneous bands, a conservative upper bound on Gikuriro’s mean-diet regret relative to the feasible cash class is

\[
\max\{0,\max_q[-\underline{\Delta}_{gq}]\}
\approx 0.666
\]

HDDS groups. This is an implication of the existing bands, not a new confidence procedure. The manuscript has not established that such a bound is small enough for a useful decision.

**Feasible revision:** report the fitted optimum, an uncertainty set for the optimal policy, and regret bounds for candidate decisions. Comparisons among cash policies also matter; Gikuriro-versus-cash contrasts alone do not establish which cash policy is best. Specify a policy-relevant tolerance or loss function rather than treating nonrejection as the decision conclusion. Regret-based assessment fits naturally with the treatment-choice literature. :chatgpt-content-reference{index="22"}

This is feasible with the existing data, although useful precision cannot be guaranteed.

## 5. Keep the dietary estimand coherent and distinguish food access from the program’s nutritional objective

The reconstructed HDDS is a defensible household food-access measure, and the manuscript appropriately avoids treating its illustrative shortfall thresholds as clinical hunger cutoffs. FAO’s guidance distinguishes household dietary diversity from individual dietary assessment; the household score does not identify a particular child’s nutrient intake. :chatgpt-content-reference{index="23"}

Nonetheless, interpreting every increasing transformation of HDDS as an alternative nutritional priority needs care. The score includes oils, sweets, and condiments alongside other food groups. Improving the index is not automatically an improvement in every nutritionally relevant dimension. This limitation is especially important when evaluating a bundled program whose stated objectives concern maternal and child nutrition. The paper recognizes the distinction, but its title and broader motivation still place more weight on nutrition than the primary estimand can bear. 

There is a separate statistical-coherence issue. Outcome-specific ANCOVAs use different baseline transformations, so the fitted threshold effects need not correspond to one estimated outcome distribution, nor satisfy the finite-sample identity linking the mean to the sum of survival probabilities. The appendix acknowledges this correctly. It is nevertheless a limitation for a paper whose main incremental contribution is distributional. 

**Feasible revision:** supplement the threshold regressions with coherent, population-standardized arm distributions from which means and shortfalls are derived consistently. Show which food categories account for changes, and clearly separate food-access results from health claims. Three shortfall thresholds cannot characterize the entire class of increasing-concave objectives.

Also check which child anthropometric outcomes from the parent experiment remain available in the corrected release. The published study measured child growth; the household extract should not be mistaken for the complete outcome set of the original experiment. Existing child outcomes could support a broader comparison where accessible. Actual child-specific nutrient intake, richer repeated dietary measurement, and longer-run outcomes may require new data. :chatgpt-content-reference{index="26"}

## 6. The inference code is plausible, but total village count is not a sufficient finite-sample diagnostic

From source inspection, the WLS sandwich and contrast covariance calculations are correctly organized. The code aggregates village scores, applies the stated CR1 correction, and uses shared multiplier draws for joint inference. I did not identify a sign error or an omission of covariance between the Gikuriro and cash coefficients. The manuscript appropriately describes the multiplier bands as asymptotic rather than exact randomization inference.  

However, the smaller cash arms contain 22 villages each and the large arm 34. Information for particular contrasts can be concentrated further by unequal weights, leverage, block structure, or rare dietary thresholds. Reporting 248 clusters for every regression does not establish that every contrast has satisfactory finite-sample behavior. 

**Feasible revision:** report contrast-relevant leverage and weight concentration, outcome support by arm, and leave-one-village or leave-one-block sensitivity. Add an appropriate small-sample cluster adjustment or a carefully implemented wild-cluster/design-based sensitivity analysis. CR2/Satterthwaite methods are one relevant option, with attention to the corrected implementation results for weighted fixed-effects models. :chatgpt-content-reference{index="30"}

Do not mechanically replace village clustering with clustering on the 22 randomization blocks. Blocking and the dependence structure are different issues. Likewise, a weak null about a weighted policy contrast is not automatically a sharp null permitting an exact permutation test.

There is a smaller, demonstrable multiplicity redundancy: for every outcome, the Gikuriro arm-versus-control test is duplicated by the Gikuriro-minus-control policy test. Thus the advertised 221 rows contain seventeen obvious duplicates; the secondary family has eight analogous duplicates. Duplicates leave the max-\(t\) maximum unchanged but make Holm adjustment unnecessarily conservative. This is not an anti-conservative error or evidence that the principal results are wrong. Deduplicate the families and document their actual composition.  

## 7. The lottery identity is valid, but policy transport requires substantially more than that identity

Proposition 2 is mathematically sound under its maintained assumptions. A lottery over stable package-specific outcome distributions produces a mixture distribution, and a linear objective over the simplex with one budget constraint has an optimum supported on at most two packages. The proof correctly handles both binding and slack budgets. 

The policy interpretation remains conditional. In the experiment, Gikuriro was assigned to 74 of 248 villages and large cash to 34. Universal Gikuriro, 24% large-cash coverage, and universal mixtures of cash packages change the allocation of treatment across villages. Preserving each treated village’s within-village package does not establish invariance to changes in neighboring treatment, market demand, implementation capacity, or saving networks. 

This matters in the cash/in-kind literature: local price effects can differ between modalities and settings. The paper’s acknowledgment of spillovers is appropriate, but the policy values should consistently be described as **conditional transported values**, not outcomes directly randomized at the proposed scale. :chatgpt-content-reference{index="35"}

The expected-budget formulation is also valid as written. In particular, unequal village sizes do not automatically invalidate a constant-probability lottery: if assignment probabilities are the same for every village, expected household-weighted coverage follows the same probability. The unresolved issue is the **realized spending constraint**, not a necessary failure of expected-cost accounting.

**Feasible revision:** specify the donor’s actual constraint—expected budget, hard cap, universal minimum assistance, or geographic continuity. Retain the current exercise explicitly as an expected-cost benchmark, or add a finite-village allocation exercise using available size information. Report ineligible-household outcomes where the released data support them, rather than treating all public-service consequences as necessarily unmeasured.

Credible extrapolation to different saturation, prices, or delivery scale requires additional identifying information or new data; it cannot be supplied by the mixture formula alone.

## 8. Cost uncertainty needs an implemented sensitivity analysis, not only a paragraph of qualifications

The Gikuriro and upper-cash costs differ by only approximately **\$3.247 per eligible household**, or **2.61% of the Gikuriro cost**. This produces the 0.819% large-cash share in the upper/large policy. Relatively small accounting changes can therefore alter whether upper cash is below the budget and which policy pairs constitute feasible vertices. 

The manuscript recognizes cost uncertainty, but all reported statistical intervals hold costs fixed. That is acceptable as a conditional analysis, not as a complete calibration of an implementable policy frontier. 

The distinction between a **constant unit cost** and a **fixed activation cost** should also be made explicit. A cost structure such as

\[
C_a(n)=F_a\mathbf 1\{n>0\}+m_an
\]

does not generally preserve the linear cost constraint used in the proposition. The observed average cost incorporates accounting and participation assumptions; it is not automatically the marginal cost of changing coverage.

**Feasible revision:** present a transparent grid of alternative relative costs, participation assumptions, and overhead allocations; rebuild the feasible set for every scenario; and show how candidate policies and conclusions change. If cost inputs have a defensible sampling model, propagate that uncertainty jointly. If uncertainty is accounting or transport uncertainty rather than sampling variation, use labeled scenarios instead of manufacturing confidence intervals.

There is also a precise implementation issue for this extension: `policy_vertices()` examines pairs in a fixed arm order and only checks `ca < budget < cb`. That works for the current ordered costs, but may miss feasible pairs if sensitivity scenarios reverse cost ordering. Sort each pair by its scenario-specific costs. 

The omitted-benefit threshold is useful bookkeeping, but it is not a calibrated welfare result. Expressing omitted benefits in HDDS-equivalent units does not identify those benefits or justify their valuation.

## 9. The saving mechanism is compatible with the evidence, not tested by it

I found no substantive algebraic error in Proposition 1. The interiority condition

\[
\beta(w+t-\underline f)>y/R
\]

is correct, as are the stated solutions and comparative statics. The envelope derivative is positive when saving is positive. The corner solution is also discussed appropriately. 

Its economic content is nevertheless modest. A costless improvement in the return available to the household expands opportunities; under the chosen preferences and positive background future income, it shifts expenditure toward saving. The intervention is not shown to change \(R\), and the model’s parameters are not estimated. Saving groups can affect borrowing, commitment, risk, fees, and social obligations; the broader program also changes other resources and opportunities.

The empirical saving result is suggestive, but it is an effect of the **entire assigned bundle**. Its reported secondary-family Holm value is 0.056. Neither that result nor the large-cash asset response identifies the proposed intertemporal channel or measures a welfare improvement. The manuscript says this explicitly; the remaining problem is how much contribution the model can support despite that admission. 

**Feasible revision:** show the purchased-food and own-produced-food expenditure results already computed by the code but omitted from the main secondary-outcomes table. Document their different recall periods and source transformations. These outcomes are closer to the model’s expenditure predictions, although still not causal mediation evidence.   

Either compress the model into a clearly labeled illustration or develop predictions that distinguish it from competing mechanisms. Do not condition on realized saving to claim mediation. Identification of a saving-technology mechanism would require suitable additional variation and measurements—potentially a factorial design, saving terms and returns, or richer longitudinal data.

## 10. The replication architecture is promising, but there is a specific provenance-validation gap

The package has valuable features: a single driver, separate inputs and outputs, generated numerical macros, explicit inference settings, an independent-software reference, and a self-audit that distinguishes internal checks from journal certification. Those features are consistent with the spirit of JPE reproducibility requirements. They do not themselves constitute independent reproduction, which the paper correctly acknowledges.  :chatgpt-content-reference{index="45"}

**The concrete defect is in the source-to-extract verification chain.** `code/prepare_data.py` checks the hash of `data/raw/source.zip`, but reads `household_panel.dta` and `CostsAndCompliance.xlsx` from a separately extracted directory. It does not extract those files itself or verify that their bytes match the corresponding members of the checked archive. Moreover, it rewrites `provenance.json`; `run.py --from-source` subsequently validates the newly generated inputs against that newly written manifest. Thus a valid archive could coexist with stale or altered extracted files without this sequence detecting the mismatch. This is a source-verification gap, **not evidence that the present extract is incorrect**.  

**Feasible revision:** extract directly from the verified archive, verify member hashes, preserve an immutable reference manifest, and compare regenerated extracts against that reference before replacing files. Add a test showing that an altered extracted input is rejected.

The codebook also needs analytical definitions, not only inherited labels: sampling/tracking weights, monetary units and price bases, index construction, zero handling, source imputations, and any winsorization or other preprocessing. The discovery of substituted diet scores makes documenting upstream treatment of the secondary outcomes particularly important.

The MIT license explicitly excludes research data and states the claimed CC BY terms. I could corroborate the corrected deposit’s description, but did not independently inspect its license field or archive contents. Preserve that rights evidence and an explicit record of transformations. For eventual publication, archive the exact package in a trusted repository, not solely a mutable hosting account. JPE guidance distinguishes public accessibility from redistribution rights and durable preservation.  :chatgpt-content-reference{index="49"}

# Minor comments and presentation revisions

1. **Title and scope.** “Catholic Aid” describes an implementing organization, not a randomized religious characteristic. “Nutrition” and “Saving” also suggest a broader outcome and mechanism contribution than is established. A title centered on dietary diversity, coverage, and cash benchmarking would better represent the analysis. Retain appropriate credit to CRS, SNV, USAID, and the original investigators. 

2. **Assignment versus receipt.** Replace headings referring to gains “among recipients” with gains among eligible households in assigned villages. Likewise, define “universal Gikuriro” as universal assignment or offer under the original participation pattern, not verified treatment receipt by every household. The cost file itself documents incomplete participation. 

3. **Threshold corollary.** Qualify the claim that sufficiently large cash crosses a dietary threshold: it requires at least one remaining uncrossed threshold. A household already at the twelve-group ceiling cannot increase its score. This is a minor scope correction, not a failure of the main comparative statics. 

4. **Table construction.** `regression_table()` reports the observation count from the first outcome and hardcodes 248 villages. I have not demonstrated an incorrect displayed count in the inspected results, but these should be derived separately where samples differ, with an assertion when one common count is displayed. 

5. **Stale implementation comment.** The estimator says preconstructed baseline variables supplement absent panel rows, but the inspected code maps baseline values from the baseline records and does not implement that fallback. Correct the comment or document and test an explicit fallback. Do not silently change the reconstructed-diet baseline definition. 

6. **Numerical display and labels.** Avoid displaying \(p=0.0000\); use an inequality at the chosen precision. Replace raw food-variable names with readable labels. Make probability units, shortfall normalization, adjustment family, and interval type immediately visible in each exhibit.  

7. **Prose and citations.** The writing is clear but repeats the same limitations across the introduction, results, discussion, and conclusion. Consolidate the policy-transport assumptions and identification limits, leaving space for the contribution comparison and decision analysis. Expand citations where they change the argument—particularly direct food-assistance comparisons, prices/spillovers, and decision uncertainty—rather than adding a long generic literature review.

8. **Analysis-plan status.** Keep the existing distinction between a dated secondary-analysis plan and prospective trial registration. The amendment log transparently records changes after initial estimates, including family expansion and corrected baseline imputation. Preserve that history; it supports transparency but cannot establish blinded confirmation.  

# Strongest honest contribution achievable with the released evidence

The strongest attainable paper is a **distributional, selection-aware cash-benchmarking reanalysis of a specified eligible population**, not a general evaluation of Catholic aid and not an identified saving-mechanism paper.

Its contribution would be to show which observed-package allocations remain defensible after aligning population weights, preserving partial information in incomplete food modules, constructing coherent dietary distributions, accounting for policy selection, and varying cost assumptions. The output should be a set of supported or unresolved policy choices and bounds on foregone outcomes—not simply a collection of nonrejections.

Much of that work is feasible without new data collection. Additional outcomes already measured by the parent experiment should be used where the corrected release permits. New measurements would be required for claims about actual child nutrient intake, saving returns, unobserved long-run benefits, or materially different saturation and delivery conditions.

The present reported evidence supports a narrower statement: large cash improves measured dietary diversity under the maintained estimation assumptions, while the same-budget comparisons do not establish which allocation is preferable. It does **not** establish equivalence, a small cost of choosing Gikuriro, or a welfare advantage arising from saving.  

## Conditions under which I would change the recommendation

Successful numerical replication and the technical revisions above would improve credibility, but **would not alone change my leading-general-interest recommendation**. The decisive requirement is a substantial incremental economic result: an informative distributional or decision conclusion that survives credible treatment of selection, weighting, costs, and policy transport; a genuinely new applicable method; or compelling additional evidence distinguishing the proposed mechanism.

For a more narrowly positioned field-journal article or research note, the transparent observed-package reanalysis could be valuable after these issues are addressed. At the requested standard, however, the manuscript currently offers careful accounting and appropriately restrained conclusions more than a sufficiently important new finding. **My provisional recommendation remains reject.**