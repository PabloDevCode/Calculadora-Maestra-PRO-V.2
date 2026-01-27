import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

def login_form():
    """
    Maneja el login verificando contra Google Sheets.
    """
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = None

    if st.session_state["authenticated"]:
        return True

    # --- UI LOGIN ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <h2 style="color: #1E3A8A; margin:0;">🔐 Calculadora Maestra</h2>
            <p style="color: #666; font-size: 14px;">Ingreso de Clientes</p>
        </div>
        <br>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username_input = st.text_input("Usuario")
            password_input = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar", type="primary", use_container_width=True)

            if submit:
                try:
                    # 1. Conectamos con Google Sheets
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    
                    # 2. Leemos la hoja (ttl=0 para que NO guarde caché y lea siempre fresco)
                    # Si tienes muchos usuarios, puedes poner ttl=60 (1 min de caché)
                    df = conn.read(ttl=0)
                    
                    # 3. Limpieza de datos (por si quedan espacios vacíos en el Excel)
                    df = df.astype(str) # Convertir todo a texto para evitar errores
                    df['usuario'] = df['usuario'].str.strip()
                    df['password'] = df['password'].str.strip()
                    df['activo'] = df['activo'].str.upper().str.strip()

                    # 4. Buscamos el usuario
                    user_found = df[
                        (df['usuario'] == username_input) & 
                        (df['password'] == password_input) & 
                        (df['activo'] == 'SI')
                    ]

                    if not user_found.empty:
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = username_input
                        st.success(f"¡Hola de nuevo, {username_input}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Credenciales inválidas o acceso expirado.")
                        
                except Exception as e:
                    st.error("⚠️ Error de conexión con la base de datos.")
                    #st.exception(e) # Descomentar solo para ver el error real si falla

    return False

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["project_cart"] = []
    st.rerun()