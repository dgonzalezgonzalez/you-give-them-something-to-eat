# Small views of the public replication extracts

These CSV parts repeat the original header and partition the rows of the three already-public household/child extracts in `data/input/`. They serve readers whose file interface cannot return a large CSV. They change no scientific inputs and are not additional observations.

`manifest.json` records order, row counts and SHA256 hashes. Keep the first part's header, omit the header from every later part, and concatenate their data rows in manifest order. This reconstructs each original CSV byte for byte, including its line endings. `python code/public_data_views.py --verify` checks that reconstruction against the independently frozen input references. `python code/public_data_views.py` creates the views from those same checked originals.

Data remain **CC BY 4.0**. Attribute McIntosh and Zeitlin (2024), *Cash Versus Kind*, [article DOI](https://doi.org/10.1093/ej/ueae050), and the [corrected Zenodo release](https://doi.org/10.5281/zenodo.15881329). Diego González-González's replication programs select fields, replace linkage identifiers with arbitrary keys, and document transformations. The withdrawn/restricted predecessor is not used.

The household and child records are numeric deidentified research extracts. Their codebooks, missing-value rules, cohort selection, weights and inference limits are in `data/input/analytical-codebook.json` and the repository README. Reading these parts is not evidence of running the full master or independent replication.
