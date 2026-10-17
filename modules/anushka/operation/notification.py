
"""Reusable Streamlit notifications for Anushka's file operations."""

import streamlit as st


def show_success(message: str) -> None:
    """Display a successful operation message."""
    st.success(message, icon="✅")


def show_error(message: str) -> None:
    """Display an operation error message."""
    st.error(message, icon="❌")


def show_info(message: str) -> None:
    """Display an informational message."""
    st.info(message, icon="ℹ️")


def show_warning(message: str) -> None:
    """Display a warning message."""
    st.warning(message, icon="⚠️")
