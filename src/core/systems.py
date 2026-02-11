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
        altura_calculo = (self.altura + 0.40) if requiere_empalme else self.altura
        
        # 2. CÁLCULO BASE
        ml_solera_base = self.largo * 2 
        cant_montantes_modulacion = math.ceil(self.largo / self.sep) + 1
        
        ml_montante_total = cant_montantes_modulacion * altura_calculo
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

        # 4. MATERIALES
        # Perfiles
        cant_soleras_u = math.ceil(((ml_solera_base + ml_solera_refuerzo) * self.desp) / MC.L_PERFIL_DW)
        cant_montantes_u = math.ceil(((ml_montante_total + ml_montante_refuerzo) * self.desp) / MC.L_PERFIL_DW)

        self.add_material(Cat.ESTRUCTURA, MC.SOLERA_70, MC.UNITS["U"], cant_soleras_u)
        self.add_material(Cat.ESTRUCTURA, MC.MONTANTE_69, MC.UNITS["U"], cant_montantes_u)

        # Placas
        sup_placa_neta = max(0, sup_placa_bruta - sup_descuento_placas)
        sup_placa_final = sup_placa_neta * self.capas
        cant_placas = math.ceil((sup_placa_final * self.desp) / MC.SUP_PLACA)
        self.add_material(Cat.EMPLACADO, MC.PLACA_12, MC.UNITS["U"], cant_placas)

        # Fijaciones
        t1_estructura = (cant_montantes_modulacion * 4) + (len(self.aberturas) * 8)
        if requiere_empalme:
            t1_estructura += (cant_montantes_modulacion * 4)
            
        self.add_material(Cat.FIJACIONES, MC.T1, MC.UNITS["U"], math.ceil(t1_estructura * 1.10))

        cant_t2 = (sup_placa_final * 18)
        self.add_material(Cat.FIJACIONES, MC.T2_AGUJA, MC.UNITS["U"], math.ceil(cant_t2 * 1.05))

        cant_tarugos = math.ceil((self.largo / 0.60) * 2)
        self.add_material(Cat.FIJACIONES, MC.TARUGO_8, MC.UNITS["U"], math.ceil(cant_tarugos * 1.05))

        # Terminaciones
        self.add_material(Cat.TERMINACION, MC.CINTA, MC.UNITS["M"], math.ceil(sup_placa_final * 1.55))
        
        # [CORRECCIÓN] Masilla: Base por m2 + Adicional por cantoneras
        consumo_masilla = (sup_placa_final * 0.90) + (ml_cantonera * 0.40) # Agregamos carga por cantonera
        self.add_material(Cat.TERMINACION, MC.MASILLA, MC.UNITS["KG"], math.ceil(consumo_masilla))
        
        if ml_cantonera > 0:
            self.add_material(Cat.TERMINACION, MC.CANTONERA, MC.UNITS["U"], math.ceil((ml_cantonera * self.desp) / 2.60))

        if self.aislacion:
            # [CORRECCIÓN] Nombre unificado
            sup_aislacion = (self.largo * self.altura) - (sup_descuento_placas / self.caras)
            self.add_material(Cat.AISLACION, "Aislación", MC.UNITS["M2"], math.ceil(sup_aislacion * self.desp))

        return self.get_dataframe(), {"m2": round(sup_placa_neta/self.capas/self.caras, 2), "detalle": "Muro"}


# ==============================================================================
# SISTEMA 2: CIELORRASO
# ==============================================================================
class DrywallCeiling(ConstructionSystem):
    def __init__(self, ancho, largo_real, separacion, desperdicio, aislacion=False, espesor_placa="9.5", largo_vela=0.60):
        l1, l2 = sorted([ancho, largo_real])
        self.ancho_menor = l1
        self.largo_mayor = l2
        self.largo_vela = largo_vela
        super().__init__(l1 * l2, 1, separacion, desperdicio)
        self.aislacion = aislacion
        self.nombre_placa = MC.PLACA_9 if "9.5" in espesor_placa else MC.PLACA_12

    def calculate(self):
        sup_neta = self.ancho_menor * self.largo_mayor
        perimetro = (self.ancho_menor + self.largo_mayor) * 2

        # Estructura
        ml_solera = self.largo_mayor * 2
        cant_soleras_u = math.ceil((ml_solera * self.desp) / MC.L_PERFIL_DW)
        
        ml_cierre = self.ancho_menor * 2
        
        largo_portante = self.ancho_menor + (0.40 if self.ancho_menor > 2.60 else 0)
        num_portantes = math.ceil(self.largo_mayor / self.sep) + 1
        ml_portadoras = num_portantes * largo_portante

        largo_maestra = self.largo_mayor + (0.40 if self.largo_mayor > 2.60 else 0)
        num_maestras = math.ceil(self.ancho_menor / 1.10) + 1
        ml_maestras = num_maestras * largo_maestra

        puntos_por_maestra = math.ceil(self.largo_mayor / 0.80) + 1
        total_velas = num_maestras * puntos_por_maestra
        ml_velas = total_velas * self.largo_vela

        total_ml_montantes = ml_cierre + ml_portadoras + ml_maestras + ml_velas
        cant_montantes_u = math.ceil((total_ml_montantes * self.desp) / MC.L_PERFIL_DW)

        self.add_material(Cat.ESTRUCTURA, MC.SOLERA_35, MC.UNITS["U"], cant_soleras_u)
        self.add_material(Cat.ESTRUCTURA, MC.MONTANTE_35, MC.UNITS["U"], cant_montantes_u)

        # Placas
        cant_placas = math.ceil((sup_neta * self.desp) / MC.SUP_PLACA)
        self.add_material(Cat.EMPLACADO, self.nombre_placa, MC.UNITS["U"], cant_placas)

        # Fijaciones
        cruces = num_portantes * num_maestras
        t1_total = (cruces * 2) + (cruces * 1) 
        t1_base = 0
        if self.ancho_menor > 2.60: t1_base += num_portantes * 4
        if self.largo_mayor > 2.60: t1_base += num_maestras * 4
        
        self.add_material(Cat.FIJACIONES, MC.T1, MC.UNITS["U"], math.ceil((t1_total + t1_base) * 1.10))
        
        t2_total = (sup_neta * 18) + (cruces * 4)
        self.add_material(Cat.FIJACIONES, MC.T2_AGUJA, MC.UNITS["U"], math.ceil(t2_total * 1.05))

        fijaciones_pared = math.ceil(perimetro / 0.60)
        self.add_material(Cat.FIJACIONES, MC.TARUGO_8, MC.UNITS["U"], math.ceil(total_velas + fijaciones_pared))

        if self.aislacion:
            # [CORRECCIÓN] Nombre unificado
            self.add_material(Cat.AISLACION, "Aislación", MC.UNITS["M2"], math.ceil(sup_neta * self.desp))

        self.add_material(Cat.TERMINACION, MC.MASILLA, MC.UNITS["KG"], math.ceil(sup_neta * 0.90))
        self.add_material(Cat.TERMINACION, MC.CINTA, MC.UNITS["M"], math.ceil(sup_neta * 1.50))

        return self.get_dataframe(), {"m2": round(sup_neta, 2), "detalle": "Cielorraso"}


# ==============================================================================
# SISTEMA 3: STEEL FRAME
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
        
        ml_pgu = (self.largo * 2) 
        for ab in self.aberturas:
            if ab['alto'] < 2.0:
                ml_pgu += (ab['ancho'] + 0.20) * ab['cant']
        
        cant_pgu_u = math.ceil((ml_pgu * self.desp) / MC.L_PERFIL_SF)
        
        cant_montantes_teoricos = math.ceil(self.largo / self.sep) + 1
        extras_aberturas = 0
        for ab in self.aberturas:
            qty = ab['cant']
            sup_aberturas += (ab['ancho'] * ab['alto'] * qty)
            perimetro_mochetas += ((ab['ancho'] + ab['alto']) * 2) * qty
            extras_aberturas += (2 * qty)
            
        total_postes_necesarios = cant_montantes_teoricos + extras_aberturas
        
        posts_por_barra = math.floor(6.00 / self.altura) if self.altura > 0 else 1
        if posts_por_barra < 1: posts_por_barra = 1
        
        cant_pgc_u = math.ceil((total_postes_necesarios * self.desp) / posts_por_barra)

        self.add_material(Cat.ESTRUCTURA, MC.PGU_100, MC.UNITS["U"], cant_pgu_u)
        self.add_material(Cat.ESTRUCTURA, MC.PGC_100, MC.UNITS["U"], cant_pgc_u)
        
        ml_fleje = math.sqrt(self.largo**2 + self.altura**2) * 2
        self.add_material(Cat.RIGIDIZACION, MC.FLEJE, MC.UNITS["M"], math.ceil(ml_fleje))

        sup_neta = max(0, sup_bruta - sup_aberturas)
        sup_eifs_total = sup_neta + (perimetro_mochetas * 0.15)

        self.add_material(Cat.EIFS_SUSTRATO, MC.OSB_11, MC.UNITS["U"], math.ceil((sup_bruta * self.desp) / 2.97))
        self.add_material(Cat.EIFS_AISLACION, MC.TYVEK, MC.UNITS["M2"], math.ceil(sup_bruta * 1.10)) 
        self.add_material(Cat.EIFS_AISLACION, MC.EPS_ALTA, MC.UNITS["M2"], math.ceil(sup_neta * 1.08)) 
        self.add_material(Cat.EIFS_BASE, MC.BASE_COAT, MC.UNITS["KG"], math.ceil(sup_eifs_total * 6.5))
        self.add_material(Cat.EIFS_BASE, MC.MALLA, MC.UNITS["M2"], math.ceil(sup_eifs_total * 1.15))

        sup_interior = sup_neta * self.capas_int
        self.add_material(Cat.INTERIOR, MC.PLACA_12, MC.UNITS["U"], math.ceil((sup_interior * self.desp) / MC.SUP_PLACA))

        if self.aislacion:
            # [CORRECCIÓN] Nombre unificado
            self.add_material(Cat.AISLACION, "Aislación", MC.UNITS["M2"], math.ceil(sup_neta * self.desp))

        self.add_material(Cat.FIJACIONES, MC.TORNILLO_HEX, MC.UNITS["U"], math.ceil(total_postes_necesarios * 8))
        self.add_material(Cat.FIJACIONES, MC.T2_MECHA, MC.UNITS["U"], math.ceil(sup_bruta * 18)) 
        self.add_material(Cat.FIJACIONES, MC.TORNILLO_EPS, MC.UNITS["U"], math.ceil(sup_eifs_total * 15))
        
        if perimetro_mochetas > 0:
            self.add_material(Cat.TERMINACION, MC.CANTONERA, MC.UNITS["U"], math.ceil((perimetro_mochetas * self.desp) / 2.60))

        return self.get_dataframe(), {"m2": round(sup_eifs_total, 2), "detalle": "EIFS"}