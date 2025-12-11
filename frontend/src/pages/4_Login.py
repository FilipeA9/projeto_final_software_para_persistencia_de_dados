"""
Login Page - User authentication.

Streamlit page for user login.
"""

import streamlit as st
from src.services.api_client import TuristandoAPI

st.set_page_config(page_title="Login - Turistando", page_icon="🔑", layout="wide")


def login_page():
    """Render login page."""
    st.title("🔑 Login")
    st.markdown("Entre na sua conta do **Turistando** para acessar recursos exclusivos!")
    
    # Check if already logged in
    if st.session_state.get("logged_in", False):
        st.info("ℹ️ Você já está logado!")
        if st.button("Ir para Home"):
            st.switch_page("src/Home.py")
        return
    
    # Login form
    with st.form("login_form"):
        st.subheader("Credenciais de Acesso")
        
        login = st.text_input(
            "Nome de Usuário ou Email*",
            placeholder="usuario123 ou usuario@example.com",
            help="Digite seu nome de usuário ou email",
        )
        
        password = st.text_input(
            "Senha*",
            type="password",
            placeholder="Digite sua senha",
        )
        
        st.markdown("---")
        
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            submit = st.form_submit_button("✅ Entrar", use_container_width=True)
        
        with col_cancel:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if cancel:
            st.switch_page("src/Home.py")
        
        if submit:
            # Validation
            if not login or not password:
                st.error("❌ Por favor, preencha todos os campos.")
                return
            
            # Call API
            api = TuristandoAPI()
            
            try:
                with st.spinner("Autenticando..."):
                    result = api.login(login, password)
                
                # Store session info
                st.session_state["logged_in"] = True
                st.session_state["access_token"] = result["access_token"]
                st.session_state["user"] = result["user"]
                
                st.success(f"✅ Login realizado com sucesso! Bem-vindo de volta, {result['user']['login']}!")
                
                # Redirect to home
                st.info("Redirecionando para a página inicial...")
                st.rerun()
                
            except Exception as e:
                error_msg = str(e)
                if "401" in error_msg or "invalid credentials" in error_msg.lower():
                    st.error("❌ Credenciais inválidas. Verifique seu usuário/email e senha.")
                else:
                    st.error(f"❌ Erro ao fazer login: {error_msg}")
    
    # Registration link
    st.markdown("---")
    st.markdown("Ainda não tem uma conta?")
    if st.button("✍️ Criar Conta"):
        st.switch_page("src/pages/3_Register.py")


if __name__ == "__main__":
    login_page()
