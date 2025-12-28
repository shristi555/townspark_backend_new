import pytest
from unittest.mock import Mock
from rest_framework.exceptions import ErrorDetail
from core.renderers import GlobalResponseRenderer


class TestGlobalResponseRenderer:
    """Test suite for GlobalResponseRenderer"""

    @pytest.fixture
    def renderer(self):
        """Create a renderer instance"""
        return GlobalResponseRenderer()

    @pytest.fixture
    def mock_renderer_context(self):
        """Create a mock renderer context"""
        response = Mock()
        response.status_code = 200
        return {
            "response": response,
            "view": Mock(),
            "request": Mock(),
        }

    def test_nested_validation_error_extraction(self, renderer, mock_renderer_context):
        """Test extraction of nested validation error structure"""
        # This is the problematic structure from the logs
        data = {
            "success": False,
            "response": None,
            "error": {
                "type": "validation_error",
                "details_type": "object",
                "details": {
                    "detail": "Validation failed",
                    "errors": {
                        "email": [
                            ErrorDetail(
                                string="user with this email already exists.",
                                code="unique",
                            )
                        ],
                        "phone_number": [
                            ErrorDetail(
                                string="A user with this phone number already exists.",
                                code="invalid",
                            )
                        ],
                    },
                },
            },
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        # Should extract nested errors to top level
        assert result_data["success"] is False
        assert result_data["response"] is None
        assert result_data["error"]["type"] == "validation_error"

        # Details should be the errors object, not nested
        assert "email" in result_data["error"]["detail"]
        assert "phone_number" in result_data["error"]["detail"]

        # Should extract string from ErrorDetail
        assert (
            result_data["error"]["detail"]["email"]
            == "user with this email already exists."
        )
        assert (
            result_data["error"]["detail"]["phone_number"]
            == "A user with this phone number already exists."
        )

        # Should not have nested 'detail' or 'errors' keys
        assert "errors" not in result_data["error"]["detail"]

    def test_error_detail_string_extraction(self, renderer, mock_renderer_context):
        """Test extraction of ErrorDetail objects to plain strings"""
        data = {
            "success": False,
            "response": None,
            "error": {
                "type": "validation_error",
                "detail": {
                    "field1": [ErrorDetail(string="Error message 1", code="invalid")],
                    "field2": ErrorDetail(string="Error message 2", code="required"),
                    "field3": "Plain string error",
                },
            },
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        assert result_data["error"]["detail"]["field1"] == "Error message 1"
        assert result_data["error"]["detail"]["field2"] == "Error message 2"
        assert result_data["error"]["detail"]["field3"] == "Plain string error"

    def test_success_response_format(self, renderer, mock_renderer_context):
        """Test successful response format"""
        data = {
            "success": True,
            "response": {"id": 1, "name": "Test User"},
            "error": None,
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["response"] == {"id": 1, "name": "Test User"}
        assert result_data["error"] is None

    def test_details_type_string(self, renderer, mock_renderer_context):
        """Test details_type is 'string' for string errors"""
        data = {
            "success": False,
            "response": None,
            "error": {"type": "error", "detail": "This is a string error"},
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        assert result_data["error"]["details_type"] == "string"
        assert result_data["error"]["detail"] == "This is a string error"

    def test_details_type_object(self, renderer, mock_renderer_context):
        """Test details_type is 'object' for dict errors"""
        data = {
            "success": False,
            "response": None,
            "error": {
                "type": "validation_error",
                "detail": {"field1": "Error 1", "field2": "Error 2"},
            },
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        assert result_data["error"]["details_type"] == "object"
        assert isinstance(result_data["error"]["detail"], dict)

    def test_details_type_list(self, renderer, mock_renderer_context):
        """Test details_type is 'list' for list errors"""
        data = {
            "success": False,
            "response": None,
            "error": {"type": "error", "detail": ["Error 1", "Error 2", "Error 3"]},
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        assert result_data["error"]["details_type"] == "list"
        assert isinstance(result_data["error"]["detail"], list)

    def test_list_of_error_details_extraction(self, renderer, mock_renderer_context):
        """Test extraction of list containing ErrorDetail objects"""
        data = {
            "success": False,
            "response": None,
            "error": {
                "type": "validation_error",
                "detail": {
                    "field": [
                        ErrorDetail(string="Error 1", code="invalid"),
                        ErrorDetail(string="Error 2", code="required"),
                    ]
                },
            },
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        # Should take first error from list
        assert result_data["error"]["detail"]["field"] == "Error 1"

    def test_empty_error_list(self, renderer, mock_renderer_context):
        """Test handling of empty error lists"""
        data = {
            "success": False,
            "response": None,
            "error": {"type": "validation_error", "detail": {"field": []}},
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        assert result_data["error"]["detail"]["field"] == ""

    def test_none_values_handling(self, renderer, mock_renderer_context):
        """Test handling of None values"""
        data = {
            "success": False,
            "response": None,
            "error": {"type": "error", "detail": None},
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        assert result_data["error"]["detail"] == ""

    def test_deeply_nested_errors_extraction(self, renderer, mock_renderer_context):
        """Test extraction of deeply nested error structures"""
        data = {
            "success": False,
            "response": None,
            "error": {
                "type": "validation_error",
                "detail": {
                    "detail": {
                        "errors": {
                            "field": [
                                ErrorDetail(string="Nested error", code="invalid")
                            ]
                        }
                    }
                },
            },
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        # Should flatten nested structure
        assert "field" in result_data["error"]["detail"]
        assert result_data["error"]["detail"]["field"] == "Nested error"

    def test_mixed_error_types(self, renderer, mock_renderer_context):
        """Test handling of mixed error types in same response"""
        data = {
            "success": False,
            "response": None,
            "error": {
                "type": "validation_error",
                "detail": {
                    "field1": ErrorDetail(string="Error 1", code="invalid"),
                    "field2": [ErrorDetail(string="Error 2", code="required")],
                    "field3": "Plain error",
                    "field4": ["Multiple", "errors"],
                },
            },
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        assert result_data["error"]["detail"]["field1"] == "Error 1"
        assert result_data["error"]["detail"]["field2"] == "Error 2"
        assert result_data["error"]["detail"]["field3"] == "Plain error"
        assert result_data["error"]["detail"]["field4"] == "Multiple"

    def test_non_field_errors_extraction(self, renderer, mock_renderer_context):
        """Test extraction of non_field_errors"""
        data = {
            "success": False,
            "response": None,
            "error": {
                "type": "validation_error",
                "detail": {
                    "non_field_errors": [
                        ErrorDetail(string="General error", code="invalid")
                    ]
                },
            },
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        assert result_data["error"]["detail"]["non_field_errors"] == "General error"

    def test_consistent_output_structure(self, renderer, mock_renderer_context):
        """Test that output always has consistent structure"""
        data = {
            "success": False,
            "response": None,
            "error": {"type": "validation_error", "detail": {"field": "error"}},
        }

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        # Must have these top-level keys
        assert "success" in result_data
        assert "response" in result_data
        assert "error" in result_data

        # Error must have these keys
        assert "type" in result_data["error"]
        assert "detail" in result_data["error"]
        assert "details_type" in result_data["error"]

    def test_raw_string_response(self, renderer, mock_renderer_context):
        """Test rendering of raw string responses"""
        data = "Plain string response"

        result = renderer.render(data, renderer_context=mock_renderer_context)
        import json

        result_data = json.loads(result)

        assert result_data["success"] is True
        assert result_data["response"] == "Plain string response"
        assert result_data["error"] is None
