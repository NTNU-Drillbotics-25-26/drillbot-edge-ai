---
id: azimuth-torque-sensor
title: What the azimuth torque sensor measures
aliases:
  - what does the torque sensor measure
  - what does the azimuth torque sensor measure
  - how is azimuth torque measured
  - where is the azimuth torque sensor
  - torque sensor function
  - azimuth torque
screen: left_monitor
component: torque_gauge
raw_tags:
  - AzimuthTorque
  - TorqueSensor
  - Torque
status: confirmed_on_current_rig
source_type: telemetry
historic: false
---

The azimuth torque sensor measures the torque applied to the drill pipe by the azimuth (orientation) system.

**Sensor type:** Hollow torque sensor

**Measurement range:** 0 to 30 Nm (per Phase I 2025 report)

**Purpose:**
- Provides feedback for closed-loop orientation control
- Detects resistance to azimuth rotation
- Identifies rod windup conditions
- Input for stuck bit detection

**How it works:** The sensor is mounted in-line with the azimuth drive system. As the system applies torque to rotate the drill pipe orientation, the sensor measures the reactive torque.

**What high azimuth torque indicates:**
- Rod windup (cable tangled)
- Resistance to orientation change
- Potential stuck condition
