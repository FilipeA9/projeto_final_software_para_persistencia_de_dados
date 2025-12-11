"""
Comments list component.

Displays comments for tourist spots with sorting and pagination.
"""

import streamlit as st
from typing import Optional
from datetime import datetime
from services.api_client import TuristandoAPI


def render_comments_list(
    api: TuristandoAPI,
    spot_id: int,
    page: int = 1,
    per_page: int = 20,
    ordenacao: str = "recentes"
):
    """
    Render comments list with pagination and sorting.
    
    Args:
        api: API client instance.
        spot_id: Tourist spot ID.
        page: Current page number.
        per_page: Items per page.
        ordenacao: Sort order (recentes, antigas, mais_curtidos).
    """
    try:
        # Fetch comments
        response = api.get_spot_comments(
            spot_id=spot_id,
            page=page,
            per_page=per_page,
            ordenacao=ordenacao
        )
        
        comments = response.get("comments", [])
        pagination = response.get("pagination", {})
        total = pagination.get("total", 0)
        
        # Header with count
        st.subheader(f"💬 Comments ({total})")
        
        if total == 0:
            st.info("No comments yet. Be the first to share your thoughts!")
            return
        
        # Sorting options
        col1, col2 = st.columns([2, 1])
        with col1:
            sort_option = st.selectbox(
                "Sort by",
                options=["recentes", "antigas", "mais_curtidos"],
                format_func=lambda x: {
                    "recentes": "Most Recent",
                    "antigas": "Oldest First",
                    "mais_curtidos": "Most Liked"
                }[x],
                index=["recentes", "antigas", "mais_curtidos"].index(ordenacao),
                key=f"sort_comments_{spot_id}"
            )
        
        # If sort changed, update
        if sort_option != ordenacao:
            st.rerun()
        
        # Display comments
        for comment in comments:
            render_comment_card(api, comment)
        
        # Pagination
        if total > per_page:
            render_pagination(pagination, spot_id)
        
    except Exception as e:
        st.error(f"❌ Error loading comments: {e}")


def render_comment_card(api: TuristandoAPI, comment: dict):
    """
    Render a single comment card.
    
    Args:
        api: API client instance.
        comment: Comment data dictionary.
    """
    with st.container():
        # Header: User and date
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # User info
            usuario = comment.get("usuario", {})
            username = usuario.get("login", f"User {comment.get('usuarioId', 'Unknown')}")
            st.markdown(f"**{username}**")
        
        with col2:
            # Date
            try:
                created_at = datetime.fromisoformat(comment["createdAt"].replace("Z", "+00:00"))
                date_str = created_at.strftime("%b %d, %Y %H:%M")
                st.caption(date_str)
            except:
                st.caption("Recently")
        
        with col3:
            # Likes counter
            metadata = comment.get("metadata", {})
            likes = metadata.get("likes", 0)
            st.caption(f"👍 {likes}")
        
        # Comment text
        texto = comment.get("texto", "")
        st.write(texto)
        
        # Actions
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            # Like button
            if st.button("👍 Like", key=f"like_{comment['_id']}", use_container_width=True):
                try:
                    api.like_comment(comment["_id"])
                    st.success("Liked!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col2:
            # Report button
            if st.button("🚩 Report", key=f"report_{comment['_id']}", use_container_width=True):
                try:
                    api.report_comment(comment["_id"])
                    st.warning("Comment reported for moderation")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.divider()


def render_pagination(pagination: dict, spot_id: int):
    """
    Render pagination controls.
    
    Args:
        pagination: Pagination metadata.
        spot_id: Tourist spot ID.
    """
    page = pagination.get("page", 1)
    per_page = pagination.get("perPage", 20)
    total = pagination.get("total", 0)
    
    total_pages = (total + per_page - 1) // per_page
    
    if total_pages <= 1:
        return
    
    st.divider()
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if page > 1:
            if st.button("⏮️ First", key=f"first_page_{spot_id}"):
                st.session_state[f"comment_page_{spot_id}"] = 1
                st.rerun()
    
    with col2:
        if page > 1:
            if st.button("◀️ Prev", key=f"prev_page_{spot_id}"):
                st.session_state[f"comment_page_{spot_id}"] = page - 1
                st.rerun()
    
    with col3:
        st.markdown(f"<div style='text-align: center; padding-top: 8px;'>Page {page} of {total_pages}</div>", unsafe_allow_html=True)
    
    with col4:
        if page < total_pages:
            if st.button("Next ▶️", key=f"next_page_{spot_id}"):
                st.session_state[f"comment_page_{spot_id}"] = page + 1
                st.rerun()
    
    with col5:
        if page < total_pages:
            if st.button("Last ⏭️", key=f"last_page_{spot_id}"):
                st.session_state[f"comment_page_{spot_id}"] = total_pages
                st.rerun()


def render_compact_comments(
    api: TuristandoAPI,
    spot_id: int,
    max_comments: int = 3
):
    """
    Render a compact comments preview.
    
    Args:
        api: API client instance.
        spot_id: Tourist spot ID.
        max_comments: Maximum number of comments to show.
    """
    try:
        response = api.get_spot_comments(
            spot_id=spot_id,
            page=1,
            per_page=max_comments,
            ordenacao="recentes"
        )
        
        comments = response.get("comments", [])
        total = response.get("pagination", {}).get("total", 0)
        
        if total == 0:
            st.caption("No comments yet")
            return
        
        st.caption(f"💬 {total} comment{'s' if total != 1 else ''}")
        
        for comment in comments[:max_comments]:
            # Simple comment display
            usuario = comment.get("usuario", {})
            username = usuario.get("login", f"User {comment.get('usuarioId')}")
            texto = comment.get("texto", "")
            
            # Truncate long comments
            if len(texto) > 150:
                texto = texto[:147] + "..."
            
            st.markdown(f"**{username}**: {texto}")
        
        if total > max_comments:
            st.caption(f"... and {total - max_comments} more")
        
    except Exception as e:
        st.caption(f"Error loading comments: {e}")
