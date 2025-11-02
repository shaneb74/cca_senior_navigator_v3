"""
Regional Cost Data Provider

Provides regional multipliers using precedence system:
ZIP → ZIP3 → State → Default

Data sources:
- config/regional_cost_config.json (existing regional multipliers)
- Fallback to national averages
"""

import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass
class RegionalMultiplier:
    """Regional cost multiplier."""

    multiplier: float
    region_name: str
    precision: str  # "zip", "zip3", "state", or "national"


class RegionalDataProvider:
    """Provides regional cost multipliers with precedence system."""

    _config: dict[str, Any] | None = None
    _config_path = "config/regional_cost_config.json"

    @classmethod
    def _load_config(cls) -> dict[str, Any]:
        """Load regional config once and cache.

        Transforms array-based config into lookup dicts for fast access.
        """
        if cls._config is None:
            config_path = os.path.join(os.getcwd(), cls._config_path)
            if os.path.exists(config_path):
                with open(config_path) as f:
                    raw_config = json.load(f)

                # Transform array-based structure into lookup dicts
                cls._config = {
                    "zip_multipliers": {},
                    "zip3_multipliers": {},
                    "state_multipliers": {},
                    "default_multiplier": raw_config.get("zip_multipliers", {}).get("default", 1.0),
                }

                # Process WA-specific ZIPs first (higher precedence)
                zip_data = raw_config.get("zip_multipliers", {})
                for entry in zip_data.get("by_zip_wa", []):
                    zip_code = entry["zip"]
                    cls._config["zip_multipliers"][zip_code] = {
                        "multiplier": entry["multiplier"],
                        "name": entry.get("notes", zip_code),
                    }

                # Process general ZIPs
                for entry in zip_data.get("by_zip", []):
                    zip_code = entry["zip"]
                    # Don't overwrite WA-specific entries
                    if zip_code not in cls._config["zip_multipliers"]:
                        cls._config["zip_multipliers"][zip_code] = {
                            "multiplier": entry["multiplier"],
                            "name": entry.get("notes", zip_code),
                        }

                # Process WA-specific ZIP3s
                for entry in zip_data.get("by_zip3_wa", []):
                    zip3 = entry["zip3"]
                    cls._config["zip3_multipliers"][zip3] = {
                        "multiplier": entry["multiplier"],
                        "name": entry.get("notes", f"Region {zip3}"),
                    }

                # Process general ZIP3s
                for entry in zip_data.get("by_zip3", []):
                    zip3 = entry["zip3"]
                    # Don't overwrite WA-specific entries
                    if zip3 not in cls._config["zip3_multipliers"]:
                        cls._config["zip3_multipliers"][zip3] = {
                            "multiplier": entry["multiplier"],
                            "name": entry.get("notes", f"Region {zip3}"),
                        }

                # Process states (WA and general combined)
                for entry in zip_data.get("by_state_wa", []):
                    state = entry["state"]
                    cls._config["state_multipliers"][state] = {
                        "multiplier": entry["multiplier"],
                        "name": state,
                    }

                for entry in zip_data.get("by_state", []):
                    state = entry["state"]
                    # Don't overwrite WA-specific entry
                    if state not in cls._config["state_multipliers"]:
                        cls._config["state_multipliers"][state] = {
                            "multiplier": entry["multiplier"],
                            "name": state,
                        }
            else:
                # Fallback to empty config
                cls._config = {
                    "zip_multipliers": {},
                    "zip3_multipliers": {},
                    "state_multipliers": {},
                    "default_multiplier": 1.0,
                }
        return cls._config

    @classmethod
    def get_multiplier(
        cls, zip_code: str | None = None, state: str | None = None
    ) -> RegionalMultiplier:
        """Get regional multiplier using precedence system.

        Precedence (most specific to least specific):
        1. ZIP code (exact match)
        2. ZIP3 (first 3 digits)
        3. State
        4. National default (1.0)

        Args:
            zip_code: 5-digit ZIP code (optional)
            state: 2-letter state code (optional)

        Returns:
            RegionalMultiplier with multiplier value and metadata
        """
        config = cls._load_config()

        # Try ZIP code exact match
        if zip_code and len(zip_code) >= 5:
            zip5 = zip_code[:5]
            if zip5 in config.get("zip_multipliers", {}):
                return RegionalMultiplier(
                    multiplier=config["zip_multipliers"][zip5]["multiplier"],
                    region_name=config["zip_multipliers"][zip5].get("name", zip5),
                    precision="zip",
                )

        # Try ZIP3 (first 3 digits)
        if zip_code and len(zip_code) >= 3:
            zip3 = zip_code[:3]
            if zip3 in config.get("zip3_multipliers", {}):
                return RegionalMultiplier(
                    multiplier=config["zip3_multipliers"][zip3]["multiplier"],
                    region_name=config["zip3_multipliers"][zip3].get("name", f"Region {zip3}"),
                    precision="zip3",
                )

        # Try state
        if state:
            state_upper = state.upper()
            if state_upper in config.get("state_multipliers", {}):
                return RegionalMultiplier(
                    multiplier=config["state_multipliers"][state_upper]["multiplier"],
                    region_name=config["state_multipliers"][state_upper].get("name", state_upper),
                    precision="state",
                )

        # Fallback to national default
        return RegionalMultiplier(
            multiplier=config.get("default_multiplier", 1.0),
            region_name="National Average",
            precision="national",
        )

    @classmethod
    def get_all_states(cls) -> dict[str, str]:
        """Get all available states with names.

        Returns:
            Dict mapping state code to state name
        """
        config = cls._load_config()
        return {
            code: data.get("name", code)
            for code, data in config.get("state_multipliers", {}).items()
        }
