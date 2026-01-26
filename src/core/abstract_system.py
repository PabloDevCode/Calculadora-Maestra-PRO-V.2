# src/core/abstract_system.py
from abc import ABC, abstractmethod
import math
import pandas as pd

class ConstructionSystem(ABC):
    """Clase base que garantiza que todos los sistemas funcionen igual."""
    
    def __init__(self, largo: float, altura: float, separacion: float, desperdicio: float):
        self.largo = largo
        self.altura = altura
        self.sup = largo * altura
        self.sep = separacion
        self.desp = 1 + (desperdicio / 100)
        self._materials_list = []

    def add_material(self, category, name, unit, quantity):
        if quantity > 0:
            self._materials_list.append({
                "Categoría": category,
                "Material": name,
                "Unidad": unit,
                "Cantidad": math.ceil(quantity) # Redondeo siempre hacia arriba
            })

    @abstractmethod
    def calculate(self) -> pd.DataFrame:
        pass

    def get_dataframe(self):
        return pd.DataFrame(self._materials_list)