# Response to round-one referee: revision in progress

Report: `round-1-report.md`, copied verbatim from the completed ChatGPT Pro response. Frozen reviewed commit: `046ce79`. Recommendation: provisional reject at a leading general-interest economics journal. Source/code/arithmetic review was performed; microdata execution, archive reconstruction and PDF inspection were not. No acceptance is claimed.

All numbered comments below are retained. “Planned” is not evidence that a revision has been implemented. The final response will give actual files, estimates and remaining limitations. Revisions after the secondary-analysis plan will be logged as exploratory, prompted by the referee.

## Major comments

| ID | Referee request | Response and implementation plan | Status |
|---|---|---|---|
| M1 | Establish incremental contribution; crosswalk and closest original specifications | Acknowledge the mean coverage contrast is a positive rescaling of cost-effectiveness, already in the parent study. Reproduce its pooled-small-cash/source-score/LASSO-control specification, then a transparent change ladder. Center the extension on coherent distributions, observation bounds, cost scenarios and decision regret. Important novelty remains an empirical requirement, not a wording fix. | Planned; publication obstacle unresolved |
| M2 | Target population, assignment probabilities, sampling/tracking weights | Export all 22 block-by-arm quotas and probabilities. Verify invariant eligibility/weights and baseline linkage. Inspect frame and tracking-weight documentation; compare pooled ANCOVA with explicit inverse-assignment HT/Hájek estimators and explain alternative weighting estimands. Narrow representativeness where input provenance does not support stronger claims. | Three panel invariants verified; design-aligned estimates planned |
| M3 | Item-informed missing-score intervals; population-aligned bounds with uncertainty | Use an observed positive subcategory to identify its food group; derive score lower/upper endpoints for partial modules and [0,12] only for fully unobserved diets. Include every baseline eligible household. Add sampling bands for selection bounds and explicit missing-mean sensitivities; do not infer a ranking from sample bounds alone. | Planned |
| M4 | Fitted best cash policy, optimal-policy uncertainty, regret and tolerance | Feature lower/large cash as the fitted mean optimum. Add all cash-versus-cash comparisons, policy confidence sets and simultaneous regret bounds; illustrate tolerances rather than invent donor preferences. Preserve uncertainty and do not force a winner. | Planned |
| M5 | Coherent dietary distributions; food categories; child outcomes | Use one positive-weight, design-aligned empirical distribution per arm and derive all means/thresholds/shortfalls from it. Analyze all integer shortfall thresholds for concave objectives. Retain household food-access interpretation. Inspect corrected individual panel for available growth outcomes; no child nutrient or long-run claims without those measurements. | Individual panel contains HAZ/WAZ/MUAC; analyses planned |
| M6 | Finite-sample diagnostics, leverage, leave-out sensitivity, inference, duplicated tests | Deduplicate Gikuriro-versus-control copies before Holm and joint-family enumeration. Report arm/contrast concentration and support; use leave-village/block sensitivity and a justified small-sample cluster procedure. Blocking is not a reason to mechanically cluster errors on blocks; weak policy nulls are not sharp permutation nulls. | Planned |
| M7 | Conditional transport, donor constraint and ineligible spillovers | State expected-cost benchmark and stable-package/no-cross-village-interference assumptions once. Universal means assignment/offer at original take-up. Estimate available ineligible outcomes. Hard realized caps, price and saturation effects remain beyond identification without additional information. | Planned; unobserved transport effects remain limits |
| M8 | Cost/participation/overhead scenarios; pair-ordering bug | Make vertex enumeration independent of the order of scenario costs; rebuild all feasible pairs for a labeled relative-cost grid. Distinguish constant unit costs from fixed activation costs. Do not fabricate cost sampling distributions or value omitted benefits. | Planned |
| M9 | Display food spending; recall periods; compress mechanism | Show purchased-food and own-production estimates and source definitions. Present saving model as a conditional illustration, qualify ceiling, and do not condition on realized saving to infer mediation. Identification of returns/fees or a factorial mechanism requires new variation. | Planned; mechanism identification unavailable |
| M10 | Bind extraction to archive; immutable reference; rich codebook; rights and durable archive | Direct verified-ZIP reads and member SHA256 recording now reproduce exactly the frozen input hashes. Add an immutable input reference and an adversarial provenance check. Expand sampling/monetary/index/preprocessing definitions using actual source evidence. Preserve corrected deposit rights metadata. Git provides frozen commits; a DOI archive requires an authorized archival destination and is not implied by GitHub publication. | Direct ZIP chain fixed in 0a9f811; remaining work planned |

## Minor comments

| ID | Request | Response plan | Status |
|---|---|---|---|
| m1 | Title accurately reflects food access, coverage and benchmarking | Retain required opening and Catholic organization setting; revise subtitle around dietary diversity and allocation. | Planned |
| m2 | Assignment/offer, not recipients/verified universal receipt | Revise headings, abstract and definitions consistently. | Planned |
| m3 | Threshold corollary respects twelve-group ceiling | Require an uncrossed reachable threshold; no diversity gain at ceiling. | Planned |
| m4 | Derive outcome-specific sample/village counts | Display separate sample ranges/counts or assert a shared count; remove hardcoded 248. | Planned |
| m5 | Remove false fallback comment | State actual baseline mapping; do not add undocumented source-score fallback. | Planned |
| m6 | No zero p-values, readable food labels and units | Use inequalities for tiny p-values and explicit probability/shortfall units, family and interval types. | Planned |
| m7 | Reduce repetitive limits, add relevant literature | Consolidate transport/identification restrictions; expand specific cash-food, price and decision literature. | Planned |
| m8 | Preserve plan/amendment history | Keep original plan unchanged; append dated review-driven revisions and label new inference families. | Preserved; new amendments to be added |

## Recommendation and limitations

The referee explicitly says that technical credibility alone would not change the leading-general-interest recommendation. The revision will test whether a more informative decision result is available. Acceptance, scientific novelty, identified mechanisms, or new field observations will not be manufactured. Every feasible comment will receive an actual implementation and result, while unmet requirements will be identified plainly before resubmission.
