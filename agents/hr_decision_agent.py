# agents/hr_decision_agent.py

def hr_decision_agent(experience_level: str, skill_match: str) -> str:
    """
    Routing logic:
      - If skills match → interview_agent
      - If no skill match but experience is Mid or Senior → escalation_agent
      - Otherwise → rejection_agent
    """

    # 1️⃣ Normalize both values: strip whitespace, trailing punctuation, and lowercase
    lvl = experience_level.strip().rstrip(" .").lower()     # "mid-level."
    match = skill_match.strip().rstrip(" .").lower()        # "no match"

    # 2️⃣ Route
    if match == "match":
        return "interview_agent"
    if lvl in ("mid-level", "senior-level"):
        return "escalation_agent"
    return "rejection_agent"
