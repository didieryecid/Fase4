# ==============================================================
# BLOQUE 4: Clase Reserva (cliente + servicio + duracion + estado)
# ==============================================================
import itertools                                 # Contador de ids de reservas

from entidades import Entidad, Cliente
from servicios import Servicio
from excepciones import (ErrorSistema, ErrorValidacion, ReservaInvalidaError,
                         ServicioNoDisponibleError, OperacionNoPermitidaError, registro)


class Reserva(Entidad):
    """Integra un cliente, un servicio, la duracion y el estado de la reserva."""

    _contador = itertools.count(1)               # Contador de ids exclusivo de reservas
    PENDIENTE, CONFIRMADA, CANCELADA, PROCESADA = "Pendiente", "Confirmada", "Cancelada", "Procesada"

    def __init__(self, cliente, servicio, horas):
        # Verifica que los objetos recibidos sean del tipo correcto
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva requiere un cliente valido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva requiere un servicio valido.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no esta disponible.")
        try:
            horas = servicio.validar_parametros(horas)   # Cada servicio valida a su manera
        except ErrorValidacion as error:
            # Encadenamiento: se traduce a un error de reserva conservando la causa
            raise ReservaInvalidaError(f"Parametros de reserva incorrectos: {error.mensaje}") from error
        self._cliente = cliente                  # Atributos encapsulados
        self._servicio = servicio
        self._horas = horas
        self._estado = self.PENDIENTE            # Toda reserva nace pendiente
        self._costo_final = None                 # Se calcula al procesar
        super().__init__()

    # ---------- Propiedades de solo lectura ----------
    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def horas(self):
        return self._horas

    @property
    def estado(self):
        return self._estado

    @property
    def costo_final(self):
        return self._costo_final

    # ---------- Operaciones de negocio ----------
    def confirmar(self):
        """Pendiente -> Confirmada."""
        if self._estado != self.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva en estado '{self._estado}'.")
        if not self._servicio.disponible:        # El servicio pudo desactivarse tras reservar
            raise ServicioNoDisponibleError(f"El servicio '{self._servicio.nombre}' ya no esta disponible.")
        self._estado = self.CONFIRMADA
        registro.info("Reserva #%s confirmada.", self.id)

    def cancelar(self):
        """Cancela mientras no este procesada ni cancelada."""
        if self._estado in (self.PROCESADA, self.CANCELADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva en estado '{self._estado}'.")
        self._estado = self.CANCELADA
        registro.info("Reserva #%s cancelada.", self.id)

    def procesar(self, impuesto=None, descuento=None):
        """Confirmada -> Procesada, calculando el costo (usa los parametros opcionales)."""
        if self._estado != self.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"Solo se procesan reservas confirmadas (estado actual: '{self._estado}').")
        try:
            costo = self._servicio.calcular_costo(self._horas, impuesto, descuento)
        except ErrorSistema as error:
            registro.error("Reserva #%s: fallo al calcular el costo: %s", self.id, error)
            # Se relanza como operacion no permitida, encadenando el error original
            raise OperacionNoPermitidaError(f"No se pudo procesar la reserva: {error.mensaje}") from error
        else:
            # Solo se ejecuta si el try NO lanzo excepcion
            self._costo_final = costo
            self._estado = self.PROCESADA
            registro.info("Reserva #%s procesada. Costo final: $%s", self.id, f"{costo:,.2f}")
            return costo
        finally:
            # Se ejecuta SIEMPRE, haya o no error
            registro.info("Intento de procesamiento de la reserva #%s finalizado.", self.id)

    def describir(self):
        costo = f"${self._costo_final:,.2f}" if self._costo_final is not None else "pendiente de calculo"
        return (f"Reserva #{self.id} | {self._cliente.nombre} -> {self._servicio.nombre} "
                f"| {self._horas:g} h | {self._estado} | Costo: {costo}")
