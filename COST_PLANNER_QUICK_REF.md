# Cost Planner Quick Reference

## 🎯 Which One Do I Use?

**Always use Cost Planner V2** unless you're doing historical research.

## 📂 File Locations

### Cost Planner V2 (ACTIVE) ✅
```
products/cost_planner_v2/          # Main folder
config/cost_planner_v2_modules.json # Configuration
```

### Cost Planner (LEGACY) ⚠️
```
products/cost_planner/             # Legacy folder
config/cost_config.v3.json         # Old config
```

## 🔑 Navigation Keys

```python
# In nav.json and session state:
"cost"      # Legacy (hidden, not used)
"cost_v2"   # Active V2 (used in production)
```

## 📝 Quick Commands

### Add a New Module (V2)
1. Edit: `config/cost_planner_v2_modules.json`
2. Add tile in: `products/cost_planner_v2/hub.py`
3. Restart app

### View Documentation
```bash
# V2 Development Guide
cat products/cost_planner_v2/MODULE_DEVELOPMENT_GUIDE.md

# Legacy Info
cat products/cost_planner/README_LEGACY.md

# Architecture Overview
cat COST_PLANNER_ARCHITECTURE.md
```

## ⚡ One-Liner Cheat Sheet

| Task | File to Edit |
|------|-------------|
| Add module | `config/cost_planner_v2_modules.json` |
| Change hub layout | `products/cost_planner_v2/hub.py` |
| Modify renderer | `products/cost_planner_v2/module_renderer.py` |
| Route changes | `products/cost_planner_v2/product.py` |

---

**Remember:** Everything active is in **V2**. Don't touch `cost_planner/` (no "v2").
