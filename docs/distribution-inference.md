# Distributional information, consistency and institutional comparators

Fourth revision, 30 September 2026. This extends `design-inference.md`. It retains the finite conditional-assignment event: fixed released weights, exchangeable labels conditional on block counts, independent blocks and stable reported-score potential outcomes. It is not a new concentration theorem, verification of the original assignment law, or sharp joint potential-outcome region. Full derivations are in the manuscript, including Proposition 3 and its appendix proof.

## Support-only benchmark

Five pure packages are individually affordable. Under any allocation at least one has share no greater than 1/5. Giving it mean twelve and every other package mean zero produces regret at least 9.6. Equal probability on control, Gikuriro and the three small cash packages attains 9.6 over all nine comparator vertices and costs $79.033734. This protection is diversification under ignorance, not information from household outcomes. The support-only six-group negative-shortfall bound is 0.8 on a unit-range objective.

## Coherent projection

For each arm define probabilities p_ad over integer scores d=0,...,12. Nonnegativity and sum_d p_ad=1 are combined with L_av <= sum_d v(d)p_ad <= U_av for every protected transformation. For full baseline, limits use the lower endpoint's finite lower bound and upper endpoint's finite upper bound. The observed-ratio version uses its separate family's intervals and one common item-identified-diet observation indicator.

All 25 displayed transformations enter the distribution constraints. Shortfall_1 equals survival_1 minus one and shortfall_12 equals mean/12 minus one, so there are 23 distinct primitives in the original multiplicity calculation. The existing 276-target baseline event or separate 138-target observed event already protects these constraints. Projection adds no multiplicity penalty; their conjunction is not called a 95% event.

On its event the true distribution is feasible. Each arm's scalar image is an interval by compactness/convexity. The specified outer polytopes have no cross-arm constraints, so the scalar projection is exactly a product of arm intervals. Fixed individual weights and potential outcomes can impose further restrictions: exact scalar projection is not joint identification sharpness. An empty polytope fails explicitly instead of dropping constraints.

The code reproduces the referee's independently computed 8.151078 mean projection as 8.151077610089386. This checks summary-input optimization arithmetic, not the referee's unperformed household execution. Its shortfall analogue is 0.6867785653268217.

## Deterministic consistency

Let S_a be actually assigned households, W=sum_i w_i, [l_i,u_i] their item-implied transformed endpoints and [L,H] the transformation support. Then the full-baseline arm mean lies between

    (sum_{i in S_a} w_i l_i + L sum_{i not in S_a} w_i)/W
    (sum_{i in S_a} w_i u_i + H sum_{i not in S_a} w_i)/W.

These valid scalar restrictions need consistency and support but no assignment probabilities. For a single unrestricted scalar mean, unknown counterfactual scores can attain support endpoints; the interval can be sharp while the combined moment polytope remains an outer set.

For a potential identified-diet ratio, assigned identified households contribute known numerator N_a and denominator D_a, and U_a is total unassigned baseline weight. Bounds are (N_a+L U_a)/(D_a+U_a) and (N_a+H U_a)/(D_a+U_a) when that denominator is positive. A full-support convention handles zero; an undefined potential ratio is not described as an identified population mean. Assigned unidentified diets remain excluded even if a particular transformed endpoint is known.

The logical distribution projection gives 8.073763943408215 groups. Intersection with all finite primitive distributional constraints gives **7.720304788340825**; shortfall gives **0.6365671615711074**. The mean tightening from support-only is 1.879695211659175 groups, about 19.58%. This is criterion-specific information, not the general value of conducting an experiment. The bound remains too wide for a small-loss recommendation and does not establish an optimal confidence procedure or an impossibility theorem.

## Institutional comparator and unused funds

Six explicit hypothetical classes address an expected-cost ceiling, 75% assisted, universal assistance, binding expected spending, universal assistance with binding spending, and 25% minimum Gikuriro. None is established as a CRS mandate. Geographic continuity and a hard realized cap are not represented by these expected-cost rules.

Own-menu regret constrains both choice and comparator. Common-menu regret constrains the choice and retains the original comparator; each column optimizes separately. The output also evaluates the own-menu optimum against the common menu. Universal assistance gives own-menu mean loss 7.503192 but optimized common-menu loss **8.138075**, above the unrestricted 7.720305. Binding expected spending gives common-menu loss **7.848443**. Smaller own-menu numbers do not establish better outcomes.

For gamma in [0,1], when Gikuriro cost equals budget, its minimum-share class is gamma*e_GK+(1-gamma)*Q. Restricting both comparator and choice therefore scales minimized regret by 1-gamma for any fixed mean region. At 25%, the bound is 5.790228591255619=0.75*7.720304788340825. This is a geometric consequence of excluding alternatives, not empirical evidence favoring that mandate.

The baseline criterion gives unused resources no value. Hypothetical resource sensitivities use q'mu+eta*(budget-c'q), with the comparator using the same eta. Comparator advantage is (r-q)'mu+eta*c'(q-r). Values eta=0,.001,.005,.01,.02,.05 groups per unused USD are unestimated normative scenarios. Their losses belong to an augmented objective, not diet alone or a calibrated welfare function.

All 32 cost cases are rebuilt for both current finite regions using unchanged outcomes/coherent point means. Vertices change with prices and feasibility. National-scale average costs, separately computed at 56,127 beneficiary households for each cash amount, remain a proportional-accounting assumption. Mixed-rollout activation/marginal costs and changed participation/delivery outcomes are not identified.

## Actual implementation checks

Distribution validation passes 31 checks, including exhaustive scalar completions, observation preservation, scale invariance, incompatible-CDF failure, affine duplicates, complete projection/nesting, 192 feasible endpoint witnesses and independent epigraph LPs over all 64 box corners for sixteen allocations. Maximum independent LP discrepancy is about 1.78e-15.

Institutional validation passes 178 checks: exact original/binding-budget vertices, homothetic identity, independent own/common corner LPs, feasible choices, common-comparator ordering, resource scenarios and all 64 aligned cost calculations. Maximum LP difference is about 3.55e-15. These are implementation checks, not external full microdata replication or validation of the failed block approximation. Coverage follows from the stated finite event and valid deterministic restrictions.
