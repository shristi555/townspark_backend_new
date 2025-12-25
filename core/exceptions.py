from rest_framework.views import exception_handler


def global_exception_handler(exc, context):
    # Call DRF's default handler first to get the standard error response
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # Handles case where DRF doesn't catch the error (e.g. database connection lost)
    # This ensures the client always gets JSON, never an HTML 500 page
    from rest_framework.response import Response

    return Response(
        {
            "success": False,
            "response": None,
            "error": {"message": "Internal Server Error", "details": str(exc)},
        },
        status=500,
    )
