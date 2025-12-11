"""
Spot management list component.

Displays list of spots with admin management actions.
"""

import streamlit as st
from typing import Optional
from services.api_client import TuristandoAPI


def render_spot_management_list(
    api: TuristandoAPI,
    token: str,
    page: int = 1,
    per_page: int = 10
):
    """
    Render spot management list with edit/delete actions.
    
    Args:
        api: API client instance.
        token: Admin authentication token.
        page: Current page number.
        per_page: Items per page.
    """
    st.subheader("🗺️ Manage Tourist Spots")
    
    # Filters
    with st.expander("🔍 Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_cidade = st.text_input("City", key="admin_filter_cidade")
        with col2:
            filter_estado = st.text_input("State", key="admin_filter_estado")
        with col3:
            filter_pais = st.text_input("Country", key="admin_filter_pais")
        
        filter_search = st.text_input("Search in name/description", key="admin_filter_search")
    
    try:
        # Fetch spots
        skip = (page - 1) * per_page
        result = api.list_spots(
            skip=skip,
            limit=per_page,
            cidade=filter_cidade if filter_cidade else None,
            estado=filter_estado if filter_estado else None,
            pais=filter_pais if filter_pais else None,
            search=filter_search if filter_search else None
        )
        
        spots = result.get("spots", [])
        total = result.get("total", 0)
        
        # Header with count
        st.caption(f"Total spots: {total}")
        
        if not spots:
            st.info("No spots found. Create your first one!")
            return
        
        # Display spots
        for spot in spots:
            render_spot_management_card(api, spot, token)
        
        # Pagination
        if total > per_page:
            render_management_pagination(total, page, per_page)
        
    except Exception as e:
        st.error(f"❌ Error loading spots: {e}")


def render_spot_management_card(api: TuristandoAPI, spot: dict, token: str):
    """
    Render a single spot management card.
    
    Args:
        api: API client instance.
        spot: Spot data dictionary.
        token: Admin authentication token.
    """
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Spot info
            st.markdown(f"### {spot['nome']}")
            st.caption(f"📍 {spot['cidade']}, {spot['estado']}, {spot['pais']}")
            
            # Description preview
            desc = spot.get('descricao', '')
            if len(desc) > 150:
                desc = desc[:147] + "..."
            st.write(desc)
            
            # Stats
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                avg_rating = spot.get('avg_rating')
                if avg_rating:
                    st.metric("Rating", f"{avg_rating:.1f}⭐")
                else:
                    st.caption("No ratings")
            with col_b:
                rating_count = spot.get('rating_count', 0)
                st.caption(f"{rating_count} reviews")
            with col_c:
                st.caption(f"ID: {spot['id']}")
        
        with col2:
            # Actions
            st.markdown("**Actions**")
            
            # View button
            if st.button(f"👁️ View", key=f"view_{spot['id']}", use_container_width=True):
                st.session_state[f"view_spot_{spot['id']}"] = True
            
            # Edit button
            if st.button(f"✏️ Edit", key=f"edit_{spot['id']}", use_container_width=True):
                st.session_state[f"edit_spot_{spot['id']}"] = True
                st.rerun()
            
            # Delete button
            if st.button(f"🗑️ Delete", key=f"delete_{spot['id']}", use_container_width=True):
                st.session_state[f"confirm_delete_{spot['id']}"] = True
        
        # Delete confirmation dialog
        if st.session_state.get(f"confirm_delete_{spot['id']}", False):
            with st.expander("⚠️ Confirm Deletion", expanded=True):
                st.warning(f"Are you sure you want to delete **{spot['nome']}**? This action cannot be undone.")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ Yes, Delete", key=f"confirm_yes_{spot['id']}", type="primary"):
                        try:
                            import requests
                            response = requests.delete(
                                f"{api.base_url}{api.api_prefix}/spots/{spot['id']}",
                                headers={"Authorization": f"Bearer {token}"}
                            )
                            response.raise_for_status()
                            st.success(f"✅ Spot '{spot['nome']}' deleted successfully!")
                            del st.session_state[f"confirm_delete_{spot['id']}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error deleting spot: {e}")
                
                with col_b:
                    if st.button("❌ Cancel", key=f"confirm_no_{spot['id']}"):
                        del st.session_state[f"confirm_delete_{spot['id']}"]
                        st.rerun()
        
        # Edit dialog
        if st.session_state.get(f"edit_spot_{spot['id']}", False):
            with st.expander(f"✏️ Editing: {spot['nome']}", expanded=True):
                from components.spot_form import render_spot_form
                
                if render_spot_form(api, token, spot):
                    del st.session_state[f"edit_spot_{spot['id']}"]
                    st.rerun()
                
                if st.button("Close Editor", key=f"close_edit_{spot['id']}"):
                    del st.session_state[f"edit_spot_{spot['id']}"]
                    st.rerun()
        
        st.divider()


def render_management_pagination(total: int, page: int, per_page: int):
    """
    Render pagination controls for management list.
    
    Args:
        total: Total number of items.
        page: Current page number.
        per_page: Items per page.
    """
    total_pages = (total + per_page - 1) // per_page
    
    if total_pages <= 1:
        return
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if page > 1:
            if st.button("⏮️ First", key="admin_first_page"):
                st.session_state["admin_page"] = 1
                st.rerun()
    
    with col2:
        if page > 1:
            if st.button("◀️ Prev", key="admin_prev_page"):
                st.session_state["admin_page"] = page - 1
                st.rerun()
    
    with col3:
        st.markdown(f"<div style='text-align: center; padding-top: 8px;'>Page {page} of {total_pages}</div>", unsafe_allow_html=True)
    
    with col4:
        if page < total_pages:
            if st.button("Next ▶️", key="admin_next_page"):
                st.session_state["admin_page"] = page + 1
                st.rerun()
    
    with col5:
        if page < total_pages:
            if st.button("Last ⏭️", key="admin_last_page"):
                st.session_state["admin_page"] = total_pages
                st.rerun()


def render_spot_statistics(api: TuristandoAPI):
    """
    Render overall statistics dashboard.
    
    Args:
        api: API client instance.
    """
    st.subheader("📊 Platform Statistics")
    
    try:
        # Fetch total spots
        result = api.list_spots(skip=0, limit=1)
        total_spots = result.get("total", 0)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Spots", total_spots)
        
        with col2:
            # This would require a new API endpoint
            st.metric("Total Photos", "N/A")
        
        with col3:
            # This would require a new API endpoint
            st.metric("Total Ratings", "N/A")
        
        with col4:
            # This would require a new API endpoint  
            st.metric("Total Comments", "N/A")
        
        st.caption("💡 Tip: Add more analytics endpoints to get detailed statistics")
        
    except Exception as e:
        st.error(f"❌ Error loading statistics: {e}")
