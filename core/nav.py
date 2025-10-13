import importlib
import json
from typing import Callable, Dict

import streamlit as st

# Registry records
PRODUCTS = {
    "gcp": {"hub": "concierge", "title": "Guided Care Plan", "route": "/product/gcp"},
    "cost_planner": {
        "hub": "concierge",
        "title": "Cost Planner",
        "route": "/products/cost_planner",
    },
    "pfma": {
        "hub": "concierge",
        "title": "Plan with My Advisor",
        "route": "/products/pfma",
    },
}


def _import_callable(path: str) -> Callable:
    mod, fn = path.split(":")
    return getattr(importlib.import_module(mod), fn)


def load_nav(ctx: dict) -> Dict[str, dict]:
    with open("config/nav.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    role = ctx["auth"].get("role", "guest")
    is_auth = ctx["auth"].get("is_authenticated", False)
    flags = {k for k, v in ctx.get("flags", {}).items() if v}

    pages: Dict[str, dict] = {}
    for group in cfg["groups"]:
        for item in group["items"]:
            if item.get("requires_auth") and not is_auth:
                continue
            if item.get("hide_when_auth") and is_auth:
                continue
            if "roles" in item and role not in item["roles"]:
                continue
            if "flags" in item and not set(item["flags"]).issubset(flags):
                continue
            pages[item["key"]] = {
                "label": item["label"],
                "render": _import_callable(item["module"]),
                "group": group["label"],
                "hidden": item.get("hidden", False),
            }
    return pages


def route_to(key: str):
    st.query_params.update({"page": key})
    st.rerun()


def current_route(default: str, pages: Dict[str, dict]) -> str:
    r = st.query_params.get("page", default)
    return r if r in pages else default
