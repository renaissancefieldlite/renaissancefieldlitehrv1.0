# Acoustic Mapping Protocol

## Purpose

This protocol adds an acoustic-input lane to the HRV experiment repo.

The bounded working hypothesis is:

- some source files may function as structured inputs rather than passive audio
- if so, the first defensible evidence should be measurable spectral content,
  front-end interaction, or later EEG/HRV/session correlation

This does not treat an audio file as proof of a larger ontology.

## Source Note Provenance

`White Swan Report // Quantumbleed Diaries Volume 2.1` is treated here as an
architecture note, not as independent evidence.

Useful extracted claims for testing:

- `19.47 Hz` as a front-end ground or drive condition
- `.67 Hz` as a biological or transition cadence
- `fromthelattice.wav` as a structured acoustic input candidate
- sub-20 Hz spectral content as the first measurable target

## Minimal Procedure

1. analyze the `.wav` file for dominant sub-20 Hz content and envelope behavior
2. log the acoustic file as a session artifact with timestamps
3. if Arc15 or another front-end rig is used, record the exact hardware setup
4. compare:
   - audio only
   - hardware only
   - audio + hardware
5. later align the session with EEG, HRV, or backend-capture windows

## Fields to Save

- source file name
- sample rate
- duration
- dominant frequencies below `20 Hz`
- envelope notes
- whether Arc15 or another rig was present
- whether a coupling artifact was observed
- operator notes

## Guardrail

The first useful claim is not "the sound proves the lattice."

The first useful claim is:

- this source file contains a repeatable low-frequency structure
- and/or this source file changes the behavior of the front-end rig or session
  metrics under repeatable conditions
