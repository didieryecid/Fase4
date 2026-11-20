# ==============================================================
# BLOQUE 7: Interfaz grafica Tkinter - Software FJ
# Ejecutar con:  python main.py
# ==============================================================
import os                                        # Para comprobar si existe el archivo de log
import tkinter as tk                             # Libreria grafica base
from tkinter import ttk, messagebox, scrolledtext   # Widgets modernos, avisos y area de texto

from gestor import GestorSistema
from simulacion import ejecutar_simulacion
from excepciones import ARCHIVO_LOG, registro


class App(tk.Tk):
    """Ventana principal con pestanas: Clientes, Servicios, Reservas y Simulacion."""

    # Etiquetas de los dos campos extra segun el tipo de servicio
    CAMPOS_EXTRA = {
        "sala": ("Capacidad (personas):", "Proyector? (si/no):"),
        "equipo": ("Tipo de equipo:", "Cantidad:"),
        "asesoria": ("Especialista:", "Nivel (junior/senior/experto):"),
    }

    def __init__(self):
        super().__init__()                       # Inicializa la ventana Tk
        self.title("Software FJ - Clientes, Servicios y Reservas")
        self.geometry("960x620")
        self.gestor = GestorSistema()            # Logica del negocio (listas en memoria)
        self.notebook = ttk.Notebook(self)       # Contenedor de pestanas
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)
        self.barra = ttk.Label(self, text="Listo.", anchor="w")   # Barra de estado
        self.barra.pack(fill="x", padx=8, pady=(0, 6))
        self._crear_tab_clientes()
        self._crear_tab_servicios()
        self._crear_tab_reservas()
        self._crear_tab_simulacion()
        self.refrescar()                         # Carga las tablas iniciales

    # ---------------- Utilidades de interfaz ----------------
    def _campo(self, padre, etiqueta, fila, ancho=28):
        """Crea una etiqueta + caja de texto en una fila de la cuadricula."""
        ttk.Label(padre, text=etiqueta).grid(row=fila, column=0, sticky="e", padx=4, pady=3)
        entrada = ttk.Entry(padre, width=ancho)
        entrada.grid(row=fila, column=1, sticky="w", padx=4, pady=3)
        return entrada

    def _tabla(self, padre, columnas, anchos):
        """Crea una tabla (Treeview) con barra de desplazamiento."""
        marco = ttk.Frame(padre)
        marco.pack(fill="both", expand=True, padx=6, pady=6)
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=8)
        for col, ancho in zip(columnas, anchos):
            tabla.heading(col, text=col)         # Titulo de la columna
            tabla.column(col, width=ancho, anchor="w")
        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return tabla

    def _resultado(self, resultado, mensaje_ok):
        """Muestra exito en la barra o el error en un aviso; la app nunca se cae."""
        ok, valor = resultado
        if ok:
            self.barra.config(text=mensaje_ok)
        else:
            self.barra.config(text="Operacion no realizada.")
            messagebox.showwarning("Operacion no realizada", str(valor))
        self.refrescar()                         # Actualiza todas las tablas
        return ok

    @staticmethod
    def _id_seleccionado(tabla):
        """Devuelve el id (primera columna) de la fila seleccionada, o None."""
        seleccion = tabla.selection()
        if not seleccion:
            return None
        return int(tabla.item(seleccion[0])["values"][0])

    @staticmethod
    def _id_de_combo(texto):
        """Extrae el id de textos como '3 - Ana Gomez'. Devuelve None si no se puede."""
        try:
            return int(str(texto).split(" - ")[0])
        except ValueError:
            return None

    # ---------------- Pestana Clientes ----------------
    def _crear_tab_clientes(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Clientes")
        form = ttk.LabelFrame(tab, text="Registrar cliente")
        form.pack(fill="x", padx=6, pady=6)
        self.c_nombre = self._campo(form, "Nombre:", 0)
        self.c_doc = self._campo(form, "Documento:", 1)
        self.c_correo = self._campo(form, "Correo:", 2)
        self.c_tel = self._campo(form, "Telefono:", 3)
        ttk.Button(form, text="Registrar", command=self.on_registrar_cliente).grid(row=4, column=1, sticky="w", pady=6)
        self.tabla_clientes = self._tabla(tab, ("ID", "Nombre", "Documento", "Correo", "Telefono"),
                                          (50, 200, 120, 240, 120))

    def on_registrar_cliente(self):
        resultado = self.gestor.registrar_cliente(
            self.c_nombre.get(), self.c_doc.get(), self.c_correo.get(), self.c_tel.get())
        if self._resultado(resultado, "Cliente registrado correctamente."):
            for caja in (self.c_nombre, self.c_doc, self.c_correo, self.c_tel):
                caja.delete(0, "end")            # Limpia el formulario solo si todo salio bien

    # ---------------- Pestana Servicios ----------------
    def _crear_tab_servicios(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Servicios")
        form = ttk.LabelFrame(tab, text="Crear servicio")
        form.pack(fill="x", padx=6, pady=6)
        ttk.Label(form, text="Tipo:").grid(row=0, column=0, sticky="e", padx=4, pady=3)
        self.s_tipo = ttk.Combobox(form, values=list(self.CAMPOS_EXTRA), state="readonly", width=25)
        self.s_tipo.grid(row=0, column=1, sticky="w", padx=4, pady=3)
        self.s_tipo.set("sala")
        self.s_tipo.bind("<<ComboboxSelected>>", self._cambiar_etiquetas)   # Cambia etiquetas segun tipo
        self.s_nombre = self._campo(form, "Nombre:", 1)
        self.s_tarifa = self._campo(form, "Tarifa por hora:", 2)
        self.lbl_extra1 = ttk.Label(form)
        self.lbl_extra1.grid(row=3, column=0, sticky="e", padx=4, pady=3)
        self.s_extra1 = ttk.Entry(form, width=28)
        self.s_extra1.grid(row=3, column=1, sticky="w", padx=4, pady=3)
        self.lbl_extra2 = ttk.Label(form)
        self.lbl_extra2.grid(row=4, column=0, sticky="e", padx=4, pady=3)
        self.s_extra2 = ttk.Entry(form, width=28)
        self.s_extra2.grid(row=4, column=1, sticky="w", padx=4, pady=3)
        botones = ttk.Frame(form)
        botones.grid(row=5, column=1, sticky="w", pady=6)
        ttk.Button(botones, text="Crear servicio", command=self.on_crear_servicio).pack(side="left", padx=2)
        ttk.Button(botones, text="Activar/Desactivar seleccionado", command=self.on_alternar_servicio).pack(side="left", padx=2)
        self.tabla_servicios = self._tabla(tab, ("ID", "Tipo", "Nombre", "Tarifa/h", "Estado", "Detalle"),
                                           (40, 80, 160, 90, 100, 420))
        self._cambiar_etiquetas()

    def _cambiar_etiquetas(self, _evento=None):
        """Ajusta las etiquetas de los campos extra al tipo elegido."""
        e1, e2 = self.CAMPOS_EXTRA[self.s_tipo.get()]
        self.lbl_extra1.config(text=e1)
        self.lbl_extra2.config(text=e2)

    def on_crear_servicio(self):
        tipo = self.s_tipo.get()
        e1, e2 = self.s_extra1.get(), self.s_extra2.get()
        # Cada tipo recibe sus parametros propios con el nombre que su constructor espera
        if tipo == "sala":
            extra = {"capacidad": e1, "proyector": e2.strip().lower() in ("si", "si", "s", "true", "1")}
        elif tipo == "equipo":
            extra = {"tipo_equipo": e1, "cantidad": e2 or 1}
        else:
            extra = {"especialista": e1, "nivel": e2 or "junior"}
        resultado = self.gestor.crear_servicio(tipo, self.s_nombre.get(), self.s_tarifa.get(), **extra)
        if self._resultado(resultado, "Servicio creado correctamente."):
            for caja in (self.s_nombre, self.s_tarifa, self.s_extra1, self.s_extra2):
                caja.delete(0, "end")

    def on_alternar_servicio(self):
        id_servicio = self._id_seleccionado(self.tabla_servicios)
        servicio = next((s for s in self.gestor.servicios if s.id == id_servicio), None)
        nuevo = not servicio.disponible if servicio else True   # Si no hay seleccion, el gestor avisara
        self._resultado(self.gestor.cambiar_disponibilidad(id_servicio, nuevo), "Disponibilidad actualizada.")

    # ---------------- Pestana Reservas ----------------
    def _crear_tab_reservas(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reservas")
        form = ttk.LabelFrame(tab, text="Nueva reserva / procesamiento")
        form.pack(fill="x", padx=6, pady=6)
        ttk.Label(form, text="Cliente:").grid(row=0, column=0, sticky="e", padx=4, pady=3)
        self.r_cliente = ttk.Combobox(form, state="readonly", width=35)
        self.r_cliente.grid(row=0, column=1, sticky="w", padx=4, pady=3)
        ttk.Label(form, text="Servicio:").grid(row=1, column=0, sticky="e", padx=4, pady=3)
        self.r_servicio = ttk.Combobox(form, state="readonly", width=35)
        self.r_servicio.grid(row=1, column=1, sticky="w", padx=4, pady=3)
        self.r_horas = self._campo(form, "Duracion (horas):", 2, 10)
        self.r_imp = self._campo(form, "Impuesto % (opcional):", 3, 10)
        self.r_desc = self._campo(form, "Descuento % (opcional):", 4, 10)
        botones = ttk.Frame(form)
        botones.grid(row=5, column=1, sticky="w", pady=6)
        ttk.Button(botones, text="Crear reserva", command=self.on_crear_reserva).pack(side="left", padx=2)
        ttk.Button(botones, text="Confirmar", command=self.on_confirmar).pack(side="left", padx=2)
        ttk.Button(botones, text="Procesar", command=self.on_procesar).pack(side="left", padx=2)
        ttk.Button(botones, text="Cancelar", command=self.on_cancelar).pack(side="left", padx=2)
        self.tabla_reservas = self._tabla(tab, ("ID", "Cliente", "Servicio", "Horas", "Estado", "Costo final"),
                                          (40, 200, 200, 70, 110, 130))

    def on_crear_reserva(self):
        resultado = self.gestor.crear_reserva(self._id_de_combo(self.r_cliente.get()),
                                              self._id_de_combo(self.r_servicio.get()), self.r_horas.get())
        self._resultado(resultado, "Reserva creada (pendiente de confirmacion).")

    def on_confirmar(self):
        self._resultado(self.gestor.confirmar_reserva(self._id_seleccionado(self.tabla_reservas)),
                        "Reserva confirmada.")

    def on_procesar(self):
        ok, valor = self.gestor.procesar_reserva(self._id_seleccionado(self.tabla_reservas),
                                                 self.r_imp.get(), self.r_desc.get())
        self._resultado((ok, valor), f"Reserva procesada. Costo final: ${valor:,.2f}" if ok else "")

    def on_cancelar(self):
        self._resultado(self.gestor.cancelar_reserva(self._id_seleccionado(self.tabla_reservas)),
                        "Reserva cancelada.")

    # ---------------- Pestana Simulacion y log ----------------
    def _crear_tab_simulacion(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Simulacion y log")
        botones = ttk.Frame(tab)
        botones.pack(fill="x", padx=6, pady=6)
        ttk.Button(botones, text="Ejecutar simulacion (24 operaciones)", command=self.on_simular).pack(side="left", padx=2)
        ttk.Button(botones, text="Ver archivo de log", command=self.on_ver_log).pack(side="left", padx=2)
        self.texto = scrolledtext.ScrolledText(tab, wrap="word", font=("Consolas", 9))
        self.texto.pack(fill="both", expand=True, padx=6, pady=6)

    def _mostrar_texto(self, contenido):
        self.texto.config(state="normal")        # Habilita para poder escribir
        self.texto.delete("1.0", "end")
        self.texto.insert("end", contenido)
        self.texto.config(state="disabled")      # Solo lectura para el usuario

    def on_simular(self):
        try:
            lineas = ejecutar_simulacion(self.gestor)
            self._mostrar_texto("\n".join(lineas))
            self.barra.config(text="Simulacion completada.")
        except Exception as error:               # Ultimo recurso: la ventana no se cierra
            registro.critical("Fallo en la simulacion: %r", error, exc_info=True)
            messagebox.showerror("Error", f"La simulacion fallo: {error}")
        finally:
            self.refrescar()

    def on_ver_log(self):
        if not os.path.exists(ARCHIVO_LOG):
            self._mostrar_texto("Aun no existe el archivo de log.")
            return
        with open(ARCHIVO_LOG, encoding="utf-8") as archivo:   # Lee el log completo
            self._mostrar_texto(archivo.read())

    # ---------------- Refresco de datos ----------------
    def refrescar(self):
        """Vuelve a cargar tablas y listas desplegables desde el gestor."""
        for tabla in (self.tabla_clientes, self.tabla_servicios, self.tabla_reservas):
            tabla.delete(*tabla.get_children())  # Vacia cada tabla
        for c in self.gestor.clientes:
            self.tabla_clientes.insert("", "end", values=(c.id, c.nombre, c.documento, c.correo, c.telefono))
        for s in self.gestor.servicios:
            estado = "Disponible" if s.disponible else "No disponible"
            self.tabla_servicios.insert("", "end", values=(s.id, s.tipo, s.nombre, f"${s.tarifa_hora:,.0f}",
                                                           estado, s.describir().split(" | ", 3)[-1]))
        for r in self.gestor.reservas:
            costo = f"${r.costo_final:,.2f}" if r.costo_final is not None else "-"
            self.tabla_reservas.insert("", "end", values=(r.id, r.cliente.nombre, r.servicio.nombre,
                                                          f"{r.horas:g}", r.estado, costo))
        self.r_cliente["values"] = [f"{c.id} - {c.nombre}" for c in self.gestor.clientes]
        self.r_servicio["values"] = [f"{s.id} - {s.nombre}" for s in self.gestor.servicios]


if __name__ == "__main__":
    App().mainloop()                             # Inicia la interfaz
