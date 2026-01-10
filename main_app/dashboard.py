
from django.utils.translation import gettext_lazy as _

def dashboard_callback(request, context):
    """
    Callback to provide custom context to the dashboard.
    """
    context.update({
        "admin_info": {
            "name": request.user.get_full_name() or request.user.email,
            "email": request.user.email,
            "last_login": request.user.last_login,
        }
    })
    return context
