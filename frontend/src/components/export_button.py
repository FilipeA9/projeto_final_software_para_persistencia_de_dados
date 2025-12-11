"""
Export Button Component - Allow admins to export tourist spot data.

Provides UI for exporting spots in JSON or CSV format.
"""

import streamlit as st
from typing import Optional


def render_export_button(
    api_client,
    button_text: str = "📥 Export Data",
    container_width: bool = False,
):
    """
    Render an export button with format selection.
    
    Args:
        api_client: API client instance
        button_text: Text for the export button
        container_width: Whether button should use full container width
    """
    with st.expander("📥 Export Tourist Spots", expanded=False):
        st.write("Export all tourist spot data to JSON or CSV format.")
        
        # Format selection
        export_format = st.selectbox(
            "Select Format",
            options=["json", "csv"],
            format_func=lambda x: f"{x.upper()} Format",
            key="export_format_selector",
        )
        
        # Optional filters
        st.write("**Optional Filters:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_cidade = st.text_input("City", key="export_filter_cidade")
        with col2:
            filter_estado = st.text_input("State", key="export_filter_estado")
        with col3:
            filter_pais = st.text_input("Country", key="export_filter_pais")
        
        # Export button
        if st.button("📥 Export Data", key="export_data_button", use_container_width=container_width):
            with st.spinner(f"Exporting data as {export_format.upper()}..."):
                try:
                    # Build query parameters
                    params = {"format": export_format}
                    if filter_cidade:
                        params["cidade"] = filter_cidade
                    if filter_estado:
                        params["estado"] = filter_estado
                    if filter_pais:
                        params["pais"] = filter_pais
                    
                    # Make export request
                    response = api_client.get("/spots/export", params=params)
                    
                    if response.status_code == 200:
                        # Get export content
                        export_content = response.text
                        
                        # Generate filename
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"turistando_spots_{timestamp}.{export_format}"
                        
                        # Provide download button
                        st.success("✅ Export completed successfully!")
                        
                        st.download_button(
                            label=f"💾 Download {filename}",
                            data=export_content,
                            file_name=filename,
                            mime="application/json" if export_format == "json" else "text/csv",
                            use_container_width=True,
                        )
                        
                        # Show preview for JSON
                        if export_format == "json":
                            with st.expander("👁️ Preview Export Data", expanded=False):
                                import json
                                try:
                                    data = json.loads(export_content)
                                    st.json(data)
                                except:
                                    st.code(export_content, language="json")
                        else:
                            with st.expander("👁️ Preview Export Data", expanded=False):
                                st.code(export_content[:1000] + "..." if len(export_content) > 1000 else export_content)
                    
                    elif response.status_code == 403:
                        st.error("❌ Access denied: Admin privileges required.")
                    else:
                        st.error(f"❌ Export failed: {response.status_code}")
                        try:
                            error_detail = response.json().get("detail", "Unknown error")
                            st.error(f"Details: {error_detail}")
                        except:
                            pass
                            
                except Exception as e:
                    st.error(f"❌ Error during export: {str(e)}")


def render_quick_export_buttons(api_client):
    """
    Render quick export buttons for JSON and CSV.
    
    Args:
        api_client: API client instance
    """
    st.write("**Quick Export:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export JSON", key="quick_export_json", use_container_width=True):
            _perform_export(api_client, "json")
    
    with col2:
        if st.button("📥 Export CSV", key="quick_export_csv", use_container_width=True):
            _perform_export(api_client, "csv")


def _perform_export(api_client, format: str):
    """Helper function to perform export."""
    with st.spinner(f"Exporting {format.upper()}..."):
        try:
            response = api_client.get("/spots/export", params={"format": format})
            
            if response.status_code == 200:
                export_content = response.text
                
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"turistando_spots_{timestamp}.{format}"
                
                st.download_button(
                    label=f"💾 Download {filename}",
                    data=export_content,
                    file_name=filename,
                    mime="application/json" if format == "json" else "text/csv",
                    use_container_width=True,
                    key=f"download_{format}_{timestamp}",
                )
                st.success(f"✅ {format.upper()} export ready!")
            else:
                st.error(f"❌ Export failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
