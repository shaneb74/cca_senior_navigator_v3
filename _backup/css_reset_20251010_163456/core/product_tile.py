from __future__ import annotations

import html as _html
from typing import Any, List, Optional

import streamlit as st


def html_escape(s: str) -> str:
    return _html.escape(str(s), quote=True)


class BaseTile:
    def __init__(self, **kwargs: Any) -> None:
        self.key = kwargs.get("key", "")
        self.title = kwargs.get("title", "")
        self.desc = kwargs.get("desc")
        self.blurb = kwargs.get("blurb")
        self.badge_text = kwargs.get("badge_text")
        self.badges: List[str] = kwargs.get("badges") or []
        self.meta_lines: List[str] = kwargs.get("meta_lines") or []
        self.primary_label = kwargs.get("primary_label", "Open")
        self.primary_go = kwargs.get("primary_go", "#")
        self.secondary_label = kwargs.get("secondary_label")
        self.secondary_go = kwargs.get("secondary_go", "#")
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
        return f'<div class="dashboard-card__meta">{items}</div>'

    def _status(self) -> str:
        if self.status_text is not None:
            return (
                f'<div class="dashboard-status">{html_escape(self.status_text)}</div>'
            )
        if self.progress is None:
            return ""
        try:
            value = float(self.progress)
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
        if self.primary_label:
            if self.locked:
                buttons.append(
                    '<span class="dashboard-cta dashboard-cta--primary is-disabled" aria-disabled="true">'
                    f"{html_escape(self.primary_label)}</span>"
                )
            else:
                buttons.append(
                    f'<a class="dashboard-cta dashboard-cta--primary" href="?go={html_escape(self.primary_go)}">'
                    f"{html_escape(self.primary_label)}</a>"
                )
        if self.secondary_label:
            if self.locked:
                buttons.append(
                    '<span class="dashboard-cta dashboard-cta--ghost is-disabled" aria-disabled="true">'
                    f"{html_escape(self.secondary_label)}</span>"
                )
            else:
                buttons.append(
                    f'<a class="dashboard-cta dashboard-cta--ghost" href="?go={html_escape(self.secondary_go)}">'
                    f"{html_escape(self.secondary_label)}</a>"
                )
        return (
            f'<div class="dashboard-card__actions">{"".join(buttons)}</div>'
            if buttons
            else ""
        )

    def _pills(self) -> str:
        pills: List[str] = []
        if self.badge_text:
            pills.append(
                f'<div class="badge badge--brand">{html_escape(self.badge_text)}</div>'
            )
        for badge in self.badges:
            pills.append(
                f'<div class="badge badge--neutral">{html_escape(str(badge))}</div>'
            )
        return f'<div class="dashboard-badges">{"".join(pills)}</div>' if pills else ""


class ProductTileHub(BaseTile):
    def render(self) -> None:
        if not self.visible:
            return
        # ONE markdown call => ONE grid child
        out: List[str] = []
        out.append(
            f'<div class="ptile dashboard-card"{self._variant()}{self._style()}>'
        )
        out.append('<div class="dashboard-card__head">')
        pills = self._pills()
        if pills:
            out.append(pills)
        out.append(
            '<div class="dashboard-card__title-row">'
            f'<h3 class="dashboard-card__title">{html_escape(self.title)}</h3>'
            f"{self._status()}"
            "</div>"
        )
        if self.desc:
            out.append(
                f'<p class="dashboard-card__subtitle">{html_escape(self.desc)}</p>'
            )
        if self.blurb:
            out.append(
                f'<p class="dashboard-description">{html_escape(self.blurb)}</p>'
            )
        out.append("</div>")  # /head
        meta = self._meta()
        if meta:
            out.append(meta)
        out.append(self._actions())
        out.append("</div>")  # /card
        st.markdown("".join(out), unsafe_allow_html=True)


class ModuleTileCompact(BaseTile):
    def render(self) -> None:
        if not self.visible:
            return
        out: List[str] = []
        out.append(
            f'<div class="mtile dashboard-card"{self._variant()}{self._style()}>'
        )
        out.append(
            '<div class="dashboard-card__title-row">'
            f'<h3 class="dashboard-card__title">{html_escape(self.title)}</h3>'
            f"{self._status()}"
            "</div>"
        )
        if self.blurb:
            out.append(
                f'<p class="dashboard-description">{html_escape(self.blurb)}</p>'
            )
        meta = self._meta()
        if meta:
            out.append(meta)
        out.append(self._actions())
        out.append("</div>")
        st.markdown("".join(out), unsafe_allow_html=True)


__all__ = ["ProductTileHub", "ModuleTileCompact"]
