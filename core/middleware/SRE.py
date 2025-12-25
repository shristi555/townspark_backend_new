import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response as DRFResponse


class ResponseWrapperMiddleware(MiddlewareMixin):
    """
    Middleware to wrap responses in a consistent structure.
    Converts DRF Responses into Django JsonResponse for safe rendering.
    """

    def process_response(self, request, response):
        try:
            data, status_code = self._extract_data_and_status(response)

            if data is None:
                # Non-JSON or template responses → leave untouched
                return response

            wrapped_data = self._build_wrapped_data(data, status_code)
            # ✅ Return Django JsonResponse — no render step required
            return JsonResponse(wrapped_data, status=status_code, safe=False)

        except Exception as e:
            # Fallback error response (also JsonResponse)
            return JsonResponse(
                {
                    "success": False,
                    "response": None,
                    "error": {"message": "Internal Server Error", "details": str(e)},
                },
                status=500,
            )

    def _extract_data_and_status(self, response):
        # Handle DRF Response
        if isinstance(response, DRFResponse) and hasattr(response, "data"):
            return response.data, getattr(response, "status_code", 200)

        # Handle Django JsonResponse
        if isinstance(response, JsonResponse):
            try:
                return json.loads(response.content.decode()), response.status_code
            except Exception:
                return None, None

        # Handle HttpResponse containing JSON string
        if hasattr(response, "content"):
            try:
                return json.loads(response.content.decode()), response.status_code
            except Exception:
                return None, None

        return None, None

    def _build_wrapped_data(self, data, status_code):
        # check if the data is already wrapped
        # we check if the keys 'success', 'response', and 'error' are present in the data
        # if there are success and any one of response or error keys present we consider it as already wrapped
        if isinstance(data, dict):
            if "success" in data and ("response" in data or "error" in data):
                return data

        success = 200 <= status_code < 300
        if success:
            return {
                "success": True,
                "response": data or {},
                "error": None,
            }

        message = ""
        details = None
        if isinstance(data, dict):
            message = data.get("detail") or data.get("message") or "An error occurred"
            details = data
        else:
            message = str(data)

        return {
            "success": False,
            "response": None,
            "error": {"message": message, "details": details},
        }
