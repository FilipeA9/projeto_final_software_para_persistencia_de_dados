"""
Accommodation card component for displaying accommodation information.
"""

import streamlit as st
from typing import Optional


def render_accommodation_card(accommodation: dict, show_actions: bool = False):
    """
    Render a single accommodation card.
    
    Args:
        accommodation: Accommodation dictionary with details.
        show_actions: Whether to show admin action buttons.
    """
    tipo_icons = {
        "hotel": "🏨",
        "pousada": "🏡",
        "hostel": "🛏️"
    }
    
    tipo = accommodation.get("tipo", "hotel")
    icon = tipo_icons.get(tipo, "🏨")
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {icon} {accommodation['nome']}")
            st.caption(f"**Tipo:** {tipo.title()}")
        
        with col2:
            if accommodation.get("preco_medio"):
                st.metric("Preço Médio", f"R$ {accommodation['preco_medio']:.2f}")
            else:
                st.caption("_Preço não disponível_")
        
        st.markdown(f"**📍 Endereço:** {accommodation['endereco']}")
        
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            if accommodation.get("telefone"):
                st.markdown(f"**📞 Telefone:** {accommodation['telefone']}")
        
        with col_info2:
            if accommodation.get("link_reserva"):
                st.markdown(f"[🔗 Fazer Reserva]({accommodation['link_reserva']})")
        
        if show_actions:
            st.divider()
            col_edit, col_delete = st.columns(2)
            
            with col_edit:
                if st.button(f"✏️ Editar", key=f"edit_acc_{accommodation['id']}"):
                    st.session_state[f"editing_acc_{accommodation['id']}"] = True
                    st.rerun()
            
            with col_delete:
                if st.button(f"🗑️ Deletar", key=f"delete_acc_{accommodation['id']}", type="secondary"):
                    if st.session_state.get(f"confirm_delete_acc_{accommodation['id']}"):
                        # Actually delete
                        return "delete"
                    else:
                        st.session_state[f"confirm_delete_acc_{accommodation['id']}"] = True
                        st.rerun()
            
            if st.session_state.get(f"confirm_delete_acc_{accommodation['id']}"):
                st.warning("⚠️ Tem certeza? Clique novamente para confirmar.")


def render_accommodation_list(accommodations: list, show_actions: bool = False):
    """
    Render a list of accommodations.
    
    Args:
        accommodations: List of accommodation dictionaries.
        show_actions: Whether to show admin action buttons.
    """
    if not accommodations:
        st.info("📭 Nenhuma hospedagem encontrada para este local.")
        return
    
    st.markdown(f"**{len(accommodations)} hospedagens disponíveis**")
    st.divider()
    
    for accommodation in accommodations:
        result = render_accommodation_card(accommodation, show_actions)
        if result == "delete":
            return result
        st.divider()


def render_accommodation_filters():
    """
    Render filter controls for accommodations.
    
    Returns:
        Dictionary with selected filter values.
    """
    st.sidebar.subheader("🔍 Filtros de Hospedagem")
    
    tipo_filter = st.sidebar.selectbox(
        "Tipo de Hospedagem",
        ["Todos", "Hotel", "Pousada", "Hostel"],
        key="acc_tipo_filter"
    )
    
    st.sidebar.markdown("**Faixa de Preço (R$)**")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        min_price = st.number_input(
            "Mínimo",
            min_value=0,
            value=0,
            step=50,
            key="acc_min_price"
        )
    
    with col2:
        max_price = st.number_input(
            "Máximo",
            min_value=0,
            value=0,
            step=50,
            key="acc_max_price"
        )
    
    return {
        "tipo": tipo_filter.lower() if tipo_filter != "Todos" else None,
        "min_price": min_price if min_price > 0 else None,
        "max_price": max_price if max_price > 0 else None
    }


def render_accommodation_statistics(stats: dict):
    """
    Render accommodation statistics.
    
    Args:
        stats: Statistics dictionary with counts and prices.
    """
    if stats.get("total", 0) == 0:
        st.info("📊 Nenhuma estatística disponível - adicione hospedagens primeiro.")
        return
    
    st.subheader("📊 Estatísticas de Hospedagem")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Hospedagens", stats.get("total", 0))
    
    with col2:
        avg = stats.get("avg_price", 0)
        if avg > 0:
            st.metric("Preço Médio", f"R$ {avg:.2f}")
        else:
            st.caption("_Sem informação de preço_")
    
    with col3:
        min_p = stats.get("min_price", 0)
        max_p = stats.get("max_price", 0)
        if max_p > 0:
            st.metric("Faixa de Preço", f"R$ {min_p:.2f} - {max_p:.2f}")
        else:
            st.caption("_Sem informação de preço_")
    
    # Types distribution
    types = stats.get("types", {})
    if types:
        st.markdown("**Distribuição por Tipo:**")
        for tipo, count in types.items():
            percentage = (count / stats["total"]) * 100
            st.progress(percentage / 100, text=f"{tipo.title()}: {count} ({percentage:.1f}%)")
