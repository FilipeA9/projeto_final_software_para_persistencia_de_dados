"""
Registration Page - User account creation.

Streamlit page for new user registration.
"""

import streamlit as st
from src.services.api_client import TuristandoAPI

st.set_page_config(page_title="Cadastro - Turistando", page_icon="✍️", layout="wide")


def register_page():
    """Render registration page."""
    st.title("✍️ Cadastro de Usuário")
    st.markdown("Crie sua conta no **Turistando** para explorar e avaliar pontos turísticos!")
    
    # Check if already logged in
    if st.session_state.get("logged_in", False):
        st.info("ℹ️ Você já está logado!")
        if st.button("Ir para Home"):
            st.switch_page("src/Home.py")
        return
    
    # Registration form
    with st.form("register_form"):
        st.subheader("Informações da Conta")
        
        col1, col2 = st.columns(2)
        
        with col1:
            login = st.text_input(
                "Nome de Usuário*",
                placeholder="usuario123",
                help="3-50 caracteres: letras, números, hífens e underscores",
            )
        
        with col2:
            email = st.text_input(
                "Email*",
                placeholder="usuario@example.com",
                help="Endereço de email válido",
            )
        
        password = st.text_input(
            "Senha*",
            type="password",
            placeholder="Mínimo 6 caracteres",
            help="Senha segura com pelo menos 6 caracteres",
        )
        
        password_confirm = st.text_input(
            "Confirmar Senha*",
            type="password",
            placeholder="Digite a senha novamente",
        )
        
        st.markdown("---")
        
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            submit = st.form_submit_button("✅ Criar Conta", use_container_width=True)
        
        with col_cancel:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if cancel:
            st.switch_page("src/Home.py")
        
        if submit:
            # Validation
            if not login or not email or not password or not password_confirm:
                st.error("❌ Por favor, preencha todos os campos obrigatórios.")
                return
            
            if password != password_confirm:
                st.error("❌ As senhas não coincidem.")
                return
            
            if len(password) < 6:
                st.error("❌ A senha deve ter pelo menos 6 caracteres.")
                return
            
            # Call API
            api = TuristandoAPI()
            
            try:
                with st.spinner("Criando conta..."):
                    result = api.register(login, email, password)
                
                # Store session info
                st.session_state["logged_in"] = True
                st.session_state["access_token"] = result["access_token"]
                st.session_state["user"] = result["user"]
                
                st.success(f"✅ Conta criada com sucesso! Bem-vindo, {result['user']['login']}!")
                st.balloons()
                
                # Redirect to home after 2 seconds
                st.info("Redirecionando para a página inicial...")
                st.rerun()
                
            except Exception as e:
                error_msg = str(e)
                if "already exists" in error_msg.lower():
                    st.error("❌ Este nome de usuário ou email já está cadastrado.")
                elif "invalid" in error_msg.lower():
                    st.error("❌ Dados inválidos. Verifique os campos e tente novamente.")
                else:
                    st.error(f"❌ Erro ao criar conta: {error_msg}")
    
    # Login link
    st.markdown("---")
    st.markdown("Já tem uma conta?")
    if st.button("🔑 Fazer Login"):
        st.switch_page("src/pages/4_Login.py")


if __name__ == "__main__":
    register_page()
