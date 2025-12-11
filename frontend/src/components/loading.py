"""
Loading Component - Display loading states in the frontend.

Provides consistent loading indicators across the application.
"""

import streamlit as st
from typing import Optional


def show_loading_spinner(message: str = "Loading..."):
    """
    Display a loading spinner with message.
    
    Args:
        message: Loading message to display
    """
    with st.spinner(message):
        pass


def show_loading_placeholder(message: str = "Loading data..."):
    """
    Display a loading placeholder.
    
    Args:
        message: Loading message
    """
    st.info(f"⏳ {message}")


def show_skeleton_card(count: int = 1):
    """
    Display skeleton loading cards.
    
    Args:
        count: Number of skeleton cards to show
    """
    for _ in range(count):
        with st.container():
            st.markdown("### ⬜ Loading...")
            st.caption("⬜⬜⬜⬜⬜⬜⬜⬜")
            st.progress(0.0)
            st.divider()


def show_data_loading(data_type: str = "data"):
    """
    Display data loading message.
    
    Args:
        data_type: Type of data being loaded
    """
    st.info(f"⏳ Loading {data_type}... Please wait.")


def show_processing(action: str = "Processing"):
    """
    Display processing message.
    
    Args:
        action: Action being processed
    """
    st.warning(f"⚙️ {action}... Please do not refresh the page.")
