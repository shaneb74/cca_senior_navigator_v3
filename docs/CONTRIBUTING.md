# Contributing to Senior Navigator

## Development Setup

### Prerequisites
- Python 3.9+ (recommend 3.13)
- Git
- Text editor or IDE (VS Code recommended)

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shaneb74/cca_senior_navigator_v3.git
   cd cca_senior_navigator_v3
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

---

## Code Quality Checks

### **Before Every Commit**

Run these three commands to ensure code quality:

```bash
make lint    # Ruff linting (fast)
make type    # Mypy type checking
make smoke   # Import smoke tests
```

Or run all at once:
```bash
make check   # Runs lint + type + smoke
```

### **Pre-Commit Hook**

A pre-commit hook automatically blocks:
- ❌ Backup files (`.bak*`)
- ❌ Multiple `module.json` files under `products/`
- ❌ Legacy GCP imports (`products.gcp_v1/v2/v3`)

The hook runs automatically on `git commit`. If it fails, fix the issues and commit again.

---

## Coding Standards

### **Python Style**
- **Line length:** 100 characters (enforced by Ruff)
- **Imports:** Sorted and grouped (Ruff handles this)
- **Type hints:** Use for function signatures (Python 3.9+ compatible)
  ```python
  from typing import Dict, List, Optional
  
  def calculate_cost(data: Dict[str, Any]) -> Optional[float]:
      ...
  ```

### **Naming Conventions**
- **Files:** `snake_case.py`
- **Functions:** `snake_case()`
- **Classes:** `PascalCase`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private:** `_leading_underscore()`

### **Import Order**
1. Standard library
2. Third-party (Streamlit, pandas, etc.)
3. Local modules (core, products)

```python
import json
from typing import Dict, Optional

import streamlit as st
import pandas as pd

from core.flags import get_flag
from products.cost_planner_v2.utils.cost_calculator import CostCalculator
```

---

## Project Structure

### **Adding a New Product**

1. **Create product directory:**
   ```bash
   mkdir -p products/my_product
   touch products/my_product/__init__.py
   touch products/my_product/product.py
   ```

2. **Implement render function:**
   ```python
   # products/my_product/product.py
   import streamlit as st
   
   def render():
       """Main entry point for My Product."""
       st.title("My Product")
       st.write("Product content here...")
   ```

3. **Register in navigation:**
   Edit `config/nav.json`:
   ```json
   {
     "key": "my_product",
     "label": "My Product",
     "module": "products.my_product.product:render"
   }
   ```

4. **Test:**
   ```bash
   make smoke  # Verify imports work
   streamlit run app.py
   ```

### **Adding a New Hub**

1. **Create hub file:**
   ```bash
   touch hubs/my_hub.py
   ```

2. **Implement render function:**
   ```python
   # hubs/my_hub.py
   import streamlit as st
   
   def render():
       """Main hub page."""
       st.title("My Hub")
       # Add product tiles, links, etc.
   ```

3. **Register in navigation** (same as product)

---

## Import Rules

### ✅ **Allowed**
```python
# Products import core
from core.flags import get_flag
from core.ui import render_header
from core.paths import get_static

# Products import their own utils
from products.cost_planner_v2.utils.cost_calculator import CostCalculator

# Products import shared utilities
from products.resources_common.coming_soon import render_coming_soon
```

### ❌ **Avoid**
```python
# DON'T cross-import between products
from products.gcp_v4.logic import compute_recommendation  # ❌

# DON'T hardcode paths
image_path = "static/images/logo.png"  # ❌

# Instead, use helper
from core.paths import get_static
image_path = get_static("images/logo.png")  # ✅
```

---

## Testing

### **Smoke Tests** (Fast)
```bash
make smoke
```
Verifies all imports work. Add new products here:
```python
# tests/smoke_imports.py
def test_imports():
    from products.my_product import product  # Add this line
    assert hasattr(product, 'render')
```

### **Unit Tests** (Comprehensive)
```bash
pytest tests/
```

### **Manual Testing Checklist**
- [ ] App starts without errors
- [ ] Navigation works (all pages accessible)
- [ ] GCP flow completes
- [ ] Cost Planner flow completes
- [ ] Feature flags toggle correctly
- [ ] No console errors in browser dev tools

---

## Git Workflow

### **Branch Naming**
- `feature/description` - New features
- `fix/description` - Bug fixes
- `chore/description` - Maintenance tasks
- `docs/description` - Documentation updates

### **Commit Messages**
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new assessment module
fix: correct keep_home logic in Cost Planner
chore: update dependencies
docs: add architecture diagram
refactor: extract cost calculation to utils
test: add smoke tests for new product
```

### **Pull Request Process**

1. **Create branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and commit:**
   ```bash
   make lint type smoke  # Check quality
   git add .
   git commit -m "feat: add my feature"
   ```

3. **Push and create PR:**
   ```bash
   git push origin feature/my-feature
   # Create PR on GitHub
   ```

4. **PR Checklist:**
   - [ ] All checks pass (`make lint type smoke`)
   - [ ] Manual testing completed
   - [ ] Documentation updated (if needed)
   - [ ] No console errors
   - [ ] Commit messages follow convention

---

## Common Tasks

### **Update Dependencies**
```bash
pip install -r requirements.txt
pip freeze > requirements.txt  # Update after adding new packages
```

### **Clear Cache**
```bash
# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# Clear Streamlit cache
rm -rf .streamlit/cache
```

### **Update Navigation**
Edit `config/nav.json` to add/remove/reorder pages.

### **Add Static Assets**
```bash
cp my_image.png static/images/
# Reference in code:
from core.paths import get_static
image_path = get_static("images/my_image.png")
```

---

## Troubleshooting

### **Import Errors**
```bash
# Verify imports work
make smoke

# Check Python path
python -c "import sys; print(sys.path)"
```

### **Streamlit Not Loading**
```bash
# Check port availability
lsof -i :8501

# Use different port
streamlit run app.py --server.port 8502
```

### **Type Errors**
```bash
# Run mypy with verbose output
mypy products core --verbose
```

### **Pre-Commit Hook Fails**
```bash
# See what's blocked
git diff --cached --name-only

# If false positive, contact maintainer
```

---

## Resources

- **Repository Structure:** [docs/REPO_STRUCTURE.md](./REPO_STRUCTURE.md)
- **Architecture:** [docs/ARCHITECTURE.md](./ARCHITECTURE.md)
- **Streamlit Docs:** https://docs.streamlit.io/
- **Ruff Docs:** https://docs.astral.sh/ruff/
- **Mypy Docs:** https://mypy.readthedocs.io/

---

## Questions?

Contact the maintainers:
- GitHub Issues: https://github.com/shaneb74/cca_senior_navigator_v3/issues
- Email: shaneb@conciergecareadvisors.com
