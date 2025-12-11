"""
Photo upload component for tourist spots.

Provides UI for uploading and managing photos (admin only).
"""

import streamlit as st
from typing import Optional
from services.api_client import TuristandoAPI
import base64


def render_photo_upload(
    api: TuristandoAPI,
    spot_id: int,
    token: str
) -> bool:
    """
    Render photo upload form.
    
    Args:
        api: API client instance.
        spot_id: Tourist spot ID.
        token: Admin authentication token.
    
    Returns:
        True if photo was uploaded successfully.
    """
    st.subheader("📸 Upload Photo")
    
    with st.form(key=f"photo_upload_{spot_id}"):
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a photo",
            type=["jpg", "jpeg", "png", "webp"],
            help="Supported formats: JPG, PNG, WebP. Max size: 5MB"
        )
        
        # Photo title
        titulo = st.text_input(
            "Photo Title (optional)",
            max_chars=255,
            placeholder="e.g., Sunset view from the top"
        )
        
        # Preview
        if uploaded_file:
            st.image(uploaded_file, caption="Preview", use_column_width=True)
            
            # File info
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.caption(f"File: {uploaded_file.name} ({file_size_mb:.2f} MB)")
            
            if file_size_mb > 5:
                st.warning("⚠️ File size exceeds 5MB limit")
        
        # Submit button
        submitted = st.form_submit_button("📤 Upload Photo", use_container_width=True, type="primary")
        
        if submitted:
            if not uploaded_file:
                st.error("❌ Please select a photo to upload")
                return False
            
            # Check file size
            if uploaded_file.size > 5 * 1024 * 1024:
                st.error("❌ File size exceeds 5MB limit")
                return False
            
            try:
                # Upload photo using multipart/form-data
                import requests
                
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                }
                
                data = {}
                if titulo:
                    data["titulo"] = titulo
                
                response = requests.post(
                    f"{api.base_url}{api.api_prefix}/spots/{spot_id}/photos",
                    files=files,
                    data=data,
                    headers={"Authorization": f"Bearer {token}"}
                )
                response.raise_for_status()
                
                st.success("✅ Photo uploaded successfully!")
                st.balloons()
                return True
                
            except Exception as e:
                error_msg = str(e)
                
                if "403" in error_msg:
                    st.error("❌ Admin access required")
                elif "401" in error_msg:
                    st.error("❌ Authentication error. Please login again.")
                elif "404" in error_msg:
                    st.error("❌ Tourist spot not found")
                elif "400" in error_msg:
                    st.error("❌ Invalid file format or data")
                else:
                    st.error(f"❌ Error uploading photo: {error_msg}")
                
                return False
    
    return False


def render_photo_gallery_manager(
    api: TuristandoAPI,
    spot_id: int,
    token: str
):
    """
    Render photo gallery with delete functionality.
    
    Args:
        api: API client instance.
        spot_id: Tourist spot ID.
        token: Admin authentication token.
    """
    st.subheader("🖼️ Photo Gallery Management")
    
    try:
        # Fetch photos
        photos = api.get_spot_photos(spot_id)
        
        if not photos:
            st.info("No photos yet. Upload the first one!")
            return
        
        st.caption(f"Total photos: {len(photos)}")
        
        # Display photos in grid
        cols_per_row = 3
        for i in range(0, len(photos), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                idx = i + j
                if idx < len(photos):
                    photo = photos[idx]
                    
                    with col:
                        # Display photo
                        st.image(photo["thumbnail_url"], use_column_width=True)
                        
                        # Photo info
                        if photo.get("titulo"):
                            st.caption(f"📝 {photo['titulo']}")
                        
                        st.caption(f"ID: {photo['id'][:8]}...")
                        
                        # Delete button
                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_photo_{photo['id']}",
                            use_container_width=True
                        ):
                            try:
                                import requests
                                response = requests.delete(
                                    f"{api.base_url}{api.api_prefix}/photos/{photo['id']}",
                                    headers={"Authorization": f"Bearer {token}"}
                                )
                                response.raise_for_status()
                                st.success("Photo deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
        
    except Exception as e:
        st.error(f"❌ Error loading photos: {e}")


def render_batch_upload(
    api: TuristandoAPI,
    spot_id: int,
    token: str
):
    """
    Render batch photo upload (multiple files at once).
    
    Args:
        api: API client instance.
        spot_id: Tourist spot ID.
        token: Admin authentication token.
    """
    st.subheader("📸 Batch Photo Upload")
    
    uploaded_files = st.file_uploader(
        "Choose multiple photos",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        help="Upload up to 10 photos at once. Max 5MB each."
    )
    
    if uploaded_files:
        st.caption(f"Selected: {len(uploaded_files)} photos")
        
        # Show previews
        if len(uploaded_files) <= 5:
            cols = st.columns(len(uploaded_files))
            for i, (col, file) in enumerate(zip(cols, uploaded_files)):
                with col:
                    st.image(file, caption=file.name, use_column_width=True)
        else:
            st.caption("Preview limited to first 5 photos")
        
        if st.button("📤 Upload All Photos", type="primary"):
            if len(uploaded_files) > 10:
                st.error("❌ Maximum 10 photos per batch")
                return
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            success_count = 0
            for i, file in enumerate(uploaded_files):
                try:
                    # Check size
                    if file.size > 5 * 1024 * 1024:
                        status_text.warning(f"⚠️ Skipped {file.name} (too large)")
                        continue
                    
                    # Upload
                    import requests
                    files = {"file": (file.name, file.getvalue(), file.type)}
                    
                    response = requests.post(
                        f"{api.base_url}{api.api_prefix}/spots/{spot_id}/photos",
                        files=files,
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    response.raise_for_status()
                    
                    success_count += 1
                    status_text.success(f"✅ Uploaded {file.name}")
                    
                except Exception as e:
                    status_text.error(f"❌ Failed {file.name}: {e}")
                
                # Update progress
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            st.success(f"✅ Successfully uploaded {success_count}/{len(uploaded_files)} photos!")
            
            if success_count > 0:
                st.balloons()
