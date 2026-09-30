# Writing and requested detector screen

The manuscript follows the Diego academic-writing skill and its public corpus notes: sole-author singular voice, question before mechanism, defined estimands, interpretable units, and conclusions bounded by identification and uncertainty. The draft discloses Codex assistance. Detector output is not a claim about who wrote the paper.

The requested [econ-ai-detector](https://github.com/paulgp/econ-ai-detector) was inspected at commit `11285447a3ccdc300bef25bc0a4a1eb42fd489cb`. Its published ensemble uses an AND rule for second-highest window scores. The optional `code/style_screen.py` runs the released logistic-regression component with the official PDF extraction, reference cut, 250-word windows and prose gate.

For the submitted PDF at paper commit `046ce79`, 25 of 26 windows were scored. The second-highest LR probability was **0.248438**, below **0.33489**, the default necessary LR threshold. Therefore the documented AND rule cannot flag this PDF on these windows, regardless of the unmeasured neural margins. The neural component was not run, and no full ensemble scores or authorship conclusions are fabricated. `output/style-lr.json` preserves model/PDF hashes, exact versions and every LR probability. Revisions require rescreening. The screen is optional and does not enter scientific estimates.
