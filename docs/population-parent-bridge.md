# Parent population benchmark and observed-package frontier

This is a post-ninth-report revision using unchanged public numeric inputs. No historical freeze or earlier report has been rewritten. Scripts `population_crosswalk.py` and `population_uncertainty.py` are in the default master; the independent author implementation check is `validate_population_revision.py`.

## Estimator crosswalk

The [December 2020 parent manuscript](https://gps.ucsd.edu/_files/faculty/mcintosh/cm_Gikuriro_Manuscript.pdf), Table VIII, reports dietary effects 0.12 (Gikuriro), 0.00 (pooled small cash), −0.28 (large cash), with 2,718 observations. Its public PDF was downloaded on 1 October 2026: 846,154 bytes; SHA256 `dd4f1d72d4fead7039ff6dfd5e397dbaff4338eed7eaf60749dcc6c1e08ad038`. It is source material, excluded from redistribution here.

The corrected release with source scores, source sampling weights, current released fixed diet controls, block effects and eligibility indicator gives 0.124737, 0.000925 and −0.276389 on 2,718 observations. These reproduce the published rounding and count. This is narrower than reproducing the historical analysis: historical population programs, selected-control versions, sharpened q-values and all table entries are not verified. The current fixed list is taken from released `CovariateLists.xlsx`; covariate selection is not rerun.

Splitting only the three small arms on that sample gives lower −0.194697, middle −0.112955, upper 0.294093, Gikuriro 0.123183 and large −0.277987. Restricting source scores to the 2,692 item-identified common observations changes upper to 0.264288. Switching to item scores on that same sample changes none of the fitted coefficients. The complete-module restriction instead has 2,688 observations. The output retains all seven specified steps and sample counts. These are sequential accounting comparisons, not a unique causal decomposition of estimator changes.

The separate cost-linear reconstruction uses the earlier paper's described population-cost regressor, centered at the published Gikuriro population cost. Gikuriro minus interpolated cash is 0.163066 (village CR1 SE 0.122275). The same source-score sample with separate arms gives Gikuriro minus upper −0.170910. The released current programs define a TCE regressor but do not execute the historical population benchmark; this implementation is an explicit reconstruction of the description. It is not mislabeled as recovered historical code.

Pooled respondent assignment-weighted ratios differ from baseline-share averages of stratum ratios by at most 0.013326 groups across arms. Their close numerical values do not equate their potential-observation estimands. The new frontier permits lotteries over every observed package; the parent pooled and cost-linear contrasts do not themselves select that unrestricted menu. If package means in both strata are affine in cost, budget-exhausting cash lotteries tie within each stratum. Fitted differences exploit departures from that response and choices leaving funds unused; the data do not establish that those departures are causal rather than sampling or observation selection.

## Joint uncertainty

All new families are exploratory and declared after the genuine ninth report. Common block/village score indexing retains covariance between stratum estimates rather than adding their variances as if independent.

- Direct Gikuriro-versus-cash cross-stratum differences: 16 ratio tests (eight non-Gikuriro vertices × two cost conventions); 32 regression tests (the same × two specifications).
- Cash-versus-cash: every unordered pair of eight cash/control vertices, both cost menus, and four objectives (eligible, ineligible, baseline aggregate, ineligible minus eligible). There are 224 ratio tests and 448 regression tests including both specifications.
- Each of these four families receives its own Holm adjustment. They are not pooled into a claimed global family or combined with the older 64-test family or finite events.

For lower/large, the ineligible-minus-eligible Gikuriro contrast is 0.771497 (block SE 0.241665; Holm p 0.065697). Village WLS gives 0.674438 (Holm p 0.027101); baseline ANCOVA gives 0.558860 (Holm p 0.209086). All remain visible. Cross-equation village covariance uses the separate stratum CR1 corrections and minimum stratum G−1 degrees of freedom; this is a working approximation, not validated finite inference.

Upper minus lower/large cash in the aggregate is 0.850427 by ratios (Holm p 0.122420), 0.861773 by WLS (Holm p 0.020752), and 0.521877 by baseline ANCOVA (Holm p 1). The two standalone finite mean boxes each admit all means equal to five in both strata; thus neither certifies a unique cash winner or switch. Ratio stress failures, selection limits and original assignment assumptions remain. No new simulations, draws or extra certificate precision were added.

## Cost-denominator audit

The parent labels eligible cost as effective spending per study-eligible household and population cost as spending per village household. Its explanation distinguishes avertable participation costs from costs incurred despite eligible nonparticipation. The numeric workbook contains five rows of values, not formulas or a detailed costing ledger.

The eligible identity `beneficiary_cost × (1 − averted_share + averted_share × eligible_compliance)` reproduces all columns to source rounding (largest absolute residual 0.000023 dollars). For cash, `beneficiary_cost × population_compliance` reproduces population cost to rounding. **It does not reproduce Gikuriro:** the product is 26.539051, whereas the stored population cost is 28.020941, leaving 1.481890 dollars. The additional formula/denominator for this component is unavailable from the inspected workbook and text. The residual is preserved as an unresolved accounting component, not explained by rounding or invented overhead assumptions.

Baseline eligibility share times Gikuriro eligible cost is 14.404666, not 28.020941. Treatment extended outside survey eligibility and the non-averted components differ, so a pure frame-unit conversion is unwarranted. Conditional implied ineligible participation rates are stored for accounting only; they are not verified receipt rates linked to these households. Each source cost column defines its own hypothetical trial-participation menu and Gikuriro budget. Neither identifies marginal scale costs or a hard spending cap.

## Verification limits

The author-side validator separately reconstructs weighted least squares using scaled SVD and residual derivatives, common-village covariance, all new regression contrasts, all new block-ratio contrasts, multiplicity, finite-box tie witnesses and cost residuals. Its 734 checks pass locally. This validates implementation, not nominal sampling coverage or economic importance. The full revised master completed in 1,070.066282 seconds from an empty-output source copy; 124 local comparisons pass, with the initially stale warm output-map mismatch separately preserved. Actual final cold PDF/visual/style scope is recorded in separate receipts. The ninth referee's linked audit ZIP and summary have not been received locally; their contents are not used as author-verified files.
