# ==============================================================
# BLOQUE 1: Excepciones personalizadas y configuracion de logs
# ==============================================================
import logging                                   # Libreria estandar para registrar eventos
import os                                        # Para construir la ruta del archivo de log

# ---------------- Jerarquia de excepciones ----------------

class ErrorSistema(Exception):
    """Excepcion base de todo el sistema Software FJ."""
    codigo = "E000"                              # Codigo identificador del error

    def __init__(self, mensaje="Error en el sistema"):
        super().__init__(mensaje)                # Inicializa la excepcion estandar
        self.mensaje = mensaje                   # Guarda el mensaje para usarlo luego

    def __str__(self):
        return f"[{self.codigo}] {self.mensaje}"  # Formato: [codigo] mensaje


class ErrorValidacion(ErrorSistema):
    """Errores por datos invalidos."""
    codigo = "E100"


class ParametroFaltanteError(ErrorValidacion):
    """Se omitio un parametro obligatorio."""
    codigo = "E101"


class ParametroInvalidoError(ErrorValidacion):
    """Un parametro tiene tipo o valor incorrecto."""
    codigo = "E102"


class ClienteInvalidoError(ErrorValidacion):
    """Datos de cliente invalidos o cliente inexistente/duplicado."""
    codigo = "E110"


class ServicioInvalidoError(ErrorValidacion):
    """Datos de servicio invalidos o servicio inexistente."""
    codigo = "E120"


class ServicioNoDisponibleError(ErrorSistema):
    """El servicio existe pero no se puede reservar ahora."""
    codigo = "E200"


class ReservaInvalidaError(ErrorSistema):
    """Intento de reserva incorrecto."""
    codigo = "E300"


class OperacionNoPermitidaError(ErrorSistema):
    """La operacion no es valida para el estado actual."""
    codigo = "E400"


class CalculoInconsistenteError(ErrorSistema):
    """Un calculo de costos produjo un resultado incoherente."""
    codigo = "E500"


# ---------------- Configuracion del archivo de logs ----------------

# El log se guarda junto a este archivo, sin importar desde donde se ejecute
ARCHIVO_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sistema.log")


def _crear_logger():
    """Crea (una sola vez) el logger que escribe en sistema.log."""
    logger = logging.getLogger("SoftwareFJ")     # Obtiene/crea el logger con nombre propio
    if not logger.handlers:                      # Evita duplicar handlers si se importa varias veces
        logger.setLevel(logging.INFO)            # Registra INFO, WARNING, ERROR y CRITICAL
        manejador = logging.FileHandler(ARCHIVO_LOG, encoding="utf-8")  # Escribe en archivo
        manejador.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s"))  # Formato: fecha | nivel | mensaje
        logger.addHandler(manejador)             # Conecta el manejador al logger
    return logger


registro = _crear_logger()                       # Logger unico que usaran todos los modulos
