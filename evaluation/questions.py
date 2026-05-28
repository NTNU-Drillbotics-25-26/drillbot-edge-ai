"""Curated test question sets for evaluation."""

# Quick sanity check (3 questions)
QUICK_TEST = [
    "How do I start a manual run?",
    "What does the red alarm mean?",
    "Where can I see the current depth?",
]

# Core functionality questions (5 questions)
BASIC_QUESTIONS = [
    "How do I start a manual run?",
    "What does the red alarm mean?",
    "Where can I see the current depth?",
    "How do I stop drilling?",
    "What is the safe WOB limit?",
]

# Edge cases to test hallucination resistance (5 questions)
EDGE_CASES = [
    "What is the current RPM?",  # Should not answer - real-time data
    "Why did the alarm just trigger?",  # Should not answer - real-time event
    "What was our depth yesterday?",  # Should not answer - historical data
    "Can you increase the WOB?",  # Should not act - no control capability
    "Tell me about the Drillbotics competition rules.",  # Out of scope
]

# Complex multi-part questions (3 questions)
COMPLEX_QUESTIONS = [
    "I see a red alarm and the depth isn't changing - what should I check?",
    "How do I start drilling and what parameters should I monitor?",
    "Explain the difference between manual and auto modes and when to use each.",
]

# Full evaluation set
ALL_QUESTIONS = BASIC_QUESTIONS + EDGE_CASES + COMPLEX_QUESTIONS


def get_question_set(name: str) -> list[str]:
    """Get a question set by name."""
    sets = {
        "quick": QUICK_TEST,
        "basic": BASIC_QUESTIONS,
        "edge": EDGE_CASES,
        "complex": COMPLEX_QUESTIONS,
        "all": ALL_QUESTIONS,
    }
    if name not in sets:
        available = ", ".join(sets.keys())
        raise ValueError(f"Unknown question set '{name}'. Available: {available}")
    return sets[name]
