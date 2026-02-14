from fpdf import FPDF
import pandas as pd
from datetime import datetime

class PDFReport(FPDF):
    def __init__(self, user_name="Usuario", client_data=None):
        super().__init__()
        self.user_name = str(user_name).upper()
        self.client_data = client_data if client_data else {}

    def header(self):
        # --- ENCABEZADO PRINCIPAL (AZUL) ---
        if self.page_no() == 1:
            self.set_fill_color(40, 55, 71) 
            self.rect(0, 0, 210, 35, 'F') 
            self.set_font('Helvetica', 'B', 16)
            self.set_text_color(255, 255, 255)
            self.set_xy(10, 8)
            self.cell(0, 10, 'CÓMPUTO MÉTRICO TÉCNICO', 0, 0, 'L')
            self.set_font('Helvetica', '', 10)
            self.set_xy(10, 16)
            self.cell(0, 10, 'Calculadora Maestra Pro - Informe Oficial', 0, 0, 'L')
            self.set_draw_color(255, 255, 255)
            self.line(130, 5, 130, 30)
            self.set_xy(135, 8)
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(200, 200, 200)
            self.cell(65, 5, "LICENCIA OTORGADA A:", 0, 2, 'R')
            self.set_font('Helvetica', 'B', 11)
            self.set_text_color(255, 255, 255)
            self.cell(65, 6, self.user_name, 0, 2, 'R')
            self.set_font('Helvetica', 'I', 7)
            self.set_text_color(255, 100, 100)
            self.cell(65, 5, "COPIA NO AUTORIZADA", 0, 0, 'R')
            
            # --- [CORRECCIÓN 1] DATOS DEL CLIENTE EN LÍNEAS SEPARADAS ---
            c_name = self.client_data.get('nombre', '')
            c_loc = self.client_data.get('ubicacion', '')
            
            if c_name or c_loc:
                self.set_xy(0, 35)
                self.set_fill_color(240, 240, 240) # Gris muy suave
                self.rect(0, 35, 210, 16, 'F') # Agrandamos un poco el alto
                
                self.set_xy(10, 37)
                self.set_font('Helvetica', 'B', 9)
                self.set_text_color(50, 50, 50)
                
                if c_name:
                    self.cell(0, 5, f"CLIENTE: {c_name.upper()}", 0, 1, 'L')
                
                if c_loc:
                    self.set_x(10) # Reseteamos margen X
                    self.cell(0, 5, f"UBICACIÓN: {c_loc.upper()}", 0, 1, 'L')
                
                self.ln(10) # Espacio extra
            else:
                self.ln(25) # Espacio normal

        else:
            self.set_fill_color(240, 240, 240) 
            self.rect(0, 0, 210, 10, 'F')
            self.set_font('Helvetica', 'B', 8)
            self.set_text_color(100, 100, 100)
            self.set_xy(10, 0)
            self.cell(0, 10, f'ANEXO TÉCNICO | {self.user_name}', 0, 0, 'L')
            self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
        texto_pie = f'Reporte generado el {hoy} por {self.user_name} | Página {self.page_no()}'
        self.cell(0, 10, texto_pie, 0, 0, 'C')

    def print_final_disclaimer(self):
        self.ln(15)
        self.set_draw_color(180, 0, 0)
        self.set_line_width(0.5)
        ejex = self.get_x()
        ejey = self.get_y()
        self.line(10, ejey, 200, ejey)
        self.ln(5)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(150, 0, 0)
        texto_legal = (
            f"AVISO DE CONFIDENCIALIDAD Y PROPIEDAD INTELECTUAL\n"
            f"Este documento técnico y los cálculos contenidos en él son de uso exclusivo "
            f"para el titular de la licencia: {self.user_name}.\n"
            "Queda estrictamente prohibida su distribución, venta o reproducción parcial o total "
            "sin la autorización expresa del proveedor del software."
        )
        self.multi_cell(0, 5, texto_legal, align='C')

    def chapter_title(self, title, subtitle=""):
        self.set_font('Helvetica', 'B', 12)
        self.set_fill_color(220, 220, 220)
        self.set_text_color(0, 0, 0)
        
        if self.get_y() > 250:
            self.add_page()
            
        self.ln(5)
        self.cell(0, 8, f"  {title}", 0, 1, 'L', 1)
        if subtitle:
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(50, 50, 50)
            self.cell(0, 6, f"   {subtitle}", 0, 1, 'L')
        self.ln(2)

    def generate_table(self, df):
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(52, 152, 219) 
        self.set_text_color(255, 255, 255)
        self.set_draw_color(200, 200, 200)

        w_cat, w_mat, w_uni, w_cant = 40, 95, 20, 25
        h = 6

        self.cell(w_cat, h, "CATEGORÍA", 1, 0, 'C', 1)
        self.cell(w_mat, h, "MATERIAL", 1, 0, 'C', 1)
        self.cell(w_uni, h, "UNIDAD", 1, 0, 'C', 1)
        self.cell(w_cant, h, "CANT.", 1, 1, 'C', 1)

        self.set_font('Helvetica', size=8)
        self.set_text_color(0, 0, 0)
        
        alternate = False
        for _, row in df.iterrows():
            if alternate:
                self.set_fill_color(245, 245, 245)
            else:
                self.set_fill_color(255, 255, 255)
            
            cat = str(row['Categoría'])[:22]
            mat = str(row['Material'])[:55]
            try:
                cat = cat.encode('latin-1', 'replace').decode('latin-1')
                mat = mat.encode('latin-1', 'replace').decode('latin-1')
            except:
                pass
                
            fill_mode = True 
            self.cell(w_cat, h, cat, 1, 0, 'L', fill_mode)
            self.cell(w_mat, h, mat, 1, 0, 'L', fill_mode)
            self.cell(w_uni, h, str(row['Unidad']), 1, 0, 'C', fill_mode)
            self.cell(w_cant, h, f"{int(row['Cantidad'])}", 1, 1, 'C', fill_mode)
            alternate = not alternate 

def create_pdf_bytes(project_items, df_total, total_m2_global, user_name, total_mo_global=0, client_name="", client_loc=""):
    """
    project_items: Lista directa del carrito (st.session_state["project_cart"])
    """
    c_data = {"nombre": client_name, "ubicacion": client_loc}
    
    pdf = PDFReport(user_name, client_data=c_data)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25) 

    # RESUMEN EJECUTIVO
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_text_color(50, 50, 50)
    # [CORRECCIÓN 2] Decimales formateados
    pdf.cell(0, 10, f"RESUMEN DE PROYECTO: Superficie Total Computada: {total_m2_global:.2f} m2", ln=True)
    pdf.ln(5)

    # PARTE 1: Total Unificado
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(40, 55, 71)
    pdf.cell(0, 10, "RESUMEN TOTAL DE COMPRAS (UNIFICADO)", ln=True, align='C')
    pdf.ln(5)
    pdf.generate_table(df_total)
    
    pdf.ln(10)

    # PARTE 2: Detalle (ITEM POR ITEM - CORRECCIÓN 3)
    pdf.add_page() 
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, "DETALLE DE MATERIALES POR AMBIENTE", ln=True)
    
    for item in project_items:
        nombre = item['nombre']
        sistema = item['sistema']
        m2 = item['meta']['m2']
        df_item = item['df']
        
        # Título: "Cocina (Drywall) - 15.20 m2"
        pdf.chapter_title(f"{nombre} ({sistema})", subtitle=f"Superficie: {m2:.2f} m2")
        pdf.generate_table(df_item)
        pdf.ln(4)

    # PARTE 3: Presupuesto Mano de Obra
    if total_mo_global > 0:
        pdf.add_page()
        pdf.set_fill_color(220, 255, 220) 
        pdf.rect(0, 0, 210, 30, 'F') 
        pdf.ln(5)
        
        pdf.set_font("Helvetica", 'B', 16)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(0, 10, "PRESUPUESTO ESTIMADO DE MANO DE OBRA", ln=True, align='C')
        pdf.ln(10)
        
        pdf.set_font("Helvetica", 'B', 11)
        pdf.set_text_color(0, 0, 0)
        
        pdf.cell(140, 10, "CONCEPTO POR AMBIENTE", 1)
        pdf.cell(50, 10, "SUBTOTAL", 1, 1, 'C')
        
        pdf.set_font("Helvetica", '', 10)
        
        # Iteramos por ITEM también para el detalle de mano de obra
        for item in project_items:
            mo_item = item['meta'].get('total_mo_item', 0)
            if mo_item > 0:
                nombre = item['nombre']
                m2 = item['meta']['m2']
                pdf.cell(140, 8, f"{nombre} ({m2:.2f} m2)", 1)
                pdf.cell(50, 8, f"${mo_item:,.0f}", 1, 1, 'C')
        
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(140, 12, "TOTAL MANO DE OBRA", 1, 0, 'R')
        pdf.set_fill_color(200, 255, 200)
        pdf.cell(50, 12, f"${total_mo_global:,.0f}", 1, 1, 'C', 1)

    pdf.print_final_disclaimer()
    
    
    salida = pdf.output(dest='S')
    if isinstance(salida, str):
        return salida.encode('latin-1')
    return bytes(salida)