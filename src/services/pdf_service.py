from fpdf import FPDF
import pandas as pd
from datetime import datetime

class PDFReport(FPDF):
    def __init__(self, user_name="Usuario"):
        super().__init__()
        self.user_name = str(user_name).upper()

    def header(self):
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
            self.ln(25)
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

def create_pdf_bytes(systems_dict, df_total, total_m2_global, user_name):
    """
    Genera el PDF con el orden: TOTAL -> DETALLE.
    """
    pdf = PDFReport(user_name)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25) 

    # RESUMEN EJECUTIVO
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, f"RESUMEN DE PROYECTO: Superficie Total Computada: {total_m2_global} m2", ln=True)
    pdf.ln(5)

    # [CORRECCIÓN DE ORDEN] PARTE 1: Total Unificado
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(40, 55, 71)
    pdf.cell(0, 10, "RESUMEN TOTAL DE COMPRAS (UNIFICADO)", ln=True, align='C')
    pdf.ln(5)
    pdf.generate_table(df_total)
    
    pdf.ln(10) # Espacio separador

    # PARTE 2: Desglose por Sistema
    pdf.add_page() # Saltamos hoja para el detalle
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 10, "DETALLE DE MATERIALES POR AMBIENTE/SISTEMA", ln=True)
    
    for sistema, data in systems_dict.items():
        df_sys = data['df']
        m2_sys = data['m2']
        pdf.chapter_title(f"SISTEMA: {sistema}", subtitle=f"Superficie: {m2_sys} m2")
        pdf.generate_table(df_sys)
        pdf.ln(4)

    pdf.print_final_disclaimer()
    return bytes(pdf.output())