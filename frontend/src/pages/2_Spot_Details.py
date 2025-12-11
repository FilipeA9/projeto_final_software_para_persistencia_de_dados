"""
Spot Details Page - Detailed view of a tourist spot.

Displays full spot information, photos, and ratings.
"""

import streamlit as st
from src.services.api_client import TuristandoAPI

st.set_page_config(page_title="Detalhes do Ponto", page_icon="📍", layout="wide")

# Initialize API client
api = TuristandoAPI()

# Get spot ID from session state or URL
spot_id = st.session_state.get("selected_spot_id")

if not spot_id:
    st.warning("⚠️ Nenhum ponto turístico selecionado.")
    st.info("Vá para a página 'Explorar Pontos' para selecionar um destino.")
    if st.button("🔍 Ir para Explorar Pontos"):
        st.switch_page("pages/1_Explore_Spots.py")
    st.stop()

# Fetch spot details
try:
    with st.spinner("Carregando detalhes..."):
        spot = api.get_spot(spot_id)
        photos = api.get_spot_photos(spot_id)
        rating_stats = api.get_spot_rating_stats(spot_id)
        ratings = api.get_spot_ratings(spot_id, limit=10)
    
    # Header
    st.title(f"📍 {spot['nome']}")
    
    # Location info
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**Localização**: {spot['cidade']}, {spot['estado']}, {spot['pais']}")
        st.write(f"**Endereço**: {spot['endereco']}")
        st.write(f"**Coordenadas**: {spot['latitude']}, {spot['longitude']}")
    
    with col2:
        # Rating summary
        if rating_stats['average']:
            st.metric("Avaliação Média", f"{rating_stats['average']:.1f} ⭐")
            st.caption(f"{rating_stats['total']} avaliações")
        else:
            st.info("Sem avaliações ainda")
        
        st.metric("Fotos", spot['photo_count'])
    
    st.divider()
    
    # Description
    st.subheader("📝 Descrição")
    st.write(spot['descricao'])
    
    st.divider()
    
    # Photos section
    st.subheader(f"📸 Fotos ({len(photos)})")
    
    if photos:
        # Display photos in grid
        cols = st.columns(3)
        for idx, photo in enumerate(photos):
            with cols[idx % 3]:
                st.image(
                    f"http://localhost:8000{photo['thumbnail_url']}",
                    caption=photo.get('titulo', 'Sem título'),
                    use_container_width=True,
                )
    else:
        st.info("Nenhuma foto disponível para este ponto turístico.")
    
    st.divider()
    
    # Accommodations section
    st.subheader("🏨 Hospedagens Próximas")
    
    try:
        accommodations_data = api.get_spot_accommodations(spot_id)
        accommodations = accommodations_data.get('accommodations', [])
        
        if accommodations:
            from src.components.accommodation_card import render_accommodation_list
            
            # Show filters if logged in as admin
            user = st.session_state.get("user")
            is_admin = user and user.get("role") == "ADMIN"
            
            render_accommodation_list(accommodations, show_actions=is_admin)
            
            # Admin: quick add button
            if is_admin:
                from src.components.accommodation_form import render_quick_add_accommodation_button
                st.divider()
                render_quick_add_accommodation_button(spot_id)
        else:
            st.info("📭 Nenhuma hospedagem cadastrada para este local ainda.")
            
            # Admin: show add button
            user = st.session_state.get("user")
            if user and user.get("role") == "ADMIN":
                from src.components.accommodation_form import render_quick_add_accommodation_button
                render_quick_add_accommodation_button(spot_id)
    
    except Exception as e:
        st.warning(f"⚠️ Não foi possível carregar hospedagens: {e}")
    
    st.divider()
    
    # Ratings section
    st.subheader("⭐ Avaliações")
    
    if rating_stats['total'] > 0:
        # Rating distribution
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**Distribuição de Avaliações:**")
            for stars in range(5, 0, -1):
                count = rating_stats[str(stars)]
                percentage = (count / rating_stats['total'] * 100) if rating_stats['total'] > 0 else 0
                st.write(f"{'⭐' * stars} ({stars}): {count} ({percentage:.0f}%)")
        
        with col2:
            st.write("**Avaliações Recentes:**")
            if ratings:
                for rating in ratings:
                    st.write(f"**{rating['nota']} ⭐** - {rating.get('comentario', 'Sem comentário')}")
                    st.caption(f"Avaliado em {rating['created_at']}")
                    st.divider()
            else:
                st.info("Nenhuma avaliação detalhada disponível.")
    else:
        st.info("Este ponto turístico ainda não possui avaliações.")
    
    # Back button
    if st.button("⬅️ Voltar para Explorar Pontos"):
        st.switch_page("pages/1_Explore_Spots.py")

except Exception as e:
    st.error(f"❌ Erro ao carregar detalhes: {e}")
    st.info("Certifique-se de que o backend está rodando em http://localhost:8000")
    
    if st.button("🔍 Voltar para Explorar Pontos"):
        st.switch_page("pages/1_Explore_Spots.py")
