import pandas as pd
import math

# --- CLASE BASE ---
class BaseCalculator:
    def __init__(self, largo, altura, ancho, separacion, desperdicio, caras, capas, aislacion, aberturas, metros_cajon=0, largo_vela=0.60, **kwargs):
        """
        __init__ Acepta **kwargs al final para absorber cualquier parámetro extra
        que venga del Factory pero que esta clase base no necesite usar.
        Esto evita el error: 'unexpected keyword argument'.
        """
        self.largo = largo
        self.altura = altura
        self.ancho = ancho 
        self.separacion = separacion 
        self.desperdicio = 1 + (desperdicio / 100)
        self.caras = caras
        self.capas = capas
        self.aislacion = aislacion
        self.aberturas = aberturas
        self.metros_cajon = metros_cajon
        self.largo_vela = largo_vela 
        # kwargs se ignora aquí intencionalmente para limpiar argumentos no usados

    def _calcular_superficie_real(self):
        """Calcula m2 brutos menos aberturas"""
        sup_bruta = 0
        if self.altura > 0: # Es pared
            sup_bruta = self.largo * self.altura
        else: # Es cielorraso
            sup_bruta = self.largo * self.ancho

        sup_aberturas = 0
        for ab in self.aberturas:
            sup_aberturas += (ab['ancho'] * ab['alto']) * ab['cant']
        
        return max(sup_bruta - sup_aberturas, 0)
    
    def _get_largo_estructural(self, longitud_a_cubrir):
        """
        Calcula los metros lineales REALES necesarios considerando empalmes de 40cm.
        (SOLO PARA DRYWALL Y CIELORRASOS - NO APLICAR EN STEEL FRAME)
        """
        if longitud_a_cubrir <= 2.60:
            return longitud_a_cubrir
        
        remanente = longitud_a_cubrir - 2.60
        perfiles_extra = math.ceil(remanente / 2.20)
        longitud_total_material = longitud_a_cubrir + (perfiles_extra * 0.40)
        return longitud_total_material

    def _agregar_cajones(self, data):
        """Lógica de Cajones/Dinteles"""
        if self.metros_cajon > 0:
            # Estructura
            data.append({"Material": "Solera 35mm (2.60m)", "Cantidad": math.ceil((self.metros_cajon * 1.5) / 2.6), "Unidad": "Unidad", "Categoría": "Perfiles"})
            data.append({"Material": "Montante 34mm (2.60m)", "Cantidad": math.ceil((self.metros_cajon * 1.5) / 2.6), "Unidad": "Unidad", "Categoría": "Perfiles"})
            
            m2_cajon = self.metros_cajon * 0.8
            es_steel = "SteelFrameCalculator" in self.__class__.__name__
            nombre_placa = "Placa Cementicia/Exterior" if es_steel else "Placa Standard 12.5mm (1.20x2.40)"
            
            placas_extra = math.ceil(m2_cajon / 2.88)
            data.append({"Material": nombre_placa, "Cantidad": placas_extra, "Unidad": "Unidad", "Categoría": "Placas"})
            
            cant_cantoneras = math.ceil(self.metros_cajon / 2.60)

            if es_steel:
                data.append({"Material": "Cantonera PVC con Malla (2.50m)", "Cantidad": cant_cantoneras, "Unidad": "Unidad", "Categoría": "Masillas y Acc."})
            else:
                data.append({"Material": "Cantonera Metálica (2.60m)", "Cantidad": cant_cantoneras, "Unidad": "Unidad", "Categoría": "Masillas y Acc."})
                # Tornillos T2 sueltos (Unidad)
                tornillos_cantonera = cant_cantoneras * 24
                tornillos_placa_cajon = m2_cajon * 15
                total_t2_extra = math.ceil(tornillos_cantonera + tornillos_placa_cajon)
                data.append({"Material": "Tornillos T2", "Cantidad": total_t2_extra, "Unidad": "Unidad", "Categoría": "Tornillos"})

        return data

# --- CALCULADORA DRYWALL (TABIQUES) ---
class DrywallCalculator(BaseCalculator):
    # Hereda __init__ de BaseCalculator, gracias a **kwargs no fallará si recibe espesor_cielo
    
    def calculate(self):
        m2_real = self._calcular_superficie_real()
        m2_con_desperdicio = m2_real * self.desperdicio
        
        # PLACAS
        sup_placas = m2_con_desperdicio * self.caras * self.capas
        m2_placa = 2.88 
        cant_placas = math.ceil(sup_placas / m2_placa)

        # PERFILES 
        ml_montante_unitario = self._get_largo_estructural(self.altura)
        
        ml_soleras = (self.largo * 2) * self.desperdicio
        cant_soleras = math.ceil(ml_soleras / 2.60)

        extras_aberturas = sum([ab['cant'] * 2 for ab in self.aberturas])
        num_montantes = ((self.largo / self.separacion) + 1) + extras_aberturas
        
        total_ml_montantes = num_montantes * ml_montante_unitario * self.desperdicio
        cant_montantes = math.ceil(total_ml_montantes / 2.60)

        # TORNILLOS (UNIDADES ENTERAS)
        tornillos_t1 = (cant_montantes * 4) + (ml_soleras * 2) 
        if self.altura > 2.60:
            num_empalmes_por_montante = math.ceil((self.altura - 2.60) / 2.20)
            tornillos_t1 += (num_empalmes_por_montante * num_montantes * 4)

        tornillos_t2 = m2_real * 18 * self.caras * self.capas
        
        # INSUMOS (KG y METROS)
        metros_cinta = m2_real * 1.60 * self.caras
        kg_masilla = m2_real * 1.2 * self.caras

        cant_aislacion = 0
        if self.aislacion:
            cant_aislacion = math.ceil(m2_con_desperdicio / 12)

        data = [
            {"Material": "Placa Standard 12.5mm (1.20x2.40)", "Cantidad": cant_placas, "Unidad": "Unidad", "Categoría": "Placas"},
            {"Material": "Solera 70mm (2.60m)", "Cantidad": cant_soleras, "Unidad": "Unidad", "Categoría": "Perfiles"},
            {"Material": "Montante 69mm (2.60m)", "Cantidad": cant_montantes, "Unidad": "Unidad", "Categoría": "Perfiles"},
            {"Material": "Tornillos T1 Aguja", "Cantidad": math.ceil(tornillos_t1), "Unidad": "Unidad", "Categoría": "Tornillos"},
            {"Material": "Tornillos T2 Aguja", "Cantidad": math.ceil(tornillos_t2), "Unidad": "Unidad", "Categoría": "Tornillos"},
            {"Material": "Cinta de Papel", "Cantidad": math.ceil(metros_cinta), "Unidad": "ml", "Categoría": "Masillas y Acc."},
            {"Material": "Masilla", "Cantidad": math.ceil(kg_masilla), "Unidad": "kg", "Categoría": "Masillas y Acc."},
            {"Material": "Fijaciones/Tarugos 8mm", "Cantidad": math.ceil((ml_soleras*2)), "Unidad": "Unidad", "Categoría": "Fijaciones"},
        ]
        if cant_aislacion > 0:
            data.append({"Material": "Lana de Vidrio 50mm (Rollo)", "Cantidad": cant_aislacion, "Unidad": "Rollo", "Categoría": "Aislación"})

        data = self._agregar_cajones(data)
        # Forzamos conversión a int para visualización limpia
        df = pd.DataFrame(data)
        df["Cantidad"] = df["Cantidad"].apply(lambda x: int(math.ceil(x)))
        return df, {"m2": round(m2_real, 2)}

# --- CALCULADORA CIELORRASO ---
class CielorrasoCalculator(BaseCalculator):
    def __init__(self, **kwargs):
        # Extraemos lo especifico de esta clase
        self.espesor_cielo = kwargs.pop('espesor_cielo', '9.5mm')
        # Pasamos el resto a Base (que ahora acepta basura en kwargs)
        super().__init__(**kwargs)

    def calculate(self):
        m2_real = self._calcular_superficie_real()
        m2_con_desperdicio = m2_real * self.desperdicio
        
        lado_largo = max(self.largo, self.ancho)
        lado_corto = min(self.largo, self.ancho)
        perimetro_total = (lado_largo + lado_corto) * 2

        # 1. PLACAS
        m2_placa = 2.88
        nombre_placa = f"Placa {self.espesor_cielo} (1.20x2.40)"
        cant_placas = math.ceil(m2_con_desperdicio / m2_placa)

        # 2. ESTRUCTURA 
        ml_soleras = lado_largo * 2
        cant_soleras = math.ceil(ml_soleras / 2.60) 

        ml_montantes_perimetro = lado_corto * 2
        
        largo_efectivo_portante = self._get_largo_estructural(lado_corto)
        num_vigas_portantes = math.ceil(lado_largo / self.separacion) + 1
        ml_portantes = num_vigas_portantes * largo_efectivo_portante
        
        largo_efectivo_maestra = self._get_largo_estructural(lado_largo)
        separacion_maestras = 1.10
        num_vigas_maestras = math.ceil(lado_corto / separacion_maestras) + 1
        ml_maestras = num_vigas_maestras * largo_efectivo_maestra
        
        velas_por_maestra = math.ceil(lado_largo / 0.80) 
        total_velas = velas_por_maestra * num_vigas_maestras
        ml_velas = total_velas * self.largo_vela 
        
        total_ml_montantes = ml_montantes_perimetro + ml_portantes + ml_maestras + ml_velas
        cant_montantes = math.ceil((total_ml_montantes * self.desperdicio) / 2.60)

        # 3. FIJACIONES
        fijaciones_perimetro = math.ceil(perimetro_total / 0.60)
        fijaciones_techo = total_velas
        total_tarugos = fijaciones_perimetro + fijaciones_techo
        
        cruces = num_vigas_portantes * num_vigas_maestras
        tornillos_uniones = cruces * 2 
        tornillos_perimetro = num_vigas_portantes * 2 
        
        num_empalmes_portantes = math.ceil((lado_corto - 2.60) / 2.20) if lado_corto > 2.60 else 0
        num_empalmes_maestras = math.ceil((lado_largo - 2.60) / 2.20) if lado_largo > 2.60 else 0
        total_empalmes = (num_empalmes_portantes * num_vigas_portantes) + (num_empalmes_maestras * num_vigas_maestras)
        tornillos_empalmes = total_empalmes * 4

        tornillos_t1 = tornillos_uniones + tornillos_perimetro + tornillos_empalmes
        tornillos_t2 = m2_real * 18
        
        kg_masilla = m2_real * 1.2
        metros_cinta = m2_real * 1.6

        data = [
            {"Material": nombre_placa, "Cantidad": cant_placas, "Unidad": "Unidad", "Categoría": "Placas"},
            {"Material": "Solera 35mm (2.60m)", "Cantidad": cant_soleras, "Unidad": "Unidad", "Categoría": "Perfiles"},
            {"Material": "Montante 34mm (2.60m)", "Cantidad": cant_montantes, "Unidad": "Unidad", "Categoría": "Perfiles"},
            {"Material": "Tornillos T1 Aguja", "Cantidad": math.ceil(tornillos_t1), "Unidad": "Unidad", "Categoría": "Tornillos"},
            {"Material": "Tornillos T2 Aguja", "Cantidad": math.ceil(tornillos_t2), "Unidad": "Unidad", "Categoría": "Tornillos"},
            {"Material": "Fijaciones 8mm (Kit)", "Cantidad": total_tarugos, "Unidad": "Kit", "Categoría": "Fijaciones"},
            {"Material": "Cinta de Papel", "Cantidad": math.ceil(metros_cinta), "Unidad": "ml", "Categoría": "Masillas y Acc."},
            {"Material": "Masilla", "Cantidad": math.ceil(kg_masilla), "Unidad": "kg", "Categoría": "Masillas y Acc."},
        ]

        if self.aislacion:
            cant_ais = math.ceil(m2_con_desperdicio / 12)
            data.append({"Material": "Lana de Vidrio (Rollo)", "Cantidad": cant_ais, "Unidad": "Rollo", "Categoría": "Aislación"})

        data = self._agregar_cajones(data)
        df = pd.DataFrame(data)
        df["Cantidad"] = df["Cantidad"].apply(lambda x: int(math.ceil(x)))
        return df, {"m2": round(m2_real, 2)}

# --- CALCULADORA STEEL FRAME ---
class SteelFrameCalculator(BaseCalculator):
    def calculate(self):
        m2_real = self._calcular_superficie_real()
        m2_con_desperdicio = m2_real * self.desperdicio

        cant_placas_ext = math.ceil(m2_con_desperdicio / 2.88)
        cant_placas_int = math.ceil((m2_con_desperdicio * self.capas) / 2.88)

        ml_pgu_total = (self.largo * 2) * self.desperdicio
        cant_pgu = math.ceil(ml_pgu_total / 6.00) 

        extras_aberturas = sum([ab['cant'] * 2 for ab in self.aberturas])
        num_montantes = (math.ceil(self.largo / self.separacion) + 1) + extras_aberturas
        posts_por_barra = math.floor(6.00 / self.altura)
        if posts_por_barra < 1: posts_por_barra = 1 
        cant_pgc = math.ceil((num_montantes * self.desperdicio) / posts_por_barra)

        tornillos_hex = num_montantes * 4 
        tornillos_t2_mecha = m2_real * 20 
        tornillos_t2_aguja = m2_real * 18 * self.capas 

        data = [
            {"Material": "Placa Cementicia 10mm (1.20x2.40)", "Cantidad": cant_placas_ext, "Unidad": "Unidad", "Categoría": "Placas Ext."},
            {"Material": "Placa Yeso 12.5mm (1.20x2.40)", "Cantidad": cant_placas_int, "Unidad": "Unidad", "Categoría": "Placas Int."},
            {"Material": "PGU 100mm (6m)", "Cantidad": cant_pgu, "Unidad": "Barra", "Categoría": "Perfiles Steel"},
            {"Material": "PGC 100mm (6m)", "Cantidad": cant_pgc, "Unidad": "Barra", "Categoría": "Perfiles Steel"},
            {"Material": "Tornillos Hexagonal", "Cantidad": math.ceil(tornillos_hex), "Unidad": "Unidad", "Categoría": "Fijaciones"},
            {"Material": "Tornillos T2 Mecha", "Cantidad": math.ceil(tornillos_t2_mecha), "Unidad": "Unidad", "Categoría": "Tornillos"},
            {"Material": "Tornillos T2 Aguja", "Cantidad": math.ceil(tornillos_t2_aguja), "Unidad": "Unidad", "Categoría": "Tornillos"},
            {"Material": "Barrera Agua/Viento (Rollo)", "Cantidad": math.ceil(m2_con_desperdicio/30), "Unidad": "Rollo", "Categoría": "Aislación"},
        ]

        if self.aislacion:
             data.append({"Material": "Lana de Vidrio Alta Densidad", "Cantidad": math.ceil(m2_con_desperdicio/12), "Unidad": "Rollo", "Categoría": "Aislación"})

        data = self._agregar_cajones(data)
        df = pd.DataFrame(data)
        df["Cantidad"] = df["Cantidad"].apply(lambda x: int(math.ceil(x)))
        return df, {"m2": round(m2_real, 2)}

# --- FACTORY ---
class CalculatorFactory:
    @staticmethod
    def get_calculator(tipo_sistema, **kwargs):
        # NOTA: No usamos .pop() aquí para metros_cajon/largo_vela porque
        # BaseCalculator ahora maneja **kwargs, así que es seguro pasarlos.
        # Pero si queremos ser explícitos, los extraemos.
        # Para evitar problemas de doble asignación, la estrategia más limpia
        # es dejar que kwargs fluya y BaseCalculator lo capture.
        
        # Sin embargo, para mantener coherencia con el código existente:
        metros_cajon = kwargs.get('metros_cajon', 0)
        largo_vela = kwargs.get('largo_vela', 0.60)
        
        # Pasamos TODO en kwargs. BaseCalculator sabrá que hacer.
        # CielorrasoCalculator extraerá espesor_cielo si existe.
        
        if "Drywall" in tipo_sistema:
            return DrywallCalculator(**kwargs)
        elif "Cielorraso" in tipo_sistema:
            return CielorrasoCalculator(**kwargs)
        elif "Steel" in tipo_sistema:
            return SteelFrameCalculator(**kwargs)
        else:
            raise ValueError("Sistema no soportado")