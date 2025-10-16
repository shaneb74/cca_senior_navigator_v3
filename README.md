# Senior Navigator - Care Planning Platform

A Streamlit-based web application for senior care navigation, helping families make informed decisions about care options, costs, and resources.

## Project Structure

```
cca_senior_navigator_v3/
├── app.py                          # Main application entry point
├── layout.py                       # Global layout and styling
├── config/                         # Configuration files
│   ├── nav.json                   # Navigation structure
│   └── ui_config.json             # UI settings
├── core/                          # Core system modules
│   ├── mcip.py                    # Master Care Intelligence Panel (orchestration)
│   ├── navi.py                    # Navi intelligence layer
│   ├── nav.py                     # Navigation routing
│   ├── state.py                   # Session state management
│   ├── session_store.py           # Persistence layer
│   └── url_helpers.py             # UID preservation utilities
├── hubs/                          # Hub pages (main navigation destinations)
│   ├── concierge.py               # Main journey hub
│   ├── learning.py                # Educational resources
│   ├── partners.py                # Trusted partners
│   └── resources.py               # Additional resources
├── products/                      # Product modules (interactive tools)
│   ├── gcp_v4/                    # Guided Care Plan v4
│   ├── cost_planner_v2/           # Cost Planner v2
│   └── pfma_v2/                   # Plan with My Advisor v2
├── pages/                         # Page components
│   ├── welcome.py                 # Landing page
│   ├── someone_else.py            # Contextual welcome (for someone)
│   └── self.py                    # Contextual welcome (for self)
├── ui/                            # UI components
│   ├── header_simple.py           # Simple header component
│   └── footer_simple.py           # Simple footer component
├── assets/                        # Static assets
│   └── css/
│       └── theme.css              # Global CSS
└── static/                        # Public static files
    └── images/                    # Images and icons
```

## Key Architecture Concepts

### MCIP (Master Care Intelligence Panel)
The central orchestration system that:
- Tracks user journey progress across products
- Manages product unlock logic
- Publishes and consumes product outcomes (recommendations, assessments)
- Persists state via contracts stored in `data/users/{uid}.json`

### Navi (Intelligence Layer)
Single intelligence layer for:
- Journey coordination across products
- Next-best action recommendations
- Dynamic Q&A and context-aware guidance

### Session Persistence
- **UID Preservation**: User ID stored in URL query params (`?uid=anon_xxxxx`)
- **File-based Storage**: Session data persisted to `data/users/{uid}.json`
- **MCIP Contracts**: Core journey state stored in `mcip_contracts` key

### Navigation System
- **Dynamic Loading**: Pages loaded from `config/nav.json`
- **UID Preservation**: All navigation maintains UID in query params
- **Query Param Routing**: Uses `?page=key` for navigation

## Getting Started

### Prerequisites
- Python 3.13+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/shaneb74/cca_senior_navigator_v3.git
cd cca_senior_navigator_v3
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Clear User Data (Development)

```bash
python clear_data.py --clear-all
```

## Development Guidelines

### Adding a New Page

1. Add entry to `config/nav.json`:
```json
{
  "key": "my_page",
  "label": "My Page",
  "module": "pages.my_page:render",
  "hidden": false
}
```

2. Create the page module:
```python
# pages/my_page.py
import streamlit as st
from ui.header_simple import render_header_simple
from ui.footer_simple import render_footer_simple

def render(ctx=None):
    render_header_simple(active_route="my_page")
    st.title("My Page")
    # Your page content here
    render_footer_simple()
```

3. Restart Streamlit to pick up changes.

### Adding a New Product

1. Create product directory: `products/my_product/`
2. Create `product.py` with `render()` function
3. Register in `core/nav.py` PRODUCTS dict
4. Add to MCIP tracking in `core/mcip.py` if needed

### Working with MCIP

**Mark a product complete:**
```python
from core.mcip import MCIP
MCIP.mark_product_complete("my_product")
```

**Check product status:**
```python
if MCIP.is_product_complete("gcp"):
    # GCP is complete
    pass
```

**Publish product outcome:**
```python
from core.mcip import MCIP, CareRecommendation
rec = CareRecommendation(
    tier="assisted_living",
    tier_score=85.0,
    # ... other fields
)
MCIP.publish_care_recommendation(rec)
```

### Session State Best Practices

1. **Always preserve UID**: Use `add_uid_to_href()` for all href links
2. **Use MCIP for product state**: Don't create parallel state systems
3. **Avoid shared references**: Use `copy.deepcopy()` for nested dicts/lists
4. **Check MCIP first**: Always read from MCIP, not legacy session state

## Configuration Files

### nav.json
Defines navigation structure, groups, and page routing.

### ui_config.json
Controls UI element visibility (header nav items, etc.)

## Testing

The application uses manual testing workflows. Key test scenarios:

1. **Complete GCP → Verify Cost Planner unlocked**
2. **Navigate through journey → Verify state persists**
3. **Restart app → Verify progress restored from disk**
4. **Clear data → Verify fresh state**

## Deployment

The application is designed for Streamlit Cloud deployment:

1. Push to GitHub
2. Connect repository in Streamlit Cloud
3. Deploy from `dev` or `main` branch

## Key Features

- 🧭 **Guided Care Planning**: Step-by-step assessment tool
- 💰 **Cost Planning**: Financial assessment and estimates
- 📅 **Advisor Scheduling**: Connect with financial advisors
- 📚 **Learning Resources**: Educational content library
- 🤝 **Trusted Partners**: Curated service provider directory
- 🤖 **Navi AI**: Contextual guidance and Q&A

## Architecture Notes

### Why UID in Query Params?
Streamlit's `session_state` is tied to WebSocket session ID. When users navigate via href links (which trigger full page reloads), a new session is created with empty state. Storing UID in query params allows us to:
1. Preserve user identity across page reloads
2. Restore session state from disk
3. Maintain progress throughout the application

### Why MCIP Contracts?
MCIP contracts are the "source of truth" for user journey state. They:
1. Persist to disk automatically
2. Survive app restarts
3. Enable cross-product coordination
4. Support analytics and reporting

## Support

For questions or issues, contact the development team.

## License

Proprietary - All rights reserved
