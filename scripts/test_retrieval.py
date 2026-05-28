from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import DEFAULT_DB_PATH, FALLBACK_DB_PATH, get_default_db_path, make_temp_db_path
from app.ingest import rebuild_database
from app.retrieve import retrieve_chunks


TEST_CASES = [
    ("How do I start a manual run?", {"screen": "startup_dialog", "component": "run_configuration"}),
    ("How do I start a directional run?", {"screen": "startup_dialog", "component": "run_configuration"}),
    ("How do I stop autonomous drilling?", {"screen": "right_monitor", "component": "right_joystick"}),
    ("How do I re-enable the drives?", {"screen": "right_monitor", "component": "right_joystick"}),
    ("How do I get vibration feedback?", {"screen": "left_monitor", "component": "left_joystick"}),
    ("How do I receive vibration feedback?", {"screen": "left_monitor", "component": "left_joystick"}),
    ("How do I change vibration source?", {"screen": "left_monitor", "component": "left_joystick"}),
    ("What does Bit lifted mean?", {"screen": "left_monitor", "component": "alarm_panel"}),
    ("Why do I see Stuck bit so often?", {"screen": "left_monitor", "component": "alarm_panel"}),
    ("What is shown on the left monitor?", {"screen": "left_monitor", "component": "dashboard"}),
    ("What is shown on the right monitor?", {"screen": "right_monitor", "component": "dashboard"}),
    ("What is the difference between WOB and WOB setpoint?", {"screen": "left_monitor", "component": "dashboard"}),
    ("What does AutonomousOperationCurrentState mean?", {"screen": "right_monitor", "component": "state_panel"}),
    ("What is Autonomous state?", {"screen": "right_monitor", "component": "state_panel"}),
    ("How do I acknowledge an alarm?", {"screen": "left_monitor", "component": "left_joystick"}),
    ("How do I set RPM setpoint to zero?", {"screen": "left_monitor", "component": "left_joystick"}),
    ("How do I set WOB to zero?", {"screen": "right_monitor", "component": "right_joystick"}),
    ("What does Critical WOB mean?", {"screen": "left_monitor", "component": "alarm_panel"}),
    ("How do I enable drives?", {"screen": "right_monitor", "component": "right_joystick"}),
    ("Which screen shows trend charts?", {"screen": "right_monitor", "component": "dashboard"}),
]


def main() -> None:
    db_path = get_default_db_path()
    # Use a per-run temp DB in sync-backed workspaces so repeated tests do not fight over locks.
    if db_path == FALLBACK_DB_PATH:
        db_path = make_temp_db_path("drillbot_retrieval")
    total = rebuild_database(db_path=db_path)
    print(f"Indexed {total} chunks from {ROOT / 'docs'}")
    print(f"Database path: {db_path}")
    print()

    for i, (question, ui_context) in enumerate(TEST_CASES, start=1):
        print(f"{i:02d}. {question}")
        results = retrieve_chunks(question, ui_context=ui_context, limit=5, db_path=db_path)
        if not results:
            print("  No results")
            print()
            continue

        for rank, chunk in enumerate(results, start=1):
            print(f"  {rank}. {chunk.title} [{chunk.status}] score={chunk.score:.2f}")
        print()


if __name__ == "__main__":
    main()
