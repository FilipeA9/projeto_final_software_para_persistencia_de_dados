"""
User Profile Component - Display logged-in user information.

Reusable component to show user profile and logout functionality.
"""

import streamlit as st
from src.services.api_client import TuristandoAPI


def user_profile_sidebar():
    """
    Display user profile in sidebar with logout option.
    
    Should be called on pages that require authentication.
    """
    if not st.session_state.get("logged_in", False):
        return
    
    user = st.session_state.get("user", {})
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Usuário Logado")
        
        st.write(f"**Login:** {user.get('login', 'N/A')}")
        st.write(f"**Email:** {user.get('email', 'N/A')}")
        
        # Role badge
        role = user.get("role", "user")
        if role == "ADMIN":
            st.markdown("🔴 **Administrador**")
        else:
            st.markdown("🟢 **Usuário**")
        
        # Logout button
        if st.button("🚪 Sair", use_container_width=True):
            logout()


def user_profile_header():
    """
    Display compact user profile in page header.
    
    Alternative to sidebar display for wide layouts.
    """
    if not st.session_state.get("logged_in", False):
        return
    
    user = st.session_state.get("user", {})
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col2:
        st.markdown(f"👤 **{user.get('login', 'Usuário')}**")
    
    with col3:
        if st.button("🚪 Sair", key="logout_header"):
            logout()


def logout():
    """Handle user logout."""
    api = TuristandoAPI()
    
    try:
        # Get token
        token = st.session_state.get("access_token")
        
        if token:
            # Call logout endpoint
            api.logout(token)
        
        # Clear session state
        st.session_state["logged_in"] = False
        st.session_state["access_token"] = None
        st.session_state["user"] = None
        
        st.success("✅ Logout realizado com sucesso!")
        st.info("Redirecionando...")
        st.rerun()
        
    except Exception as e:
        # Even if API call fails, clear local session
        st.session_state["logged_in"] = False
        st.session_state["access_token"] = None
        st.session_state["user"] = None
        
        st.warning(f"⚠️ Logout realizado localmente: {str(e)}")
        st.rerun()


def require_login(redirect_to_login: bool = True):
    """
    Check if user is logged in. Redirect to login page if not.
    
    Args:
        redirect_to_login: If True, redirects to login page. If False, just shows message.
    
    Returns:
        True if user is logged in, False otherwise.
    """
    if not st.session_state.get("logged_in", False):
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        
        if redirect_to_login:
            if st.button("🔑 Fazer Login"):
                st.switch_page("src/pages/4_Login.py")
        
        return False
    
    return True


def get_current_user():
    """
    Get current logged-in user data.
    
    Returns:
        User dict or None if not logged in.
    """
    if not st.session_state.get("logged_in", False):
        return None
    
    return st.session_state.get("user")


def get_access_token():
    """
    Get current access token.
    
    Returns:
        Token string or None if not logged in.
    """
    if not st.session_state.get("logged_in", False):
        return None
    
    return st.session_state.get("access_token")


def is_admin():
    """
    Check if current user is an admin.
    
    Returns:
        True if user is admin, False otherwise.
    """
    user = get_current_user()
    if not user:
        return False
    
    return user.get("role") == "ADMIN"
