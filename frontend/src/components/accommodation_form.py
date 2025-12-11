"""
Accommodation form component for creating and editing accommodations.
"""

import streamlit as st
import requests
from typing import Optional


def render_accommodation_form(
    spot_id: int,
    accommodation_id: Optional[int] = None,
    initial_data: Optional[dict] = None
):
    """
    Render form for creating or editing an accommodation.
    
    Args:
        spot_id: Tourist spot ID.
        accommodation_id: Accommodation ID (for editing).
        initial_data: Initial form data (for editing).
        
    Returns:
        True if form was submitted successfully, False otherwise.
    """
    is_edit = accommodation_id is not None
    form_title = "✏️ Editar Hospedagem" if is_edit else "➕ Adicionar Nova Hospedagem"
    
    st.subheader(form_title)
    
    with st.form(key=f"accommodation_form_{accommodation_id or 'new'}"):
        nome = st.text_input(
            "Nome da Hospedagem *",
            value=initial_data.get("nome", "") if initial_data else "",
            placeholder="Ex: Hotel Copacabana Palace"
        )
        
        endereco = st.text_area(
            "Endereço Completo *",
            value=initial_data.get("endereco", "") if initial_data else "",
            placeholder="Ex: Av. Atlântica, 1702 - Copacabana, Rio de Janeiro - RJ"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            tipo = st.selectbox(
                "Tipo de Hospedagem *",
                ["hotel", "pousada", "hostel"],
                index=["hotel", "pousada", "hostel"].index(initial_data.get("tipo", "hotel")) if initial_data else 0
            )
        
        with col2:
            telefone = st.text_input(
                "Telefone",
                value=initial_data.get("telefone", "") if initial_data else "",
                placeholder="Ex: +55 21 2548-7070"
            )
        
        preco_medio = st.number_input(
            "Preço Médio por Noite (R$)",
            min_value=0.0,
            value=float(initial_data.get("preco_medio", 0.0)) if initial_data and initial_data.get("preco_medio") else 0.0,
            step=10.0,
            format="%.2f"
        )
        
        link_reserva = st.text_input(
            "Link para Reserva",
            value=initial_data.get("link_reserva", "") if initial_data else "",
            placeholder="Ex: https://www.booking.com/hotel/..."
        )
        
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            submit = st.form_submit_button(
                "💾 Salvar" if is_edit else "➕ Adicionar",
                type="primary",
                use_container_width=True
            )
        
        with col_cancel:
            cancel = st.form_submit_button(
                "❌ Cancelar",
                use_container_width=True
            )
        
        if cancel:
            if is_edit and f"editing_acc_{accommodation_id}" in st.session_state:
                del st.session_state[f"editing_acc_{accommodation_id}"]
            st.rerun()
        
        if submit:
            # Validation
            if not nome or not endereco or not tipo:
                st.error("❌ Por favor, preencha todos os campos obrigatórios (*)")
                return False
            
            # Get auth token
            token = st.session_state.get("token")
            if not token:
                st.error("❌ Você precisa estar autenticado como administrador.")
                return False
            
            # Prepare data
            data = {
                "nome": nome,
                "endereco": endereco,
                "tipo": tipo,
                "telefone": telefone if telefone else None,
                "preco_medio": preco_medio if preco_medio > 0 else None,
                "link_reserva": link_reserva if link_reserva else None
            }
            
            if not is_edit:
                data["ponto_id"] = spot_id
            
            # Make API request
            try:
                headers = {"Authorization": f"Bearer {token}"}
                
                if is_edit:
                    # Update existing accommodation
                    response = requests.put(
                        f"http://localhost:8000/api/accommodations/{accommodation_id}",
                        json=data,
                        headers=headers
                    )
                else:
                    # Create new accommodation
                    response = requests.post(
                        "http://localhost:8000/api/accommodations",
                        json=data,
                        headers=headers
                    )
                
                if response.status_code in [200, 201]:
                    st.success(f"✅ Hospedagem {'atualizada' if is_edit else 'adicionada'} com sucesso!")
                    
                    # Clear editing state
                    if is_edit and f"editing_acc_{accommodation_id}" in st.session_state:
                        del st.session_state[f"editing_acc_{accommodation_id}"]
                    
                    return True
                else:
                    error_detail = response.json().get("detail", "Erro desconhecido")
                    st.error(f"❌ Erro ao salvar hospedagem: {error_detail}")
                    return False
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Erro de conexão: {str(e)}")
                return False
    
    return False


def render_quick_add_accommodation_button(spot_id: int):
    """
    Render a button to quickly add an accommodation.
    
    Args:
        spot_id: Tourist spot ID.
    """
    if st.button("➕ Adicionar Hospedagem", type="primary"):
        st.session_state["show_add_accommodation"] = True
        st.rerun()
    
    if st.session_state.get("show_add_accommodation"):
        if render_accommodation_form(spot_id):
            st.session_state["show_add_accommodation"] = False
            st.rerun()
