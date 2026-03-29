# Repeated Capture Findings

This note publishes the current repeated-capture state of HRV1.0 before the
work branches into later experiment repos.

The point of this document is not to overstate what the repo proves. The point
is to lock in what the current artifacts already show, how they relate to the
Step 2 hardware-derived model, and which comparison set should be treated as
the cleanest launch point for Experiment 1.

## Why Publish This Now

HRV1.0 already has more than a synthetic detector and one backend screenshot.
It now has:

- a repeated short-window hardware proxy in
  [`data/derived_noise/sample_noise_profile.json`](../data/derived_noise/sample_noise_profile.json)
- repeated local Aer baselines
- repeated IBM `ibm_fez` captures
- comparison reports that tie those repeated captures back to the Step 2 proxy

That is enough to publish a current state before opening the next experiment
branch.

## Step 2 Reference

Current hardware-derived model reference:

- `mean_coherence_proxy = 0.9553175210847371`
- `mean_short_window_coherence = 0.9823794452339145`
- `mean_session_stability = 0.976366014174089`

Those values define the local benchmark the repeated capture batches are being
compared against.

## Published Comparison Sets

### 1. Fresh Small-Batch Check

Artifact:

- [`data/derived_noise/fresh_batch_comparison.json`](../data/derived_noise/fresh_batch_comparison.json)

Summary:

- Aer: `3` captures, mean target-subspace probability `1.000000`
- IBM: `2` captures, mean target-subspace probability `0.984375`
- IBM mean off-target probability: `0.015625`
- Aer vs IBM target-subspace comparison: `p = 0.500000`

Read:

This was the first refreshed repeated-capture check after the runtime and model
updates. It is small, but it shows the backend lane staying close to the Step 2
proxy without the older timescale mismatch.

### 2. Ten-Vs-Ten Baseline

Artifact:

- [`data/derived_noise/ten_vs_ten_comparison.json`](../data/derived_noise/ten_vs_ten_comparison.json)

Summary:

- Aer: `10` captures, mean target-subspace probability `1.000000`
- IBM: `10` captures, mean target-subspace probability `0.968750`
- IBM mean off-target probability `0.031250`
- target-subspace difference: `p = 0.014956`
- off-target difference: `p = 0.014956`
- bell-imbalance difference: `p = 0.179198`

Read:

This is the cleanest repeated baseline in the repo right now. The Aer side is
idealized and lands exactly in the target subspace on every saved capture. The
IBM side remains close to the Step 2 proxy but shows the small off-target spill
that the hardware-derived model was built to anticipate. The fact that the
imbalance difference is not significant at this size matters because it means
the main visible separation here is target/off-target leakage, not a collapse
of the Bell-pair balance inside the target subspace.

### 3. Mixed Historical Snapshot

Artifact:

- [`data/derived_noise/current_capture_comparison.json`](../data/derived_noise/current_capture_comparison.json)

Summary:

- Aer: `5` captures, mean target-subspace probability `0.899805`
- IBM: `2` captures, mean target-subspace probability `1.000000`
- Aer vs IBM target-subspace comparison: `p = 0.373901`

Read:

This report is still useful, but it is not the cleanest baseline because it
includes older Aer artifacts that were saved before the refreshed repeated-batch
flow settled down. It should be read as a historical mixed snapshot, not as the
best current baseline.

## Current Correlation Back To Previous Test Work

The current repeated-capture findings line up with the earlier repo sequence in
a straightforward way:

1. Step 1 established that the detector path can lock onto a seeded target band
   near `0.67 Hz` in synthetic data.
2. Step 2 replaced the older long-lifetime collapse model with a repeated
   short-window backend proxy shaped by calibration-style parameters.
3. Step 3 now has repeated IBM captures that stay close to that Step 2 proxy,
   while still showing a measurable gap from idealized Aer behavior.

That is the correlation worth publishing. The repo is no longer just a concept
demo. It now contains a synthetic detector lane, a hardware-shaped proxy lane,
and repeated backend artifacts that can be compared back against the proxy.

## Recommended Read Of The Current State

- The strongest current baseline is `ten_vs_ten_comparison.json`.
- The Step 2 proxy is holding up better against IBM than the older mixed
  artifacts did.
- The main present difference between Aer and IBM is leakage/off-target
  behavior, not total loss of target-subspace structure.
- HRV1.0 is ready to publish as the foundation layer before branching into the
  next experiment repo.

## Recommended Next Step

Publish HRV1.0 in its current form as the seed layer, with the repeated-capture
comparison state made explicit.

Then roll forward into Experiment 1 using the ten-vs-ten baseline as the
starting comparison set rather than rebuilding the foundation story again from
scratch.
