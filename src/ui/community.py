import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

def guardar_telefono_comunidad(email_usuario, nuevo_telefono):
    """Guarda el teléfono asegurando integridad."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Hoja1", ttl=0)
        
        if "telefono" not in df.columns:
            df["telefono"] = ""

        # Protección de datos
        df['password'] = df['password'].astype(str).replace(r'\.0$', '', regex=True).str.strip()
        df['usuario'] = df['usuario'].astype(str).str.strip()
        df['telefono'] = df['telefono'].astype(str)

        mask = df['usuario'] == str(email_usuario).strip()
        
        if mask.any():
            idx = df.index[mask][0]
            df.at[idx, 'telefono'] = str(nuevo_telefono)
            conn.update(worksheet="Hoja1", data=df)
            st.cache_data.clear() # Limpiar caché para que auth_service lo vea después
            return True
        return False
    except Exception as e:
        st.sidebar.error(f"Error DB: {e}")
        return False

def mostrar_boton_vip():
    """Renderiza el estado 'Ya soy VIP'"""
    st.sidebar.markdown("""
    <div style="background-color: #dcfce7; padding: 12px; border-radius: 8px; border: 1px solid #22c55e; margin-bottom: 20px;">
        <h4 style="margin:0; color: #166534; font-size:14px;">✅ Soporte VIP Activo</h4>
        <p style="font-size:11px; margin:5px 0 10px 0; color: #15803d;">
            Ya tienes acceso directo a nuestro canal privado.
        </p>
        <a href="https://chat.whatsapp.com/E17DxkdMbfdIBax5QUJ5E2" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:8px; border-radius:5px; text-align:center; font-weight:bold; font-size:12px; box-shadow: 0 2px 2px rgba(0,0,0,0.1);">
                👉 IR AL GRUPO
            </div>
        </a>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_community():
    # Solo mostrar si está logueado
    if not st.session_state.get("authenticated", False):
        return

    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Comunidad")
    
    # Check persistente (cargado desde auth_service o desbloqueado ahora)
    if st.session_state.get("whatsapp_unlocked", False):
        mostrar_boton_vip()
        return

    # Formulario de Captura
    st.sidebar.caption("Ingresa tu WhatsApp para acceder al soporte técnico.")
    with st.sidebar.form("lead_magnet_wsp"):
        tel = st.text_input("Tu WhatsApp:", placeholder="+54 9...", help="Ej: +54 9 221 123 4567")
        btn = st.form_submit_button("🔓 Desbloquear Acceso", use_container_width=True)
        
        if btn:
            if len(tel) < 8:
                st.sidebar.error("Número muy corto.")
            else:
                email = st.session_state["username"]
                with st.sidebar.spinner("Registrando..."):
                    if guardar_telefono_comunidad(email, tel):
                        st.session_state["whatsapp_unlocked"] = True
                        st.rerun() # Recarga para mostrar el botón verde
                    else:
                        st.sidebar.error("Error al guardar.")