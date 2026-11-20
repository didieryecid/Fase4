# ==============================================================
# BLOQUE 5: Gestor del sistema (listas internas + manejo de errores)
# ==============================================================
from entidades import Cliente
from servicios import ReservaSala, AlquilerEquipo, Asesoria
from reserva import Reserva
from excepciones import (ErrorSistema, ParametroFaltanteError, ParametroInvalidoError,
                         ClienteInvalidoError, ServicioInvalidoError, ReservaInvalidaError, registro)


class GestorSistema:
    """Administra clientes, servicios y reservas en listas (sin base de datos)."""

    TIPOS_SERVICIO = {"sala": ReservaSala, "equipo": AlquilerEquipo, "asesoria": Asesoria}

    def __init__(self):
        self._clientes = []                      # Lista interna de clientes
        self._servicios = []                     # Lista interna de servicios
        self._reservas = []                      # Lista interna de reservas
        self._operaciones = 0                    # Contador de operaciones intentadas

    # ---------- Consultas (devuelven copias para proteger las listas) ----------
    @property
    def clientes(self):
        return list(self._clientes)

    @property
    def servicios(self):
        return list(self._servicios)

    @property
    def reservas(self):
        return list(self._reservas)

    @property
    def operaciones(self):
        return self._operaciones

    # ---------- Ejecutor central de operaciones ----------
    def _ejecutar(self, operacion, funcion, *args, **kwargs):
        """
        Ejecuta una operacion y NUNCA deja escapar una excepcion.
        Devuelve (True, resultado) o (False, mensaje_de_error).
        """
        try:
            resultado = funcion(*args, **kwargs)
        except ErrorSistema as error:            # Errores previstos del sistema
            registro.error("%s fallida: %s", operacion, error, exc_info=error.__cause__ is not None)
            return False, str(error)
        except Exception as error:               # Cualquier error imprevisto: el sistema sigue vivo
            registro.critical("%s: error inesperado: %r", operacion, error, exc_info=True)
            return False, f"Error inesperado: {error}"
        else:
            registro.info("%s exitosa.", operacion)
            return True, resultado
        finally:
            self._operaciones += 1               # Se cuenta siempre, con o sin error

    # ---------- Busquedas internas ----------
    @staticmethod
    def _buscar(lista, id_, excepcion, nombre):
        if id_ is None:
            raise ParametroFaltanteError(f"Falta seleccionar {nombre}.")
        for elemento in lista:
            if elemento.id == id_:
                return elemento
        raise excepcion(f"No existe {nombre} con id {id_}.")

    @staticmethod
    def _porcentaje(valor):
        """Convierte 19 o '19' (porcentaje) a 0.19. Vacio -> None."""
        if valor is None or str(valor).strip() == "":
            return None
        try:
            return float(valor) / 100
        except ValueError as error:
            raise ParametroInvalidoError(f"Porcentaje invalido: '{valor}'.") from error

    # ---------- Clientes ----------
    def registrar_cliente(self, nombre=None, documento=None, correo=None, telefono=None):
        def accion():
            cliente = Cliente(nombre, documento, correo, telefono)   # Puede lanzar error
            if any(c.documento == cliente.documento for c in self._clientes):
                raise ClienteInvalidoError(f"Ya existe un cliente con documento {cliente.documento}.")
            self._clientes.append(cliente)
            return cliente
        return self._ejecutar("Registro de cliente", accion)

    # ---------- Servicios ----------
    def crear_servicio(self, tipo, nombre=None, tarifa_hora=None, **extra):
        def accion():
            clase = self.TIPOS_SERVICIO.get(str(tipo).strip().lower())
            if clase is None:
                raise ServicioInvalidoError(f"Tipo de servicio desconocido: '{tipo}'.")
            try:
                servicio = clase(nombre, tarifa_hora, **extra)
            except TypeError as error:           # Parametros que no corresponden al tipo
                raise ParametroFaltanteError(f"Parametros incorrectos para '{tipo}': {error}") from error
            self._servicios.append(servicio)
            return servicio
        return self._ejecutar("Creacion de servicio", accion)

    def cambiar_disponibilidad(self, id_servicio, disponible):
        def accion():
            servicio = self._buscar(self._servicios, id_servicio, ServicioInvalidoError, "el servicio")
            servicio.disponible = disponible
            return servicio
        return self._ejecutar("Cambio de disponibilidad", accion)

    # ---------- Reservas ----------
    def crear_reserva(self, id_cliente, id_servicio, horas):
        def accion():
            cliente = self._buscar(self._clientes, id_cliente, ClienteInvalidoError, "el cliente")
            servicio = self._buscar(self._servicios, id_servicio, ServicioInvalidoError, "el servicio")
            reserva = Reserva(cliente, servicio, horas)
            self._reservas.append(reserva)
            return reserva
        return self._ejecutar("Creacion de reserva", accion)

    def confirmar_reserva(self, id_reserva):
        def accion():
            reserva = self._buscar(self._reservas, id_reserva, ReservaInvalidaError, "la reserva")
            reserva.confirmar()
            return reserva
        return self._ejecutar("Confirmacion de reserva", accion)

    def cancelar_reserva(self, id_reserva):
        def accion():
            reserva = self._buscar(self._reservas, id_reserva, ReservaInvalidaError, "la reserva")
            reserva.cancelar()
            return reserva
        return self._ejecutar("Cancelacion de reserva", accion)

    def procesar_reserva(self, id_reserva, impuesto_pct=None, descuento_pct=None):
        def accion():
            reserva = self._buscar(self._reservas, id_reserva, ReservaInvalidaError, "la reserva")
            return reserva.procesar(self._porcentaje(impuesto_pct), self._porcentaje(descuento_pct))
        return self._ejecutar("Procesamiento de reserva", accion)
