"""
Turistando - Tourism Platform

Main landing page for the Streamlit application.
"""

import streamlit as st
from src.components.user_profile import user_profile_sidebar, get_current_user

st.set_page_config(
    page_title="Turistando",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Display user profile in sidebar if logged in
user_profile_sidebar()

# Welcome message
user = get_current_user()
if user:
    st.title(f"🗺️ Bem-vindo, {user['login']}!")
else:
    st.title("🗺️ Turistando - Tourism Platform")

st.markdown("""
## Bem-vindo ao Turistando!

Descubra os melhores pontos turísticos, avalie suas experiências e planeje sua próxima aventura.

### 🎯 Recursos Disponíveis

- **🔍 Explorar Pontos Turísticos**: Navegue por milhares de destinos com filtros por cidade, estado e país
- **📸 Galerias de Fotos**: Veja imagens de outros viajantes
- **⭐ Avaliações**: Consulte ratings e reviews de outros usuários
- **❤️ Favoritos**: Salve seus destinos preferidos para referência rápida
- **🏨 Hospedagens**: Encontre acomodações próximas aos pontos turísticos

### 🚀 Começar

Use o menu lateral para navegar pelas diferentes seções:

1. **Explorar Pontos** - Descubra novos destinos
2. **Detalhes do Ponto** - Veja informações detalhadas
3. **Cadastro** - Crie sua conta para avaliar e favoritar
4. **Login** - Acesse sua conta registrada

### 📊 Estatísticas da Plataforma

""")

# Try to fetch stats from API
try:
    from src.services.api_client import TuristandoAPI
    
    api = TuristandoAPI()
    spots_data = api.list_spots(limit=1)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Pontos Turísticos", spots_data.get("total", 0))
    
    with col2:
        st.metric("API Status", "✅ Online")
    
    with col3:
        st.metric("Versão", "1.0.0")
    
except Exception as e:
    st.warning(f"⚠️ Não foi possível conectar à API: {e}")
    st.info("Certifique-se de que o backend está rodando em http://localhost:8000")

st.markdown("""
---

### 📚 Sobre o Projeto

Este é um sistema de gerenciamento de pontos turísticos desenvolvido com:

- **Backend**: FastAPI + PostgreSQL + MongoDB + Redis
- **Frontend**: Streamlit
- **Arquitetura**: Repository Pattern com cache distribuído

**Desenvolvido como projeto acadêmico para demonstração de persistência de dados híbrida.**
""")
