# Data and Code for: You give them something to eat: Dietary Diversity, Coverage, and Catholic Aid in Rwanda

Diego González-González. Research draft, 30 September 2026. Third referee revision; fourth submission in preparation. Third genuine recommendation: Reject at the unchanged standard.

This package reanalyzes the village-randomized Gikuriro evaluation implemented by Catholic Relief Services and SNV in Rwanda. It compares lotteries over observed aid packages at a fixed expected provider budget. It adds coherent dietary distributions, incomplete-outcome bounds, diversified decision accounting, finite conditional-assignment outer regions and explicit failed-coverage diagnostics. The current revision uses all protected distributional information, deterministic outcome consistency, a support-only information benchmark, and explicit institutional/resource-value sensitivities. It introduces no new experiment or identification strategy. The original study already discusses cost effectiveness and coverage: McIntosh and Zeitlin (2024), *Economic Journal* 134(664):3360–3389, [doi:10.1093/ej/ueae050](https://doi.org/10.1093/ej/ueae050).

Read [the PDF](paper/paper.pdf) or [editable LaTeX](paper/paper.tex). Public repository: [dgonzalezgonzalez/you-give-them-something-to-eat](https://github.com/dgonzalezgonzalez/you-give-them-something-to-eat), default branch `codex/research`. Codex assisted code and drafting; no language model processes data or enters scientific computation. This is a research package, not a journal decision or official JPE audit.

## Data availability, rights and scope

All default inputs are included; no credentials, restricted-data application, proprietary statistical software or external API is required. Only the **corrected** public [Zenodo deposit 15881329](https://zenodo.org/records/15881329), concept DOI 15881328, is used. Its actual CC BY 4.0 rights, public-access status, correction statement and archive checksum are preserved in [zenodo-rights.json](docs/sources/zenodo-rights.json), retrieved from the official API. It was created 15 July 2025 with nominal publication date 23 May 2024. The old restricted deposit 11265230 is not used or redistributed.

| Supplied input | Contents / origin |
|---|---|
| `households.csv` | Frozen 5,506 household-round rows and 52 numeric fields from corrected `household_panel.dta`; food module, economic outcomes, sampling weights, eligibility and randomized assignments |
| `costs.csv` | All source cost/compliance accounting columns from `CostsAndCompliance.xlsx` |
| `codebook.json` | Frozen original source labels plus initial reconstruction definitions |
| `revision_households.csv` | 5,506 matching rows of village frame counts, sampling probability, original selected diet controls and food-spending transformations |
| `children.csv` | 7,356 numeric child-round records marked for/source-observed anthropometry; arbitrary keys, eligible status, age/sex and source growth scores |
| `analytical-codebook.json` | Definitions, units, recall, zero handling, source preprocessing caveats, sampling versus assignment probabilities and actual sample rules |
| `provenance.json` | Generated source/member provenance and initial extract hashes |
| `input-reference.json` | Immutable reference for three original input byte streams at commit `046ce79` |
| `revision-reference.json` | Reference for two supplementary extracts and their corrected archive members |

All files above are under `data/input/`. Core and supplementary research data remain **CC BY 4.0**. Cite the original article and corrected deposit and identify this project's transformations. Original code is MIT licensed ([LICENSE](LICENSE)); the manuscript is furnished for reading/review without a separate reuse license. JPE template attribution/license are retained under `docs/sources/`. The full original archive and original manuscript are not redistributed.

No names, contacts, geographic codes, coordinates, exact dates, free text or administrative recipient lists are exported. Household, child, village and block keys are arbitrary sequential replacements. Field selection was reviewed; numeric-type checks alone are not a proof against reidentification.

The initial core score is missing whenever any of 16 categories is nonbinary. It exactly matches source scores on 5,414 complete modules; 92 modules across rounds/populations are incomplete. Seven source endline scores are noninteger replacements. The revision retains item information: an observed positive subcategory identifies its combined group even if another is unknown. This identifies 1,730 eligible endline diets rather than 1,728 complete modules. Fixed weighted-baseline bounds keep all 1,793 baseline eligibles, including absent endline households. The original paper's 1,794 baseline count differs by one household in the corrected release; no record is invented to repair it.

At eligible baseline the source expansion weight equals village frame eligible count divided by released sample count, within 4.77e-7. It is fixed across rounds. No unavailable intensive-tracking factor is manufactured. Conditional village assignment probabilities are published in `output/assignment_probabilities.csv`. They assume exchangeable village labels given the released block counts and independent assignments across blocks. The original randomization program and all assignment restrictions are unavailable; observed frequencies alone do not prove that design. Fixed released weights likewise do not prove representation of unsampled households. Source monetary fields and anthropometric scores retain inherited cleaning/replacement. No upstream survey-cleaning replication, unverified dollar conversion or percentage interpretation of IHS coefficients is asserted.

## Software and one-command reproduction

Tested Python **3.12.10**, NumPy **2.5.2**, pandas **3.0.5**, SciPy **1.18.1**, Matplotlib **3.11.1**. Four direct dependencies: `requirements.txt`; exact direct/transitive environment: `requirements-lock.txt`. Windows 11 x64, eight available logical processors. No GPU is needed. Allow 2 GB RAM and 150 MB for reproduction/rendered inspection; package installation adds storage. Default numerical/PDF master took approximately 80 seconds on this system. Physical RAM was not measured.

```text
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe run.py --pdf
```

On macOS/Linux activate `.venv/bin/activate`, then use `python -m pip install -r requirements-lock.txt` and `python run.py --pdf`. Without TeX, `python run.py` reproduces all numerical exhibits. There are no personal hardcoded scientific paths. After dependency installation, the default master needs no network.

PDF compilation uses existing `pdflatex` (tested MiKTeX 25.12), three passes, and standard packages: amsmath, amssymb, amsthm, booktabs, graphicx, array, natbib, setspace, hyperref, caption, geometry and lmodern. Set `PDFLATEX` if needed; the master recognizes the standard per-user Windows MiKTeX path. This is a multi-file project; standalone native compilation cannot supply its generated companion files.

The master performs:

1. Check all input bytes against generated provenance and independently frozen references.
2. `estimate.py`: original WLS ANCOVA/CR1, 204 distinct primary tests, 96 economic Holm tests and original sensitivities.
3. `referee_revision.py`: conditional assignment probabilities, coherent Hájek distributions, item-informed baseline endpoints, shared **22-block** score covariance, zero-variance support guards, three exploratory multiplier families, finite primitive arm regions and original-study crosswalk.
4. `policy_allocation.py`: retain third-submission finite-box/block-sensitivity calculations and their cost/share crosswalks. `distribution_regions.py`: project all protected mean/survival/shortfall intervals through one discrete score distribution per arm; add deterministic scalar consistency restrictions and support-only benchmarks. `institutional_allocations.py`: use the new regions for six hypothetical assistance/spending classes, both own and common comparators, six unused-resource values and all 32 fixed-outcome cost scenarios per finite method.
5. `child_cohorts.py`: pre-treatment source-flag cohort accounting and separate observed-follow-up sensitivity; `finite_cluster.py`: original ANCOVA working-model CR2 and omission diagnostics.
6. `validate_blocked_inference.py`: retain the exact covariance falsifier and four synthetic stress tests, including failures of nominal coverage. Successful execution does **not** mean the coverage approximation passed.
7. Four exhibit builders: **32 generated tables, six generated figures, four macro files**. The manuscript cites **27 tables and 1 figure**; unused supplementary exhibits are explicitly marked in the output map.
8. Core, revision, decision, distribution and institutional validators; optional three-pass compilation.

Initial resampling uses seed 20260930 and 9,999 village multipliers. The exploratory revised ratio bands use the same seed and **99,999 block multipliers**, plus a 99% Monte Carlo upper order statistic for their 95% quantile. Nested 9,999/29,999/99,999-draw sensitivities are in `multiplier_quantile_sensitivity.csv`; they measure simulation error, not sampling coverage. Declared distinct ratio families are 184 GK/cash, 828 all-policy and 1,656 endpoints; affine duplicates enter once. The finite conditional baseline family protects 276 primitive arm/transformation/endpoints; a separate observed-outcome family protects 138. Separate families are not a joint paper-wide 95% guarantee. All referee-driven analyses are exploratory; [amendments](docs/plan-amendments.md) preserve the original plan.

## Source reconstruction and verification

Optional source reconstruction requires `openpyxl==3.1.5`. Download the corrected deposit's `McIntosh and Zeitlin.zip` to `data/raw/source.zip`, then run `python run.py --from-source --pdf`. Extraction verifies archive MD5 **35fe28d475e1913e993a8305f19b4625** and SHA256 **84ce805316fef0d36466e75844afe521fb9a6dfe1fe33f454e1aa2dc71413a7e**, reads exact members directly and compares expected derived hashes before replacing analytical bytes. A stale manually extracted directory cannot substitute for the verified archive. Raw files are Git ignored.

The source-to-extract route begins with the authors' corrected processed panels, not raw questionnaires and upstream cleaning. Source economic preprocessing that cannot be recovered is explicitly documented. Reference files must not be regenerated to make a failed check pass.

Actual checks: unchanged initial WLS agrees with independent Stata/MP 19 within 1.3e-13 for coefficients and 5.2e-15 for SEs. This checks five initial ANCOVA coefficients only. Core validation passes 33 checks including that optional reference (32 in a cold copy without Stata output); revision validation passes 92; decision validation passes 14; distribution validation passes 31; institutional validation passes 178. These include CDF identities, 100 independent vertex LPs, bounded-sampling exponential moments, exhaustive small ratio fixtures, zero denominators, scale invariance, primal adversaries, cohort partitions and adversarial provenance rejection. Implementation checks do not certify the failed block approximation.

`python code/clean_check.py` (optional PyMuPDF/Pillow) ran a fresh source copy with no outputs. All **95** CSV/table/macro/PNG/PDF-text comparisons passed for the current 34-page PDF. Runtime metadata, creation timestamps and the optional Stata reference are excluded. The current cold master took 72.31 seconds. Published scientific commit `4c3ed91945245b91deb5afddb80625573cdf3857` was exported with git archive and run in the separate locked environment. All 95/95 comparisons passed, including 34-page PDF text; that master took 63.98 seconds. Its twenty public partitions also reconstruct all three immutable inputs byte-for-byte. No old run is attributed to this source. Historical third-submission scientific source `95d3e2f536de19b40bfb3f7e6718bbb8fb7c741a` passed 80 comparisons in the separately installed locked environment. That environment was originally installed from official PyPI for the first submission and is reused, not freshly reinstalled for each revision.

`code/verify_environment.py --source-dir PATH --commit-file FILE` compares a git-archive source run in a separate environment; it does not create that environment or export by itself. Historical first-submission fresh-install evidence remains distinct from revision audits.

The already-public large CSVs also have [smaller exact row partitions](data/public-views/README.md). Their 20 parts reconstruct all three input CSVs byte-for-byte against immutable references (`python code/public_data_views.py --verify`). The default scientific master reads the original inputs. These views enable file-size-limited inspection; they do not demonstrate independent household execution.

## Outputs and interpretation

The [output map](docs/output-map.csv) derives current numbering from the manuscript and records script locations and numerical sources for every cited exhibit and all four macro files. `distribution-results.tex` contains current coherent-region/institutional numbers; `decision-results.tex` retains finite-box/allocation/cohort diagnostics. Other numerical files remain generated for the crosswalk. Source facts and theory need independent review.

Diet is household food access, not child nutritional adequacy. Lower/large cash is the fitted mean winner. Choosing it over Gikuriro gives an observed-sample fitted gain of 0.237 groups. Diversification lowers the weighted-baseline block-region bound to 0.570 groups, but that approximation **fails synthetic coverage stress tests** (695/800 with equal weights; 592/800 with unequal weights). It supplies no reliable nominal 95% guarantee. Support and costs alone give mean loss 9.600 groups. Outcome consistency gives 8.073764; projection of all finite primitive information reproduces the referee's 8.151078; their coherent intersection gives 7.720305. The earlier finite mean-box bound 9.440 remains a displayed implementation benchmark, not the current headline. Its width is not an impossibility result or proof that more data are necessary. All current tolerance flags are explicitly exploratory.

The finite result conditions on fixed released weights, exchangeable quota assignments, independent blocks and stable potential outcomes. Representing the unsampled eligible frame and deploying to comparable villages need extra sampling/transport assumptions. Costs are national-scale standardized average units, not observed marginal activation costs for a mixed rollout. All 32 accounting scenarios hold effects fixed. Hard realized budgets, changed spillovers and new delivery scale are outside those guarantees.

Read [the design derivation](docs/design-inference.md), [JPE-style self-audit](docs/replication-report.qmd), [research status](docs/research-status.md), [current objective audit](docs/objective-audit-round-4.md) and [genuine referee reports/responses](docs/referee/). All three genuine Pro reports reject at the unchanged leading general-interest standard. None ran household/child microdata or inspected the manuscript PDF. The third independently reproduced summary-input allocation/projection LPs, executed the exact retrieved inference module on synthetic fixtures and reproduced equal-weight 695/800 undercoverage. The first public household part is readable, but full input reconstruction/execution remains unfulfilled. The downloadable third audit bundle was not received after one visible download attempt timed out. No acceptance or independent full replication is manufactured. The [requested LR prose screen](docs/writing-audit.md) is not evidence of human authorship.

Institutional own-menu bounds restrict both choice and comparator. They can shrink mechanically; the common-menu columns retain the original comparator and isolate restricted choices. At c_GK=budget, a 25 percent GK minimum on both sides scales own-menu regret exactly by 0.75. This is an algebraic benchmark, not evidence that the rule improves outcomes. Unused-resource values are unestimated normative scenarios, not welfare calibrations.
