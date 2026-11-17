# ==============================================================
# BLOQUE 3: Clase abstracta Servicio y servicios especializados
# ==============================================================
import itertools                                 # Contador de ids de servicios
from abc import abstractmethod                   # Para declarar metodos abstractos

from entidades import Entidad
from excepciones import (ParametroFaltanteError, ParametroInvalidoError,
                         ServicioInvalidoError, CalculoInconsistenteError)


class Servicio(Entidad):
    """Clase abstracta: define lo comun a todos los servicios de Software FJ."""

    _contador = itertools.count(1)               # Contador de ids exclusivo de servicios
    TASA_IVA = 0.19                              # Impuesto usado en calcular_costo_con_iva

    def __init__(self, nombre=None, tarifa_hora=None, disponible=True):
        if nombre is None or not str(nombre).strip():
            raise ParametroFaltanteError("Falta el nombre del servicio.")
        if tarifa_hora is None or str(tarifa_hora).strip() == "":
            raise ParametroFaltanteError("Falta la tarifa por hora del servicio.")
        try:
            tarifa = float(tarifa_hora)          # Intenta convertir la tarifa a numero
        except (TypeError, ValueError) as error:
            # Encadenamiento de excepciones: "from error" conserva la causa original
            raise ServicioInvalidoError(f"Tarifa no numerica: '{tarifa_hora}'.") from error
        if tarifa <= 0:
            raise ServicioInvalidoError("La tarifa por hora debe ser mayor que cero.")
        self._nombre = str(nombre).strip()       # Atributos protegidos (convencion _)
        self._tarifa_hora = tarifa
        self._disponible = bool(disponible)
        super().__init__()                       # Asigna id solo si todo fue valido

    # ---------- Propiedades ----------
    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = bool(valor)           # Permite activar/desactivar el servicio

    @property
    @abstractmethod
    def tipo(self):
        """Nombre corto del tipo de servicio."""

    # ---------- Metodos abstractos (cada hijo los sobrescribe) ----------
    @abstractmethod
    def _costo_base(self, horas):
        """Costo sin impuestos ni descuentos."""

    @abstractmethod
    def validar_parametros(self, horas):
        """Valida los parametros de la reserva y devuelve las horas ya convertidas."""

    # ---------- Utilidades ----------
    @staticmethod
    def _convertir_horas(horas):
        """Convierte las horas a numero y verifica que sean positivas."""
        if horas is None or str(horas).strip() == "":
            raise ParametroFaltanteError("Falta la duracion (horas) de la reserva.")
        try:
            horas = float(horas)
        except (TypeError, ValueError) as error:
            raise ParametroInvalidoError(f"Duracion no numerica: '{horas}'.") from error
        if horas <= 0:
            raise ParametroInvalidoError("La duracion debe ser mayor que cero.")
        return horas

    @staticmethod
    def _fraccion(valor, nombre):
        """Valida que un impuesto/descuento sea un numero entre 0 y 1."""
        try:
            valor = float(valor)
        except (TypeError, ValueError) as error:
            raise CalculoInconsistenteError(f"{nombre} no numerico: '{valor}'.") from error
        if not 0 <= valor <= 1:
            raise CalculoInconsistenteError(f"{nombre} fuera de rango (0 a 1): {valor}.")
        return valor

    # ---------- METODOS SOBRECARGADOS (variantes de calculo de costo) ----------
    def calcular_costo(self, horas, impuesto=None, descuento=None):
        """
        Sobrecarga mediante parametros opcionales:
          calcular_costo(h)              -> costo base
          calcular_costo(h, imp)         -> costo base + impuesto
          calcular_costo(h, imp, desc)   -> descuento primero, impuesto despues
        """
        horas = self.validar_parametros(horas)   # Validacion propia de cada tipo (polimorfismo)
        total = self._costo_base(horas)          # Calculo propio de cada tipo (polimorfismo)
        if descuento is not None:                # Variante con descuento
            total -= total * self._fraccion(descuento, "Descuento")
        if impuesto is not None:                 # Variante con impuesto
            total += total * self._fraccion(impuesto, "Impuesto")
        if total < 0:                            # Chequeo de consistencia del calculo
            raise CalculoInconsistenteError(f"Costo negativo calculado: {total}.")
        return round(total, 2)

    def calcular_costo_con_iva(self, horas):
        """Variante rapida: costo con el IVA predeterminado."""
        return self.calcular_costo(horas, impuesto=self.TASA_IVA)

    def describir(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"Servicio #{self.id} [{self.tipo}] {self.nombre} | ${self.tarifa_hora:,.0f}/h | {estado}"


class ReservaSala(Servicio):
    """Reserva de salas de reunion."""

    EXTRA_PROYECTOR = 25000                      # Cargo fijo si se incluye proyector

    def __init__(self, nombre=None, tarifa_hora=None, capacidad=None, proyector=False):
        try:
            capacidad = int(capacidad)
        except (TypeError, ValueError) as error:
            raise ServicioInvalidoError(f"Capacidad invalida: '{capacidad}'.") from error
        if capacidad <= 0:
            raise ServicioInvalidoError("La capacidad debe ser mayor que cero.")
        self._capacidad = capacidad
        self._proyector = bool(proyector)
        super().__init__(nombre, tarifa_hora)    # Valida nombre y tarifa en la clase padre

    @property
    def tipo(self):
        return "Sala"

    def validar_parametros(self, horas):
        horas = self._convertir_horas(horas)
        if horas > 8:                            # Regla propia de las salas
            raise ParametroInvalidoError("Una sala se reserva maximo por 8 horas.")
        return horas

    def _costo_base(self, horas):
        extra = self.EXTRA_PROYECTOR if self._proyector else 0
        return self.tarifa_hora * horas + extra

    def describir(self):
        proy = "con proyector" if self._proyector else "sin proyector"
        return super().describir() + f" | Capacidad: {self._capacidad} personas, {proy}"


class AlquilerEquipo(Servicio):
    """Alquiler de equipos (portatiles, proyectores, etc.)."""

    def __init__(self, nombre=None, tarifa_hora=None, tipo_equipo=None, cantidad=1):
        if tipo_equipo is None or not str(tipo_equipo).strip():
            raise ParametroFaltanteError("Falta el tipo de equipo.")
        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError) as error:
            raise ServicioInvalidoError(f"Cantidad invalida: '{cantidad}'.") from error
        if cantidad <= 0:
            raise ServicioInvalidoError("La cantidad de equipos debe ser mayor que cero.")
        self._tipo_equipo = str(tipo_equipo).strip()
        self._cantidad = cantidad
        super().__init__(nombre, tarifa_hora)

    @property
    def tipo(self):
        return "Equipo"

    def validar_parametros(self, horas):
        horas = self._convertir_horas(horas)
        if horas > 72:                           # Maximo 3 dias de alquiler
            raise ParametroInvalidoError("Un equipo se alquila maximo por 72 horas.")
        return horas

    def _costo_base(self, horas):
        return self.tarifa_hora * horas * self._cantidad   # Se cobra por cada unidad

    def describir(self):
        return super().describir() + f" | Equipo: {self._tipo_equipo} x{self._cantidad}"


class Asesoria(Servicio):
    """Asesoria especializada con recargo segun el nivel del especialista."""

    RECARGOS = {"junior": 1.0, "senior": 1.3, "experto": 1.6}   # Multiplicador por nivel

    def __init__(self, nombre=None, tarifa_hora=None, especialista=None, nivel="junior"):
        if especialista is None or not str(especialista).strip():
            raise ParametroFaltanteError("Falta el nombre del especialista.")
        nivel = str(nivel).strip().lower()
        if nivel not in self.RECARGOS:
            raise ServicioInvalidoError(f"Nivel invalido '{nivel}'. Use: {', '.join(self.RECARGOS)}.")
        self._especialista = str(especialista).strip()
        self._nivel = nivel
        super().__init__(nombre, tarifa_hora)

    @property
    def tipo(self):
        return "Asesoria"

    def validar_parametros(self, horas):
        horas = self._convertir_horas(horas)
        if horas > 6:
            raise ParametroInvalidoError("Una asesoria dura maximo 6 horas.")
        return horas

    def _costo_base(self, horas):
        return self.tarifa_hora * horas * self.RECARGOS[self._nivel]

    def describir(self):
        return super().describir() + f" | Especialista: {self._especialista} ({self._nivel})"
