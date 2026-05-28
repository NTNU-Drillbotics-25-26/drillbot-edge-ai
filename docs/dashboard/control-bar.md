---
id: control-bar
title: Control bar features
aliases:
  - control bar
  - mode badge
  - live mode
  - csv mode
  - playback controls
  - connection status
  - fullscreen mode
  - how do I go fullscreen
  - playback speed
  - how do I restart playback
screen: left_monitor
component: control_bar
raw_tags:
  - ControlBar
  - ModeBadge
  - PlaybackControls
  - ConnectionStatus
status: confirmed_on_current_rig
source_type: screen_reference
historic: false
---

The control bar appears at the top of both monitors and provides mode information and controls.

## Common Controls (Both Modes)

| Button | Function |
|--------|----------|
| 🏠 Home | Return to run configuration dialog |
| ⛶ Fullscreen | Toggle fullscreen (F11) |
| ? Info | Show keyboard shortcuts |

**Mode Badge:** Shows "LIVE MODE" or "CSV MODE"

## Live Mode Controls

**Status Indicator:**
- **CONNECTED** (green) - Receiving UDP telemetry
- **DISCONNECTED** (red) - No data from rig

No playback controls are shown in live mode.

## CSV Playback Mode Controls

**Status Indicator:**
- **READY** - File loaded, ready to play
- **PLAYING** - Currently playing
- **PAUSED** - Playback paused
- **COMPLETED** - Reached end of file

**Playback Controls:**
| Control | Function |
|---------|----------|
| Play/Pause | Toggle playback |
| Restart | Start from beginning |
| Speed selector | Choose playback speed |

**Available Speeds:** 0.5x, 1x, 2x, 3x, 5x, 10x, 15x

## Keyboard Shortcuts

- **F11** - Toggle fullscreen
- **ESC** - Exit fullscreen
- **Space** - Play/pause (CSV mode)
