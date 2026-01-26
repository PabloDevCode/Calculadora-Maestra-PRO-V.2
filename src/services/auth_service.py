# src/services/auth_service.py
import streamlit as st
import time

VALID_USERS = {
    "admin": "admin",      # Puedes cambiar esto
    "demo": "1234"
}

def login_form():
    if st.session_state.get("authenticated", False):
        return True

    st.markdown("### 🔐 Identificación Requerida")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info("Sistema Profesional de Cálculo de Materiales.")
    with col2:
        with st.form("login"):
            user = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Ingresar"):
                if VALID_USERS.get(user) == pwd:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = user
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    return False

def logout():
    st.session_state["authenticated"] = False
    st.rerun()