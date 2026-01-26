from src.core.systems import DrywallPartition, DrywallCeiling, SteelFrameEIFS

class CalculatorFactory:
    @staticmethod
    def get_calculator(tipo_sistema, **kwargs):
        # Extraemos la lista de aberturas (por defecto vacía)
        aberturas = kwargs.get('aberturas', [])
        
        if "Tabique Drywall" in tipo_sistema:
            return DrywallPartition(
                largo=kwargs.get('largo'),
                altura=kwargs.get('altura'),
                separacion=kwargs.get('separacion'),
                desperdicio=kwargs.get('desperdicio'),
                caras=kwargs.get('caras', 1),
                capas=kwargs.get('capas', 1),
                aislacion=kwargs.get('aislacion', False),
                aberturas=aberturas
            )
        elif "Cielorraso" in tipo_sistema:
            return DrywallCeiling(
                ancho=kwargs.get('ancho'),
                largo_real=kwargs.get('largo'),
                separacion=kwargs.get('separacion'),
                desperdicio=kwargs.get('desperdicio'),
                aislacion=kwargs.get('aislacion', False),
                espesor_placa=kwargs.get('espesor_cielo', "9.5")
            )
        elif "Steel Frame" in tipo_sistema:
            return SteelFrameEIFS(
                largo=kwargs.get('largo'),
                altura=kwargs.get('altura'),
                separacion=kwargs.get('separacion'),
                desperdicio=kwargs.get('desperdicio'),
                capas_int=kwargs.get('capas', 1),
                aislacion=kwargs.get('aislacion', False),
                aberturas=aberturas
            )
        else:
            raise ValueError("Sistema no soportado.")