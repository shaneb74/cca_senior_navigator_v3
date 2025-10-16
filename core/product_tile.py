from __future__ import annotations

import html as _html
import os
from html import escape as H
from typing import Any, Dict, List, Mapping, Optional

import streamlit as st

from core.events import log_event

try:  # pragma: no cover - optional import in tests
    from layout import static_url
except Exception:  # pragma: no cover
    static_url = None


SN_DEBUG_TILES = os.environ.get("SN_DEBUG_TILES", "0") == "1"


def html_escape(s: str) -> str:
    return _html.escape(str(s), quote=True)


def _normalize_img(path: Optional[str]) -> str:
    if not path:
        return ""
    s = path.strip().lstrip("/")
    if not s:
        return ""
    if s.startswith("static/"):
        return s
    if s.startswith("images/"):
        return f"static/{s}"
    return f"static/images/{s}"


def _resolve_img(img: Optional[str]) -> tuple[str, str]:
    canonical = _normalize_img(img)
    if not canonical:
        return "", ""
    if static_url:
        try:
            url = static_url(canonical) or ""
            if url:
                return url, canonical
        except Exception:
            pass
    return f"/{canonical}", canonical


def _get_progress(state: Mapping[str, Any], key: str) -> float:
    try:
        return float(state.get(key, {}).get("progress", 0))
    except Exception:
        return 0.0


def _evaluate_requirement(req: str, state: Mapping[str, Any]) -> bool:
    """
    Supported patterns:
      'gcp:complete'           -> MCIP.is_product_complete("gcp") OR progress == 100
      'cost:>=50'              -> progress >= 50
      'pfma:scheduled'         -> MCIP appointment OR state['pfma']['appointment']
      'care_tier:in_home|al|mc|mc_ha'
      'auth:required'          -> state['auth']['is_authenticated'] is True
    
    NOTE: Checks MCIP first for modern products, falls back to legacy session state.
    """
    if ":" not in req:
        return False

    key, spec = req.split(":", 1)
    key = key.strip()
    spec = spec.strip()

    # Check product completion/progress
    if key in ("gcp", "cost", "pfma", "cost_planner", "pfma_v2", "cost_v2"):
        # Map keys to MCIP product IDs
        product_map = {
            "gcp": "gcp",
            "cost": "cost_planner",
            "cost_planner": "cost_planner",
            "cost_v2": "cost_planner",
            "pfma": "pfma_v2",
            "pfma_v2": "pfma_v2"
        }
        
        if spec == "complete":
            # FIRST: Check MCIP (authoritative source for modern products)
            try:
                from core.mcip import MCIP
                product_id = product_map.get(key, key)
                if MCIP.is_product_complete(product_id):
                    return True
            except Exception:
                pass  # Fall back to legacy check
            
            # FALLBACK: Check legacy session state (for old products or during migration)
            prog = _get_progress(state, key)
            return prog >= 100
        
        if spec.startswith(">="):
            # Partial progress checks (MCIP doesn't track these, use legacy state)
            prog = _get_progress(state, key)
            try:
                threshold = float(spec[2:].strip())
                return prog >= threshold
            except Exception:
                return False
        
        if spec == "scheduled":
            # FIRST: Check MCIP appointment
            if key in ("pfma", "pfma_v2"):
                try:
                    from core.mcip import MCIP
                    appt = MCIP.get_advisor_appointment()
                    if appt and appt.scheduled:
                        return True
                except Exception:
                    pass
            
            # FALLBACK: Check legacy session state
            return state.get(key, {}).get("appointment") == "scheduled"
        
        return False

    if key == "care_tier":
        current = str(state.get("gcp", {}).get("care_tier", "")).lower()
        return current == spec.lower()

    if key == "auth":
        return spec == "required" and bool(state.get("auth", {}).get("is_authenticated", False))

    if key == "flag":
        gcp_flags = state.get("gcp", {}).get("flags", {}) or {}
        opts = [s.strip() for s in spec.split("|") if s.strip()]
        if not opts:
            return False
        return any(bool(gcp_flags.get(opt, False)) for opt in opts)

    return False


def tile_is_unlocked(tile: "BaseTile", state: Mapping[str, Any]) -> bool:
    reqs = getattr(tile, "unlock_requires", []) or []
    return all(_evaluate_requirement(r, state) for r in reqs)


def tile_requirements_satisfied(
    unlock_requires: Optional[List[str]], state: Mapping[str, Any]
) -> bool:
    reqs = unlock_requires or []
    return all(_evaluate_requirement(r, state) for r in reqs)


def _render_badges(badges: List[Any]) -> str:
    out: List[str] = []
    for badge in badges:
        if isinstance(badge, str):
            out.append(f'<span class="badge badge--neutral">{html_escape(badge)}</span>')
        elif isinstance(badge, dict):
            badge_dict: Dict[str, Any] = badge
            label = html_escape(badge_dict.get("label", ""))
            tone = badge_dict.get("tone")
            cls = "badge"
            if tone:
                cls = f"{cls} badge--{html_escape(str(tone))}"
            out.append(f'<span class="{cls}">{label}</span>')
    return "".join(out)


class BaseTile:
    def __init__(self, **kwargs: Any) -> None:
        self.key = kwargs.get("key", "")
        self.title = kwargs.get("title", "")
        self.desc = kwargs.get("desc")
        self.blurb = kwargs.get("blurb")
        self.badge_text = kwargs.get("badge_text")
        self.meta_lines: List[str] = kwargs.get("meta_lines") or []
        self.primary_label = kwargs.get("primary_label")
        primary_route = kwargs.get("primary_route")
        primary_go = kwargs.get("primary_go")
        self.primary_route = primary_route or None
        self.primary_go = primary_go or None
        self.secondary_label = kwargs.get("secondary_label")
        self.secondary_route = kwargs.get("secondary_route")
        self.secondary_go = kwargs.get("secondary_go")
        # None means “no linear status”; otherwise numeric progress
        self.progress: Optional[float] = kwargs.get(
            "progress", 0 if kwargs.get("progress") is not None else None
        )
        self.status_text: Optional[str] = kwargs.get("status_text")
        self.order = int(kwargs.get("order", 100))
        self.visible = bool(kwargs.get("visible", True))
        self.locked = bool(kwargs.get("locked", False))
        self.variant = kwargs.get("variant")  # brand|success|warn|teal|violet|...
        self.bg_from = kwargs.get("bg_from")
        self.bg_to = kwargs.get("bg_to")
        self.border_color = kwargs.get("border_color")
        self.image_square: Optional[str] = kwargs.get("image_square")
        self.lock_msg: Optional[str] = kwargs.get("lock_msg")
        self.unlock_requires: List[str] = kwargs.get("unlock_requires") or []
        self.recommended_order: Optional[int] = kwargs.get("recommended_order")
        self.recommended_total: Optional[int] = kwargs.get("recommended_total")
        self.recommended_in_hub: Optional[str] = kwargs.get("recommended_in_hub")
        self.recommended_reason: Optional[str] = kwargs.get("recommended_reason")
        self.cta_tooltip: Optional[str] = kwargs.get("cta_tooltip")
        self.is_next_step: bool = kwargs.get("is_next_step", False)  # NEW: for MCIP gradient
        self.desc_html: Optional[str] = kwargs.get("desc_html")  # NEW: for raw HTML in desc
        raw_badges = kwargs.get("badges") or []
        self.badges: List[Any] = raw_badges

    def _style(self) -> str:
        styles: List[str] = []
        if self.bg_from:
            styles.append(f"--tile-from:{self.bg_from}")
        if self.bg_to:
            styles.append(f"--tile-to:{self.bg_to}")
        if self.border_color:
            styles.append(f"--tile-border:{self.border_color}")
        return f' style="{";".join(styles)}"' if styles else ""

    def _variant(self) -> str:
        return f' data-variant="{self.variant}"' if self.variant else ""

    def _meta(self) -> str:
        if not self.meta_lines:
            return ""
        items = "".join(f"<span>{html_escape(line)}</span>" for line in self.meta_lines)
        return f'<div class="tile-meta">{items}</div>'

    def _status(self) -> str:
        if self.status_text is not None:
            return f'<div class="dashboard-status">{html_escape(self.status_text)}</div>'
        if self.progress is None:
            return ""
        try:
            value = float(self.progress or 0)
        except Exception:
            value = 0.0
        if self.locked:
            return '<div class="dashboard-status">Locked</div>'
        if value >= 100:
            return '<div class="dashboard-status">Complete</div>'
        if value > 0:
            return '<div class="dashboard-status">In progress</div>'
        return '<div class="dashboard-status">New</div>'

    def _actions(self) -> str:
        buttons: List[str] = []
        primary_label = self._resolved_primary_label()
        tooltip_attr = f' title="{html_escape(self.cta_tooltip)}"' if self.cta_tooltip else ""
        if primary_label:
            if self.locked:
                lock_title = html_escape(self.lock_msg) if self.lock_msg else ""
                title_attr = f' title="{lock_title}"' if lock_title else ""
                buttons.append(
                    f'<span class="dashboard-cta dashboard-cta--primary is-disabled" aria-disabled="true"{title_attr}>'
                    f"{html_escape(primary_label)}</span>"
                )
            else:
                href = html_escape(self._primary_href())
                buttons.append(
                    f'<a class="dashboard-cta dashboard-cta--primary" href="{href}" target="_self"{tooltip_attr}>'
                    f"{html_escape(primary_label)}</a>"
                )
        if self.secondary_label:
            if self.locked:
                buttons.append(
                    '<span class="dashboard-cta dashboard-cta--ghost is-disabled" aria-disabled="true">'
                    f"{html_escape(self.secondary_label)}</span>"
                )
            else:
                href = html_escape(self._secondary_href())
                buttons.append(
                    f'<a class="dashboard-cta dashboard-cta--ghost" href="{href}" target="_self">'
                    f"{html_escape(self.secondary_label)}</a>"
                )
        return f'<div class="tile-actions">{"".join(buttons)}</div>' if buttons else ""

    def _primary_href(self) -> str:
        href = ""
        if self.primary_route:
            href = self.primary_route
        elif self.primary_go:
            href = f"?page={self.primary_go}"
        else:
            return "#"
        
        # CRITICAL: Preserve UID in href to maintain session across navigation
        return self._add_uid_to_href(href)

    def _secondary_href(self) -> str:
        href = ""
        if self.secondary_route:
            href = self.secondary_route
        elif self.secondary_go:
            href = f"?page={self.secondary_go}"
        else:
            return "#"
        
        # CRITICAL: Preserve UID in href to maintain session across navigation
        return self._add_uid_to_href(href)
    
    def _add_uid_to_href(self, href: str) -> str:
        """Add current UID to href to preserve session across navigation."""
        if not href or href == "#":
            return href
        
        # Get current UID from session_state
        uid = None
        if 'anonymous_uid' in st.session_state:
            uid = st.session_state['anonymous_uid']
        elif 'auth' in st.session_state and st.session_state['auth'].get('user_id'):
            uid = st.session_state['auth']['user_id']
        
        if not uid:
            return href
        
        # Add uid to query string
        separator = '&' if '?' in href else '?'
        return f"{href}{separator}uid={uid}"

    def _resolved_primary_label(self) -> Optional[str]:
        # If primary_label is explicitly set, use it (even if None)
        if self.primary_label:
            return str(self.primary_label)
        
        # If no route is set, don't show a button
        if not self.primary_route and not self.primary_go:
            return None
        
        # Otherwise, determine button text from progress
        try:
            value = float(self.progress or 0)
        except Exception:
            value = 0.0
        if value <= 0:
            return "Start"
        if value >= 100:
            return "Open"
        return "Resume progress"

    def _pills(self) -> str:
        pills: List[Any] = []
        if self.badge_text:
            pills.append({"label": self.badge_text, "tone": "brand"})
        pills.extend(self.badges)
        badge_markup = _render_badges(pills)
        return f'<div class="dashboard-badges">{badge_markup}</div>' if badge_markup else ""

    def _state_class(self) -> str:
        if self.locked:
            return "locked"
        try:
            value = float(self.progress or 0)
        except Exception:
            value = 0.0
        if value >= 100:
            return "done"
        if value > 0:
            return "doing"
        return "new"


class ProductTileHub(BaseTile):
    def render_html(self) -> str:
        if not self.visible:
            return ""

        out: List[str] = []
        classes = ["ptile", "dashboard-card", f"tile--{self._state_class()}"]
        if self.variant:
            classes.append(f"tile--{self.variant}")
        
        # Add "recommended" class for MCIP gradient
        # Conditions: is the current next step, not complete, not FAQ tile
        is_recommended = (
            self.is_next_step and 
            float(self.progress or 0) < 100 and
            getattr(self, "key", "") != "faqs"
        )
        if is_recommended:
            classes.append("tile--recommended")
        
        out.append(f'<div class="{" ".join(classes)}"{self._variant()}{self._style()}>')

        lock_icon = ""
        if self.locked:
            lock_label = f"Locked: {self.lock_msg}" if self.lock_msg else "Locked"
            lock_icon = f'<span class="icon-lock" aria-label="{html_escape(lock_label)}"></span>'
            out.append(lock_icon)
        
        # Add completion badge for done tiles (not FAQ)
        is_complete = float(self.progress or 0) >= 100
        is_faq = getattr(self, "key", "") == "faqs"
        if is_complete and not is_faq:
            done_url, _ = _resolve_img("static/images/done.png")
            if done_url:
                out.append(
                    f'<div class="tile-completion-badge" aria-label="Complete">'
                    f'<img src="{done_url}" alt="Complete" />'
                    '</div>'
                )

        out.append('<div class="ptile__head">')
        logo_src, logo_path = _resolve_img(getattr(self, "image_square", None))
        if logo_src:
            debug_html = (
                f"<div class='tile-logo-debug'>img: {H(logo_path)}</div>" if SN_DEBUG_TILES else ""
            )
            out.append(
                '<div class="tile-logo" aria-hidden="true" '
                f"style=\"background-image:url('{logo_src}')\">"
                "</div>"
                f"{debug_html}"
            )
        out.append('<div class="ptile__heading">')

        step_chip = ""
        if self.recommended_order is not None:
            step_text = f"Step {self.recommended_order}"
            if self.recommended_total:
                step_text += f" of {self.recommended_total}"
            step_aria = f"Recommended step {self.recommended_order}"
            if self.recommended_total:
                step_aria += f" of {self.recommended_total}"
            step_chip = f'<div class="badge badge--step" aria-label="{html_escape(step_aria)}">{html_escape(step_text)}</div>'

        out.append('<div class="ptile__title-row">')
        out.append(f'<h3 class="tile-title">{html_escape(self.title)}</h3>')
        out.append(self._status())
        if step_chip:
            out.append(step_chip)
        out.append("</div>")

        pills = self._pills()
        if pills:
            out.append(pills)
        out.append("</div>")  # /heading
        out.append("</div>")  # /head

        if self.desc_html:
            # Allow raw HTML for special formatting (e.g., prominent recommendations)
            out.append(f'<div class="tile-subtitle">{self.desc_html}</div>')
        elif self.desc:
            out.append(f'<p class="tile-subtitle">{html_escape(self.desc)}</p>')
        if self.blurb:
            out.append(f'<p class="dashboard-description">{html_escape(self.blurb)}</p>')
        if self.recommended_reason:
            out.append(
                f'<div class="tile-status-note">{html_escape(self.recommended_reason)}</div>'
            )

        meta = self._meta()
        if meta:
            out.append(meta)
        lock_msg_html = ""
        if self.locked and self.lock_msg:
            lock_msg_html = f'<div class="tile-lock-msg">{html_escape(self.lock_msg)}</div>'
        actions_html = self._actions()
        if actions_html:
            out.append(actions_html)
        if lock_msg_html:
            out.append(lock_msg_html)
        out.append("</div>")  # /card

        try:
            log_event(
                "tile.rendered",
                {
                    "id": getattr(self, "key", None),
                    "locked": bool(self.locked),
                    "progress": float(self.progress or 0),
                    "recommended_order": self.recommended_order,
                },
            )
        except Exception:
            pass

        return "".join(out)

    def render(self) -> None:
        html = self.render_html()
        if html:
            st.markdown(html, unsafe_allow_html=True)


class ModuleTileCompact(BaseTile):
    def render_html(self) -> str:
        if not self.visible:
            return ""
        out: List[str] = []
        out.append(f'<div class="mtile dashboard-card"{self._variant()}{self._style()}>')
        out.append(
            '<div class="tile-row">'
            f'<h3 class="tile-title">{html_escape(self.title)}</h3>'
            f"{self._status()}"
            "</div>"
        )
        if self.blurb:
            out.append(f'<p class="dashboard-description">{html_escape(self.blurb)}</p>')
        meta = self._meta()
        if meta:
            out.append(meta)
        out.append(self._actions())
        out.append("</div>")
        return "".join(out)

    def render(self) -> None:
        html = self.render_html()
        if html:
            st.markdown(html, unsafe_allow_html=True)


__all__ = [
    "ProductTileHub",
    "ModuleTileCompact",
    "tile_is_unlocked",
    "tile_requirements_satisfied",
]
