import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

def validar_usuario(email_input, password_input):
    """
    Valida usuario contra Google Sheets.
    Retorna:
      - Dict {display_name, telefono} si es exitoso.
      - "INACTIVO" si el pago falló.
      - None si no existe.
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # ttl=0 es CRÍTICO para leer datos frescos
        df = conn.read(worksheet="Hoja1", ttl=0) 
        
        # 1. Limpieza de datos (Evita errores de tipos y espacios)
        if 'usuario' in df.columns:
            df['usuario'] = df['usuario'].astype(str).str.strip()
        if 'password' in df.columns:
            df['password'] = df['password'].astype(str).replace(r'\.0$', '', regex=True).str.strip()
        
        # 2. Búsqueda exacta de credenciales
        usuario_encontrado = df[
            (df['usuario'] == str(email_input).strip()) & 
            (df['password'] == str(password_input).strip())
        ]
        
        if not usuario_encontrado.empty:
            fila = usuario_encontrado.iloc[0]
            raw_estado = str(fila['activo']).strip().upper()
            valores_validos = ['TRUE', '1', '1.0', 'SI', 'YES', 'APPROVED']
            
            if raw_estado in valores_validos:
                # ÉXITO: Devolvemos nombre y teléfono para persistencia
                return {
                    "display_name": fila['display_name'],
                    "telefono": fila.get('telefono', '') # Usamos .get por si la columna no existe
                }
            else:
                return "INACTIVO"
        
        return None 
        
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def login_form():
    """Renderiza el formulario y gestiona la sesión."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["display_name"] = None
        st.session_state["whatsapp_unlocked"] = False # Nuevo estado

    if st.session_state["authenticated"]:
        return True

    # --- UI LOGIN ORIGINAL ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <h2 style="color: #1E3A8A; margin:0;">🔐 Acceso Clientes</h2>
            <p style="color: #666; font-size: 14px;">Ingresa tus datos de suscripción</p>
        </div>
        <br>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            user_in = st.text_input("Usuario (Email)")
            pass_in = st.text_input("Contraseña (ID Transacción)", type="password")
            submit = st.form_submit_button("Ingresar", type="primary", use_container_width=True)

            if submit:
                if not user_in or not pass_in:
                    st.warning("⚠️ Faltan datos.")
                else:
                    resultado = validar_usuario(user_in, pass_in)
                    
                    if isinstance(resultado, dict):
                        # --- LOGIN EXITOSO ---
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = user_in
                        
                        # 1. Cargar Nombre
                        raw_name = resultado.get("display_name")
                        if not pd.isna(raw_name) and str(raw_name).strip() not in ["nan", "", "None"]:
                            st.session_state["display_name"] = str(raw_name)
                        else:
                            st.session_state["display_name"] = user_in

                        # 2. Cargar Teléfono (PERSISTENCIA COMUNIDAD VIP)
                        raw_tel = str(resultado.get("telefono", ""))
                        if len(raw_tel) > 6 and raw_tel.lower() not in ["nan", "none", ""]:
                            st.session_state["whatsapp_unlocked"] = True
                        else:
                            st.session_state["whatsapp_unlocked"] = False
                        
                        st.success(f"¡Bienvenido/a, {st.session_state['display_name']}!")
                        time.sleep(1)
                        st.rerun()
                        
                    elif resultado == "INACTIVO":
                        st.error("🔒 Cuenta inactiva. Verifica tu pago.")
                    else:
                        st.error("❌ Usuario o contraseña incorrectos.")

    return False

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["display_name"] = None
    st.session_state["whatsapp_unlocked"] = False
    st.session_state["project_cart"] = []

def actualizar_nombre_display(email_usuario, nuevo_nombre):
    """Actualiza el nombre preservando la integridad de datos."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Hoja1", ttl=0)
        
        # Protección de formato
        if 'password' in df.columns:
            df['password'] = df['password'].astype(str).replace(r'\.0$', '', regex=True).str.strip()
        if 'usuario' in df.columns:
            df['usuario'] = df['usuario'].astype(str).str.strip()
        
        mask = df['usuario'] == str(email_usuario).strip()
        
        if mask.any():
            idx = df.index[mask][0]
            df.at[idx, 'display_name'] = str(nuevo_nombre)
            conn.update(worksheet="Hoja1", data=df)
            st.cache_data.clear()
            return True
        return False
    except Exception as e:
        st.error(f"Error guardando nombre: {e}")
        return False