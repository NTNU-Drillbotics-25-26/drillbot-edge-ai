---
id: formation-detection
title: Formation detection
aliases:
  - formation predicted
  - predict formation
  - formation prediction
  - what formation am I in
  - can the system detect formation
  - layer change
  - detect formation
  - layer detection
  - lithology detection
screen: right_monitor
component: ml_algorithm
raw_tags:
  - FormationDetection
  - LayerChange
  - LithologyChange
  - MachineLearning
status: confirmed_on_current_rig
source_type: specification
historic: false
---

# Formation Detection

The system can detect layer changes during drilling but does not predict formation in advance.

**Capability:** Real-time detection of when the bit transitions from one rock layer to another.

**Method:** Machine learning algorithm analyzes sensor data patterns including:
- Rate of penetration (ROP) changes
- Torque variations
- MSE (Mechanical Specific Energy) shifts
- Vibration signatures

**What triggers a Lithology Change alarm:**
- Significant change in drilling response
- Transition to different rock properties (harder or softer)

**Limitations:**
- Cannot predict what formation lies ahead
- Detection occurs after transition begins
- Accuracy depends on contrast between layers

**Reference:** For implementation details, see the Phase II 2026 Report.
