# Counterfactual Experiment Matrix V1.6

V1.6 executes multiple isolated counterfactual cases against one immutable
baseline. Every case receives its own replay, state diff and impact vector.

A case is:

`id + cycle_index + proposal_text`

The matrix deliberately preserves cases independently. It does not rank,
score, select a winner, or infer causality. This makes it suitable for
controlled runtime experiments where different proposal inputs are compared
to the same baseline.
