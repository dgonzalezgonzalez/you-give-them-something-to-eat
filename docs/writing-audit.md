# Writing and requested detector screen

The manuscript follows Diego's public academic corpus: singular author voice, question before mechanism, explicit estimands/units and conclusions limited by evidence. Codex assistance is disclosed. The screen is not an authorship claim.

The requested [econ-ai-detector](https://github.com/paulgp/econ-ai-detector) was inspected at commit 11285447a3ccdc300bef25bc0a4a1eb42fd489cb. code/style_screen.py uses its official PDF extraction, reference cut, 250-word windows and prose gate for the released LR component. Scientific estimates do not depend on it.

First-submission commit 046ce79 had a second-highest LR probability 0.248438 below the necessary threshold 0.33489 (historical result retained in Git). The revised 32-page PDF has 35 scored windows of 36, second-highest LR **0.230204**, below **0.33489**. PDF SHA256 **113e38748b8bd034bcb648dba9be77b8b03bdc40538488adcf32bac240e3ed05**. The documented ensemble uses an AND condition, so it cannot flag this PDF on these windows when its necessary LR condition fails. The neural component was not run; no full ensemble scores, neural margins or proof of human authorship are inferred.

output/style-lr.json records actual model/PDF hashes, package versions and window probabilities. Further substantive revisions require rescreening, not a promised non-flag.
