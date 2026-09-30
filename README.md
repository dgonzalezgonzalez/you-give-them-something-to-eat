# Data and Code for: You give them something to eat: Dietary Diversity, Coverage, and Catholic Aid in Rwanda

Diego González-González. Research draft, 30 September 2026. First referee revision.

This package reanalyzes the village-randomized Gikuriro evaluation implemented by Catholic Relief Services and SNV in Rwanda. It compares lotteries over observed aid packages at a fixed expected provider budget. It adds coherent dietary distributions, incomplete-outcome bounds, finite-policy regret and explicit inference diagnostics. It introduces no new experiment or identification strategy. The original study already discusses cost effectiveness and coverage: McIntosh and Zeitlin (2024), *Economic Journal* 134(664):3360–3389, [doi:10.1093/ej/ueae050](https://doi.org/10.1093/ej/ueae050).

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

The initial core score is missing whenever any of 16 categories is nonbinary. It exactly matches source scores on 5,414 complete modules; 92 modules across rounds/populations are incomplete. Seven source endline scores are noninteger replacements. The revision retains item information: an observed positive subcategory identifies its combined group even if another is unknown. This identifies 1,730 eligible endline diets rather than 1,728 complete modules. Full-population bounds keep all 1,793 baseline eligibles, including absent endline households. The original paper's 1,794 baseline count differs by one household in the corrected release; no record is invented to repair it.

At eligible baseline the source expansion weight equals village frame eligible count divided by released sample count, within 4.77e-7. It is fixed across rounds. No unavailable intensive-tracking factor is manufactured. Known village assignment probabilities are separately published in `output/assignment_probabilities.csv`. Source monetary fields and anthropometric scores retain inherited cleaning/replacement. No upstream survey-cleaning replication, unverified dollar conversion or percentage interpretation of IHS coefficients is asserted.

## Software and one-command reproduction

Tested Python **3.12.10**, NumPy **2.5.2**, pandas **3.0.5**, SciPy **1.18.1**, Matplotlib **3.11.1**. Four direct dependencies: `requirements.txt`; exact direct/transitive environment: `requirements-lock.txt`. Windows 11 x64, eight available logical processors. No GPU is needed. Allow 2 GB RAM and 150 MB for reproduction/rendered inspection; package installation adds storage. Default numerical/PDF master took approximately 38 seconds on this system. Physical RAM was not measured.

```text
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe run.py --pdf
```

On macOS/Linux activate `.venv/bin/activate`, then use `python -m pip install -r requirements-lock.txt` and `python run.py --pdf`. Without TeX, `python run.py` reproduces all numerical exhibits. There are no personal hardcoded scientific paths. After dependency installation, the default master needs no network.

PDF compilation uses existing `pdflatex` (tested MiKTeX 25.12), three passes, and standard packages: amsmath, amssymb, amsthm, booktabs, graphicx, array, natbib, setspace, hyperref, caption, geometry and lmodern. Set `PDFLATEX` if needed; the master recognizes the standard per-user Windows MiKTeX path. This is a multi-file project; standalone native compilation cannot supply its generated companion files.

The master performs:

1. Check input bytes against generated provenance **and independent immutable references**.
2. `estimate.py`: original WLS ANCOVA/CR1, 204 distinct primary tests (221 display rows), 96 distinct secondary Holm tests, foods (80), heterogeneity (10), observation (5), original sensitivities.
3. `referee_revision.py`: explicit assignment probabilities, positive-weight Hájek distributions, item-informed baseline-population bounds, all 36 policy pairs, regret/tolerances, source-specification crosswalk, cost scenarios, child/ineligible analyses.
4. `finite_cluster.py`: CR2/Satterthwaite working-model correction, concentration/leverage and all village/block omission fits.
5. Two exhibit builders: **19 tables, four figures**, both empirical macro files, and [complete output map](docs/output-map.csv) derived from current manuscript numbering.
6. `validate.py` and `validate_revision.py`: nonzero exit on failed scientific invariants, independent LP comparisons or adversarial provenance checks.
7. Optional three-pass LaTeX compilation to `paper/paper.pdf`.

Statistical seed **20260930**, **9,999** shared Rademacher draws. Revision families have 184 distinct Gikuriro/cash tests, 828 all-policy pairwise tests and 1,656 bound endpoints. Mean/shortfall-12 and survival-1/shortfall-1 affine duplicates enter only once. Child and ineligible extensions each have fifteen Holm tests. All extensions after first review are exploratory and logged in [plan amendments](docs/plan-amendments.md); the original plan is preserved unchanged. No blind or prospective registration claim is made.

## Source reconstruction and verification

Optional source reconstruction requires `openpyxl==3.1.5`. Download the corrected deposit's `McIntosh and Zeitlin.zip` to `data/raw/source.zip`, then run `python run.py --from-source --pdf`. Extraction verifies archive MD5 **35fe28d475e1913e993a8305f19b4625** and SHA256 **84ce805316fef0d36466e75844afe521fb9a6dfe1fe33f454e1aa2dc71413a7e**, reads exact members directly and compares expected derived hashes before replacing analytical bytes. A stale manually extracted directory cannot substitute for the verified archive. Raw files are Git ignored.

The source-to-extract route begins with the authors' corrected processed panels, not raw questionnaires and upstream cleaning. Source economic preprocessing that cannot be recovered is explicitly documented. Reference files must not be regenerated to make a failed check pass.

Actual checks: original main WLS matches independent Stata/MP 19 within 1.3e-13 for coefficients and 5.2e-15 for standard errors. Stata checks those five coefficients only. To rerun: `do code/validate_stata.do`, then `python code/validate.py`; Stata is optional. Core validation passes 33 checks; revision validation passes 92, including discrete CDF identities and 100 independently solved LPs. Isolated tampered-data/re-written-manifest and corrupt-source fixtures are rejected. Those invariants are numerical evidence, not proof that an asymptotic interval has exact finite-design coverage.

Optional `python code/clean_check.py` (PyMuPDF/Pillow) runs a source copy with no outputs and compares CSVs, tables, macros, PNGs and PDF page text. `verify_environment.py` compares `tmp/published-clean/` exported from the commit recorded in `tmp/published-commit.txt` and run in the separate locked environment. Runtime metadata and PDF timestamps are excluded. Audit results are recorded under `output/`. First-submission fresh-install evidence is historical; new source-copy results are distinct and dated.

## Outputs and interpretation

The [output map](docs/output-map.csv) maps every current table/figure and both in-text macro sets to script lines and numerical sources. Estimates and diagnostics are inspectable CSVs under `output/`; tables and plots are in `output/tables/` and `output/figures/`. `paper/results.tex` and `paper/revision-results.tex` contain all reported new empirical macros. External trial facts, bibliography and theory require source/mathematical review.

Diet is a household food-access proxy, not measured child nutrient adequacy. All mean candidate policies remain compatible with optimality. Missing-diet envelopes include sampling uncertainty, while the original coarse sample bounds are retained only as an audit crosswalk. The ratio/multiplier inference is cluster asymptotic, not an exact blocked-design randomization procedure. CR2 is a specified working-model sensitivity. Costs are fixed in inference; cost/take-up grids are accounting assumptions with effects held fixed. Transport requires stable package delivery and no cross-village interference. Hard realized caps and true fixed activation costs require additional inputs.

Read [the JPE-style self-audit](docs/replication-report.qmd), [research status](docs/research-status.md) and [referee reports/responses](docs/referee/). The first genuine ChatGPT Pro report recommended reject at a leading general-interest journal. No report, acceptance, field observation or mechanism identification is manufactured. The requested optional prose screen is documented in [writing audit](docs/writing-audit.md); it uses the released logistic-regression component and is not evidence of human authorship.
