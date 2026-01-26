from src.core.abstract_system import ConstructionSystem
from src.config.materials_db import MaterialConst as MC, Categories as Cat
import math
import pandas as pd

# ==============================================================================
# SISTEMA 1: TABIQUE DIVISORIO (W111)
# ==============================================================================
class DrywallPartition(ConstructionSystem):
    def __init__(self, largo, altura, separacion, desperdicio, caras=1, capas=1, aislacion=False, 
                 aberturas=[]):
        super().__init__(largo, altura, separacion, desperdicio)
        self.caras = caras
        self.capas = capas
        self.aislacion = aislacion
        self.aberturas = aberturas

    def calculate(self):
        # 1. ANÁLISIS DE EMPALMES
        requiere_empalme = self.altura > 2.60
        altura_calculo = (self.altura + 0.30) if requiere_empalme else self.altura
        
        # 2. CÁLCULO BASE
        ml_solera_base = self.largo * 2 
        cant_montantes_modulacion = math.ceil(self.largo / 0.40) + 1
        ml_montante_base = cant_montantes_modulacion * altura_calculo
        sup_placa_bruta = (self.largo * self.altura) * self.caras

        # 3. PROCESAMIENTO DE ABERTURAS
        sup_descuento_placas = 0
        ml_solera_refuerzo = 0   
        ml_montante_refuerzo = 0 
        ml_cantonera = 0
        
        for ab in self.aberturas:
            qty = ab['cant']
            w = ab['ancho']
            h = ab['alto']
            sup_descuento_placas += (w * h * qty) * self.caras
            
            es_puerta = h >= 2.00
            if es_puerta:
                ml_solera_refuerzo += (w + 0.40) * qty
                ml_cantonera += ((h * 2) + w) * qty
            else:
                ml_solera_refuerzo += ((w + 0.40) * 2) * qty
                ml_cantonera += ((h * 2) + (w * 2)) * qty
            
            ml_montante_refuerzo += (self.altura * 2) * qty

        # 4. CONSOLIDACIÓN
        cant_soleras_u = ((ml_solera_base + ml_solera_refuerzo) * self.desp) / MC.L_PERFIL_DW
        cant_montantes_u = ((ml_montante_base + ml_montante_refuerzo) * self.desp) / MC.L_PERFIL_DW

        self.add_material(Cat.ESTRUCTURA, MC.SOLERA_70, MC.UNITS["U"], cant_soleras_u)
        self.add_material(Cat.ESTRUCTURA, MC.MONTANTE_69, MC.UNITS["U"], cant_montantes_u)

        sup_placa_neta = max(0, sup_placa_bruta - sup_descuento_placas)
        sup_placa_final = sup_placa_neta * self.capas
        
        factor_desp_placa = 1.05 if self.altura <= 2.40 else 1.10
        factor_total_placa = factor_desp_placa + (self.desp - 1.0) 

        cant_placas = (sup_placa_final * factor_total_placa) / MC.SUP_PLACA
        self.add_material(Cat.EMPLACADO, MC.PLACA_12, MC.UNITS["U"], cant_placas)

        # Fijaciones
        cant_t1 = (cant_montantes_modulacion + (len(self.aberturas)*2)) * 8 * 1.10
        self.add_material(Cat.FIJACIONES, MC.T1, MC.UNITS["U"], cant_t1)

        cant_t2 = (sup_placa_final * 18) * 1.05
        self.add_material(Cat.FIJACIONES, MC.T2_AGUJA, MC.UNITS["U"], cant_t2)

        cant_tarugos = ((self.largo / 0.60) * 2) * 1.05
        self.add_material(Cat.FIJACIONES, MC.TARUGO_8, MC.UNITS["U"], cant_tarugos)

        self.add_material(Cat.TERMINACION, MC.CINTA, MC.UNITS["M"], sup_placa_final * 1.55)
        self.add_material(Cat.TERMINACION, MC.MASILLA, MC.UNITS["KG"], sup_placa_final * 0.90)
        
        if ml_cantonera > 0:
            self.add_material(Cat.TERMINACION, MC.CANTONERA, MC.UNITS["U"], (ml_cantonera * self.desp) / 2.60)

        if self.aislacion:
            sup_aislacion = (self.largo * self.altura) - (sup_descuento_placas / self.caras)
            self.add_material(Cat.AISLACION, MC.LANA_VIDRIO, MC.UNITS["M2"], sup_aislacion * self.desp)

        # RETORNO CON METADATA DE SUPERFICIE (Sup de una cara neta)
        sup_referencia = (self.largo * self.altura) - (sup_descuento_placas / self.caras)
        return self.get_dataframe(), {"m2": round(sup_referencia, 2), "detalle": "Muro Neto"}


# ==============================================================================
# SISTEMA 2: CIELORRASO JUNTA TOMADA (D112)
# ==============================================================================
class DrywallCeiling(ConstructionSystem):
    def __init__(self, ancho, largo_real, separacion, desperdicio, aislacion=False, espesor_placa="9.5"):
        l1, l2 = sorted([ancho, largo_real])
        self.ancho_menor = l1
        self.largo_mayor = l2
        self.plenum = 0.60 
        super().__init__(l1 * l2, 1, separacion, desperdicio)
        self.aislacion = aislacion
        self.nombre_placa = MC.PLACA_9 if "9.5" in espesor_placa else MC.PLACA_12

    def calculate(self):
        sup_neta = self.ancho_menor * self.largo_mayor
        perimetro = (self.ancho_menor + self.largo_mayor) * 2

        ml_solera = perimetro
        longitud_portadora = self.ancho_menor
        cant_lineas_portadoras = math.ceil(self.largo_mayor / 0.40) + 1
        ml_portadoras = cant_lineas_portadoras * longitud_portadora

        longitud_maestra = self.largo_mayor
        cant_lineas_maestras = math.ceil(self.ancho_menor / 1.10) + 1
        ml_maestras = cant_lineas_maestras * longitud_maestra

        puntos_por_maestra = math.ceil(longitud_maestra / 1.00) + 1
        total_puntos_cuelgue = cant_lineas_maestras * puntos_por_maestra
        ml_velas = total_puntos_cuelgue * self.plenum

        cant_soleras_u = (ml_solera * self.desp) / MC.L_PERFIL_DW
        total_ml_montantes = ml_portadoras + ml_maestras + ml_velas
        cant_montantes_u = (total_ml_montantes * self.desp) / MC.L_PERFIL_DW

        self.add_material(Cat.ESTRUCTURA, MC.SOLERA_35, MC.UNITS["U"], cant_soleras_u)
        self.add_material(Cat.ESTRUCTURA, MC.MONTANTE_35, MC.UNITS["U"], cant_montantes_u)

        factor_desp_placa = 1.15 if sup_neta < 15 else 1.10
        factor_total = factor_desp_placa + (self.desp - 1.0)
        cant_placas = (sup_neta * factor_total) / MC.SUP_PLACA
        self.add_material(Cat.EMPLACADO, self.nombre_placa, MC.UNITS["U"], cant_placas)

        nodos_cruce = cant_lineas_portadoras * cant_lineas_maestras
        cant_t1 = ((nodos_cruce * 2) + (total_puntos_cuelgue * 4)) * 1.10
        self.add_material(Cat.FIJACIONES, MC.T1, MC.UNITS["U"], cant_t1)

        cant_t2 = (sup_neta * 18) * 1.05
        self.add_material(Cat.FIJACIONES, MC.T2_AGUJA, MC.UNITS["U"], cant_t2)

        fijaciones_techo = total_puntos_cuelgue
        fijaciones_pared = (perimetro / 0.60)
        self.add_material(Cat.FIJACIONES, MC.TARUGO_8, MC.UNITS["U"], (fijaciones_techo + fijaciones_pared) * 1.05)

        if self.aislacion:
            self.add_material(Cat.AISLACION, MC.LANA_VIDRIO, MC.UNITS["M2"], sup_neta * self.desp)

        self.add_material(Cat.TERMINACION, MC.MASILLA, MC.UNITS["KG"], sup_neta * 0.90)
        self.add_material(Cat.TERMINACION, MC.CINTA, MC.UNITS["M"], sup_neta * 1.50)

        # RETORNO CON METADATA
        return self.get_dataframe(), {"m2": round(sup_neta, 2), "detalle": "Cielorraso"}


# ==============================================================================
# SISTEMA 3: STEEL FRAME + EIFS
# ==============================================================================
class SteelFrameEIFS(ConstructionSystem):
    def __init__(self, largo, altura, separacion, desperdicio, capas_int=1, aislacion=False,
                 aberturas=[]):
        super().__init__(largo, altura, separacion, desperdicio)
        self.capas_int = capas_int
        self.aislacion = aislacion
        self.aberturas = aberturas

    def calculate(self):
        sup_bruta = self.largo * self.altura
        sup_aberturas = 0
        perimetro_mochetas = 0
        
        ml_pgu = self.largo * 2
        cant_pgc_modulacion = math.ceil(self.largo / 0.40) + 1
        ml_pgc = cant_pgc_modulacion * self.altura
        ml_pgc += self.largo 

        for ab in self.aberturas:
            qty = ab['cant']
            w = ab['ancho']
            h = ab['alto']
            tipo = 'ventana' if h < 2.0 else 'puerta'
            
            sup_aberturas += (w * h * qty)
            perimetro_mochetas += ((w + h) * 2) * qty
            
            ml_pgc += ((self.altura * 2) + (h * 2)) * qty
            if w < 1.20:
                ml_pgc += ((w + 0.40) * 2) * qty
            else:
                ml_pgc += ((w + 0.60) * 3) * qty
            if tipo == 'ventana':
                ml_pgu += (w + 0.20) * qty

        ml_fleje = math.sqrt(self.largo**2 + self.altura**2) * 2
        cant_pgu_u = (ml_pgu * self.desp) / MC.L_PERFIL_SF
        cant_pgc_u = (ml_pgc * self.desp) / MC.L_PERFIL_SF 
        self.add_material(Cat.ESTRUCTURA, MC.PGU_100, MC.UNITS["U"], cant_pgu_u)
        self.add_material(Cat.ESTRUCTURA, MC.PGC_100, MC.UNITS["U"], cant_pgc_u)
        self.add_material(Cat.RIGIDIZACION, MC.FLEJE, MC.UNITS["M"], ml_fleje)

        espesor_muro = 0.15 
        sup_mochetas = perimetro_mochetas * espesor_muro
        sup_neta = max(0, sup_bruta - sup_aberturas)
        sup_eifs_total = sup_neta + sup_mochetas

        self.add_material(Cat.EIFS_SUSTRATO, MC.OSB_11, MC.UNITS["U"], (sup_bruta * self.desp) / 2.97)
        self.add_material(Cat.EIFS_AISLACION, MC.TYVEK, MC.UNITS["M2"], sup_bruta * 1.10) 
        self.add_material(Cat.EIFS_AISLACION, MC.EPS_ALTA, MC.UNITS["M2"], sup_neta * 1.08) 
        self.add_material(Cat.EIFS_BASE, MC.BASE_COAT, MC.UNITS["KG"], sup_eifs_total * 6.5)
        self.add_material(Cat.EIFS_BASE, MC.MALLA, MC.UNITS["M2"], sup_eifs_total * 1.15)

        sup_interior = sup_neta * self.capas_int
        self.add_material(Cat.INTERIOR, MC.PLACA_12, MC.UNITS["U"], (sup_interior * self.desp) / MC.SUP_PLACA)

        if self.aislacion:
            self.add_material(Cat.AISLACION, MC.LANA_VIDRIO, MC.UNITS["M2"], sup_neta * self.desp)

        cant_montantes_totales = math.ceil(ml_pgc / self.altura) 
        self.add_material(Cat.FIJACIONES, MC.TORNILLO_HEX, MC.UNITS["U"], cant_montantes_totales * 4)
        self.add_material(Cat.FIJACIONES, MC.T2_MECHA, MC.UNITS["U"], sup_bruta * 18) 
        self.add_material(Cat.FIJACIONES, MC.TORNILLO_EPS, MC.UNITS["U"], sup_eifs_total * 15)
        
        if perimetro_mochetas > 0:
            self.add_material(Cat.TERMINACION, MC.CANTONERA, MC.UNITS["U"], (perimetro_mochetas * self.desp) / 2.60)

        # RETORNO CON METADATA (Sup EIFS Total)
        return self.get_dataframe(), {"m2": round(sup_eifs_total, 2), "detalle": "EIFS + Mochetas"}