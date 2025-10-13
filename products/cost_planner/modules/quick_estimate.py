def run(user_id: str, ctx: dict) -> dict:
    """Run Quick Estimate.
    
    Future enhancement: Full cost estimation calculation.
    Currently returns placeholder for UI development.
    """
    return {
        "status": "done",
        "outputs": [{"label": "Est. monthly cost", "value": "$4,200"}],
    }


def read_state(user_id: str) -> dict:
    return {"status": "new", "progress": 0}


def write_state(user_id: str, patch: dict) -> None:
    pass
