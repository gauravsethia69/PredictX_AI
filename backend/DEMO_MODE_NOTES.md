# PredictX AI - Emergency Two-Machine Demo Mode

## Real baseline used
Healthy motor samples supplied on 2026-08-10:
- Temperature: 25.8-25.9 C (mean 25.85 C)
- Current: 1.33-1.36 A (mean 1.3475 A)
- Sound: 1591-1661 ADC index (mean 1631.5)
- Vibration channel: excluded from health scoring because the current module is unreliable

## Machine 1
- MACHINE-001 remains the real ESP32 feed.
- Raw temperature/current/sound/vibration values are stored unchanged.
- Health/status are recalculated in the backend from temperature/current/sound only.
- Typical supplied readings produce ~96% health and ~4% failure probability.

## Machine 2
- MACHINE-002 is explicitly a demo fault simulation derived from each MACHINE-001 reading.
- Sound = 65% of live value.
- Vibration = 15% of live value.
- Current = 135% of live value.
- Temperature = live value + 2.5 C.
- Health is about 36%, failure risk about 83%, status Critical.
- Diagnosis: mechanical shaft resistance / bearing stall suspected.

## Dynamic behavior
The /api/readings and /api/trends endpoints now derive MACHINE-002 history from the live MACHINE-001 stream. This lets charts continue moving as new ESP32 readings arrive.

## Demo transparency
The frontend/backend should identify MACHINE-002 as a demo fault simulation rather than a second physical sensor package.
