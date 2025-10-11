def run(user_id: str, ctx: dict) -> dict:
    """Run VA Benefits assessment."""
    # TODO: Implement VA benefits logic
    return {
        "status": "done",
        "outputs": [{"label": "Aid & Attendance", "value": "Eligible"}],
    }


def read_state(user_id: str) -> dict:
    """Read VA Benefits state."""
    # TODO: Implement state reading
    return {"status": "new", "progress": 0}


def write_state(user_id: str, patch: dict) -> None:
    """Write VA Benefits state."""
    # TODO: Implement state writing
    pass
