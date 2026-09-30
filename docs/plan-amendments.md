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
