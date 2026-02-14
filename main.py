import streamlit as st
import pandas as pd
import time  
from src.core.factory import CalculatorFactory
from src.services.auth_service import login_form, logout, actualizar_nombre_display 
from src.services.pdf_service import create_pdf_bytes
from src.ui.community import render_sidebar_community

st.set_page_config(page_title="Calculadora Maestra Pro", page_icon="🏗️", layout="wide")

if "project_cart" not in st.session_state: st.session_state["project_cart"] = []
if "temp_aberturas" not in st.session_state: st.session_state["temp_aberturas"] = []

def eliminar_item(index):
    if 0 <= index < len(st.session_state["project_cart"]):
        del st.session_state["project_cart"][index]

def eliminar_abertura_temp(index):
    if 0 <= index < len(st.session_state["temp_aberturas"]):
        del st.session_state["temp_aberturas"][index]

def agregar_abertura_temp(ancho, alto, cantidad):
    if cantidad > 0:
        st.session_state["temp_aberturas"].append({"ancho": ancho, "alto": alto, "cant": cantidad})

def limpiar_form_aberturas():
    st.session_state["temp_aberturas"] = []

def main():
    if not login_form():
        return
    
    # --- ONBOARDING ---
    usuario_actual = st.session_state.get("username")
    nombre_actual = st.session_state.get("display_name")
    
    safe_nombre = str(nombre_actual).strip()
    safe_user = str(usuario_actual).strip()
    lista_invalidos = ['nan', 'none', '', 'null', 'none']

    if safe_nombre.lower() in lista_invalidos or safe_nombre.lower() == safe_user.lower():
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("### 👋 ¡Bienvenido al equipo!")
            st.info("Para generar presupuestos profesionales, necesitamos configurar el nombre de tu empresa.")
            with st.form("form_nombre_inicial"):
                nuevo_nombre = st.text_input("Nombre de tu Empresa / Marca:", placeholder="Ej: Construcciones Pérez S.A.")
                st.caption("ℹ️ Este nombre aparecerá en el encabezado de tus PDFs.")
                if st.form_submit_button("Guardar y Comenzar 🚀", type="primary", use_container_width=True):
                    if len(nuevo_nombre) < 3:
                        st.error("Nombre muy corto.")
                    else:
                        with st.spinner("Configurando..."):
                            if actualizar_nombre_display(usuario_actual, nuevo_nombre):
                                st.session_state["display_name"] = nuevo_nombre
                                st.success("¡Listo!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Error al guardar.")
        st.stop()

    # --- APP ---
    if st.session_state["authenticated"]:
        render_sidebar_community()

    with st.sidebar:
        display_text = str(st.session_state.get('display_name', '')).strip()
        texto_licencia = display_text.upper() if display_text.lower() not in lista_invalidos else "USUARIO"

       

        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 6px solid #1E3A8A; margin-bottom: 25px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
            <p style="margin: 0; font-size: 10px; color: #666; text-transform: uppercase; letter-spacing: 1px;">Licencia Propietaria</p>
            <h2 style="margin: 5px 0 0 0; font-size: 20px; color: #1E3A8A; font-weight: 800; font-family: sans-serif; line-height: 1.2;">{texto_licencia}</h2>
            <p style="margin: 5px 0 0 0; font-size: 11px; color: #2ecc71; font-weight: bold;">● SESIÓN ACTIVA</p>
        </div>
        """, unsafe_allow_html=True)

        # --- DATOS CLIENTE ---
        cliente_nombre = ""
        cliente_ubicacion = ""
        with st.expander("👤 Datos del Cliente (Opcional)"):
            cliente_nombre = st.text_input("Nombre Cliente:", placeholder="Ej: Juan Pérez")
            cliente_ubicacion = st.text_input("Ubicación/Obra:", placeholder="Ej: Av. Libertador 1234")
        
        st.header("1. Definir Estructura")
        nombre_ambiente = st.text_input("Etiqueta (ej: Cocina)", "Muro 1")
        sistema = st.selectbox("Sistema", ["Tabique Drywall (Interior)", "Cielorraso (Junta Tomada)", "Steel Frame (Muro EIFS)"])
        
        st.subheader("2. Dimensiones")
        col1, col2 = st.columns(2)
        
        if "Cielorraso" in sistema:
            ancho = col1.number_input("Ancho (m)", 0.5, 50.0, 3.0)
            largo = col2.number_input("Largo (m)", 0.5, 50.0, 4.0)
            largo_vela = st.number_input("Largo de Vela/Bajada (m)", 0.1, 5.0, 0.60, step=0.10)
            altura = 0
        else:
            largo = col1.number_input("Largo (m)", 0.5, 100.0, 5.0)
            altura = col2.number_input("Altura (m)", 0.5, 20.0, 2.6)
            ancho = 0
            largo_vela = 0.60
            
            st.markdown("---")
            with st.expander("🪟 Gestión de Aberturas"):
                cA, cB, cC = st.columns([1.2, 1.2, 1])
                new_w = cA.number_input("Ancho", 0.1, 5.0, 0.9, key="nw")
                new_h = cB.number_input("Alto", 0.1, 5.0, 2.0, key="nh")
                new_q = cC.number_input("Cant.", 1, 10, 1, key="nq")
                if st.button("⬇️ Agregar"): agregar_abertura_temp(new_w, new_h, new_q)
                
                if st.session_state["temp_aberturas"]:
                    st.divider()
                    for i, ab in enumerate(st.session_state["temp_aberturas"]):
                        c_txt, c_del = st.columns([4, 1])
                        c_txt.text(f"• {ab['cant']}x ({ab['ancho']}x{ab['alto']}m)")
                        c_del.button("X", key=f"del_{i}", on_click=eliminar_abertura_temp, args=(i,))

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

        st.divider()
        st.subheader("💰 Mano de Obra (Estimada)")
        precio_mo = st.number_input("Precio por m² ($)", min_value=0.0, value=0.0, step=100.0)

        st.divider()
        if st.button("➕ Agregar al Proyecto", type="primary"):
            try:
                calc = CalculatorFactory.get_calculator(
                    tipo_sistema=sistema, largo=largo, altura=altura, ancho=ancho,
                    separacion=sep/100, desperdicio=desp, caras=caras, capas=capas,
                    aislacion=aislacion, espesor_cielo=espesor_cielo,
                    aberturas=list(st.session_state["temp_aberturas"]),
                    metros_cajon=0,
                    largo_vela=largo_vela
                )
                
                df_res, metadata = calc.calculate()
                
                metadata['precio_mo_unitario'] = precio_mo
                metadata['total_mo_item'] = precio_mo * metadata['m2']

                st.session_state["project_cart"].append({
                    "nombre": nombre_ambiente, "sistema": sistema,
                    "dims": f"{largo}x{altura or ancho}m",
                    "df": df_res, "meta": metadata
                })
                
                st.toast(f"✅ Agregado: {nombre_ambiente}")
                limpiar_form_aberturas()
            except Exception as e:
                st.error(f"Error: {e}")

        c_r, c_l = st.columns(2)
        if c_r.button("🗑️ Reiniciar"):
            st.session_state["project_cart"] = []
            st.rerun()
        c_l.button("🔒 Salir", on_click=logout)
     # ... dentro de with st.sidebar: ...
        st.markdown("---")
        with st.expander("⚖️ Términos y Condiciones", expanded=False):
            st.markdown("""
            <div style='font-size: 10px; color: #666;'>
            1. <b>Estimación Teórica:</b> Los cálculos son aproximados y se basan en consumo estándar teórico.<br>
            2. <b>Verificación en Obra:</b> Es responsabilidad del usuario verificar las cantidades y medidas antes de realizar la compra.<br>
            3. <b>Desperdicios:</b> No se consideran desperdicios extraordinarios por errores de corte o daños.<br>
            4. <b>Responsabilidad:</b> La aplicación no se responsabiliza por diferencias de stock, sobrantes o faltantes.
            </div>
            """, unsafe_allow_html=True)
    # --- MAIN DASHBOARD ---
    st.title("📋 Tu Proyecto")

    if not st.session_state["project_cart"]:
        st.info("👈 Configura tu primer ambiente en el menú lateral.")
    else:
        all_dfs = [item['df'] for item in st.session_state["project_cart"]]
        total_m2 = sum([item['meta']['m2'] for item in st.session_state["project_cart"]])
        total_mo_global = sum([item['meta']['total_mo_item'] for item in st.session_state["project_cart"]])
        
        df_total = pd.concat(all_dfs).groupby(["Material", "Unidad", "Categoría"], as_index=False)["Cantidad"].sum()

        tab1, tab2 = st.tabs(["📋 Detalle", "📦 Total & PDF"])
        
        with tab1:
            for i, item in enumerate(st.session_state["project_cart"]):
                m2_item = item['meta']['m2']
                mo_item = item['meta']['total_mo_item']
                
                titulo = f"📍 {item['nombre']} ({m2_item:.2f} m²)"
                if mo_item > 0:
                    titulo += f" | 👷 ${mo_item:,.0f}"
                
                with st.expander(titulo, expanded=True):
                    st.dataframe(item['df'], use_container_width=True, hide_index=True)
                    if st.button("Eliminar", key=f"d{i}"): eliminar_item(i); st.rerun()

        with tab2:
            c_m2, c_mo = st.columns(2)
            c_m2.metric("Superficie Total", f"{total_m2:.2f} m²")
            c_mo.metric("Mano de Obra Estimada", f"${total_mo_global:,.0f}")
            
            st.markdown("### Lista de Materiales")
            st.dataframe(df_total, use_container_width=True, hide_index=True)
            
            st.divider()
            try:
                pdf_bytes = create_pdf_bytes(
                    st.session_state["project_cart"], 
                    df_total, 
                    total_m2, 
                    texto_licencia,
                    total_mo_global,
                    cliente_nombre,
                    cliente_ubicacion
                )
                
                # [LÓGICA DE NOMBRE ARCHIVO PERSONALIZADO]
                nombre_archivo = "computo_materiales.pdf"
                if cliente_nombre and cliente_nombre.strip():
                    # Sanitizamos el nombre
                    nombre_limpio = "".join([c if c.isalnum() else "_" for c in cliente_nombre.strip()])
                    nombre_archivo = f"computo - {nombre_limpio}.pdf"

                st.download_button(
                    label="📄 Descargar PDF Oficial", 
                    data=pdf_bytes, 
                    file_name=nombre_archivo, # <--- Variable dinámica
                    mime="application/pdf", 
                    type="primary"
                )
            except Exception as e:
                st.error(f"Error PDF: {e}")

if __name__ == "__main__":
    main()