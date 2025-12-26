from rest_framework.renderers import JSONRenderer


class GlobalResponseRenderer(JSONRenderer):
    """
    Converts all API responses into a consistent {success, response, error} format.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context["response"].status_code
        success = 200 <= status_code < 300

        # first check if the data is already wrapped
        # we check if the keys 'success', 'response', and 'error' are present in the data
        if (
            isinstance(data, dict)
            and "success" in data
            and ("response" in data or "error" in data)
        ):
            return super().render(data, accepted_media_type, renderer_context)

        # check if there was success i.e status code is in 2xx range
        if success:
            wrapped_data = {
                "success": True,
                "response": data if data is not None else {},
                "error": None,
            }

        # Handle Error Responses (4xx and 5xx)
        else:
            message = "An error occurred"
            details = data

            if isinstance(data, dict):
                # DRF usually puts the main error in 'detail'
                message = data.get("detail", data.get("message", "Unknown Server side Error"))
            elif isinstance(data, list):
                message = "Multiple unknown errors occurred"

            wrapped_data = {
                "success": False,
                "response": None,
                "error": {"message": message, "details": details},
            }

        return super().render(wrapped_data, accepted_media_type, renderer_context)
