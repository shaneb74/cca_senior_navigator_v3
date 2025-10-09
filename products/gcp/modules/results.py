def run(user_id: str, ctx: dict) -> dict:
    """Run GCP Results."""
    # TODO: Implement results logic
    return {
        "status": "done",
        "outputs": [
            {"label": "Recommendation", "value": "In-Home Care"},
            {"label": "Notes", "value": "Mobility support recommended"}
        ]
    }


def read_state(user_id: str) -> dict:
    return {"status": "new", "progress": 0}


def write_state(user_id: str, patch: dict) -> None:
    pass