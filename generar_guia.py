from fpdf import FPDF

class PDFGuia(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_fill_color(40, 55, 71)
        self.set_text_color(255,255,255)
        self.cell(0, 15, ' GUÍA DE COMANDOS - CALCULADORA MAESTRA', 0, 1, 'C', 1)
        self.ln(5)

    def add_section(self, title, data):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 8, title, 0, 1, 'L', 1)
        self.ln(2)
        
        self.set_font('Courier', '', 10) # Courier para que parezca código
        for cmd, desc in data:
            self.set_text_color(180, 0, 0) # Rojo oscuro para comando
            self.cell(90, 6, cmd, 1)
            self.set_text_color(50, 50, 50) # Gris para descripción
            self.set_font('Helvetica', '', 9)
            self.cell(0, 6, desc, 1, 1)
            self.set_font('Courier', '', 10)
        self.ln(5)

pdf = PDFGuia()
pdf.add_page()

# Datos
rutina = [
    ("venv\\Scripts\\activate", "ACTIVA el entorno. Házlo siempre al iniciar."),
    ("streamlit run main.py", "EJECUTA la aplicación en el navegador."),
    ("Ctrl + C", "DETIENE la ejecución en la terminal."),
    ("deactivate", "SALE del entorno virtual.")
]

mantenimiento = [
    ("pip install [nombre]", "Instala una librería nueva."),
    ("pip freeze > requirements.txt", "Guarda las versiones actuales en el archivo."),
    ("pip install -r requirements.txt", "Instala todo desde el archivo (Rescate)."),
    ("python -m venv venv", "CREA el entorno (Solo 1 vez).")
]

tips = [
    ("cls", "Limpia la pantalla de la terminal (Windows)."),
    ("Arrow Up (Flecha Arriba)", "Repite el último comando escrito."),
    ("Tab", "Autocompleta nombres de archivos/carpetas.")
]

pdf.add_section("1. RUTINA DIARIA (VIDA O MUERTE)", rutina)
pdf.add_section("2. MANTENIMIENTO Y DEPENDENCIAS", mantenimiento)
pdf.add_section("3. TRUCOS DE TERMINAL", tips)

pdf.output("Guia_Comandos_Python.pdf")
print("✅ ¡PDF Generado con éxito! Busca 'Guia_Comandos_Python.pdf' en tu carpeta.")