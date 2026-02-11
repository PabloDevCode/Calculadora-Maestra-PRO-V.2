from src.core.systems import DrywallPartition, DrywallCeiling, SteelFrameEIFS

class CalculatorFactory:
    @staticmethod
    def get_calculator(tipo_sistema, **kwargs):
        # Limpiamos kwargs que no correspondan a la clase destino
        # para evitar errores de "unexpected argument"
        
        # Parámetros comunes
        largo = kwargs.get('largo')
        altura = kwargs.get('altura')
        ancho = kwargs.get('ancho')
        separacion = kwargs.get('separacion')
        desperdicio = kwargs.get('desperdicio')
        aislacion = kwargs.get('aislacion')
        aberturas = kwargs.get('aberturas', [])
        
        # Parámetros específicos (usamos .get con default)
        largo_vela = kwargs.get('largo_vela', 0.60)
        espesor_cielo = kwargs.get('espesor_cielo', '9.5mm')
        caras = kwargs.get('caras', 1)
        capas = kwargs.get('capas', 1)
        metros_cajon = kwargs.get('metros_cajon', 0) # Por ahora no lo usamos dentro de la clase sistema pero lo recibimos

        if "Drywall" in tipo_sistema:
            return DrywallPartition(
                largo=largo, altura=altura, separacion=separacion, 
                desperdicio=desperdicio, caras=caras, capas=capas, 
                aislacion=aislacion, aberturas=aberturas
            )
        elif "Cielorraso" in tipo_sistema:
            return DrywallCeiling(
                ancho=ancho, largo_real=largo, separacion=separacion, 
                desperdicio=desperdicio, aislacion=aislacion, 
                espesor_placa=espesor_cielo, largo_vela=largo_vela
            )
        elif "Steel" in tipo_sistema:
            return SteelFrameEIFS(
                largo=largo, altura=altura, separacion=separacion, 
                desperdicio=desperdicio, capas_int=capas, 
                aislacion=aislacion, aberturas=aberturas
            )
        else:
            raise ValueError("Sistema no soportado")