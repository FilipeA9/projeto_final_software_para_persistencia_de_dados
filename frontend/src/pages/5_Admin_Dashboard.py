"""
Admin Dashboard - Management interface for tourist spots.

Admin-only page for creating, editing, and managing tourist spots and photos.
"""

import streamlit as st
from services.api_client import TuristandoAPI
from components.spot_form import render_spot_form
from components.photo_upload import render_photo_upload, render_photo_gallery_manager, render_batch_upload
from components.spot_management import render_spot_management_list, render_spot_statistics

# Page configuration
st.set_page_config(
    page_title="Admin Dashboard - Turistando",
    page_icon="🔧",
    layout="wide"
)

# Initialize API client
api = TuristandoAPI()

# Check authentication and admin role
if "token" not in st.session_state or not st.session_state.get("token"):
    st.warning("⚠️ Please login to access the admin dashboard")
    st.stop()

if st.session_state.get("user_role") != "ADMIN":
    st.error("🚫 Admin access required")
    st.caption("This page is only accessible to administrators.")
    st.stop()

# Page header
st.title("🔧 Admin Dashboard")
st.caption(f"Welcome, {st.session_state.get('username', 'Admin')}")

# Tabs for different admin functions
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Statistics",
    "🗺️ Manage Spots",
    "➕ Create New Spot",
    "📸 Manage Photos",
    "🏨 Accommodations",
    "📦 Import/Export"
])

# Tab 1: Statistics
with tab1:
    render_spot_statistics(api)
    
    st.divider()
    
    st.subheader("🔍 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Create New Spot", key="quick_create", use_container_width=True):
            st.session_state["active_tab"] = "Create New Spot"
            st.rerun()
    
    with col2:
        if st.button("🗺️ Manage All Spots", key="quick_manage", use_container_width=True):
            st.session_state["active_tab"] = "Manage Spots"
            st.rerun()
    
    with col3:
        if st.button("📸 Upload Photos", key="quick_photos", use_container_width=True):
            st.session_state["active_tab"] = "Manage Photos"
            st.rerun()

# Tab 2: Manage Spots
with tab2:
    page = st.session_state.get("admin_page", 1)
    render_spot_management_list(api, st.session_state["token"], page=page, per_page=10)

# Tab 3: Create New Spot
with tab3:
    if render_spot_form(api, st.session_state["token"], spot_data=None):
        st.info("✅ Spot created! Go to 'Manage Spots' tab to see it.")

# Tab 4: Manage Photos
with tab4:
    st.subheader("📸 Photo Management")
    
    # Spot selector
    st.markdown("### Select a Spot")
    
    try:
        # Fetch spots for selection
        result = api.list_spots(skip=0, limit=100)
        spots = result.get("spots", [])
        
        if not spots:
            st.info("No spots available. Create a spot first in the 'Create New Spot' tab.")
        else:
            # Spot selection
            spot_options = {f"{spot['nome']} ({spot['cidade']})": spot['id'] for spot in spots}
            selected_spot_name = st.selectbox(
                "Choose a tourist spot",
                options=list(spot_options.keys())
            )
            
            if selected_spot_name:
                selected_spot_id = spot_options[selected_spot_name]
                
                st.divider()
                
                # Photo upload section
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    render_photo_upload(api, selected_spot_id, st.session_state["token"])
                
                with col2:
                    render_batch_upload(api, selected_spot_id, st.session_state["token"])
                
                st.divider()
                
                # Photo gallery management
                render_photo_gallery_manager(api, selected_spot_id, st.session_state["token"])
    
    except Exception as e:
        st.error(f"❌ Error loading spots: {e}")

# Tab 5: Accommodations Management
with tab5:
    st.header("🏨 Accommodation Management")
    st.caption("Add and manage accommodations for tourist spots")
    
    try:
        # Get all spots for selection
        spots = api.list_spots(limit=1000)
        
        if spots['spots']:
            # Spot selector
            spot_options = {spot['nome']: spot['id'] for spot in spots['spots']}
            selected_spot_name = st.selectbox(
                "Select a Tourist Spot",
                options=[""] + list(spot_options.keys()),
                key="acc_spot_select"
            )
            
            if selected_spot_name:
                selected_spot_id = spot_options[selected_spot_name]
                
                st.divider()
                
                # Show accommodations
                try:
                    accommodations_data = api.get_spot_accommodations(selected_spot_id)
                    accommodations = accommodations_data.get('accommodations', [])
                    
                    # Statistics
                    try:
                        stats = api.get_accommodation_statistics(selected_spot_id)
                        from components.accommodation_card import render_accommodation_statistics
                        render_accommodation_statistics(stats)
                        st.divider()
                    except:
                        pass
                    
                    # Add accommodation form
                    from components.accommodation_form import render_accommodation_form
                    
                    with st.expander("➕ Add New Accommodation", expanded=len(accommodations) == 0):
                        if render_accommodation_form(selected_spot_id):
                            st.success("✅ Accommodation added!")
                            st.rerun()
                    
                    st.divider()
                    
                    # List accommodations
                    st.subheader(f"Accommodations ({len(accommodations)})")
                    
                    if accommodations:
                        from components.accommodation_card import render_accommodation_card
                        
                        for accommodation in accommodations:
                            # Check if editing
                            if st.session_state.get(f"editing_acc_{accommodation['id']}"):
                                with st.expander(f"✏️ Editing: {accommodation['nome']}", expanded=True):
                                    if render_accommodation_form(
                                        selected_spot_id,
                                        accommodation['id'],
                                        accommodation
                                    ):
                                        st.success("✅ Accommodation updated!")
                                        st.rerun()
                            else:
                                result = render_accommodation_card(accommodation, show_actions=True)
                                
                                # Handle delete
                                if result == "delete":
                                    try:
                                        api.delete_accommodation(
                                            accommodation['id'],
                                            st.session_state["token"]
                                        )
                                        st.success(f"✅ Deleted {accommodation['nome']}")
                                        # Clear confirmation state
                                        if f"confirm_delete_acc_{accommodation['id']}" in st.session_state:
                                            del st.session_state[f"confirm_delete_acc_{accommodation['id']}"]
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error deleting: {e}")
                            
                            st.divider()
                    else:
                        st.info("📭 No accommodations yet. Add one above!")
                
                except Exception as e:
                    st.error(f"❌ Error loading accommodations: {e}")
        else:
            st.info("No tourist spots available. Create spots first in the 'Create New Spot' tab.")
    
    except Exception as e:
        st.error(f"❌ Error loading spots: {e}")

# Tab 6: Import/Export
with tab6:
    st.header("📦 Data Import/Export")
    st.caption("Backup and restore tourist spot data")
    
    # Export section
    st.subheader("📥 Export Data")
    from components.export_button import render_export_button
    render_export_button(api.client)
    
    st.divider()
    
    # Import section
    st.subheader("📤 Import Data")
    from components.import_form import render_import_form, render_import_examples
    
    # Show examples first
    render_import_examples()
    
    st.divider()
    
    # Import form
    render_import_form(api.client)
    
    st.divider()
    
    # Information
    with st.expander("ℹ️ About Import/Export", expanded=False):
        st.markdown("""
        ### Export Features
        - Export all tourist spots to **JSON** or **CSV** format
        - Apply filters (city, state, country) to export specific data
        - Include metadata (export timestamp, record count)
        - Download directly to your computer
        
        ### Import Features
        - Import tourist spots from **JSON** or **CSV** files
        - Automatic validation of required fields
        - Error reporting for invalid records
        - Detailed summary of import results
        
        ### Use Cases
        - **Backup**: Export data regularly for backup purposes
        - **Migration**: Export from one environment, import to another
        - **Bulk Creation**: Create many spots using CSV/JSON files
        - **Data Analysis**: Export to CSV for analysis in Excel/Python
        
        ### Important Notes
        - ⚠️ Imported spots will be created with your user as the creator
        - ⚠️ Duplicate spots may be created if you import existing data
        - ⚠️ Invalid records will be skipped with error messages
        - ✅ All operations are logged for audit purposes
        """)

# Sidebar info
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔧 Admin Tools")
    st.caption("You have full access to:")
    st.markdown("""
    - ➕ Create new tourist spots
    - ✏️ Edit existing spots
    - 🗑️ Delete spots (soft delete)
    - 📸 Upload and manage photos
    - 📊 View platform statistics
    """)
    
    st.markdown("---")
    st.caption("⚠️ **Important**: Changes affect all users immediately. Use with caution.")
