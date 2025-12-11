"""
Error Display Component - Consistent error display across the frontend.

Provides formatted error messages for different error types.
"""

import streamlit as st
from typing import Optional, Dict, Any


def show_error(
    message: str,
    error_type: str = "error",
    details: Optional[str] = None,
):
    """
    Display an error message.
    
    Args:
        message: Main error message
        error_type: Type of error (error, warning, info)
        details: Additional error details
    """
    if error_type == "error":
        st.error(f"❌ {message}")
    elif error_type == "warning":
        st.warning(f"⚠️ {message}")
    else:
        st.info(f"ℹ️ {message}")
    
    if details:
        with st.expander("Show Details"):
            st.code(details)


def show_api_error(response, context: str = "operation"):
    """
    Display API error with context.
    
    Args:
        response: API response object
        context: Context of the operation
    """
    status_code = response.status_code
    
    try:
        error_data = response.json()
        if isinstance(error_data, dict) and "error" in error_data:
            error_info = error_data["error"]
            message = error_info.get("message", f"{context} failed")
            
            st.error(f"❌ {message}")
            
            # Show validation errors if present
            if "details" in error_info:
                with st.expander("Validation Errors"):
                    for detail in error_info["details"]:
                        st.write(f"- **{detail.get('field')}**: {detail.get('message')}")
        else:
            show_generic_error(status_code, context)
    except:
        show_generic_error(status_code, context)


def show_generic_error(status_code: int, context: str = "operation"):
    """
    Display a generic error message.
    
    Args:
        status_code: HTTP status code
        context: Context of the operation
    """
    error_messages = {
        400: "Invalid request data",
        401: "Authentication required. Please login.",
        403: "Access denied. Insufficient permissions.",
        404: "Resource not found",
        409: "Conflict. Resource already exists.",
        422: "Validation error. Please check your input.",
        429: "Too many requests. Please try again later.",
        500: "Server error. Please try again later.",
        503: "Service unavailable. Please try again later.",
    }
    
    message = error_messages.get(status_code, f"An error occurred ({status_code})")
    st.error(f"❌ {context.capitalize()} failed: {message}")


def show_validation_error(field: str, message: str):
    """
    Display a validation error for a specific field.
    
    Args:
        field: Field name
        message: Validation error message
    """
    st.error(f"⚠️ **{field}**: {message}")


def show_connection_error():
    """Display connection error message."""
    st.error("❌ Cannot connect to the server")
    st.info("Please ensure the backend is running on http://localhost:8000")


def show_not_found_error(resource: str = "Resource"):
    """
    Display not found error.
    
    Args:
        resource: Type of resource not found
    """
    st.warning(f"⚠️ {resource} not found")
    st.info("The requested item may have been deleted or moved.")


def show_permission_error(action: str = "perform this action"):
    """
    Display permission error.
    
    Args:
        action: Action that requires permission
    """
    st.error(f"🚫 You don't have permission to {action}")
    st.info("Contact an administrator if you believe this is an error.")


def show_timeout_error():
    """Display timeout error message."""
    st.warning("⏱️ Request timed out")
    st.info("The server is taking too long to respond. Please try again.")


def show_rate_limit_error():
    """Display rate limit error."""
    st.error("🚦 Too many requests")
    st.info("You've exceeded the rate limit. Please wait a moment and try again.")
