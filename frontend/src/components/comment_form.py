"""
Comment submission component.

Provides UI for submitting comments on tourist spots.
"""

import streamlit as st
from typing import Optional
from services.api_client import TuristandoAPI


def render_comment_form(
    api: TuristandoAPI,
    spot_id: int,
    token: Optional[str] = None
) -> bool:
    """
    Render comment submission form.
    
    Args:
        api: API client instance.
        spot_id: Tourist spot ID.
        token: User authentication token.
    
    Returns:
        True if comment was submitted successfully.
    """
    if not token:
        st.info("🔒 Please login to post a comment")
        return False
    
    with st.form(key=f"comment_form_{spot_id}"):
        st.subheader("💬 Add a Comment")
        
        # Comment text area
        texto = st.text_area(
            "Your Comment",
            max_chars=2000,
            height=150,
            placeholder="Share your thoughts, tips, or experiences about this place...",
            help="Maximum 2000 characters"
        )
        
        # Character counter
        char_count = len(texto)
        char_color = "red" if char_count > 2000 else "gray"
        st.caption(f":{char_color}[{char_count}/2000 characters]")
        
        # Submit button
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button(
                "Post Comment",
                use_container_width=True,
                type="primary"
            )
        with col2:
            st.form_submit_button("Cancel", use_container_width=True)
        
        if submitted:
            # Validate
            if not texto or len(texto.strip()) == 0:
                st.error("❌ Please enter a comment")
                return False
            
            if len(texto) > 2000:
                st.error("❌ Comment is too long (max 2000 characters)")
                return False
            
            try:
                # Submit comment
                result = api.create_comment(
                    spot_id=spot_id,
                    texto=texto,
                    token=token
                )
                st.success("✅ Comment posted successfully!")
                st.balloons()
                return True
                
            except Exception as e:
                error_msg = str(e)
                
                # Handle specific error cases
                if "404" in error_msg:
                    st.error("❌ Tourist spot not found.")
                elif "401" in error_msg or "403" in error_msg:
                    st.error("❌ Authentication error. Please login again.")
                elif "inappropriate" in error_msg.lower() or "moderation" in error_msg.lower():
                    st.error("❌ Your comment contains inappropriate content. Please revise and try again.")
                elif "400" in error_msg:
                    st.error("❌ Invalid input. Please check your comment.")
                else:
                    st.error(f"❌ Error posting comment: {error_msg}")
                
                return False
    
    return False


def render_comment_quick_form(
    api: TuristandoAPI,
    spot_id: int,
    token: Optional[str] = None,
    on_submit=None
):
    """
    Render a compact inline comment form.
    
    Args:
        api: API client instance.
        spot_id: Tourist spot ID.
        token: User authentication token.
        on_submit: Callback function to call after successful submission.
    """
    if not token:
        st.info("💬 Login to join the conversation")
        return
    
    # Quick comment input
    texto = st.text_input(
        "Add a comment...",
        max_chars=2000,
        placeholder="Share your thoughts...",
        key=f"quick_comment_{spot_id}"
    )
    
    if st.button("Post", key=f"quick_comment_btn_{spot_id}", type="primary"):
        if not texto or len(texto.strip()) == 0:
            st.warning("Please enter a comment")
            return
        
        try:
            result = api.create_comment(
                spot_id=spot_id,
                texto=texto,
                token=token
            )
            st.success("✅ Comment posted!")
            
            # Call callback if provided
            if on_submit:
                on_submit()
            
            # Rerun to show new comment
            st.rerun()
            
        except Exception as e:
            error_msg = str(e)
            if "inappropriate" in error_msg.lower() or "moderation" in error_msg.lower():
                st.error("❌ Comment contains inappropriate content")
            else:
                st.error(f"❌ Error: {error_msg}")
