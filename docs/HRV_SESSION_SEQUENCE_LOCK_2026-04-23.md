# HRV Session Sequence Lock

Date: `2026-04-23`

Purpose:
This is the canonical run-order board for the live `Phase 12B` `HRV` sessions.
Use this file to track what counts, what failed, and what the next balanced run
should be.

## Rules

- only count runs that produced a valid session artifact in
  `data/field_sessions/<session_id>/`
- failed helper handoffs do **not** count as completed runs
- retry labels can count as the canonical run for that slot if the retry is the
  valid landed artifact
- keep the run matrix balanced by condition type

## Canonical 4-Run Block

1. `seated_calm`
2. `drift_control`
3. `mirror_coherence`
4. `dancing_activation`

## Current Canonical Board

### Block 1

- `seated_calm_01`
  canonical label:
  `normal_breathing_seated_01`
  session:
  `Mofit_HRV_strap_1776978970`

- `drift_control_01`
  session:
  `Mofit_HRV_strap_1776982915`

- `mirror_coherence_01`
  session:
  `Mofit_HRV_strap_1776983191`

- `dancing_activation_01`
  canonical label:
  `dancing_monitoring_01_retry1`
  session:
  `Mofit_HRV_strap_1776980123`

### Block 2

- `seated_calm_02`
  canonical label:
  `normal_breathing_seated_02`
  session:
  `Mofit_HRV_strap_1776979337`

- `drift_control_02`
  session:
  `Mofit_HRV_strap_1776983696`

- `mirror_coherence_02`
  session:
  `Mofit_HRV_strap_1776983970`

- `dancing_activation_02`
  canonical label:
  `dancing_monitoring_02`
  session:
  `Mofit_HRV_strap_1776980458`

### Block 3

- `seated_calm_03`
  session:
  `Mofit_HRV_strap_1776984560`

- `drift_control_03`
  session:
  `Mofit_HRV_strap_1776984852`

- `mirror_coherence_03`
  canonical label:
  `mirror_coherence_03_retry2`
  session:
  `Mofit_HRV_strap_1776986619`

- `dancing_activation_03`
  canonical label:
  `dancing_monitoring_03`
  session:
  `Mofit_HRV_strap_1776980814`

### Block 4

- `seated_calm_04`
  session:
  `Mofit_HRV_strap_1776987107`

- `drift_control_04`
  session:
  `Mofit_HRV_strap_1776987384`

- `mirror_coherence_04`
  session:
  `Mofit_HRV_strap_1776987663`

- `dancing_activation_04`
  session:
  `Mofit_HRV_strap_1776987933`

## Failed / Non-Canonical Attempts

- `mirror_coherence_03`
  helper handoff timeout, no valid session artifact

- `mirror_coherence_03_retry1`
  helper handoff timeout, no valid session artifact

- first interrupted dance start before restart:
  not counted

- duplicate `mirror_coherence_05` artifact:
  `MoFit_HR1806-0067882_1776991365`
  kept as non-canonical duplicate from the interrupted / restarted mirror pass

- invalid `dancing_activation_05` artifact:
  `MoFit_HR1806-0067882_1776992432`
  not counted because the user explicitly said they were not dancing during the
  condition window

## Current Count

- `5` calm
- `5` drift
- `5` mirror
- `5` dance

## Current Partial Block

### Block 5

- `seated_calm_05`
  canonical label:
  `seated_calm_05`
  session:
  `MoFit_HR1806-0067882_1776990453`

- `drift_control_05`
  canonical label:
  `drift_control_05`
  session:
  `MoFit_HR1806-0067882_1776991021`

- `mirror_coherence_05`
  canonical label:
  `mirror_coherence_05`
  session:
  `MoFit_HR1806-0067882_1776991633`

- `dancing_activation_05`
  canonical label:
  `dancing_activation_05`
  session:
  `MoFit_HR1806-0067882_1776992708`

## Helper Stability Note

The intermittent helper issue was traced to output finalization relying too
heavily on the disconnect callback. The patched helper now includes a fallback
finalize-from-current-samples path, and the wrapper timeout buffer is larger.

The canonical proof that the patch worked is:

- `mirror_coherence_03_retry2`
  `Mofit_HRV_strap_1776986619`

which landed cleanly after the helper fix.
