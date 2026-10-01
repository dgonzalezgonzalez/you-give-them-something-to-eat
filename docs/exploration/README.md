# Population and cash-package choice: exploratory work after the eighth report

1 October 2026. This is a retrospective pilot from the existing public data. It is separate from the main paper, its protected finite event, default master and frozen eighth version. It does not claim to resolve the referee's importance objection. No ninth review has been submitted.

The question is whether the eligible-household diet objective chooses the same cash package when baseline-ineligible diets enter the objective. Eligibility is the survey firm's pre-assignment definition; it is not verified receipt. The original study allowed providers to treat outside that definition. Consequently these contrasts cannot isolate spillovers.

Broader-population effects are already discussed in [the authors' December 2020 manuscript](https://gps.ucsd.edu/_files/faculty/mcintosh/cm_Gikuriro_Manuscript.pdf), including its total-causal-effect analysis, and in [Berk Özler's 2018 World Bank discussion](https://blogs.worldbank.org/en/impactevaluations/most-good-you-can-do-whom). They are not claimed as a discovery. The possible extension is an explicit cash-package frontier under stated population/welfare weights and a fixed expected-cost menu. Its scientific importance remains to be established.

## Executed pilot

The full baseline has 1,793 eligible and 995 ineligible households. Frozen source expansion weights sum to approximately 4,002 and 30,584, respectively. These weights match the relevant village frame counts divided by each stratum's released sample counts within source floating precision. They describe the released frame convention, not national rollout or actual provider-defined eligibility. The eligible weight share is 0.115712; it is not a recipient or national population share.

Assignment probabilities use the same 248 villages and 22 conditional blocks. Item-informed intervals retain every baseline household, including absent follow-up. Identified-diet ratios select observed diets; complete-case and endpoint quantities are distinct. Sampling error remains in endpoint estimates.

For Gikuriro minus the original lower/large-cash lottery:

| Population | Identified-diet difference, groups | Exploratory block SE | Estimated missingness endpoints, groups |
|---|---:|---:|---:|
| Eligible | −0.237386 | 0.156907 | [−0.574181, 0.101475] |
| Ineligible | 0.534111 | 0.165347 | [0.115180, 0.887465] |
| Fixed baseline-weight aggregate | 0.444840 | 0.145083 | [0.035413, 0.796517] |

These endpoint estimates are **not confidence limits**. Positive endpoints do not establish a positive full-target effect. Block SEs are exploratory linearizations, with the previously documented finite-coverage limitations; they do not inherit the main paper's finite event.

The ANCOVA pilot among identified ineligible panel diets gives 0.431713 groups for this contrast (village CR1 SE 0.146119) after baseline diet and block controls. Its conventional pointwise inference is separate from block linearization, finite-design protection and a post-search simultaneous event. No favorable p-value is used as a validation criterion. All eight cash/control alternatives and both specifications remain in the CSV.

Let theta be the stipulated **total welfare weight** on eligible diets; the objective is theta times their fitted mean plus (1−theta) times the ineligible fitted mean. Under the original eligible-household cost menu, the fitted preferred package is upper cash below theta approximately 0.8440, upper/large cash until 0.9142, and lower/large cash above 0.9142. At fixed baseline-weight aggregation, upper cash is preferred. Gikuriro is never the fitted winner on this frontier. The Gikuriro/lower-large pairwise crossing at 0.6923 is not an optimal-menu switch. These numerical thresholds have sampling and missingness uncertainty; preferences were not estimated and the frontier is not an operational recommendation.

## Replication and limits

Run with the existing locked statistical environment from the repository root, in order:

```
python docs/exploration/community_diet_pilot.py
python docs/exploration/community_ancova_pilot.py
python docs/exploration/community_frontier_pilot.py
python docs/exploration/community_cost_frontier.py
```

The JSON/CSV files here are the actually generated pilot outputs. An independent author-side replay read the original public Stata file directly and recomputed all 36 stratum/endpoint arm ratios without importing the pilot/scoring/estimator modules. Maximum discrepancy was 1.78e−13; this verifies source mapping, not independent field replication or novel causal content. Its receipt is `community-source-audit.json`. Replaying that audit requires the original corrected source archive extracted at the documented ignored source path.

Next requirements include explicit treatment of source population-cost denominators, full-target missingness and sampling uncertainty, alternative estimators/weight conventions, multiple-comparison accounting, prior-art overlap and integration into a shorter economic argument. The source population-cost column must not be silently substituted for the original eligible budget. Marginal mixed-rollout costs, actual institutional welfare weights and full historical assignment restrictions remain unresolved. No investigator contact was made.

The executed cost-column sensitivity now recomputes every menu vertex separately under the two published average-cost conventions. Both choose upper cash at the baseline-weight aggregate point objective. The lower/large share changes from 15.2871% to 18.1080%; the upper/large-to-lower/large switch changes from theta 0.91424 to 0.91244. These remain fitted sensitivity results. The source Gikuriro population budget is $28.02094, whereas multiplying its eligible cost by the released baseline eligible-weight share yields $14.40467. Their differing denominators are preserved rather than silently equated or labeled an accounting error. Neither identifies the cost of a proposed mixed rollout.
