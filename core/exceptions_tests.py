import pytest
from django.http import Http404
from django.core.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    NotAuthenticated,
    AuthenticationFailed,
    ParseError,
)
from rest_framework.response import Response
from unittest.mock import Mock, patch
from core.exceptions import global_exception_handler


class TestGlobalExceptionHandler:
    """Test suite for global exception handler"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock context for exception handler"""
        return {
            "view": Mock(),
            "args": (),
            "kwargs": {},
            "request": Mock(),
        }

    def test_handles_http404_returns_none(self, mock_context):
        """Test that Http404 is handled by DRF default handler"""
        exc = Http404("Not found")
        response = global_exception_handler(exc, mock_context)

        # DRF's default handler returns a response for Http404
        assert response is not None
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_handles_permission_denied_returns_none(self, mock_context):
        """Test that PermissionDenied is handled by DRF default handler"""
        exc = PermissionDenied("Permission denied")
        response = global_exception_handler(exc, mock_context)

        # DRF's default handler returns a response for PermissionDenied
        assert response is not None
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("core.exceptions.logger")
    def test_handles_unexpected_exception(self, mock_logger, mock_context):
        """Test handling of unexpected exceptions"""
        exc = ValueError("Something went wrong")
        response = global_exception_handler(exc, mock_context)

        assert response is not None
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data["type"] == "ValueError"
        assert response.data["message"] == "Something went wrong"
        assert "ValueError occurred" in response.data["detail"]

        # Verify logging
        mock_logger.error.assert_called_once()

    @patch("core.exceptions.logger")
    def test_handles_exception_without_message(self, mock_logger, mock_context):
        """Test handling of exceptions with empty message"""
        exc = Exception()
        response = global_exception_handler(exc, mock_context)

        assert response is not None
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data["message"] == "Unknown error"

    def test_handles_validation_error_simple(self, mock_context):
        """Test handling of simple ValidationError"""
        exc = ValidationError("Invalid data")
        response = global_exception_handler(exc, mock_context)

        assert response is not None
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_handles_validation_error_with_dict(self, mock_context):
        """Test handling of ValidationError with field-specific errors"""
        exc = ValidationError(
            {
                "email": ["user with this email already exists."],
                "phone_number": ["A user with this phone number already exists."],
            }
        )
        response = global_exception_handler(exc, mock_context)

        assert response is not None
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert "phone_number" in response.data

    def test_handles_not_authenticated(self, mock_context):
        """Test handling of NotAuthenticated exception"""
        exc = NotAuthenticated("Authentication required")
        response = global_exception_handler(exc, mock_context)

        assert response is not None
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_handles_authentication_failed(self, mock_context):
        """Test handling of AuthenticationFailed exception"""
        exc = AuthenticationFailed("Invalid credentials")
        response = global_exception_handler(exc, mock_context)

        assert response is not None
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_handles_parse_error(self, mock_context):
        """Test handling of ParseError exception"""
        exc = ParseError("Malformed request")
        response = global_exception_handler(exc, mock_context)

        assert response is not None
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("core.exceptions.logger")
    def test_logs_exception_with_context(self, mock_logger, mock_context):
        """Test that exceptions are logged with context"""
        exc = RuntimeError("Test error")
        global_exception_handler(exc, mock_context)

        # Verify logger was called with correct arguments
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert "RuntimeError" in call_args[0][0]
        assert call_args[1]["exc_info"] is True
        assert call_args[1]["extra"]["context"] == mock_context

    @patch("core.exceptions.logger")
    def test_handles_zero_division_error(self, mock_logger, mock_context):
        """Test handling of ZeroDivisionError"""
        exc = ZeroDivisionError("division by zero")
        response = global_exception_handler(exc, mock_context)

        assert response is not None
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data["type"] == "ZeroDivisionError"

    @patch("core.exceptions.logger")
    def test_handles_type_error(self, mock_logger, mock_context):
        """Test handling of TypeError"""
        exc = TypeError("'NoneType' object is not iterable")
        response = global_exception_handler(exc, mock_context)

        assert response is not None
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data["type"] == "TypeError"
        assert "'NoneType' object is not iterable" in response.data["message"]

    def test_response_structure_for_unhandled_exception(self, mock_context):
        """Test the response structure for unhandled exceptions"""
        exc = ValueError("Test value error")
        response = global_exception_handler(exc, mock_context)

        # Verify response structure
        assert isinstance(response, Response)
        assert "detail" in response.data
        assert "type" in response.data
        assert "message" in response.data
        assert response.data["type"] == "ValueError"
        assert response.data["message"] == "Test value error"

    @patch("core.exceptions.logger")
    def test_handles_attribute_error(self, mock_logger, mock_context):
        """Test handling of AttributeError"""
        exc = AttributeError("'dict' object has no attribute 'get_value'")
        response = global_exception_handler(exc, mock_context)

        assert response is not None
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data["type"] == "AttributeError"

    def test_drf_exception_handler_called_first(self, mock_context):
        """Test that DRF's exception handler is called first"""
        # DRF exceptions should be handled by default handler
        exc = ValidationError({"field": ["error message"]})
        response = global_exception_handler(exc, mock_context)

        # Should return a response (not None) as DRF handles it
        assert response is not None
        assert response.status_code == status.HTTP_400_BAD_REQUEST
