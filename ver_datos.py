import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("🕵️‍♂️ Visor de Datos Crudos")

if st.button("Ver qué hay en el Excel"):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Leemos sin caché
        df = conn.read(worksheet="Hoja1", ttl=0)
        
        st.subheader("1. La Tabla Completa")
        st.dataframe(df)

        st.subheader("2. Análisis Forense (Espacios y Tipos)")
        st.info("Fíjate si hay espacios vacíos dentro de las comillas simples ' '")
        
        # Revisamos las columnas clave
        for col in ['usuario', 'password', 'activo']:
            if col in df.columns:
                st.markdown(f"**Columna: `{col}`**")
                # Mostramos cada valor tal cual lo ve Python
                for valor in df[col].unique():
                    # Usamos st.code para ver exactamente los caracteres
                    st.code(f"Valor: '{valor}' | Tipo: {type(valor)}")
            else:
                st.error(f"❌ Falta la columna {col}")

    except Exception as e:
        st.error(f"Error de conexión: {e}")