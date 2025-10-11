from __future__ import annotations

from typing import Any, Dict, List, Optional

import streamlit as st

Tile = Dict[str, Any]
Rule = Dict[str, Any]


def _get(ctx: Dict[str, Any], dotted: str, default: Any = None) -> Any:
    cur: Any = ctx
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def _ctx() -> Dict[str, Any]:
    ss = st.session_state
    return {
        "role": ss.get("role", "consumer"),
        "person_name": ss.get("person_name", ""),
        "gcp": ss.get("gcp", {}),
        "cost": ss.get("cost", {}),
        "flags": ss.get("flags", {}),
    }


def _passes(rule: Rule, ctx: Dict[str, Any]) -> bool:
    if not rule:
        return True
    if "equals" in rule:
        spec = rule["equals"]
        return _get(ctx, spec["path"]) == spec.get("value")
    if "includes" in rule:
        spec = rule["includes"]
        seq = _get(ctx, spec["path"], []) or []
        return spec.get("value") in seq
    if "exists" in rule:
        spec = rule["exists"]
        return _get(ctx, spec["path"]) is not None
    if "min_progress" in rule:
        spec = rule["min_progress"]
        try:
            return float(_get(ctx, spec["path"], 0)) >= float(spec.get("value", 0))
        except Exception:
            return False
    if "role_in" in rule:
        roles = rule["role_in"] or []
        return _get(ctx, "role") in roles
    return False


def _visible(tile: Tile, ctx: Dict[str, Any]) -> bool:
    if not tile.get("visible", True):
        return False
    rules: List[Rule] = tile.get("visible_when", []) or []
    return all(_passes(r, ctx) for r in rules)


REGISTRY: List[Tile] = [
    {
        "key": "seniorlife_ai",
        "title": "SeniorLife AI",
        "subtitle": "Wellness insights and proactive monitoring tailored for {name}.",
        "cta": "Explore",
        "go": "svc_seniorlife_ai",
        "order": 10,
        "hubs": ["concierge", "waiting_room"],
        "visible_when": [
            {"role_in": ["consumer", "care_partner"]},
            {"min_progress": {"path": "gcp.progress", "value": 0}},
        ],
    },
    {
        "key": "learning_center",
        "title": "Learning Center",
        "subtitle": "Short lessons and guides to stay ahead of every decision.",
        "cta": "Browse library",
        "go": "svc_learning",
        "order": 20,
        "hubs": ["concierge", "learning", "waiting_room"],
        "visible_when": [],
    },
    {
        "key": "care_network",
        "title": "Care Coordination Network",
        "subtitle": "Connect with vetted professionals when you need extra hands.",
        "cta": "Find partners",
        "go": "svc_partners",
        "order": 30,
        "hubs": ["concierge", "trusted_partners", "waiting_room"],
        "visible_when": [
            {"min_progress": {"path": "cost.progress", "value": 0}},
        ],
    },
]


def get_additional_services(hub: str = "concierge", limit: Optional[int] = None) -> List[Tile]:
    ctx = _ctx()
    name = ctx.get("person_name") or "your plan"
    tiles: List[Tile] = []

    for tile in REGISTRY:
        hubs = tile.get("hubs")
        if hubs and hub not in hubs:
            continue
        if not _visible(tile, ctx):
            continue
        tiles.append(
            {
                "key": tile["key"],
                "title": tile["title"],
                "subtitle": (tile.get("subtitle") or "").replace("{name}", name),
                "cta": tile.get("cta", "Open"),
                "go": tile.get("go", tile["key"]),
                "order": tile.get("order", 100),
            }
        )

    tiles.sort(key=lambda x: (x.get("order", 100), x.get("title", "").casefold()))
    if limit is not None:
        tiles = tiles[:limit]
    return tiles
