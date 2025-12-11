"""
Rating submission form component.

Provides UI for submitting and editing ratings for tourist spots.
"""

import streamlit as st
from typing import Optional
from services.api_client import TuristandoAPI


def render_rating_form(
    api: TuristandoAPI,
    spot_id: int,
    token: Optional[str] = None,
    existing_rating: Optional[dict] = None
) -> bool:
    """
    Render rating submission/edit form.
    
    Args:
        api: API client instance.
        spot_id: Tourist spot ID.
        token: User authentication token.
        existing_rating: Existing rating to edit (if any).
    
    Returns:
        True if rating was submitted successfully.
    """
    if not token:
        st.info("🔒 Please login to submit a rating")
        return False
    
    # Determine if this is an edit or new rating
    is_edit = existing_rating is not None
    form_title = "✏️ Edit Your Rating" if is_edit else "⭐ Rate This Spot"
    
    with st.form(key=f"rating_form_{spot_id}"):
        st.subheader(form_title)
        
        # Rating slider (1-5 stars)
        default_rating = existing_rating.get("nota", 5) if is_edit else 5
        nota = st.slider(
            "Rating",
            min_value=1,
            max_value=5,
            value=default_rating,
            help="Select your rating from 1 (poor) to 5 (excellent)"
        )
        
        # Display star visualization
        star_display = "⭐" * nota + "☆" * (5 - nota)
        st.markdown(f"### {star_display}")
        
        # Optional comment
        default_comment = existing_rating.get("comentario", "") if is_edit else ""
        comentario = st.text_area(
            "Review Comment (optional)",
            value=default_comment,
            max_chars=1000,
            height=150,
            placeholder="Share your experience at this tourist spot...",
            help="Maximum 1000 characters"
        )
        
        # Submit button
        submit_label = "Update Rating" if is_edit else "Submit Rating"
        submitted = st.form_submit_button(submit_label, use_container_width=True)
        
        if submitted:
            try:
                if is_edit:
                    # Update existing rating
                    rating_id = existing_rating["id"]
                    result = api.update_rating(
                        rating_id=rating_id,
                        nota=nota,
                        comentario=comentario if comentario else None,
                        token=token
                    )
                    st.success("✅ Rating updated successfully!")
                else:
                    # Create new rating
                    result = api.create_rating(
                        spot_id=spot_id,
                        nota=nota,
                        comentario=comentario if comentario else None,
                        token=token
                    )
                    st.success("✅ Rating submitted successfully!")
                
                st.balloons()
                return True
                
            except Exception as e:
                error_msg = str(e)
                
                # Handle specific error cases
                if "409" in error_msg or "already rated" in error_msg.lower():
                    st.error("❌ You have already rated this spot. Please edit your existing rating.")
                elif "404" in error_msg:
                    st.error("❌ Tourist spot not found.")
                elif "401" in error_msg or "403" in error_msg:
                    st.error("❌ Authentication error. Please login again.")
                elif "400" in error_msg:
                    st.error("❌ Invalid input. Please check your rating and comment.")
                else:
                    st.error(f"❌ Error submitting rating: {error_msg}")
                
                return False
    
    return False


def render_rating_display(rating: dict):
    """
    Display a single rating in a card format.
    
    Args:
        rating: Rating data dictionary.
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Star display
        stars = "⭐" * rating["nota"] + "☆" * (5 - rating["nota"])
        st.markdown(f"**{stars}** ({rating['nota']}/5)")
        
        # Comment (if exists)
        if rating.get("comentario"):
            st.write(rating["comentario"])
        else:
            st.caption("_No comment provided_")
    
    with col2:
        # User and date
        st.caption(f"User ID: {rating['usuario_id']}")
        
        # Format date
        from datetime import datetime
        try:
            created_at = datetime.fromisoformat(rating["created_at"].replace("Z", "+00:00"))
            date_str = created_at.strftime("%b %d, %Y")
            st.caption(f"Posted: {date_str}")
        except:
            st.caption("Posted recently")
    
    st.divider()


def render_rating_statistics(stats: dict):
    """
    Display rating statistics with distribution chart.
    
    Args:
        stats: Rating statistics dictionary.
    """
    st.subheader("📊 Rating Statistics")
    
    # Average and total
    col1, col2 = st.columns(2)
    with col1:
        avg = stats.get("average", 0) or 0
        st.metric("Average Rating", f"{avg:.2f} / 5.0")
    with col2:
        total = stats.get("total", 0)
        st.metric("Total Ratings", total)
    
    if total > 0:
        # Distribution chart
        st.subheader("Rating Distribution")
        
        # Prepare data for chart
        distribution_data = {
            "5 ⭐": stats.get("5", 0),
            "4 ⭐": stats.get("4", 0),
            "3 ⭐": stats.get("3", 0),
            "2 ⭐": stats.get("2", 0),
            "1 ⭐": stats.get("1", 0),
        }
        
        # Display as horizontal bars
        for label, count in distribution_data.items():
            percentage = (count / total * 100) if total > 0 else 0
            st.progress(percentage / 100, text=f"{label}: {count} ({percentage:.1f}%)")
