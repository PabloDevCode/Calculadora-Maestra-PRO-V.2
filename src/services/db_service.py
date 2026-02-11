import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

WORKSHEET_NAME = "hoja1"

def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def _sanitizar_dataframe(df):
    if 'usuario' in df.columns:
        df['usuario'] = df['usuario'].astype(str).str.strip()
    if 'password' in df.columns:
        df['password'] = df['password'].astype(str).replace(r'\.0$', '', regex=True).str.strip()
    if 'activo' in df.columns:
        df['activo'] = df['activo'].astype(str).str.upper().str.strip()
    return df

def verificar_usuario(usuario_input, password_input):
    try:
        conn = get_connection()
        df = conn.read(worksheet=WORKSHEET_NAME, ttl=0)
        df = _sanitizar_dataframe(df)
        
        u_clean = str(usuario_input).strip()
        p_clean = str(password_input).strip()
        
        usuario_valido = df[
            (df['usuario'] == u_clean) & 
            (df['password'] == p_clean)
        ]
        
        if not usuario_valido.empty:
            estado = usuario_valido.iloc[0]['activo']
            if estado in ['TRUE', '1', 'SI', 'YES', 'APPROVED']:
                return usuario_valido.iloc[0].to_dict()
            else:
                return "INACTIVO"
        return None
    except Exception as e:
        st.error(f"Error DB: {e}")
        return None

def actualizar_nombre_display(email_usuario, nuevo_nombre):
    try:
        conn = get_connection()
        df = conn.read(worksheet=WORKSHEET_NAME, ttl=0)
        df = _sanitizar_dataframe(df)
        
        mask = df['usuario'] == str(email_usuario).strip()
        if mask.any():
            idx = df.index[mask][0]
            df.at[idx, 'display_name'] = str(nuevo_nombre).strip()
            conn.update(worksheet=WORKSHEET_NAME, data=df)
            st.cache_data.clear()
            return True
        return False
    except Exception as e:
        st.error(f"Error Update: {e}")
        return False