---
id: run-setup
title: Run setup
aliases:
  - start a run
  - configure a run
  - how do I start drilling
  - how do I configure a run
  - live run
  - previous run
  - replay run
screen: startup_dialog
component: run_configuration
raw_tags:
  - RunSetup
  - StartupDialog
  - RunConfiguration
  - LiveMode
  - CSVMode
  - TargetWaypoints
status: confirmed_on_current_rig
source_type: procedure
historic: false
---

The Run Configuration dialog must be completed before drilling can begin.

**For a live run (new drilling):**
1. Select "Live Run" tab
2. Fill in **Well** name (e.g., "Well-01") - required
3. Fill in **Wellbore** name (e.g., "Bore-A") - required
4. **Filename** - CSV output name (auto-generated if empty)
5. **Description** - Optional notes field
6. **Target waypoints** - Manual input or file upload
7. **Manual run checkbox** - Check for manual mode (no autonomous control)

**Target points:**
- Empty = Manual drilling mode
- With targets = Autonomous directional drilling
- Can be entered manually or uploaded from file

**For reviewing a previous run (CSV Mode):**
1. Select "Previous Run" tab
2. CSV files from `assets/` directory are shown
3. Select a file to replay
4. Use playback controls (0.5x to 15x speed)

**After configuration:**
- Click Start to open the dashboard
- For autonomous drilling, press green Start Autonomous button
- For manual drilling, use joysticks directly
