"""
Favorite button component for toggling favorite status.
"""

import streamlit as st
import requests
from typing import Optional


def render_favorite_button(
    spot_id: int,
    is_favorited: bool,
    on_toggle_callback: Optional[callable] = None,
    key_suffix: str = ""
):
    """
    Render a favorite toggle button.
    
    Args:
        spot_id: Tourist spot ID.
        is_favorited: Current favorite status.
        on_toggle_callback: Callback function to call after toggle.
        key_suffix: Suffix for button key to avoid conflicts.
    """
    # Check if user is logged in
    token = st.session_state.get("token")
    if not token:
        st.caption("⭐ Login to favorite")
        return
    
    # Button appearance
    button_text = "❤️ Favorited" if is_favorited else "🤍 Favorite"
    button_type = "secondary" if is_favorited else "primary"
    
    if st.button(
        button_text,
        key=f"fav_btn_{spot_id}_{key_suffix}",
        type=button_type,
        use_container_width=True
    ):
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"http://localhost:8000/api/spots/{spot_id}/favorite/toggle",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                action = result.get("action", "updated")
                
                if action == "added":
                    st.success("✅ Added to favorites!")
                else:
                    st.info("ℹ️ Removed from favorites")
                
                # Call callback if provided
                if on_toggle_callback:
                    on_toggle_callback()
                
                # Force rerun to update UI
                st.rerun()
            else:
                error_detail = response.json().get("detail", "Unknown error")
                st.error(f"❌ Error: {error_detail}")
        
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")


def render_favorite_icon(is_favorited: bool):
    """
    Render a simple favorite status icon (non-interactive).
    
    Args:
        is_favorited: Whether the item is favorited.
    """
    if is_favorited:
        st.markdown("❤️")
    else:
        st.markdown("🤍")


def check_favorite_status(spot_id: int) -> bool:
    """
    Check if a spot is in user's favorites.
    
    Args:
        spot_id: Tourist spot ID.
        
    Returns:
        True if favorited, False otherwise.
    """
    token = st.session_state.get("token")
    if not token:
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"http://localhost:8000/api/spots/{spot_id}/favorite/status",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json().get("is_favorited", False)
    except:
        pass
    
    return False


def render_favorite_button_compact(spot_id: int, key_suffix: str = ""):
    """
    Render a compact favorite button that checks status automatically.
    
    Args:
        spot_id: Tourist spot ID.
        key_suffix: Suffix for button key.
    """
    # Check if user is logged in
    token = st.session_state.get("token")
    if not token:
        return
    
    # Check favorite status
    is_favorited = check_favorite_status(spot_id)
    
    # Render button
    render_favorite_button(spot_id, is_favorited, key_suffix=key_suffix)
