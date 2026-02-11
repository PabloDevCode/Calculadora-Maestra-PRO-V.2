import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

def guardar_telefono_comunidad(email_usuario, nuevo_telefono):
    """
    Guarda el teléfono asegurando que no se rompan los IDs de Make.
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Hoja1", ttl=0)
        
        # Asegurar columna telefono
        if "telefono" not in df.columns:
            df["telefono"] = ""

        # 🛡️ PROTECCIÓN CRÍTICA DE DATOS
        df['password'] = df['password'].astype(str).replace(r'\.0$', '', regex=True).str.strip()
        df['usuario'] = df['usuario'].astype(str).str.strip()
        df['telefono'] = df['telefono'].astype(str) # Forzamos texto en telefono también

        # Buscar usuario
        mask = df['usuario'] == str(email_usuario).strip()
        
        if mask.any():
            idx = df.index[mask][0]
            df.at[idx, 'telefono'] = str(nuevo_telefono)
            conn.update(worksheet="Hoja1", data=df)
            return True
        else:
            return False
            
    except Exception as e:
        st.sidebar.error(f"Error guardando datos: {e}")
        return False

def mostrar_boton_final():
    st.sidebar.success("¡Acceso Habilitado!")
    st.sidebar.markdown(f"""
    <a href="https://chat.whatsapp.com/E17DxkdMbfdIBax5QUJ5E2?mode=gi_t" target="_blank" style="text-decoration:none;">
        <div style="background-color:#25D366; color:white; padding:10px; border-radius:5px; text-align:center; font-weight:bold;">
            👉 UNIRME AL GRUPO
        </div>
    </a>
    """, unsafe_allow_html=True)

def render_sidebar_community():
    # Solo mostrar si está logueado
    if not st.session_state.get("authenticated", False):
        return

    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Comunidad VIP")
    
    # Verificamos si ya lo desbloqueó en esta sesión
    if st.session_state.get("whatsapp_unlocked", False):
        mostrar_boton_final()
        return

    st.sidebar.info("Ingresa tu WhatsApp para acceder al soporte técnico.")

    with st.sidebar.form("lead_magnet_wsp"):
        tel = st.text_input("Tu WhatsApp:", placeholder="+54 9...", help="Ej: +54 9 221 123 4567")
        btn = st.form_submit_button("🔓 Desbloquear Acceso", use_container_width=True)
        
        if btn:
            if len(tel) < 8:
                st.sidebar.error("Número muy corto.")
            else:
                email = st.session_state["username"]
                with st.sidebar.spinner("Registrando..."):
                    ok = guardar_telefono_comunidad(email, tel)
                
                if ok:
                    st.session_state["whatsapp_unlocked"] = True
                    st.rerun()
                else:
                    st.sidebar.error("Error al guardar. Intenta de nuevo.")