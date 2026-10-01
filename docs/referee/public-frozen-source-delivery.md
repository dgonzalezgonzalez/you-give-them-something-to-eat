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

After that terminal cancellation, the existing job was rerun once with GitHub's job-rerun operation. Job `110461012630` **completed successfully**, using the same source and unchanged workflow. It passed all 130 scientific comparisons, executed an uninterrupted 1,024.9883737564087-second cold master, and produced a 41-page PDF and the 1,753-check population validator. The retry does not alter workflow permissions, the frozen paper or input files. A fresh shallow public clone separately ran the standard-library builder successfully and matched the local source archive/input/PDF hashes; that is packaging verification, not another scientific master run.

## Actual downloaded delivery

Artifact **11177335489** was downloaded: **18,343,090 bytes**, SHA256 `abf081e5ddb4dfce9e00364295731abf88b983aad06db0aca8faee854c999872`, matching GitHub. Actual expiry is **31 October 2026, 16:24:58 UTC**. The inner ZIP is `tmp/hosted-cold/output/public-frozen-source-v0.9.0.zip`, accompanied by its JSON manifest. Its **15,632,930 bytes** hash to `7cc8d9fc77ee33f349363e6b93e5e016b5df34f49f5f6e98a034c2874f25b6db`; its compression bytes differ from the local archive. All **1,983 regular-file payloads** match the frozen Git tar archive exactly, with 2,005 ZIP entries including directories. All nine input hashes and the canonical frozen PDF hash pass. Both ZIP CRC checks pass. No payload difference is inferred from differing compression bytes.

The actual receipt is [hosted-public-source-delivery-83a046e.json](../hosted-public-source-delivery-83a046e.json). The actual retry PDF's title/author text and page count were checked; no new all-page rendered review is attributed to it. Earlier all-page inspection remains attached to the actual source559dd45 artifact. Public input/source delivery now permits the referee to attempt full field execution, but supplies no independent scientific replication, new verdict, acceptance or permanent archive.
