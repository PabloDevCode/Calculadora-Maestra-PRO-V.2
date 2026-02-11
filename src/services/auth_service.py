import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

def validar_usuario(email_input, password_input):
    """
    Valida usuario contra Google Sheets.
    Soporta: TRUE, 1, 1.0, SI (case insensitive)
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # ttl=0 es CRÍTICO para leer datos frescos
        df = conn.read(worksheet="Hoja1", ttl=0) 
        
        # 1. Limpieza de datos (Evita errores de tipos y espacios)
        df['usuario'] = df['usuario'].astype(str).str.strip()
        df['password'] = df['password'].astype(str).str.strip()
        
        # 2. Búsqueda exacta de credenciales
        usuario_encontrado = df[
            (df['usuario'] == email_input) & 
            (df['password'] == password_input)
        ]
        
        if not usuario_encontrado.empty:
            # 3. Validación Inteligente de Estado
            # Convertimos a string mayúscula y quitamos espacios
            raw_estado = str(usuario_encontrado.iloc[0]['activo']).strip().upper()
            
            # Lista de valores que consideramos "POSITIVOS"
            # Incluye '1.0' (lo que viste en el debug), '1', 'TRUE', 'SI'
            valores_validos = ['TRUE', '1', '1.0', 'SI', 'YES', 'APPROVED']
            
            if raw_estado in valores_validos:
                return usuario_encontrado.iloc[0]['display_name']
            else:
                return "INACTIVO" # Credenciales bien, pero pago mal
        
        return None # Credenciales mal
        
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def login_form():
    """
    Renderiza el formulario y gestiona la sesión.
    """
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["display_name"] = None

    if st.session_state["authenticated"]:
        return True

    # --- UI LOGIN ---
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
                    
                    if resultado and resultado != "INACTIVO":
                        # --- LOGIN EXITOSO ---
                        st.session_state["authenticated"] = True
                        st.session_state["username"] = user_in
                        
                        # Manejo de nombre vacío
                        nombre_mostrar = user_in
                        if not pd.isna(resultado) and str(resultado) != "nan" and str(resultado) != "":
                            nombre_mostrar = resultado
                            
                        st.session_state["display_name"] = nombre_mostrar
                        
                        st.success(f"¡Bienvenido/a, {nombre_mostrar}!")
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
    #st.rerun()

# --- MANTÉN TODO LO DE ARRIBA IGUAL, SOLO CAMBIA ESTA FUNCIÓN AL FINAL ---

def actualizar_nombre_display(email_usuario, nuevo_nombre):
    """
    Actualiza el nombre comercial en Google Sheets.
    Versión BLINDADA: Evita romper los IDs de Make al guardar.
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Hoja1", ttl=0)
        
        # 🛡️ PROTECCIÓN CRÍTICA ANTES DE GUARDAR
        # Aseguramos que los IDs (password) sean texto plano
        # Si no hacemos esto, Python guarda "1.23E+09" y rompe Make
        df['password'] = df['password'].astype(str).replace(r'\.0$', '', regex=True).str.strip()
        df['usuario'] = df['usuario'].astype(str).str.strip()
        
        # Buscar usuario
        mask = df['usuario'] == str(email_usuario).strip()
        
        if mask.any():
            idx = df.index[mask][0]
            df.at[idx, 'display_name'] = str(nuevo_nombre)
            
            # Guardamos la tabla completa ya "sanitizada"
            conn.update(worksheet="Hoja1", data=df)
            return True
        return False
    except Exception as e:
        st.error(f"Error guardando nombre: {e}")
        return False