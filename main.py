import streamlit as st
import pandas as pd
import time  
from src.core.factory import CalculatorFactory
from src.services.auth_service import login_form, logout, actualizar_nombre_display 
from src.services.pdf_service import create_pdf_bytes
from src.ui.community import render_sidebar_community

st.set_page_config(page_title="Calculadora Maestra Pro", page_icon="🏗️", layout="wide")

if "project_cart" not in st.session_state:
    st.session_state["project_cart"] = []

if "temp_aberturas" not in st.session_state:
    st.session_state["temp_aberturas"] = []

# --- CORRECCIÓN DE BUG: Validar índice antes de borrar ---
def eliminar_item(index):
    if 0 <= index < len(st.session_state["project_cart"]):
        del st.session_state["project_cart"][index]

def eliminar_abertura_temp(index):
    if 0 <= index < len(st.session_state["temp_aberturas"]):
        del st.session_state["temp_aberturas"][index]
# ---------------------------------------------------------

def agregar_abertura_temp(ancho, alto, cantidad):
    if cantidad > 0:
        st.session_state["temp_aberturas"].append({
            "ancho": ancho,
            "alto": alto,
            "cant": cantidad
        })

def limpiar_form_aberturas():
    st.session_state["temp_aberturas"] = []

def main():
    if not login_form():
        return
    
    # =========================================================================
    # 🛑 ZONA DE ONBOARDING (INTERCEPTOR DE NOMBRE)
    # =========================================================================
    usuario_actual = st.session_state.get("username")
    nombre_actual = st.session_state.get("display_name")

    safe_nombre = str(nombre_actual).strip()
    safe_user = str(usuario_actual).strip()
    
    lista_invalidos = ['nan', 'none', '', 'null', 'none']

    if safe_nombre.lower() in lista_invalidos or safe_nombre.lower() == safe_user.lower():
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("### 👋 ¡Bienvenido al equipo!")
            st.info("Para generar presupuestos profesionales, necesitamos configurar el nombre de tu empresa o marca personal.")
            
            with st.form("form_nombre_inicial"):
                nuevo_nombre = st.text_input("Nombre de tu Empresa / Marca:", placeholder="Ej: Construcciones Pérez S.A.")
                st.caption("ℹ️ Este nombre aparecerá en el encabezado de tus PDFs.")
                
                btn_guardar = st.form_submit_button("Guardar y Comenzar 🚀", type="primary", use_container_width=True)
                
                if btn_guardar:
                    if len(nuevo_nombre) < 3:
                        st.error("El nombre es muy corto.")
                    else:
                        with st.spinner("Configurando tu perfil..."):
                            exito = actualizar_nombre_display(usuario_actual, nuevo_nombre)
                        
                        if exito:
                            st.session_state["display_name"] = nuevo_nombre
                            st.success("¡Perfil configurado con éxito!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Error de conexión. Intenta nuevamente.")
        
        st.stop()
    
    # =========================================================================
    # 🏁 INICIO DE LA APP
    # =========================================================================

    if st.session_state["authenticated"]:
        render_sidebar_community()

    # --- BARRA LATERAL ---
    with st.sidebar:
        display_text = str(st.session_state.get('display_name', '')).strip()
        user_email = str(st.session_state.get('username', 'Invitado')).strip()

        if display_text.lower() in ['nan', 'none', '']:
            texto_licencia = user_email.upper()
        else:
            texto_licencia = display_text.upper()

        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 6px solid #1E3A8A; margin-bottom: 25px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
            <p style="margin: 0; font-size: 10px; color: #666; text-transform: uppercase; letter-spacing: 1px;">Licencia Propietaria</p>
            <h2 style="margin: 5px 0 0 0; font-size: 20px; color: #1E3A8A; font-weight: 800; font-family: sans-serif; line-height: 1.2;">{texto_licencia}</h2>
            <p style="margin: 5px 0 0 0; font-size: 11px; color: #2ecc71; font-weight: bold;">● SESIÓN ACTIVA Y SEGURA</p>
        </div>
        """, unsafe_allow_html=True)

        st.header("1. Definir Estructura")
        nombre_ambiente = st.text_input("Etiqueta (ej: Cocina)", "Muro 1")
        sistema = st.selectbox("Sistema", ["Tabique Drywall (Interior)", "Cielorraso (Junta Tomada)", "Steel Frame (Muro EIFS)"])
        
        st.subheader("2. Dimensiones")
        col1, col2 = st.columns(2)
        
        if "Cielorraso" in sistema:
            ancho = col1.number_input("Ancho (m)", 0.5, 50.0, 3.0)
            largo = col2.number_input("Largo (m)", 0.5, 50.0, 4.0)
            largo_vela = st.number_input("Largo de Vela/Bajada (m)", 0.1, 5.0, 0.60, step=0.10, help="Distancia desde el techo real hasta el cielorraso.")
            altura = 0
        else:
            largo = col1.number_input("Largo (m)", 0.5, 100.0, 5.0)
            altura = col2.number_input("Altura (m)", 0.5, 20.0, 2.6)
            ancho = 0
            largo_vela = 0.60
            
            # --- GESTIÓN DE ABERTURAS ---
            st.markdown("---")
            with st.expander("🪟 Gestión de Aberturas", expanded=False):
                cA, cB, cC = st.columns([1.2, 1.2, 1])
                new_w = cA.number_input("Ancho", 0.1, 5.0, 0.9, key="new_w")
                new_h = cB.number_input("Alto", 0.1, 5.0, 2.0, key="new_h")
                new_q = cC.number_input("Cant.", 1, 10, 1, key="new_q")
                
                if st.button("⬇️ Agregar Abertura"):
                    agregar_abertura_temp(new_w, new_h, new_q)
                
                if len(st.session_state["temp_aberturas"]) > 0:
                    st.divider()
                    st.markdown("**Aberturas agregadas:**")
                    for i, ab in enumerate(st.session_state["temp_aberturas"]):
                        c_txt, c_del = st.columns([4, 1])
                        c_txt.text(f"• {ab['cant']} un. de {ab['ancho']}x{ab['alto']}m")
                        c_del.button("X", key=f"del_temp_{i}", on_click=eliminar_abertura_temp, args=(i,))

        st.markdown("---")
        st.subheader("3. Especificaciones")
        sep = st.select_slider("Modulación (cm)", [40, 48, 60], value=40)
        desp = st.slider("Desperdicio (%)", 0, 20, 10)
        aislacion = st.checkbox("Incluir Aislación")
        
        caras, capas, espesor_cielo = 1, 1, "9.5mm"
        
        if "Drywall" in sistema:
            caras = st.radio("Caras", [1, 2], horizontal=True, index=1)
            capas = 1 if st.radio("Placas x Cara", ["1", "2"], horizontal=True) == "1" else 2
        elif "Cielorraso" in sistema:
            espesor_cielo = st.radio("Placa", ["9.5mm", "12.5mm"], horizontal=True)
        elif "Steel" in sistema:
            capas = 1 if st.radio("Placas Interior", ["1", "2"], horizontal=True) == "1" else 2

        # Lógica de Cajones (Deshabilitada temporalmente como pedido)
        metros_cajon = 0 

        st.divider()
        
        if st.button("➕ Agregar al Proyecto", type="primary"):
            try:
                lista_aberturas_final = list(st.session_state["temp_aberturas"])
                
                # Invocación robusta al Factory
                calc = CalculatorFactory.get_calculator(
                    tipo_sistema=sistema, largo=largo, altura=altura, ancho=ancho,
                    separacion=sep/100, desperdicio=desp, caras=caras, capas=capas,
                    aislacion=aislacion, espesor_cielo=espesor_cielo,
                    aberturas=lista_aberturas_final,
                    metros_cajon=metros_cajon,
                    largo_vela=largo_vela
                )
                
                df_res, metadata = calc.calculate()
                
                txt_ab = "No"
                if len(lista_aberturas_final) > 0:
                    total_abs = sum(x['cant'] for x in lista_aberturas_final)
                    txt_ab = f"{total_abs} un. (Mix)"

                st.session_state["project_cart"].append({
                    "nombre": nombre_ambiente,
                    "sistema": sistema,
                    "dims": f"{largo}x{altura}m" if altura > 0 else f"{ancho}x{largo}m",
                    "aberturas": txt_ab,
                    "df": df_res,
                    "meta": metadata
                })
                
                st.toast(f"✅ {nombre_ambiente} Agregado ({metadata['m2']} m2)")
                limpiar_form_aberturas()
                
            except Exception as e:
                st.error(f"Error en cálculo: {e}")

        c_reset, c_logout = st.columns(2)
        if c_reset.button("🗑️ Reiniciar"):
            st.session_state["project_cart"] = []
            st.session_state["temp_aberturas"] = []
            st.rerun()
        c_logout.button("🔒 Salir", on_click=logout)

    # =========================================================================
    # VISTA PRINCIPAL (CARRITO)
    # =========================================================================
    st.title("🛒 Tu Proyecto")

    if not st.session_state["project_cart"]:
        st.info("👈 Configura tu primer ambiente en el menú lateral y dale a 'Agregar'.")
        st.markdown("""
        <div style="text-align: center; color: #ccc; margin-top: 50px;">
            <h1>🏗️</h1>
            <p>Tu lista de materiales aparecerá aquí</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Pestañas
        tab1, tab2 = st.tabs(["📋 Detalle por Ambiente", "📦 Total & PDF"])
        
        with tab1:
            for i, item in enumerate(st.session_state["project_cart"]):
                with st.expander(f"📍 {item['nombre']} ({item['sistema']}) - {item['meta']['m2']} m²", expanded=True):
                    st.dataframe(item['df'], use_container_width=True, hide_index=True)
                    if st.button(f"Eliminar {item['nombre']}", key=f"del_{i}"):
                        eliminar_item(i) # Función protegida
                        st.rerun()

        with tab2:
            st.markdown("### Total de Materiales a Comprar")
            # Unificar dataframes
            all_dfs = [item['df'] for item in st.session_state["project_cart"]]
            total_m2_obra = sum([item['meta']['m2'] for item in st.session_state["project_cart"]])

            if all_dfs:
                df_total = pd.concat(all_dfs)
                # Agrupar por Material y Unidad, sumando Cantidad
                df_final = df_total.groupby(["Material", "Unidad", "Categoría"], as_index=False)["Cantidad"].sum()
                
                st.dataframe(df_final, use_container_width=True, hide_index=True)
                
                st.divider()
                st.subheader("📄 Descargar Presupuesto")
                
                # Generación del PDF
                try:
                    # Preparar datos por sistema para el PDF
                    sistemas_activos = list(set([item['sistema'] for item in st.session_state["project_cart"]]))
                    system_data_final = {}
                    
                    for sys in sistemas_activos:
                        items_sys = [x for x in st.session_state["project_cart"] if x['sistema'] == sys]
                        if items_sys:
                            df_sys_raw = pd.concat([x['df'] for x in items_sys])
                            df_sys_grouped = df_sys_raw.groupby(["Material", "Unidad", "Categoría"], as_index=False)["Cantidad"].sum()
                            m2_sys = sum([x['meta']['m2'] for x in items_sys])
                            system_data_final[sys] = {'df': df_sys_grouped, 'm2': round(m2_sys, 2)}

                    nombre_para_pdf = texto_licencia
                    
                    pdf_bytes = create_pdf_bytes(
                        system_data_final, 
                        df_final, 
                        total_m2_obra, 
                        nombre_para_pdf
                    )
                    
                    st.download_button(
                        label="Descargar PDF 📥",
                        data=pdf_bytes,
                        file_name="computo_materiales.pdf",
                        mime="application/pdf",
                        type="primary"
                    )
                except Exception as e:
                    st.error(f"Error al generar PDF: {e}")

if __name__ == "__main__":
    main()