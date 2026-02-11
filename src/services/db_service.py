import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# -----------------------------------------------------------------------------
# CONSTANTES CRÍTICAS DE NEGOCIO (NO TOCAR)
# -----------------------------------------------------------------------------
WORKSHEET_NAME = "hoja1"
COLS_ESPERADAS = ['usuario', 'password', 'activo', 'telefono', 'display_name', 'fecha_alta']

def get_connection():
    """Establece la conexión con Google Sheets."""
    return st.connection("gsheets", type=GSheetsConnection)

def _sanitizar_dataframe(df):
    """
    LIMPIEZA CRÍTICA DE DATOS:
    1. Convierte todo a string para evitar errores de tipos.
    2. Elimina el '.0' de los IDs numéricos que vienen de Make.
    3. Quita espacios en blanco.
    """
    # Forzamos conversión a string de las columnas clave
    if 'usuario' in df.columns:
        df['usuario'] = df['usuario'].astype(str).str.strip()
    
    if 'password' in df.columns:
        # Aquí solucionamos el bug de '123456.0' -> '123456'
        df['password'] = df['password'].astype(str).replace(r'\.0$', '', regex=True).str.strip()
        
    if 'activo' in df.columns:
        # Normalizamos el TRUE/FALSE de Sheets
        df['activo'] = df['activo'].astype(str).str.upper().str.strip()
        
    return df

def verificar_usuario(usuario_input, password_input):
    """
    Verifica credenciales contra Google Sheets con TTL=0 (Datos frescos).
    """
    conn = get_connection()
    try:
        # Lectura fresca (TTL=0) para captar pagos recientes de Make
        df = conn.read(worksheet=WORKSHEET_NAME, ttl=0)
        
        # Limpieza defensiva
        df = _sanitizar_dataframe(df)
        
        u_clean = str(usuario_input).strip()
        p_clean = str(password_input).strip()
        
        # Buscamos coincidencia exacta: Usuario + Password + Activo=TRUE
        usuario_valido = df[
            (df['usuario'] == u_clean) & 
            (df['password'] == p_clean) & 
            (df['activo'] == 'TRUE')
        ]
        
        if not usuario_valido.empty:
            # Retornamos los datos del usuario para la sesión (incluyendo display_name)
            return usuario_valido.iloc[0].to_dict()
            
        return None

    except Exception as e:
        st.error(f"Error de conexión con Base de Datos: {e}")
        return None

def actualizar_nombre_display(usuario_email, nuevo_nombre):
    """
    Actualiza SOLO la columna display_name del usuario específico.
    Mantiene la integridad de las otras filas.
    """
    conn = get_connection()
    try:
        # 1. Leemos todo el dataset
        df = conn.read(worksheet=WORKSHEET_NAME, ttl=0)
        df = _sanitizar_dataframe(df) # Importante limpiar para encontrar al usuario
        
        # 2. Localizamos el índice del usuario
        idx = df.index[df['usuario'] == str(usuario_email).strip()].tolist()
        
        if not idx:
            return False # Usuario no encontrado (raro si ya está logueado)
        
        # 3. Actualizamos en memoria
        # IMPORTANTE: No tocamos 'usuario', 'password', 'activo', 'telefono'
        df.at[idx[0], 'display_name'] = str(nuevo_nombre).strip()
        
        # 4. Escribimos de vuelta (Update)
        conn.update(worksheet=WORKSHEET_NAME, data=df)
        
        # Limpiamos caché para que el cambio se refleje inmediato
        st.cache_data.clear()
        return True

    except Exception as e:
        st.error(f"Error al guardar perfil: {e}")
        return False