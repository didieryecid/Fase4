# Software FJ - Sistema Integral de Gestion de Clientes, Servicios y Reservas

Aplicacion orientada a objetos en Python (Tkinter), sin base de datos. Solo usa archivo de log.

## Integrantes
- Didier Yecid Quintero Gonzalez

## Estructura (un bloque por archivo)
| Archivo | Contenido |
|---|---|
| `excepciones.py` | Excepciones personalizadas y configuracion de logs |
| `entidades.py` | Clase abstracta `Entidad` y `Cliente` |
| `servicios.py` | `Servicio` (abstracta), `ReservaSala`, `AlquilerEquipo`, `Asesoria` |
| `reserva.py` | `Reserva` (confirmar, cancelar, procesar) |
| `gestor.py` | Listas internas y ejecucion segura de operaciones |
| `simulacion.py` | 24 operaciones validas e invalidas |
| `main.py` | Interfaz grafica Tkinter |

## Como ejecutar
1. `python main.py` (interfaz) o `python simulacion.py` (solo consola).
2. Los errores y eventos quedan en `sistema.log`.
