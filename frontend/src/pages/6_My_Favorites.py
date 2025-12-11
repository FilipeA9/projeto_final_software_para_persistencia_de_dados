"""
My Favorites Page - Display user's favorite tourist spots.
"""

import streamlit as st
from services.api_client import TuristandoAPI

# Page configuration
st.set_page_config(
    page_title="My Favorites - Turistando",
    page_icon="❤️",
    layout="wide"
)

# Initialize API client
api = TuristandoAPI()

# Check authentication
if "token" not in st.session_state or not st.session_state.get("token"):
    st.warning("⚠️ Please login to view your favorites")
    st.info("You need to be logged in to save and view favorite tourist spots.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Go to Login", use_container_width=True):
            st.switch_page("pages/4_Login.py")
    with col2:
        if st.button("📝 Register Now", use_container_width=True):
            st.switch_page("pages/3_Register.py")
    
    st.stop()

# Page header
st.title("❤️ My Favorites")
st.caption(f"Favorite tourist spots for {st.session_state.get('username', 'you')}")

# Fetch favorites
try:
    with st.spinner("Loading your favorites..."):
        import requests
        
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        response = requests.get(
            "http://localhost:8000/api/favorites",
            headers=headers
        )
        
        if response.status_code == 200:
            favorites = response.json()
        else:
            st.error(f"❌ Error loading favorites: {response.status_code}")
            favorites = []
    
    if not favorites:
        st.info("📭 You haven't favorited any tourist spots yet!")
        st.markdown("""
        ### How to add favorites:
        1. Go to **Explore Spots** page
        2. Browse tourist attractions
        3. Click the **Favorite** button (🤍) on spots you like
        4. Come back here to see your collection!
        """)
        
        if st.button("🔍 Explore Tourist Spots", type="primary"):
            st.switch_page("pages/1_Explore_Spots.py")
    else:
        # Display favorites count
        st.markdown(f"### You have {len(favorites)} favorite spot{'s' if len(favorites) != 1 else ''}")
        
        # Add filters
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input(
                "🔍 Search favorites",
                placeholder="Search by name or location...",
                key="fav_search"
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                ["Most Recent", "Alphabetical (A-Z)", "Highest Rated"],
                key="fav_sort"
            )
        
        st.divider()
        
        # Filter favorites
        filtered_favorites = favorites
        
        if search_query:
            search_lower = search_query.lower()
            filtered_favorites = [
                fav for fav in favorites
                if search_lower in fav['spot_nome'].lower()
                or search_lower in fav['spot_cidade'].lower()
                or search_lower in fav['spot_estado'].lower()
            ]
        
        # Sort favorites
        if sort_by == "Alphabetical (A-Z)":
            filtered_favorites = sorted(filtered_favorites, key=lambda x: x['spot_nome'])
        elif sort_by == "Highest Rated":
            filtered_favorites = sorted(
                filtered_favorites,
                key=lambda x: x.get('spot_avg_rating') or 0,
                reverse=True
            )
        # Most Recent is already the default order from API
        
        if not filtered_favorites:
            st.info(f"No favorites found matching '{search_query}'")
        else:
            # Display favorites in grid
            for i in range(0, len(filtered_favorites), 2):
                cols = st.columns(2)
                
                for j, col in enumerate(cols):
                    if i + j < len(filtered_favorites):
                        fav = filtered_favorites[i + j]
                        
                        with col:
                            with st.container():
                                # Spot card
                                st.markdown(f"### 📍 {fav['spot_nome']}")
                                st.caption(f"{fav['spot_cidade']}, {fav['spot_estado']}, {fav['spot_pais']}")
                                
                                # Rating
                                if fav.get('spot_avg_rating'):
                                    rating_stars = "⭐" * int(fav['spot_avg_rating'])
                                    st.markdown(
                                        f"**Rating:** {rating_stars} "
                                        f"{fav['spot_avg_rating']:.1f} "
                                        f"({fav.get('spot_rating_count', 0)} reviews)"
                                    )
                                else:
                                    st.caption("_No ratings yet_")
                                
                                # Favorited date
                                st.caption(f"❤️ Favorited on: {fav['favorited_at'][:10]}")
                                
                                # Actions
                                col_view, col_unfav = st.columns([1, 1])
                                
                                with col_view:
                                    if st.button(
                                        "👁️ View Details",
                                        key=f"view_{fav['spot_id']}",
                                        use_container_width=True
                                    ):
                                        st.session_state["selected_spot_id"] = fav['spot_id']
                                        st.switch_page("pages/2_Spot_Details.py")
                                
                                with col_unfav:
                                    if st.button(
                                        "💔 Remove",
                                        key=f"unfav_{fav['spot_id']}",
                                        type="secondary",
                                        use_container_width=True
                                    ):
                                        # Confirm and remove
                                        try:
                                            response = requests.delete(
                                                f"http://localhost:8000/api/spots/{fav['spot_id']}/favorite",
                                                headers=headers
                                            )
                                            
                                            if response.status_code == 204:
                                                st.success(f"✅ Removed {fav['spot_nome']} from favorites")
                                                st.rerun()
                                            else:
                                                st.error("❌ Error removing favorite")
                                        except Exception as e:
                                            st.error(f"❌ Error: {str(e)}")
                                
                                st.divider()

except Exception as e:
    st.error(f"❌ Error loading favorites: {e}")
    st.info("Make sure the backend is running at http://localhost:8000")

# Sidebar info
with st.sidebar:
    st.markdown("---")
    st.markdown("### ❤️ About Favorites")
    st.caption("""
    Favorites let you save tourist spots you're interested in for quick access later.
    
    Your favorites are private and only visible to you.
    """)
    
    st.markdown("---")
    
    if st.button("🔍 Discover More Spots"):
        st.switch_page("pages/1_Explore_Spots.py")
