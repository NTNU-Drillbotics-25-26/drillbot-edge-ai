---
id: load-cell-wob
title: How WOB is measured
aliases:
  - how is wob measured
  - what is the load cell used for
  - where is the wob sensor
  - where is the load cell
  - load cell function
  - wob measurement
screen: left_monitor
component: wob_gauge
raw_tags:
  - LoadCell
  - WOB
  - WeightOnBit
status: confirmed_on_current_rig
source_type: telemetry
historic: false
---

WOB (Weight on Bit) is measured using a load cell that detects the force applied to the bit during drilling.

**Sensor type:** Cylindrical load cell

**Location:** Mounted behind the carriage and beneath the nut bracket

**How it works:**
1. Drilling force compresses the load cell
2. The sensor outputs a voltage proportional to force
3. Voltage is converted to force (Newtons or kg)
4. Force is displayed as WOB on the left monitor

**Usage:**
- Real-time monitoring of drilling load
- Input for WOB control loop
- Safety limit enforcement
- Drilling optimization (ROP vs WOB)

**Calibration:** The load cell is zeroed before each run to account for string weight. See WOB zero procedure.
