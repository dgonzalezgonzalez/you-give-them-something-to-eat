# Public frozen-source artifact delivery

The completed eighth supplement could download a GitHub hosted artifact, but that output archive contains no canonical microdata. A separate transport step now packages the already-public **v0.9.0 / f44a2f6cee1c19f86a6925c4b5685f8c468d58e4** Git source, including all nine inputs, code, dependencies, documentation and LaTeX/PDF. It introduces no new data or scientific analysis. The local source ZIP is 15,632,930 bytes, SHA256 `d03761f2bcf1ab4f1520b007b8d3d811e1012961f32f53604ab0d35dc029beea`; all nine archived input streams equal their frozen Git blobs and the frozen PDF hash is verified. Hosted ZIP bytes/hashes must be measured independently rather than inferred from this local archive.

A proposed new workflow could not be pushed because the existing OAuth connection lacks `workflow` scope. The unpublished workflow was removed; no new permission or change to the existing workflow is made. `code/verify_hosted_run.py` now calls `docs/referee/build_public_frozen_bundle.py` **after** its unchanged scientific comparisons. The builder fetches only the public frozen tag if the existing checkout is shallow, authenticates both annotated-object and resolved-commit IDs, creates the archive/manifest, and places them in the existing cold-output artifact upload path. The new wrapper commit is after the frozen ninth source. The original v0.9.0/source559dd45 correspondence, earlier 130-comparison success and immutable tags remain unchanged.

The builder runs independently with standard-library Python:

```text
python docs/referee/build_public_frozen_bundle.py
```

It writes only ignored `tmp/public-review-v0.9.0`. The hosted wrapper additionally copies `public-frozen-source-v0.9.0.zip` and its JSON manifest into the existing artifact's `output/` directory. Unzip the GitHub artifact, then this inner archive, and read `source/README.md`. The outer artifact retains actual run outputs/receipt; the inner source archive contains the inputs needed for genuine independent execution.

This is public GitHub source delivery, not a local ChatGPT upload, independent replication, a ninth verdict or durable DOI preservation. CI artifacts expire after 30 days. The separately measured completed run/artifact identities and downloaded-byte proof will be recorded only after those actions occur. Existing scientific comparisons and tolerances are unchanged; source packaging errors are reported separately and fail delivery without rewriting scientific execution history.

## Attempt 1 and retry

Actual run `36878350333`, source `83a046e13ba47898a54613309935542489e1cad0`, first job `110423464648` was **completed/cancelled**. Its 20-minute limit expired during slow Ubuntu TeX downloads. Statistical installation passed; public-input verification and the cold master were skipped. Artifact upload failed because no outputs existed. No scientific or packaging result is attributed to this attempt. The earlier successful frozen-source run `36867532625` remains separate.

After that terminal cancellation, the existing job was rerun once with GitHub's job-rerun operation. Latest job `110461012630` is executing the same source and unchanged workflow. Its result and any artifact bytes remain pending. The retry does not alter workflow permissions, the frozen paper or input files. A fresh shallow public clone independently ran the standard-library builder successfully and matched the local source archive/input/PDF hashes; that is packaging verification, not another scientific master run.
