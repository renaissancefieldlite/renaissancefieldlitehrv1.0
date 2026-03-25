# Arc15 Hardware Protocol

## Purpose

This document adds `Arc15 / FG200.67` as an external hardware-front-end lane in
the HRV experiment repo.

The bounded working hypothesis is:

- Arc15 may function as an external front-end or topographic stabilizer
  candidate
- if so, it should produce measurable coupling artifacts before any larger
  architecture claim is made

This repo does not treat external AI commentary about Arc15 as evidence. The
evidence path here is the recorded hardware session itself.

## Reported Configuration

Current reported setup:

- base unit: `FG200.67`
- modified with `15` x `20 mm` spheres on the array
- primary test drive on Arc15: `19.47 Hz`
- secondary generator: `100 Hz`
- measurement path: oscilloscope observation

## Initial Observed Result

The current reported observation is:

- the `100 Hz` generator appeared to affect the reading on the Arc15 channel

That should be logged as a coupling artifact or cross-channel interaction until
better waveform capture is attached.

## Recommended Session Fields

### Hardware Description

- device id
- rig label
- geometry or modification notes
- sphere count
- sphere size
- wiring / grounding notes

### Drive Conditions

- primary generator frequency
- primary amplitude
- secondary generator frequency
- secondary amplitude
- waveform type for each generator
- probe placement

### Oscilloscope Fields

- scope model
- channel assignments
- vertical scale
- horizontal scale
- observed amplitude shift
- observed phase shift
- visible beat or envelope behavior
- whether cross-coupling was observed

### Interpretation Guardrail

Cross-coupling on a scope is not by itself proof of quantum consciousness.
It is evidence that the rig is not isolated and that the front-end may be doing
something measurable worth studying further.

## Next Stronger Step

1. repeat the same Arc15 session with fixed grounding and probe layout
2. save waveform exports if the scope allows it
3. compare:
   - Arc15 only
   - secondary generator only
   - both together
4. log the session in the normalized schema
5. later align that session with EEG, HRV, or backend-capture timelines
