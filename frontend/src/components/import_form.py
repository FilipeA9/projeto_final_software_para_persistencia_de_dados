"""
Import Form Component - Allow admins to import tourist spot data.

Provides UI for importing spots from JSON or CSV files.
"""

import streamlit as st
from typing import Optional


def render_import_form(api_client):
    """
    Render import form for uploading and importing spot data.
    
    Args:
        api_client: API client instance
    """
    with st.expander("📤 Import Tourist Spots", expanded=False):
        st.write("Import tourist spot data from JSON or CSV files.")
        
        # Format selection
        import_format = st.selectbox(
            "Select Format",
            options=["json", "csv"],
            format_func=lambda x: f"{x.upper()} Format",
            key="import_format_selector",
        )
        
        # File uploader
        uploaded_file = st.file_uploader(
            f"Choose a {import_format.upper()} file",
            type=[import_format],
            key="import_file_uploader",
            help=f"Upload a {import_format.upper()} file containing tourist spot data",
        )
        
        # Show format requirements
        with st.expander("📋 Format Requirements", expanded=False):
            if import_format == "json":
                st.markdown("""
                **JSON Format:**
                ```json
                {
                  "data": [
                    {
                      "nome": "Spot Name",
                      "descricao": "Description",
                      "cidade": "City",
                      "estado": "State",
                      "pais": "Country",
                      "latitude": -23.5505,
                      "longitude": -46.6333,
                      "endereco": "Address (optional)"
                    }
                  ]
                }
                ```
                
                **Required Fields:**
                - nome (max 200 chars)
                - cidade, estado, pais
                - latitude (-90 to 90)
                - longitude (-180 to 180)
                
                **Optional Fields:**
                - descricao (max 2000 chars)
                - endereco
                """)
            else:  # csv
                st.markdown("""
                **CSV Format:**
                ```
                nome,descricao,cidade,estado,pais,latitude,longitude,endereco
                "Spot Name","Description","City","State","Country",-23.5505,-46.6333,"Address"
                ```
                
                **Required Columns:**
                - nome (max 200 chars)
                - cidade, estado, pais
                - latitude (-90 to 90)
                - longitude (-180 to 180)
                
                **Optional Columns:**
                - descricao (max 2000 chars)
                - endereco
                
                **Note:** Use quotes for fields containing commas.
                """)
        
        # Import button
        if uploaded_file is not None:
            if st.button("📤 Import Data", key="import_data_button", use_container_width=True):
                with st.spinner(f"Importing data from {import_format.upper()}..."):
                    try:
                        # Read file content
                        content = uploaded_file.read().decode("utf-8")
                        
                        # Make import request
                        response = api_client.post(
                            "/spots/import",
                            params={"format": import_format, "content": content},
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            summary = result.get("summary", {})
                            imported_spots = result.get("imported_spots", [])
                            errors = result.get("errors", [])
                            
                            # Display summary
                            st.success("✅ Import completed!")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Records", summary.get("total_records", 0))
                            with col2:
                                st.metric("Successfully Imported", summary.get("successfully_imported", 0))
                            with col3:
                                st.metric("Failed", summary.get("invalid_records", 0) + summary.get("failed_imports", 0))
                            
                            # Show imported spots
                            if imported_spots:
                                with st.expander(f"✅ Successfully Imported ({len(imported_spots)})", expanded=True):
                                    for spot in imported_spots:
                                        st.write(f"- **{spot['nome']}** (ID: {spot['id']}) - {spot['cidade']}")
                            
                            # Show errors
                            if errors:
                                with st.expander(f"❌ Errors ({len(errors)})", expanded=False):
                                    for error in errors:
                                        st.error(error)
                            
                            # Clear uploader
                            st.info("💡 Upload another file to import more data.")
                        
                        elif response.status_code == 403:
                            st.error("❌ Access denied: Admin privileges required.")
                        else:
                            st.error(f"❌ Import failed: {response.status_code}")
                            try:
                                error_detail = response.json().get("detail", "Unknown error")
                                st.error(f"Details: {error_detail}")
                            except:
                                pass
                                
                    except Exception as e:
                        st.error(f"❌ Error during import: {str(e)}")
                        st.exception(e)
        else:
            st.info("📁 Please upload a file to begin import.")


def render_import_examples():
    """
    Render example import files for download.
    """
    st.write("**📥 Download Example Files:**")
    
    col1, col2 = st.columns(2)
    
    # JSON example
    with col1:
        json_example = """{
  "data": [
    {
      "nome": "Cristo Redentor",
      "descricao": "Icônica estátua Art Déco de Jesus Cristo no topo do Morro do Corcovado",
      "cidade": "Rio de Janeiro",
      "estado": "RJ",
      "pais": "Brasil",
      "latitude": -22.9519,
      "longitude": -43.2105,
      "endereco": "Parque Nacional da Tijuca"
    },
    {
      "nome": "Museu do Amanhã",
      "descricao": "Museu de ciências na Praça Mauá",
      "cidade": "Rio de Janeiro",
      "estado": "RJ",
      "pais": "Brasil",
      "latitude": -22.8941,
      "longitude": -43.1802,
      "endereco": "Praça Mauá, 1"
    }
  ]
}"""
        st.download_button(
            label="📄 Download JSON Example",
            data=json_example,
            file_name="example_import.json",
            mime="application/json",
            use_container_width=True,
        )
    
    # CSV example
    with col2:
        csv_example = """nome,descricao,cidade,estado,pais,latitude,longitude,endereco
"Cristo Redentor","Icônica estátua Art Déco de Jesus Cristo no topo do Morro do Corcovado","Rio de Janeiro","RJ","Brasil",-22.9519,-43.2105,"Parque Nacional da Tijuca"
"Museu do Amanhã","Museu de ciências na Praça Mauá","Rio de Janeiro","RJ","Brasil",-22.8941,-43.1802,"Praça Mauá, 1"
"""
        st.download_button(
            label="📄 Download CSV Example",
            data=csv_example,
            file_name="example_import.csv",
            mime="text/csv",
            use_container_width=True,
        )
