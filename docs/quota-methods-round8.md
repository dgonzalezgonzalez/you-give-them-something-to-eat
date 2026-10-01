# Eighth revision: protection and actual decisions

The field methods and certificate chains remain as described in `quota-methods-round7.md`. This revision changes the presentation and known-population comparison, without replacing empirical input bytes, field estimates, weights, costs, statistical scales or rational proposals. Each field method still has its own conditional event. Their observed minimum is not a jointly protected choice.

## Exact tolerance classification

The rectangular decision keeps its upper loss as a `Fraction`. Counts at or below 0.05 and 0.10 compare that fraction with 1/20 and 1/10 before conversion to floating point. Float summaries remain descriptive Monte Carlo statistics. This repair prevents a rational value near a boundary from being classified according to its rounded binary representation.

## Simple rules and paired uncertainty

No-learning assigns each arm probability one-half. With constant treatment shift delta its exact regret is abs(delta)/2; averaging the four equally weighted shifts yields 9/200 = 0.045. Empirical best compares the HT midpoints of the reported intervals. Both arms have the same denominator and half quota, so the denominator cancels. Unreported [0,1] scores use midpoint 0.5; ties use one-half. This is an explicit rule specification, not a claim about missing potential outcomes. Neither simple rule has a comparable certified loss.

All seven rules receive the same 256 assignments in each of the unchanged 144 cells. For paired regret differences d_r, Monte Carlo SE is sqrt(sum((d_r - dbar)^2)/(R-1)/R), with R=256. Each cell uses a separate declared random stream. An equal-cell mean over C fixed cells has variance sum(cell SE squared)/C squared. These standard errors condition on the catalogue; they do not estimate uncertainty over an empirical population of decision problems, provide multiplicity-adjusted comparisons or validate coverage.

The public CSV retains every per-draw regret. Independent validators recompute means and paired/marginal SEs from those values and check benchmark ties, observed winners, missing-midpoint behavior and the exact no-learning average. The effect table displays quota minus restricted empirical Bernstein, with paired SEs; positive differences favor empirical Bernstein. All effects, reporting patterns, coverage/fallback counts and adverse results remain. No performance-based method tuning is added.

## Inspection and assignment evidence

Round-eight views provide all case summaries and four small draw parts per case, separate from scientific inputs. Their manifest states published LF hashes and CSV-parser scope. Historical field views and their frozen canonical hashes remain unchanged. Eighty small public gzip/base64 text parts reconstruct all nine existing input files exactly; the manifest supplies part and final-byte hashes. These are access conveniences, not independent replication evidence or an alternative source dataset.

The AEA registry was retrieved, while its access-controlled analysis plan was not. The assignment audit records computer randomization, unspecified detailed restrictions and an arm-count inconsistency. Uniform conditional quota assignment remains maintained. No restricted-access request or investigator message was sent.
