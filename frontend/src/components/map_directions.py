"""
Map Directions Component - Display location and directions for tourist spots.

Shows interactive map links, coordinates, and distance information.
"""

import streamlit as st
from typing import Optional, Dict, Any


def display_directions(
    spot_id: int,
    spot_name: str,
    api_client,
    user_location: Optional[tuple] = None,
):
    """
    Display directions and location information for a tourist spot.
    
    Args:
        spot_id: ID of the tourist spot
        spot_name: Name of the spot
        api_client: API client instance for making requests
        user_location: Optional tuple of (latitude, longitude) for user's location
    """
    st.subheader("📍 Location & Directions")
    
    # Fetch directions information
    try:
        params = {}
        if user_location:
            params["from_latitude"] = user_location[0]
            params["from_longitude"] = user_location[1]
        
        response = api_client.get(f"/spots/{spot_id}/directions", params=params)
        
        if response.status_code == 200:
            directions = response.json()
            
            # Display coordinates
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Latitude", 
                    f"{directions['coordinates']['latitude']:.6f}"
                )
            with col2:
                st.metric(
                    "Longitude", 
                    f"{directions['coordinates']['longitude']:.6f}"
                )
            
            # Display address
            location = directions["location"]
            st.write("**Address:**")
            st.write(f"{location['address']}")
            st.write(f"{location['city']}, {location['state']}, {location['country']}")
            
            # Display distance if calculated
            if "distance" in directions:
                st.info(f"📏 Distance from your location: **{directions['distance']['text']}**")
            
            # Google Maps links
            st.write("---")
            st.write("**🗺️ Open in Maps:**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.link_button(
                    "View Location",
                    directions["googleMapsUrl"],
                    use_container_width=True,
                )
            with col2:
                st.link_button(
                    "Get Directions",
                    directions["googleMapsDirectionsUrl"],
                    use_container_width=True,
                )
            
            # Text directions
            with st.expander("📝 Text Directions", expanded=False):
                for i, instruction in enumerate(directions["textDirections"], 1):
                    st.write(f"{i}. {instruction}")
                    
        else:
            st.error(f"Failed to fetch directions: {response.status_code}")
            
    except Exception as e:
        st.error(f"Error loading directions: {str(e)}")


def display_map_with_marker(latitude: float, longitude: float, spot_name: str):
    """
    Display a simple map with a marker using Streamlit's map feature.
    
    Args:
        latitude: Spot latitude
        longitude: Spot longitude
        spot_name: Name of the spot for tooltip
    """
    import pandas as pd
    
    # Create dataframe for map
    map_data = pd.DataFrame({
        'lat': [latitude],
        'lon': [longitude],
    })
    
    st.map(map_data, zoom=13)


def get_user_location_input() -> Optional[tuple]:
    """
    Display input fields for user to enter their current location.
    
    Returns:
        Tuple of (latitude, longitude) if both provided, None otherwise
    """
    st.write("**Calculate distance from your location:**")
    
    col1, col2 = st.columns(2)
    with col1:
        user_lat = st.number_input(
            "Your Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=None,
            step=0.0001,
            format="%.6f",
            help="Enter your current latitude (e.g., -23.550520)",
        )
    with col2:
        user_lon = st.number_input(
            "Your Longitude",
            min_value=-180.0,
            max_value=180.0,
            value=None,
            step=0.0001,
            format="%.6f",
            help="Enter your current longitude (e.g., -46.633308)",
        )
    
    if user_lat is not None and user_lon is not None:
        return (user_lat, user_lon)
    return None


def display_directions_card(
    spot_id: int,
    spot_name: str,
    latitude: float,
    longitude: float,
    api_client,
):
    """
    Display a compact directions card with expand option.
    
    Args:
        spot_id: ID of the tourist spot
        spot_name: Name of the spot
        latitude: Spot latitude
        longitude: Spot longitude
        api_client: API client instance
    """
    with st.expander("📍 Location & Directions", expanded=True):
        # Show map
        display_map_with_marker(latitude, longitude, spot_name)
        
        st.write("---")
        
        # Get user location for distance calculation
        user_location = get_user_location_input()
        
        if user_location:
            if st.button("Calculate Distance", key=f"calc_distance_{spot_id}"):
                display_directions(spot_id, spot_name, api_client, user_location)
        else:
            # Show directions without distance
            display_directions(spot_id, spot_name, api_client)


def display_compact_map_link(
    latitude: float,
    longitude: float,
    spot_name: str,
):
    """
    Display a compact link to open location in Google Maps.
    
    Args:
        latitude: Spot latitude
        longitude: Spot longitude
        spot_name: Name for the tooltip
    """
    maps_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
    st.markdown(
        f"📍 [View **{spot_name}** on Google Maps]({maps_url})",
        unsafe_allow_html=False,
    )


def display_distance_badge(distance_km: float):
    """
    Display a badge showing distance.
    
    Args:
        distance_km: Distance in kilometers
    """
    if distance_km < 1:
        st.caption(f"📏 {distance_km * 1000:.0f} meters away")
    elif distance_km < 10:
        st.caption(f"📏 {distance_km:.1f} km away")
    else:
        st.caption(f"📏 {distance_km:.0f} km away")
