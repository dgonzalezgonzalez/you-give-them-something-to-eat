# Small public views of the fifth-revision quota receipt

These are lossless views of `output/quota-loss-bound.json`, generated and round-trip checked by `docs/referee/build_round5_views.py`. They are public inspection aliases, not scientific inputs, new observations, household replication or a referee's execution. The canonical method and manuscript at scientific commit `fd958c196d6b68a36430890ca28c30e349031dff` passed the fresh hosted full master/PDF and 95/95 comparison checks. Later review documentation does not change that code/paper/canonical result.

Start with [summary.json](summary.json), then [the manifest](manifest.json) for exact view hashes/byte sizes. Each view is at most 15,161 bytes. The main script remains `code/quota_allocation.py`; directed support/HT arithmetic is `code/quota_arithmetic.py`; block moments are `code/quota_moments.py`. The coverage and numerical arguments are in `docs/quota-inference.md` and the paper appendix. The original scientific extract bytes are unchanged.

The six coherent-distribution models contain exact stored C/intercept/A/b/floor constants:

- [Control](model-Control.json)
- [Gikuriro](model-Gikuriro.json)
- [Lower cash](model-Lower.json)
- [Middle cash](model-Middle.json)
- [Upper cash](model-Upper.json)
- [Large cash](model-Large.json)

Each objective's nine supporting witnesses record tau, six convex tangent candidates/gradients, interval error allowances, independently feasible inequality/equality LP duals and direction-rounding bounds. For example, [mean against middle cash](witness-mean-Middle.json) supplies the binding reported mean upper bound. [Six-group shortfall against middle cash](witness-shortfall_6-Middle.json) supplies its binding shortfall bound. All eighteen filenames and support values are indexed in summary.json and manifest.json. A reader can replay them with the public arithmetic module without trusting a convex optimizer's success flag.

The displayed 5.868-group and 0.503-unit values round the verified bounds upward. The proposals are approximate exchange-search results, not certified minimax optima. `output/quota-search.json` records a fresh optional production-region search: 387.29 seconds, mean upper diagnostic 5.8671824456 / gap 0.00019747 and shortfall 0.5025619383 / gap 0.00013635. This separate floating search does not replace the enclosed canonical verification. Its output can differ from the earlier search that selected the stored proposals.

All coverage is conditional on the stated quota/independent-block/fixed-weight/potential-diet assumptions. The new standalone event is not intersected with the earlier nominal 95% regions. Bound width, operational objectives, original assignment-law verification and leading-journal economic contribution remain unresolved. No fifth referee recommendation has been received.
