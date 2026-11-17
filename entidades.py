# ==============================================================
# BLOQUE 2: Clase abstracta Entidad y clase Cliente
# ==============================================================
import itertools                                 # Para generar identificadores consecutivos
import re                                        # Expresiones regulares (validar correo)
from abc import ABC, abstractmethod              # Herramientas para clases abstractas

from excepciones import (ParametroFaltanteError, ClienteInvalidoError)


class Entidad(ABC):
    """Clase abstracta que representa cualquier entidad general del sistema."""

    def __init__(self):
        # Cada familia (Cliente, Servicio, Reserva) define su propio contador _contador
        self._id = next(type(self)._contador)    # Asigna el siguiente id disponible

    @property
    def id(self):
        """Identificador de solo lectura (encapsulacion)."""
        return self._id

    @abstractmethod
    def describir(self):
        """Cada entidad debe describirse a si misma (polimorfismo)."""

    def __str__(self):
        return self.describir()                  # Al imprimir el objeto se muestra su descripcion


class Cliente(Entidad):
    """Cliente con datos personales encapsulados y validados."""

    _contador = itertools.count(1)               # Contador de ids exclusivo de clientes

    def __init__(self, nombre=None, documento=None, correo=None, telefono=None):
        # Verifica que ningun parametro obligatorio falte o este vacio
        for campo, valor in (("nombre", nombre), ("documento", documento),
                             ("correo", correo), ("telefono", telefono)):
            if valor is None or not str(valor).strip():
                raise ParametroFaltanteError(f"Falta el parametro obligatorio: {campo}")
        # Atributos privados (doble guion bajo): no se accede a ellos desde fuera
        self.__nombre = self._validar_nombre(nombre)
        self.__documento = self._validar_documento(documento)
        self.__correo = self._validar_correo(correo)
        self.__telefono = self._validar_telefono(telefono)
        super().__init__()                       # Solo se asigna id si todo fue valido

    # ---------- Validadores (metodos estaticos reutilizables) ----------
    @staticmethod
    def _validar_nombre(nombre):
        nombre = str(nombre).strip()             # Quita espacios al inicio y final
        if len(nombre) < 3 or not all(c.isalpha() or c.isspace() for c in nombre):
            raise ClienteInvalidoError("Nombre invalido: minimo 3 letras, sin numeros ni simbolos.")
        return nombre.title()                    # Normaliza a formato Titulo

    @staticmethod
    def _validar_documento(documento):
        documento = str(documento).strip()
        if not documento.isdigit() or not 5 <= len(documento) <= 12:
            raise ClienteInvalidoError("Documento invalido: solo digitos, entre 5 y 12.")
        return documento

    @staticmethod
    def _validar_correo(correo):
        correo = str(correo).strip().lower()
        if not re.match(r"^[\w.+-]+@[\w-]+\.[\w.-]+$", correo):  # Patron basico de email
            raise ClienteInvalidoError(f"Correo invalido: '{correo}'.")
        return correo

    @staticmethod
    def _validar_telefono(telefono):
        telefono = str(telefono).strip()
        if not telefono.isdigit() or not 7 <= len(telefono) <= 10:
            raise ClienteInvalidoError("Telefono invalido: solo digitos, entre 7 y 10.")
        return telefono

    # ---------- Propiedades (getters y setters) ----------
    @property
    def nombre(self):
        return self.__nombre

    @property
    def documento(self):
        return self.__documento                  # Sin setter: el documento no se puede cambiar

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        self.__correo = self._validar_correo(valor)   # Reutiliza la validacion al modificar

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        self.__telefono = self._validar_telefono(valor)

    def describir(self):
        return f"Cliente #{self.id}: {self.nombre} | Doc: {self.documento} | {self.correo} | Tel: {self.telefono}"
