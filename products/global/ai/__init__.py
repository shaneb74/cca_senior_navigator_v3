"""Global AI services for Senior Navigator."""

# Import using __import__ to avoid 'global' keyword issue
import importlib
_advisor = importlib.import_module("products.global.ai.advisor_service")
get_answer = _advisor.get_answer

__all__ = ["get_answer"]
