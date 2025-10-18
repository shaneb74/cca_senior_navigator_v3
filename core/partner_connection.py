"""
Generic Partner Connection Module Renderer

JSON-DRIVEN ARCHITECTURE:
All partner connection flows are defined in config/partners.json.
This module reads the 'connection' config and dynamically renders:
- Form fields (type, label, validation)
- Submission webhooks
- Confirmation messages
- Next steps

NO HARDCODED PARTNER LOGIC - Everything driven by JSON config.
Add new partners or modify flows by editing partners.json only.

Example partner connection config:
{
  "connection": {
    "type": "lead_capture",
    "inline": true,
    "title": "Connect with Partner",
    "description": "Share your info...",
    "fields": [
      {"id": "name", "type": "text", "label": "Full Name", "required": true}
    ],
    "submit": {
      "webhook": "https://partner.com/api/leads",
      "method": "POST",
      "payload_template": {...}
    },
    "confirmation": {
      "title": "Thank you!",
      "message": "Partner will contact you soon."
    }
  }
}
"""

from datetime import datetime
from typing import Optional,  Any

import requests
import streamlit as st

from core.session_store import safe_rerun


def render_partner_connection(partner: dict[str, Any], ctx: dict[str, Any] | None = None) -> None:
    """
    Render partner connection module based on JSON config.

    This function NEVER needs modification - all behavior defined in
    partners.json 'connection' section.

    Args:
        partner: Partner dict from partners.json
        ctx: Optional context (user data, flags, GCP tier)
    """
    connection_config = partner.get("connection", {})

    if not connection_config:
        st.warning(f"Connection not configured for {partner.get('name', 'this partner')}.")
        return

    partner_id = partner.get("id")
    submitted_key = f"partner_{partner_id}_submitted"

    # Show confirmation if already submitted
    if st.session_state.get(submitted_key):
        _show_confirmation(connection_config.get("confirmation", {}), partner_id)
        return

    # Render connection form
    _render_connection_form(partner, connection_config, ctx)


def _render_connection_form(
    partner: dict[str, Any], config: dict[str, Any], ctx: dict[str, Any] | None
) -> None:
    """Render the connection form from JSON config."""
    partner_id = partner.get("id")

    # Form header
    st.markdown(f"### {config.get('title', 'Connect with ' + partner.get('name', 'Partner'))}")

    if desc := config.get("description"):
        st.write(desc)

    # Dynamic form fields
    with st.form(f"partner_connect_{partner_id}", clear_on_submit=False):
        field_values = {}

        for field in config.get("fields", []):
            field_values[field["id"]] = _render_field(field, partner_id)

        # Consent checkbox (always include for GDPR/privacy)
        consent = st.checkbox(
            "I consent to share my information with this partner", key=f"{partner_id}_consent"
        )

        submitted = st.form_submit_button("Submit", use_container_width=True)

    # Handle submission
    if submitted:
        if not consent:
            st.error("Please consent to share your information.")
        elif _validate_fields(field_values, config.get("fields", [])):
            success = _submit_lead(partner, field_values, config.get("submit", {}), ctx)
            if success:
                st.session_state[f"partner_{partner_id}_submitted"] = True
                safe_rerun()
        else:
            st.error("Please fill all required fields correctly.")


def _render_field(field_config: dict[str, Any], partner_id: str) -> Any:
    """Dynamically render form field based on JSON type."""
    field_type = field_config.get("type", "text")
    field_id = field_config["id"]
    label = field_config.get("label", field_id.title())
    required = field_config.get("required", False)
    placeholder = field_config.get("placeholder", "")

    # Add asterisk for required fields
    label_display = f"{label} {'*' if required else ''}"

    # Unique key per partner + field
    key = f"{partner_id}_{field_id}"

    # Render based on type
    if field_type == "text":
        return st.text_input(label_display, placeholder=placeholder, key=key)

    elif field_type == "email":
        return st.text_input(label_display, placeholder=placeholder, key=key)

    elif field_type == "tel" or field_type == "phone":
        return st.text_input(label_display, placeholder=placeholder, key=key)

    elif field_type == "number":
        min_val = field_config.get("min", None)
        max_val = field_config.get("max", None)
        return st.number_input(label_display, min_value=min_val, max_value=max_val, key=key)

    elif field_type == "select" or field_type == "dropdown":
        options = field_config.get("options", [])
        return st.selectbox(
            label_display, options=[""] + options if not required else options, key=key
        )

    elif field_type == "multiselect":
        options = field_config.get("options", [])
        return st.multiselect(label_display, options=options, key=key)

    elif field_type == "textarea":
        return st.text_area(label_display, placeholder=placeholder, key=key, height=100)

    elif field_type == "checkbox":
        return st.checkbox(label_display, key=key)

    elif field_type == "date":
        return st.date_input(label_display, key=key)

    elif field_type == "time":
        return st.time_input(label_display, key=key)

    else:
        st.error(f"Unknown field type: {field_type}")
        return None


def _validate_fields(field_values: dict[str, Any], field_configs: list[dict[str, Any]]) -> bool:
    """Validate form fields based on JSON config."""
    for field_config in field_configs:
        field_id = field_config["id"]
        required = field_config.get("required", False)
        field_type = field_config.get("type", "text")
        value = field_values.get(field_id)

        # Check required fields
        if required:
            if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
                return False

        # Validate email format
        if field_type == "email" and value:
            if "@" not in value or "." not in value:
                return False

        # Validate phone format (basic)
        if field_type in ["tel", "phone"] and value:
            # Remove common separators
            cleaned = value.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
            if not cleaned.isdigit() or len(cleaned) < 10:
                return False

    return True


def _submit_lead(
    partner: dict[str, Any],
    fields: dict[str, Any],
    submit_config: dict[str, Any],
    ctx: dict[str, Any] | None,
) -> bool:
    """Submit lead to partner webhook using JSON-defined payload."""
    partner_id = partner.get("id")
    partner_name = partner.get("name", "Partner")

    # Build payload from template
    payload = _build_payload(submit_config.get("payload_template", {}), fields, ctx, partner)

    # Get webhook URL
    webhook = submit_config.get("webhook")

    if not webhook:
        st.warning(f"No webhook configured for {partner_name}. Lead captured locally.")
        _log_lead_locally(partner_id, fields, payload)
        return True

    # Send to partner webhook
    try:
        method = submit_config.get("method", "POST").upper()
        headers = submit_config.get("headers", {})

        # Replace environment variables in headers
        headers = {k: _interpolate_string(v, {}) for k, v in headers.items()}

        if method == "POST":
            response = requests.post(webhook, headers=headers, json=payload, timeout=10)
        elif method == "PUT":
            response = requests.put(webhook, headers=headers, json=payload, timeout=10)
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return False

        response.raise_for_status()

        # Log successful submission
        _log_lead_locally(partner_id, fields, payload, success=True)

        return True

    except requests.exceptions.RequestException as e:
        st.error(f"Error submitting to {partner_name}: {str(e)}")
        # Still log locally even if webhook fails
        _log_lead_locally(partner_id, fields, payload, success=False, error=str(e))
        return False


def _build_payload(
    template: dict[str, Any],
    fields: dict[str, Any],
    ctx: dict[str, Any] | None,
    partner: dict[str, Any],
) -> dict[str, Any]:
    """Build submission payload from template with variable interpolation."""
    if not template:
        # Default payload if no template defined
        return {
            "partner_id": partner.get("id"),
            "partner_name": partner.get("name"),
            "timestamp": datetime.now().isoformat(),
            "fields": fields,
            "context": ctx or {},
        }

    payload = {}
    context_data = {
        "fields": fields,
        "context": ctx or {},
        "partner": partner,
        "timestamp": datetime.now().isoformat(),
    }

    for key, value in template.items():
        if isinstance(value, str):
            payload[key] = _interpolate_string(value, context_data)
        elif isinstance(value, dict):
            payload[key] = _build_payload(value, fields, ctx, partner)
        elif isinstance(value, list):
            payload[key] = [
                _interpolate_string(str(v), context_data) if isinstance(v, str) else v
                for v in value
            ]
        else:
            payload[key] = value

    return payload


def _interpolate_string(template: str, data: dict[str, Any]) -> str:
    """Interpolate variables in string template (e.g., ${fields.name})."""
    result = template

    # Replace ${fields.fieldname}
    if "fields" in data:
        for field_id, field_value in data["fields"].items():
            result = result.replace(f"${{fields.{field_id}}}", str(field_value))

    # Replace ${context.key}
    if "context" in data:
        for key, value in data["context"].items():
            result = result.replace(f"${{context.{key}}}", str(value))

    # Replace ${partner.key}
    if "partner" in data:
        for key, value in data["partner"].items():
            if isinstance(value, (str, int, float)):
                result = result.replace(f"${{partner.{key}}}", str(value))

    return result


def _log_lead_locally(
    partner_id: str,
    fields: dict[str, Any],
    payload: dict[str, Any],
    success: bool = True,
    error: Optional[str] = None,
) -> None:
    """Log lead submission locally (for analytics/backup)."""
    # Store in session state for now (could be database in production)
    if "partner_leads" not in st.session_state:
        st.session_state.partner_leads = []

    lead_record = {
        "partner_id": partner_id,
        "timestamp": datetime.now().isoformat(),
        "fields": fields,
        "payload": payload,
        "success": success,
        "error": error,
    }

    st.session_state.partner_leads.append(lead_record)

    # Note: Currently stored in session state only
    # Production implementation would persist to database or send to CRM API


def _show_confirmation(confirmation_config: dict[str, Any], partner_id: str) -> None:
    """Show confirmation message from JSON config."""
    title = confirmation_config.get("title", "Thank you!")
    message = confirmation_config.get("message", "Your information has been submitted.")

    st.success(f"### {title}")
    st.write(message)

    # Next steps
    if next_steps := confirmation_config.get("next_steps"):
        st.markdown("**Next Steps:**")
        for step in next_steps:
            st.markdown(f"- {step}")

    # CTA button
    cta_config = confirmation_config.get("cta", {})
    cta_label = cta_config.get("label", "Close")
    cta_action = cta_config.get("action", "close")

    if st.button(cta_label, key=f"{partner_id}_cta", use_container_width=True):
        if cta_action == "close":
            # Clear submitted state and collapse tile
            st.session_state[f"partner_{partner_id}_submitted"] = False
            st.session_state[f"partner_{partner_id}_expanded"] = False
            safe_rerun()
        elif cta_action.startswith("navigate:"):
            # Navigate to another page
            page = cta_action.replace("navigate:", "")
            st.switch_page(page)


__all__ = ["render_partner_connection"]
