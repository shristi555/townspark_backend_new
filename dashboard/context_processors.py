from .utils import get_analytics_data


def admin_analytics(request):
    """Context processor that injects dashboard analytics for admin pages.

    - Only populates data for the admin namespace (to avoid running on every request).
    - Delegates the heavy lifting to `dashboard.utils.get_analytics_data` so the
      same logic is reused for Unfold and Jazzmin dashboards.
    """
    context = {}

    try:
        resolver_match = getattr(request, "resolver_match", None)
        is_admin = (
            resolver_match is not None and resolver_match.namespace == "admin"
        ) or request.path.startswith("/admin")
    except Exception:
        is_admin = False

    if not is_admin:
        return {}

    # reuse existing utility (it mutates/returns the context dict)
    return get_analytics_data(request, context) or {}
