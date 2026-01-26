# src/config/materials_db.py

class Categories:
    ESTRUCTURA = "Estructura"
    EMPLACADO = "Emplacado"
    FIJACIONES = "Fijaciones"
    AISLACION = "Aislación"
    TERMINACION = "Terminación"
    RIGIDIZACION = "Rigidización"
    EIFS_SUSTRATO = "EIFS - Sustrato"
    EIFS_AISLACION = "EIFS - Aislación"
    EIFS_BASE = "EIFS - Base"
    INTERIOR = "Interior"

class MaterialConst:
    # Dimensiones
    L_PERFIL_DW = 2.60
    L_PERFIL_SF = 6.00
    SUP_PLACA = 2.88
    
    # Materiales
    SOLERA_70 = "Solera 70mm (2.6m)"
    MONTANTE_69 = "Montante 69mm (2.6m)"
    SOLERA_35 = "Solera 35mm (2.6m)"
    MONTANTE_35 = "Montante 35mm (2.6m)"
    PLACA_12 = "Placa Yeso 12.5mm"
    PLACA_9 = "Placa Yeso 9.5mm"
    
    # Steel Frame
    PGU_100 = "PGU 100mm (6m)"
    PGC_100 = "PGC 100mm (6m)"
    FLEJE = "Fleje Acero Galvanizado"
    OSB_11 = "Placa OSB 11.1mm"
    TYVEK = "Barrera Agua/Viento (Tyvek)"
    EPS_ALTA = "Plancha EPS Alta Densidad"
    BASE_COAT = "Base Coat"
    MALLA = "Malla Fibra de Vidrio"
    
    # NUEVO AGREGADO
    CANTONERA = "Cantonera / Esquinero (2.6m)"
    
    # Insumos
    T1 = "Tornillos T1"
    T2_AGUJA = "Tornillos T2 Aguja"
    T2_MECHA = "Tornillos T2 Mecha"
    TORNILLO_HEX = "Tornillo Hexagonal"
    TORNILLO_EPS = "Tornillos + Arandelas PVC (EPS)"
    TARUGO_8 = "Tarugos 8mm + Tornillo"
    LANA_VIDRIO = "Aislación Térmica/Acústica"
    MASILLA = "Masilla (Juntas)"
    CINTA = "Cinta de Papel"

    UNITS = { "U": "Unidades", "M": "Metros", "M2": "m²", "KG": "Kg" }