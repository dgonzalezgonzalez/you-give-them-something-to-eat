# Writing and requested detector screen

The manuscript follows Diego's public academic corpus: first-person singular, economic question before mechanism, explicit populations/units, separate reduced forms and mechanisms, conclusions limited by evidence. Codex assistance remains disclosed.

The requested [econ-ai-detector](https://github.com/paulgp/econ-ai-detector) was inspected at commit 11285447a3ccdc300bef25bc0a4a1eb42fd489cb. `code/style_screen.py` uses its official PDF extraction, reference cut, 250-word windows and prose gate for the released logistic-regression component. Scientific estimates do not depend on it.

Current 31-page PDF SHA256: **170d9108814256b209f48a65cf8ac38360a1d4868715de25c7f564620f270bf5**. The LR screen scored **22 of 23** windows; second-highest probability **0.186711** is below **0.33489**. Under the documented AND rule, this necessary-condition failure prevents an ensemble flag for these windows. The neural component was not run; no neural margins or full ensemble score are invented. A non-flag does not establish human authorship.

Historical screens remain recoverable in Git: first submission 0.248438 and second submission 0.230204, each below the same necessary threshold. `output/style-lr.json` records actual PDF/model hashes, versions and all window probabilities. Further PDF edits require a new actual screen.
