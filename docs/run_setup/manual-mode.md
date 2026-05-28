---
id: manual-mode
title: How to start a manual run
aliases:
  - manual mode
  - manual run
  - start manual drilling
  - how do I start a manual run
  - how to drill manually
  - manual drilling setup
screen: startup_dialog
component: run_configuration
raw_tags:
  - ManualMode
  - is_manual_run
  - RunConfiguration
status: confirmed_on_current_rig
source_type: procedure
historic: false
---

Manual mode allows the operator to control drilling directly without autonomous steering.

**To start a manual run:**
1. Open the Run Configuration dialog
2. Select "Live Run"
3. Fill in Well and Wellbore names
4. Leave Target Points **empty**
5. Click Start

**Why no target points:** Starting with no target points means the run is treated as manual drilling. The system will not attempt autonomous trajectory control.

**During manual operation:**
- Use joysticks to control hoisting, rotation, and azimuth
- Monitor parameters on the left monitor
- The operator has full control of all drilling parameters

**Switching to manual during autonomous:**
Press the red Disable Drives button on either joystick to stop autonomous drilling and return control to manual mode.
