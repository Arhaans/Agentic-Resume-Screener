def interview_agent() -> str:
    """Shortlist for an HR interview."""
    return "Candidate has been shortlisted for an HR interview."

def escalation_agent() -> str:
    """Escalate senior-level but non-matching candidates."""
    return (
        "Candidate has senior-level experience but doesn't match skills; "
        "escalating to recruiter."
    )

def rejection_agent() -> str:
    """Reject candidates who do not qualify."""
    return "Candidate does not meet requirements and has been rejected."
