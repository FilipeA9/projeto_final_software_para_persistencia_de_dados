"""
Spot management form component.

Provides UI for creating and editing tourist spots (admin only).
"""

import streamlit as st
from typing import Optional
from decimal import Decimal
from services.api_client import TuristandoAPI


def render_spot_form(
    api: TuristandoAPI,
    token: str,
    spot_data: Optional[dict] = None
) -> bool:
    """
    Render spot creation/edit form.
    
    Args:
        api: API client instance.
        token: Admin authentication token.
        spot_data: Existing spot data for editing (None for new spot).
    
    Returns:
        True if spot was saved successfully.
    """
    is_edit = spot_data is not None
    form_title = "✏️ Edit Tourist Spot" if is_edit else "➕ Create New Tourist Spot"
    
    with st.form(key=f"spot_form_{spot_data['id'] if is_edit else 'new'}"):
        st.subheader(form_title)
        
        # Basic Information
        st.markdown("### 📝 Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input(
                "Spot Name *",
                value=spot_data.get("nome", "") if is_edit else "",
                max_chars=255,
                placeholder="e.g., Cristo Redentor"
            )
        
        with col2:
            endereco = st.text_input(
                "Full Address *",
                value=spot_data.get("endereco", "") if is_edit else "",
                placeholder="Street, number, district"
            )
        
        descricao = st.text_area(
            "Description *",
            value=spot_data.get("descricao", "") if is_edit else "",
            height=150,
            placeholder="Detailed description of the tourist spot..."
        )
        
        # Location
        st.markdown("### 📍 Location")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cidade = st.text_input(
                "City *",
                value=spot_data.get("cidade", "") if is_edit else "",
                max_chars=100,
                placeholder="e.g., Rio de Janeiro"
            )
        
        with col2:
            estado = st.text_input(
                "State *",
                value=spot_data.get("estado", "") if is_edit else "",
                max_chars=100,
                placeholder="e.g., RJ"
            )
        
        with col3:
            pais = st.text_input(
                "Country *",
                value=spot_data.get("pais", "") if is_edit else "",
                max_chars=100,
                placeholder="e.g., Brasil"
            )
        
        # Coordinates
        st.markdown("### 🗺️ Coordinates")
        st.caption("Use Google Maps to find accurate coordinates")
        
        col1, col2 = st.columns(2)
        
        with col1:
            latitude = st.number_input(
                "Latitude *",
                value=float(spot_data.get("latitude", 0)) if is_edit else 0.0,
                min_value=-90.0,
                max_value=90.0,
                format="%.6f",
                help="Latitude between -90 and 90"
            )
        
        with col2:
            longitude = st.number_input(
                "Longitude *",
                value=float(spot_data.get("longitude", 0)) if is_edit else 0.0,
                min_value=-180.0,
                max_value=180.0,
                format="%.6f",
                help="Longitude between -180 and 180"
            )
        
        # Map preview link
        if latitude != 0 and longitude != 0:
            maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
            st.markdown(f"[🗺️ Preview on Google Maps]({maps_url})")
        
        st.divider()
        
        # Submit buttons
        col1, col2 = st.columns([1, 3])
        
        with col1:
            submitted = st.form_submit_button(
                "💾 Save Spot" if is_edit else "➕ Create Spot",
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            if st.form_submit_button("Cancel", use_container_width=True):
                return False
        
        if submitted:
            # Validate required fields
            if not all([nome, descricao, cidade, estado, pais, endereco]):
                st.error("❌ Please fill all required fields (marked with *)")
                return False
            
            if latitude == 0 and longitude == 0:
                st.error("❌ Please provide valid coordinates")
                return False
            
            try:
                # Prepare data
                spot_payload = {
                    "nome": nome,
                    "descricao": descricao,
                    "cidade": cidade,
                    "estado": estado,
                    "pais": pais,
                    "latitude": str(latitude),
                    "longitude": str(longitude),
                    "endereco": endereco
                }
                
                if is_edit:
                    # Update existing spot
                    import requests
                    response = requests.put(
                        f"{api.base_url}{api.api_prefix}/spots/{spot_data['id']}",
                        json=spot_payload,
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    response.raise_for_status()
                    st.success("✅ Spot updated successfully!")
                else:
                    # Create new spot
                    import requests
                    response = requests.post(
                        f"{api.base_url}{api.api_prefix}/spots",
                        json=spot_payload,
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    response.raise_for_status()
                    st.success("✅ Spot created successfully!")
                
                st.balloons()
                return True
                
            except Exception as e:
                error_msg = str(e)
                
                if "403" in error_msg:
                    st.error("❌ Admin access required")
                elif "401" in error_msg:
                    st.error("❌ Authentication error. Please login again.")
                elif "400" in error_msg:
                    st.error("❌ Invalid input data. Please check all fields.")
                else:
                    st.error(f"❌ Error saving spot: {error_msg}")
                
                return False
    
    return False


def render_quick_spot_preview(spot: dict):
    """
    Render a quick preview card for a spot.
    
    Args:
        spot: Spot data dictionary.
    """
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{spot['nome']}**")
            st.caption(f"📍 {spot['cidade']}, {spot['estado']}, {spot['pais']}")
            
            # Truncate description
            desc = spot.get('descricao', '')
            if len(desc) > 100:
                desc = desc[:97] + "..."
            st.caption(desc)
        
        with col2:
            # Stats
            avg_rating = spot.get('avg_rating')
            if avg_rating:
                st.metric("Rating", f"{avg_rating:.1f}⭐")
            else:
                st.caption("No ratings")
