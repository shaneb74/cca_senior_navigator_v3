# core/ui/product_tile.py
import streamlit as st
from datetime import datetime

class ProductTile:
    """Reusable Streamlit component for product tiles with dynamic states, workflow cues, and interactive sub-product forms."""

    def __init__(
        self,
        title: str,
        icon_path: str,
        pre_start_text: str,
        in_progress_text: str,
        post_complete_text: str,
        buttons: list[dict],
        workflow_type: str = None,  # Optional: 'assessment', 'financial', 'planning', or custom
        workflow_config: list[dict] = None,  # List of steps: {'id': int, 'label': str, 'type': str, 'options': list, 'required': bool}
        visible: bool = True,
        locked: bool = False,
        order: int = 0,
        prereq: str = None,
        role: str = "member",
        progress: float = 0.0,
        paid: bool = False,
        meta: dict = None,
        parent_product: str = None
    ):
        """Initialize a product tile with configurable attributes, including workflow for sub-products."""
        self.title = title
        self.icon_path = icon_path
        self.pre_start_text = pre_start_text
        self.in_progress_text = in_progress_text
        self.post_complete_text = post_complete_text
        self.buttons = buttons
        self.workflow_type = workflow_type  # Guides styling/layout
        self.workflow_config = workflow_config or []  # Dynamic workflow steps
        self.visible = visible
        self.locked = locked
        self.order = order
        self.prereq = prereq
        self.role = role
        self.progress = max(0.0, min(100.0, progress))
        self.paid = paid
        self.meta = meta or {"steps": 0, "time": "N/A", "last_activity": None}
        self.parent_product = parent_product
        self.state = "new"
        self.on_click = None
        self.start_here = False
        self.go_next = False

    def _get_state(self, session_state_key: str) -> str:
        """Determine tile state based on session state or prereq."""
        if self.locked or not self.visible or not self._is_prereq_met(st.session_state):
            return "locked"
        state_data = st.session_state.get(session_state_key, {})
        if not state_data:
            return "new"
        if state_data.get("progress", 0) < 100:
            return "in progress"
        return "done"

    def _is_prereq_met(self, session_state: dict) -> bool:
        """Check if prerequisite product is completed."""
        if not self.prereq:
            return True
        prereq_state = session_state.get(self.prereq, {})
        return prereq_state.get("progress", 0) == 100

    def _set_workflow_cues(self, tiles: list['ProductTile']) -> None:
        """Set start_here and go_next cues based on order and completion."""
        if not tiles or self.order == 0 or self.parent_product:
            return
        tiles.sort(key=lambda x: x.order)
        for i, tile in enumerate(tiles):
            if tile.parent_product:
                continue
            tile.start_here = (i == 0 and tile._is_prereq_met(st.session_state) and not tile.locked)
            tile.go_next = (i > 0 and tiles[i-1].state == "done" and tile._is_prereq_met(st.session_state) and not tile.locked)

    def _render_widget(self, step: dict) -> tuple:
        """Render a single workflow widget based on type and return the value."""
        step_id = step['id']
        label = step['label']
        widget_type = step['type']
        options = step.get('options', [])
        value = st.session_state.get(f"{self.title}_{step_id}", options[0] if widget_type == "radio" and options else "")
        required = step.get('required', False)

        if widget_type == "radio":
            cols = st.columns(min(4, len(options)))
            selected = value
            for i, opt in enumerate(options):
                with cols[i % len(cols)]:
                    if st.button(opt, key=f"{self.title}_{step_id}_{opt}", disabled=selected == opt):
                        st.session_state[f"{self.title}_{step_id}"] = opt
                        st.rerun()
                    if selected == opt:
                        st.markdown(f"<span style='background: #E0E0E0; padding: 5px; border-radius: 3px; color: #333;'>● {opt}</span>", unsafe_allow_html=True)
            return selected if selected in options else (None if required else "")
        elif widget_type == "text":
            return st.text_input(label, value=value, key=f"{self.title}_{step_id}")
        elif widget_type == "slider":
            return st.slider(label, step.get('min', 0), step.get('max', 100), value=value or step.get('default', 0), key=f"{self.title}_{step_id}")
        elif widget_type == "dropdown":
            return st.selectbox(label, options, index=options.index(value) if value in options else 0, key=f"{self.title}_{step_id}")
        elif widget_type == "pill_list":
            current_pills = st.session_state.get(f"{self.title}_{step_id}", [])
            new_pill = st.text_input(label, key=f"{self.title}_{step_id}_input")
            if st.button("Add", key=f"{self.title}_{step_id}_add") and new_pill:
                if new_pill not in current_pills:
                    current_pills.append(new_pill)
                    st.session_state[f"{self.title}_{step_id}"] = current_pills
                    st.rerun()
            for i, pill in enumerate(current_pills):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"<span style='background: #007BFF; color: white; padding: 2px 8px; border-radius: 12px; margin-right: 5px;'>{pill}</span>", unsafe_allow_html=True)
                with col2:
                    if st.button("×", key=f"{self.title}_{step_id}_remove_{i}"):
                        current_pills.remove(pill)
                        st.session_state[f"{self.title}_{step_id}"] = current_pills
                        st.rerun()
            return current_pills
        return None  # Default for unsupported types

    def _render_workflow(self, session_state_key: str) -> bool:
        """Render the workflow form if this tile is active, styled per workflow_type."""
        if st.session_state.get("current_tile") != self.title:
            return False

        # Workflow header (Back link + title)
        col_back, col_title = st.columns([1, 4])
        with col_back:
            if st.button("← Back", key=f"{self.title}_back"):
                st.session_state["current_tile"] = None
                st.rerun()
        with col_title:
            st.markdown(f"**{self.title}**")

        st.markdown(f"**Assessment for someone: {st.session_state.get('person_name', 'John')}**")

        form_data = st.session_state.get(self.title, {})
        num_steps = len(self.workflow_config)
        completed_steps = sum(1 for step in self.workflow_config if form_data.get(step['id']))
        self.progress = (completed_steps / num_steps) * 100 if num_steps > 0 else 0
        
        # Initialize session state for progress if needed
        if session_state_key not in st.session_state:
            st.session_state[session_state_key] = {"progress": self.progress}
        
        st.session_state[session_state_key]["progress"] = self.progress

        # Render numbered questions with styled layout
        for step in self.workflow_config:
            step_id = step['id']
            label = step['label']
            st.markdown(f"**{step_id}.** {label} {'(required)' if step.get('required', False) else ''}")

            value = self._render_widget(step)
            if value is not None:
                form_data[step_id] = value

            st.markdown("---")  # Separator between questions

        st.session_state[self.title] = form_data

        # Complete button
        all_required_filled = all(form_data.get(step['id']) for step in self.workflow_config if step.get('required', False))
        if st.button("Complete", key=f"{self.title}_complete", disabled=not all_required_filled, use_container_width=True):
            self.progress = 100
            st.session_state[session_state_key]["progress"] = 100
            st.session_state["current_tile"] = None
            if hasattr(self, 'run_func'):
                self.run_func(form_data)
            st.rerun()

        return True

    def render(self, session_state_key: str, tiles: list['ProductTile'] = None) -> None:
        """Render the product tile with dynamic content and optional workflow."""
        if not self.visible:
            return

        self.state = self._get_state(session_state_key)
        if tiles:
            self._set_workflow_cues(tiles)

        st.markdown(
            f"""
            <div class="product-tile" style="background: #FFFFFF; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px;">
            """,
            unsafe_allow_html=True
        )

        icon_src = f"static/images/{self.icon_path}" if self.icon_path else ""
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="color: #333333; font-size: 16px; font-weight: bold; margin: 0;">{self.title}</h3>
                <img src="{icon_src}" style="width: 20px; height: 20px;" alt="{self.title} icon">
            </div>
            """,
            unsafe_allow_html=True
        )

        subtext = (
            self.pre_start_text if self.state == "new" else
            self.in_progress_text if self.state == "in progress" else
            self.post_complete_text
        )
        st.markdown(f'<p style="color: #666666; font-size: 12px; margin: 10px 0;">{subtext}</p>', unsafe_allow_html=True)

        if self.start_here:
            st.markdown('<span style="color: #007BFF; font-size: 12px;">Start Here</span>', unsafe_allow_html=True)
        elif self.go_next:
            st.markdown('<span style="color: #007BFF; font-size: 12px;">Next</span>', unsafe_allow_html=True)

        if self.state == "in progress":
            st.markdown(
                f"""
                <div style="width: 100px; height: 5px; background: #E0E0E0; border-radius: 5px; overflow: hidden;">
                    <div style="width: {self.progress}%; height: 100%; background: #007BFF; border-radius: 5px;"></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif self.state == "done":
            st.markdown('<span style="color: #28A745;">✓</span>', unsafe_allow_html=True)
        elif self.state == "locked":
            st.markdown('<span style="color: #666666;">🔒</span>', unsafe_allow_html=True)

        if self.paid:
            st.markdown(
                '<div style="position: absolute; top: 10px; right: 10px; background: #007BFF; color: white; padding: 2px 10px; border-radius: 5px; font-size: 10px;">Paid</div>',
                unsafe_allow_html=True
            )

        meta_text = f"Steps: {self.meta['steps']}, Time: {self.meta['time']}, Last: {self.meta['last_activity'] or 'N/A'}"
        st.markdown(f'<p style="color: #666666; font-size: 10px; margin: 5px 0;">{meta_text}</p>', unsafe_allow_html=True)

        # Render Workflow if Active
        if self._render_workflow(session_state_key):
            st.markdown('</div>', unsafe_allow_html=True)
            return

        # Buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        for i, btn in enumerate(self.buttons):
            with (col1 if i == 0 else col2 if i == 1 else col3):
                if st.button(btn["text"], key=f"{self.title}_{btn['text']}", help=btn.get("help", ""), disabled=self.locked):
                    if btn.get("callback"):
                        btn["callback"]()
                    elif self.on_click:
                        self.on_click()
                    if i == 0 and not self.locked:  # Primary button opens workflow
                        st.session_state["current_tile"] = self.title
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# Example usage with different workflow types (uncomment to test)
if __name__ == "__main__":
    st.set_page_config(page_title="Test Tile", layout="wide")
    tiles = [
        ProductTile(
            title="Guided Care Plan",
            icon_path="downward-arrow.png",
            pre_start_text="Begin here to find your best senior care living options.",
            in_progress_text="Continue your assessment...",
            post_complete_text="Summary: Recommended In-Home Care",
            buttons=[{"text": "Start", "color": "#007BFF"}, {"text": "Complete", "color": "#28A745"}],
            workflow_type="assessment",
            workflow_config=[
                {"id": 1, "label": "Financial Situation", "type": "radio", "options": ["Comfortable", "Cost Concern", "Need Help"], "required": True},
                {"id": 2, "label": "Daily Independence", "type": "radio", "options": ["Independent", "Some Help", "Full Support"], "required": True},
                {"id": 3, "label": "Chronic Conditions", "type": "pill_list", "options": [], "required": False}
            ],
            visible=True,
            locked=False,
            order=1,
            meta={"steps": 8, "time": "15 min", "last_activity": None}
        ),
        ProductTile(
            title="VA Benefits",
            icon_path="medal.png",
            pre_start_text="Check eligibility for VA benefits.",
            in_progress_text="Reviewing your VA details...",
            post_complete_text="Summary: Eligible for Aid & Attendance",
            buttons=[{"text": "Start", "color": "#007BFF"}, {"text": "Complete", "color": "#28A745"}],
            workflow_type="financial",
            workflow_config=[
                {"id": 1, "label": "Monthly Income", "type": "slider", "min": 0, "max": 5000, "required": True},
                {"id": 2, "label": "Veteran ID", "type": "text", "required": True}
            ],
            visible=True,
            locked=False,
            order=1,
            parent_product="Cost Planner",
            meta={"steps": 2, "time": "5 min", "last_activity": None}
        ),
        ProductTile(
            title="Housing Options",
            icon_path="house.png",
            pre_start_text="Plan your housing adjustments.",
            in_progress_text="Updating your housing plan...",
            post_complete_text="Summary: Retain with modifications",
            buttons=[{"text": "Start", "color": "#007BFF"}, {"text": "Complete", "color": "#28A745"}],
            workflow_type="planning",
            workflow_config=[
                {"id": 1, "label": "Home Value", "type": "slider", "min": 0, "max": 1000000, "required": True},
                {"id": 2, "label": "Option", "type": "radio", "options": ["Sell", "Rent", "Retain"], "required": True},
                {"id": 3, "label": "Move-In Date", "type": "date", "required": False}
            ],
            visible=True,
            locked=False,
            order=2,
            parent_product="Cost Planner",
            meta={"steps": 3, "time": "10 min", "last_activity": None}
        )
    ]
    for tile in tiles:
        tile.render("test_state", tiles)