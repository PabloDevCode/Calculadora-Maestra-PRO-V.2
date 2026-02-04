import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

def guardar_telefono_comunidad(email_usuario, nuevo_telefono):
    """
    Actualiza la columna 'telefono' del usuario en Google Sheets.
    Versión BLINDADA: Evita notación científica en IDs.
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Hoja1", ttl=0)
        
        # 1. Asegurar que la columna telefono existe
        if "telefono" not in df.columns:
            df["telefono"] = ""

        # 2. BLINDAJE: Convertir TODAS las columnas críticas a String
        # Esto evita que al guardar, Pandas convierta el ID 123456 a 1.2E5
        df['usuario'] = df['usuario'].astype(str)
        df['password'] = df['password'].astype(str)
        df['telefono'] = df['telefono'].astype(str)

        # 3. Buscar índice (limpiando espacios por si acaso)
        # Usamos una máscara temporal para buscar
        mask = df['usuario'].str.strip() == str(email_usuario).strip()
        
        if mask.any():
            # Obtener el índice real
            idx = df.index[mask][0]
            
            # Escribir en memoria (Forzando string)
            df.at[idx, 'telefono'] = str(nuevo_telefono)
            
            # 4. Guardar en nube (Sobrescribe con formato seguro)
            conn.update(worksheet="Hoja1", data=df)
            return True
        else:
            return False
            
    except Exception as e:
        st.sidebar.error(f"Error guardando datos: {e}")
        return False

def render_sidebar_community():
    if not st.session_state.get("authenticated", False):
        return

    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Comunidad VIP")
    
    # Si ya desbloqueó en esta sesión, mostrar botón directo
    if st.session_state.get("whatsapp_unlocked", False):
        mostrar_boton_final()
        return

    st.sidebar.info("Confirma tu WhatsApp para acceder al grupo de soporte.")

    with st.sidebar.form("lead_magnet"):
        tel = st.text_input("Tu WhatsApp:", placeholder="+54 9...", help="Ej: +54 9 11 1234 5678")
        btn = st.form_submit_button("🔓 Desbloquear", use_container_width=True)
        
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
                    st.sidebar.error("Error al actualizar base de datos.")

def mostrar_boton_final():
    st.sidebar.success("¡Acceso Habilitado!")
    st.sidebar.markdown(f"""
    <a href="https://chat.whatsapp.com/E17DxkdMbfdIBax5QUJ5E2?mode=gi_t" target="_blank" style="text-decoration:none;">
        <button style="
            background-color:#25D366; color:white; padding:10px; 
            width:100%; border-radius:5px; border:none; font-weight:bold; cursor:pointer;">
            👉 IR AL GRUPO AHORA
        </button>
    </a>
    """, unsafe_allow_html=True)