"""
Explore Spots Page - Tourist spot discovery and filtering.

Displays paginated list of tourist spots with filters.
"""

import streamlit as st
from src.services.api_client import TuristandoAPI

st.set_page_config(page_title="Explorar Pontos", page_icon="🔍", layout="wide")

st.title("🔍 Explorar Pontos Turísticos")

# Initialize API client
api = TuristandoAPI()

# Filters in sidebar
st.sidebar.header("Filtros de Busca")

search = st.sidebar.text_input("🔎 Pesquisar", placeholder="Nome ou descrição...")
cidade = st.sidebar.text_input("🏙️ Cidade", placeholder="Ex: Rio de Janeiro")
estado = st.sidebar.text_input("🗺️ Estado", placeholder="Ex: Rio de Janeiro")
pais = st.sidebar.text_input("🌍 País", placeholder="Ex: Brasil")

# Pagination
st.sidebar.header("Paginação")
page = st.sidebar.number_input("Página", min_value=1, value=1, step=1)
page_size = st.sidebar.selectbox("Itens por página", [10, 20, 50], index=1)

# Calculate skip
skip = (page - 1) * page_size

# Fetch spots
try:
    with st.spinner("Carregando pontos turísticos..."):
        result = api.list_spots(
            skip=skip,
            limit=page_size,
            cidade=cidade if cidade else None,
            estado=estado if estado else None,
            pais=pais if pais else None,
            search=search if search else None,
        )
    
    spots = result["spots"]
    total = result["total"]
    has_more = result["has_more"]
    
    # Display summary
    st.info(f"📊 Encontrados **{total}** pontos turísticos")
    
    if not spots:
        st.warning("Nenhum ponto turístico encontrado com os filtros aplicados.")
    else:
        # Display spots in cards
        for spot in spots:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(f"📍 {spot['nome']}")
                    st.write(f"**Localização**: {spot['cidade']}, {spot['estado']}, {spot['pais']}")
                    st.write(spot['descricao'])
                
                with col2:
                    # Rating display
                    if spot['avg_rating']:
                        rating = spot['avg_rating']
                        stars = "⭐" * int(round(rating))
                        st.metric("Avaliação", f"{rating:.1f} {stars}")
                        st.caption(f"{spot['rating_count']} avaliações")
                    else:
                        st.caption("Sem avaliações")
                    
                    # Favorite button (if logged in)
                    if st.session_state.get("token"):
                        from components.favorite_button import render_favorite_button_compact
                        render_favorite_button_compact(spot['id'], key_suffix=f"list_{page}")
                    
                    # Link to details
                    if st.button("Ver Detalhes", key=f"spot_{spot['id']}"):
                        st.session_state.selected_spot_id = spot['id']
                        st.switch_page("pages/2_Spot_Details.py")
                
                st.divider()
        
        # Pagination info
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if page > 1:
                if st.button("⬅️ Página Anterior"):
                    st.session_state.page = page - 1
                    st.rerun()
        
        with col2:
            total_pages = (total + page_size - 1) // page_size
            st.write(f"Página {page} de {total_pages}")
        
        with col3:
            if has_more:
                if st.button("Próxima Página ➡️"):
                    st.session_state.page = page + 1
                    st.rerun()

except Exception as e:
    st.error(f"❌ Erro ao carregar pontos turísticos: {e}")
    st.info("Certifique-se de que o backend está rodando em http://localhost:8000")
