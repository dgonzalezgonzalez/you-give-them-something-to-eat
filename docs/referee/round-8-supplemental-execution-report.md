## Supplemental execution report — frozen `v0.8.0`

**Commit:** `50c96dcea50b5aac25e5beb0912f54ff26e1b47b`  
**Scientific source:** `aa8667ccde0e00d4c5aa182a89d88b4065a6dda6`

**This remains partial replication.** I completed additional archive-byte verification and quota-region receipt checks, but **did not recover the complete household input or execute the requested full-sample field calculations**. The eighth-round **Reject** recommendation remains unchanged; this is not a new review.

### 1. Retrieval and actual-data status

The hosted artifact was downloaded into the execution environment. Its locally calculated SHA256 matches the published digest:

```text
Artifact: 11155805912
Size:     3,091,917 bytes
SHA256:   47e8bbd931910c64c5ba7ad0595673ae3ba831a5e6ef7c64196703f4804de931
```

**The archive contains outputs, not the canonical household or child microdata.** Downloading it therefore does not establish microdata replication.

For `households.csv`, **two of the required 36 compressed text parts were copied successfully and passed their individual SHA256 checks**. Additional attempted local copies failed their hashes and were excluded. These were unsuccessful transfers into my working files—not evidence that the repository’s originals are corrupted.

The verified parts decompress into an **incomplete prefix**. I parsed its complete CSV rows and checked household-round uniqueness, treatment-indicator consistency, positive available weights, dietary-score bounds, and agreement with the supplied score where all food responses were binary. These checks concern only that prefix. The gzip stream is incomplete, its final checksum is unavailable, and the complete original-file SHA256 has **not** been verified.

The previously reconstructed `costs.csv` was reverified. The remaining canonical files were not reconstructed completely.

### 2. Quota-region membership and certificate replay

Using the **downloaded author-output model constants**, I independently executed the following checks for the quota region with bin floors:

| Component | Completed scope |
|---|---|
| Population membership | Nineteen distinct rational population witnesses; exact unit mass, bin-floor and logical-inequality checks; directed evaluation of the shared exponential constraint |
| Objective values | Recalculated mean and negative six-group-shortfall arm values from the rational probability populations, rather than accepting the supplied arm means alone |
| Lower certificates | Exact-fraction replay of the finite-adversary probability/cost dual for both objectives |
| Upper certificates | Replayed all nine comparator bounds for each objective, including enclosed tangents, feasible linear-program duals, rational allocation feasibility and direction-rounding allowances |

The replay reproduced the quota lower values and the reported upward-rounded upper displays:

| Objective | Replayed lower value | Replayed upper display |
|---|---:|---:|
| Mean HDDS | 5.866228120555938 | **5.868** |
| Negative normalized six-group shortfall | 0.5022426232557802 | **0.503** |

These are **membership and certificate checks conditional on the published model constants**. I did not regenerate those constants from household observations. Membership in this implemented outer region also does not establish that each witness is jointly attainable with the original finite household weights.

**The hybrid region’s membership and complete certificate chains were not replayed in this supplement.** Accordingly, this execution does not independently complete both sides of the quota-versus-hybrid comparison.

My initial replay attempts required corrections to my handling of dictionary-valued allocation shares and string denominators. Those were errors in my local replay script, not discrepancies in the manuscript.

### 3. What remains unexecuted

The following requested tasks remain outstanding:

- Full-sample household counts, block/arm assignment probabilities, dietary scoring, weighted arm means, and the lower/large cost-matched **field** contrast.
- Child-cohort accounting from the complete child input.
- Empirical regeneration of normalizers, observation constants and model constraints; the hybrid certificate chain; the full master and Stata.
- Manuscript-PDF compilation or visual inspection.

I have **not substituted author tables or supplied means for those missing executions**. The incomplete household prefix cannot support the full-population calculations, and the verified output archive cannot replace the missing input reconstruction.

### Execution materials

The :chatgpt-content-reference{index="1"}[supplemental audit bundle](sandbox:/mnt/data/supplemental_v080_execution_audit.zip) contains the replay program, numerical receipts, verified household parts, explicitly labeled partial-prefix checks, and scope documentation. The :chatgpt-content-reference{index="2"}[machine-readable supplemental summary](sandbox:/mnt/data/supplemental_v080/supplemental_summary.json) is available separately.

The seventh/eighth reports retain their original execution limits. This supplement adds actual hosted-archive hashing and quota membership/certificate replay; it **does not convert the earlier synthetic exercises into Rwanda microdata replication**. All adverse findings and the existing **Reject** recommendation remain in place.