# Knowledge Base Authoring Guide

Instructions for creating markdown files that will be ingested into the Drillbotics operator assistant knowledge base.

## Purpose

These markdown files power a retrieval-augmented assistant that helps rig operators during drilling. The assistant answers questions like "How do I start autonomous drilling?" or "What does the stuck bit alarm mean?"

## File Structure

Each markdown file must have YAML front-matter followed by body content:

```markdown
---
id: unique-kebab-case-id
title: Human readable title
aliases:
  - question form alias 1
  - question form alias 2
  - keyword phrase
screen: left_monitor | right_monitor | startup_dialog | null
component: specific_gui_component | null
raw_tags:
  - ExactCodeIdentifier
  - AnotherIdentifier
status: confirmed_on_current_rig
source_type: procedure | alarm_meaning | control_mode | component | telemetry | specification
historic: false
---

Body content here...
```

---

## Required Fields

### `id`
- Unique identifier in kebab-case
- Example: `mode-drill-vertically`, `alarm-stuck-bit`, `right-joystick-controls`

### `title`
- Human-readable title
- Used for display and title-match scoring (+5 points)
- Example: "How to start a manual run"

### `aliases` (CRITICAL FOR RETRIEVAL)
- **3-6 aliases per file**
- Multi-word phrases get +8 points, single words get +4 points
- **Always include full question forms that operators might ask**

**Good aliases:**
```yaml
aliases:
  - what does stuck bit mean           # Full question (+8)
  - why do I see stuck bit             # Full question (+8)
  - how do I fix stuck bit             # Full question (+8)
  - stuck bit alarm                    # Key phrase (+8)
  - bit stuck                          # Variation (+8)
```

**Bad aliases:**
```yaml
aliases:
  - stuck                              # Too generic (+4, matches too much)
  - alarm                              # Too generic (+4)
  - bit                                # Too generic (+4)
```

### `status`
- `confirmed_on_current_rig` - Verified on current hardware
- `not_implemented` - Feature not available
- `historic` - Old information kept for reference

### `source_type`
Choose one:
- `procedure` - How to do something
- `alarm_meaning` - What an alarm means and how to respond
- `control_mode` - Autonomous state behavior
- `component` - Hardware component description
- `telemetry` - Sensor or data definition
- `specification` - System limits or parameters
- `troubleshooting` - Problem diagnosis
- `screen_reference` - GUI screen description
- `competition_rule` - Drillbotics competition rules

### `historic`
- `false` - Current information
- `true` - Kept for reference but may be outdated

---

## Optional But Important Fields

### `screen`
Set when content relates to a specific monitor:
- `left_monitor` - Alarms, gauges, left joystick panel
- `right_monitor` - State panel, trends, trajectory, right joystick
- `startup_dialog` - Run configuration dialog
- `null` - Not screen-specific

### `component`
The specific GUI component or system element:
- `alarm_panel`, `state_panel`, `wob_gauge`, `torque_gauge`
- `left_joystick`, `right_joystick`
- `trend_chart`, `well_progress`
- `run_configuration`
- `bha`, `downhole_sensor`, `drives`

### `raw_tags` (CRITICAL FOR RETRIEVAL)
Exact identifiers from code/GUI that operators might see or search for. Each match gets +6 points.

**Find these in:**
- UDP signal names (e.g., `AutonomousOperationCurrentState`)
- GUI component IDs (e.g., `GaugePanel`, `AlarmPanel`)
- Variable names (e.g., `WOBSetpoint`, `JoystickFeedbackMode`)
- Alarm identifiers (e.g., `stuck_bit`, `critical_wob`)

```yaml
raw_tags:
  - AutonomousOperationCurrentState    # UDP signal name
  - StuckBit                           # PascalCase from code
  - stuck_bit                          # snake_case from alarms
  - WOBSetpoint                        # Variable name
```

---

## Body Content Guidelines

### Length
- **Minimum:** 50 words
- **Ideal:** 80-150 words
- **Maximum:** 300 words (split into multiple files if longer)

### Structure by source_type

#### For `procedure` files:
```markdown
Brief description of what this procedure accomplishes.

**To [do the thing]:**
1. First step (verb-first, imperative)
2. Second step
3. Third step

**Notes:**
- Important consideration
- Edge case handling
```

#### For `alarm_meaning` files:
```markdown
**Meaning:** One sentence explaining what this alarm indicates.

**Trigger condition:** What causes this alarm to appear.

**Actions:**
1. First response action
2. Second action
3. Third action

**Note:** Additional context if needed.
```

#### For `control_mode` files:
```markdown
Brief description of what happens in this autonomous state.

**What happens in [State Name]:**
- First behavior
- Second behavior
- Control parameters

**Transition condition:** What causes exit from this state.

**Next state:** Where the system goes next.
```

#### For `component` files:
```markdown
Brief description of what this component is and does.

**Location:** Where it's physically located or in the GUI.

**Function:**
- Primary purpose
- Secondary functions

**Related components:** What it connects to or interacts with.
```

### Writing Style

1. **Use imperative verbs** for actions: "Press the button", not "You should press"
2. **Be specific**: "Press the green Start Autonomous button" not "Press the button"
3. **Use exact GUI labels**: Match what the operator sees on screen
4. **Front-load key information**: Answer the question in the first sentence
5. **Use markdown tables** for button mappings, parameters, states
6. **Use bullet lists** for actions, causes, components

---

## How to Extract Information from GUI Code

### Finding Aliases
1. Look at button labels, tooltips, status messages
2. Think: "What question would an operator ask about this?"
3. Include variations: "how do I", "what does", "why is", "where can I"

### Finding raw_tags
1. Search for signal names in UDP/networking code
2. Look for enum values and constants
3. Find component IDs in UI code
4. Check alarm/event identifiers

### Finding screen/component
1. Check which panel or monitor displays this element
2. Look at the component hierarchy in the GUI code
3. Map features to left (alarms, gauges) vs right (state, trends, trajectory)

---

## Examples

### Good Example (Procedure)
```markdown
---
id: manual-mode
title: How to start a manual run
aliases:
  - how do I start a manual run
  - how to drill manually
  - manual drilling setup
  - manual mode
  - start manual drilling
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
```

### Good Example (Alarm)
```markdown
---
id: stuck-bit
title: Stuck bit behavior
aliases:
  - stuck bit
  - what does stuck bit mean
  - why do I see stuck bit
  - stuck bit keeps appearing
  - bit is stuck
  - what to do when bit is stuck
screen: left_monitor
component: alarm_panel
raw_tags:
  - StuckBit
  - stuck_bit
  - TorqueMonitoring
status: confirmed_on_current_rig
source_type: alarm_meaning
historic: false
---

Stuck bit occurs when pipe rotation is blocked or restricted.

**Meaning:** High torque with low RPM indicates the bit cannot rotate freely.

**Trigger condition:** Torque exceeds threshold while RPM drops below expected value.

**Actions:**
1. Stop drilling immediately
2. Reduce WOB to zero
3. Hoist the bit slightly
4. Attempt to free by working the pipe

**In autonomous mode:** The system handles stuck bit automatically by hoisting and re-entering. Occasional alarms are normal.

**If stuck bit appears frequently:** Check for formation change, inadequate flow, or bit wear.
```

### Bad Example (Don't Do This)
```markdown
---
id: stuck
title: Stuck
aliases:
  - stuck        # Too generic
  - alarm        # Too generic
status: confirmed_on_current_rig
source_type: alarm_meaning
historic: false
---

Stuck bit is when the bit gets stuck.   # Too short, no structure, no useful detail
```

---

## File Organization

Place files in the appropriate subdirectory:

```
docs/
├── alarms/          # Alarm meanings and troubleshooting
├── modes/           # Autonomous state descriptions
├── safety/          # Safety procedures and limits
├── sensors/         # Sensor descriptions and data
├── system/          # System architecture and components
├── dashboard/       # GUI screen descriptions
├── joysticks/       # Joystick controls and functions
├── run_setup/       # Run configuration procedures
├── telemetry/       # Data signals and definitions
└── competition/     # Drillbotics competition rules
```

---

## Checklist Before Submitting

- [ ] `id` is unique and kebab-case
- [ ] `title` clearly describes the content
- [ ] 3-6 `aliases` including full question forms
- [ ] `raw_tags` include exact code/GUI identifiers
- [ ] `screen` and `component` set if GUI-related
- [ ] Body is 50-150 words with clear structure
- [ ] Procedures have numbered action steps
- [ ] First sentence answers the likely question
- [ ] Uses exact GUI labels and button names
- [ ] No redundancy with existing files (check first!)

---

## Scoring System Reference

The retrieval system scores documents using:

| Factor | Points | Notes |
|--------|--------|-------|
| BM25 text match | Variable | Base relevance score |
| Multi-word alias match | +8 | Phrase found in query |
| Single-word alias match | +4 | Word found in query |
| Raw tag match | +6 | Exact identifier match |
| Title match | +5 | Title words in query |
| UI context (screen/component) | 55% weight | Boosts relevant screen docs |

**Optimization strategy:**
1. Write aliases as full questions operators ask
2. Include exact identifiers in raw_tags
3. Set screen/component for all GUI-related content
4. Put key terms in title and first sentence
