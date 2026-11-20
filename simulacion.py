# ==============================================================
# BLOQUE 6: Simulacion de operaciones validas e invalidas
# ==============================================================
from entidades import Entidad
from excepciones import registro


def ejecutar_simulacion(gestor):
    """Ejecuta mas de 10 operaciones sobre el gestor y devuelve las lineas del reporte."""
    lineas = []                                  # Aqui se acumula el reporte legible
    registro.info("===== INICIO DE LA SIMULACION =====")

    def paso(descripcion, resultado):
        """Anota el resultado de un paso y devuelve el valor si fue exitoso."""
        ok, valor = resultado                    # Todas las operaciones devuelven (ok, valor)
        estado = "EXITO" if ok else "FALLO CONTROLADO"
        detalle = valor.describir() if isinstance(valor, Entidad) else valor
        lineas.append(f"{len(lineas) + 1:02d}. {descripcion} -> {estado}: {detalle}")
        return valor if ok else None

    # ---- Clientes ----
    ana = paso("Cliente valido (Ana)", gestor.registrar_cliente(
        "ana gomez", "1088123456", "ana@correo.com", "3101234567"))
    carlos = paso("Cliente valido (Carlos)", gestor.registrar_cliente(
        "Carlos Ruiz", "1090987654", "carlos@correo.com", "3207654321"))
    paso("Cliente con correo invalido", gestor.registrar_cliente(
        "Luis Mora", "1075111222", "luis-correo.com", "3001112233"))
    paso("Cliente sin nombre (parametro faltante)", gestor.registrar_cliente(
        None, "1075333444", "x@correo.com", "3001112233"))
    paso("Cliente con documento duplicado", gestor.registrar_cliente(
        "Ana Duplicada", "1088123456", "otra@correo.com", "3115556677"))

    # ---- Servicios ----
    sala = paso("Servicio sala valido", gestor.crear_servicio(
        "sala", "Sala Ejecutiva", 50000, capacidad=10, proyector=True))
    equipo = paso("Servicio equipo valido", gestor.crear_servicio(
        "equipo", "Portatil Pro", 8000, tipo_equipo="Portatil", cantidad=2))
    asesoria = paso("Servicio asesoria valido", gestor.crear_servicio(
        "asesoria", "Asesoria Cloud", 120000, especialista="Marta Diaz", nivel="senior"))
    paso("Servicio con tarifa negativa", gestor.crear_servicio(
        "sala", "Sala Rota", -100, capacidad=5))
    paso("Servicio de tipo inexistente", gestor.crear_servicio(
        "hologramas", "Demo", 1000))

    # ---- Reservas ----
    r1 = paso("Reserva valida (Ana, sala, 3 h)", gestor.crear_reserva(ana.id, sala.id, 3))
    paso("Reserva con horas excesivas (sala 20 h)", gestor.crear_reserva(ana.id, sala.id, 20))
    paso("Reserva con cliente inexistente", gestor.crear_reserva(99, sala.id, 2))
    paso("Reserva con duracion no numerica", gestor.crear_reserva(carlos.id, equipo.id, "abc"))

    paso("Confirmar reserva 1", gestor.confirmar_reserva(r1.id))
    paso("Procesar reserva 1 (IVA 19% y descuento 10%)", gestor.procesar_reserva(r1.id, 19, 10))
    paso("Procesar de nuevo la misma reserva", gestor.procesar_reserva(r1.id))
    paso("Cancelar una reserva ya procesada", gestor.cancelar_reserva(r1.id))

    # ---- Servicio no disponible ----
    paso("Desactivar asesoria", gestor.cambiar_disponibilidad(asesoria.id, False))
    paso("Reserva sobre servicio no disponible", gestor.crear_reserva(carlos.id, asesoria.id, 2))

    # ---- Calculo inconsistente (descuento > 100%) ----
    r2 = paso("Reserva valida (Carlos, equipo, 10 h)", gestor.crear_reserva(carlos.id, equipo.id, 10))
    paso("Confirmar reserva 2", gestor.confirmar_reserva(r2.id))
    paso("Procesar reserva 2 con descuento 150%", gestor.procesar_reserva(r2.id, None, 150))
    paso("Cancelar reserva 2", gestor.cancelar_reserva(r2.id))

    lineas.append("-" * 60)
    lineas.append(f"Operaciones intentadas en total: {gestor.operaciones}. El sistema siguio estable.")
    registro.info("===== FIN DE LA SIMULACION =====")
    return lineas


if __name__ == "__main__":                       # Permite correr la simulacion sin interfaz
    from gestor import GestorSistema
    for linea in ejecutar_simulacion(GestorSistema()):
        print(linea)
