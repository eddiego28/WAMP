#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import time, datetime
import pubGUI  # Importamos el módulo pubGUI para usar sus funciones y variables
from pubGUI import start_publisher, send_message_now

# Función para cargar el archivo de configuración
def load_config():
    try:
        with open(r"C:\Users\ededi\Documents\PROYECTOS\WAMP\.crossbar\config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Error", "No se pudo cargar el archivo de configuración:\n" + str(e))
        return None

config = load_config()
if config is None:
    exit(1)

# Extraer realms y transports (como en versiones anteriores)
realms = []
for worker in config.get("workers", []):
    for realm in worker.get("realms", []):
        name = realm.get("name", "")
        if name and name not in realms:
            realms.append(name)

transports = []
for worker in config.get("workers", []):
    for transport in worker.get("transports", []):
        if transport.get("type") == "websocket":
            endpoint = transport.get("endpoint", {})
            port = endpoint.get("port")
            uri = "127.0.0.1"
            path = transport.get("path", "")
            if path and not path.startswith("/"):
                path = "/" + path
            label = f"websocket@{uri}:{port}{path}"
            transports.append({
                "label": label,
                "uri": uri,
                "port": port,
                "path": path
            })

# Lista global para almacenar los formularios de mensajes cargados
multi_message_forms = []

# Interfaz gráfica principal
root = tk.Tk()
root.title("Configuración WAMP - Publicador")

# Configuración básica: Realm, Transport y Topic
tk.Label(root, text="Elige Realm:").pack(padx=10, pady=5)
realm_var = tk.StringVar(root)
if realms:
    realm_var.set(realms[0])
tk.OptionMenu(root, realm_var, *realms).pack(padx=10, pady=5)

tk.Label(root, text="Elige Transport:").pack(padx=10, pady=5)
transport_var = tk.StringVar(root)
transport_labels = [t["label"] for t in transports]
if transport_labels:
    transport_var.set(transport_labels[0])
tk.OptionMenu(root, transport_var, *transport_labels).pack(padx=10, pady=5)

tk.Label(root, text="Ingresa Topic:").pack(padx=10, pady=5)
topic_entry = tk.Entry(root, width=40)
topic_entry.pack(padx=10, pady=5)
topic_entry.insert(0, "com.ads.midshmi.topic")

# Botón para cargar el archivo JSON con mensajes (ahora "Cargar Mensajes")
def select_messages_file():
    filepath = filedialog.askopenfilename(
        title="Selecciona archivo JSON de mensajes",
        filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
    )
    if not filepath:
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{e}")
        return
    messages = data.get("messages", [])
    build_multi_messages_form(messages)

tk.Button(root, text="Cargar Mensajes", command=select_messages_file).pack(padx=10, pady=5)

# Frame para mostrar y configurar cada mensaje
frame_multi = tk.LabelFrame(root, text="Configuración de Mensajes", padx=10, pady=10)
frame_multi.pack(padx=10, pady=10, fill="both", expand=True)

# Función para construir el formulario para múltiples mensajes
def build_multi_messages_form(messages):
    global multi_message_forms
    # Limpiar el frame y la lista
    for widget in frame_multi.winfo_children():
        widget.destroy()
    multi_message_forms.clear()
    # Opciones para el modo de envío
    modos = ["Programado", "Hora de sistema", "On-demand"]
    for i, msg in enumerate(messages):
        form = {}  # Diccionario para almacenar los controles de este mensaje
        msg_frame = tk.LabelFrame(frame_multi, text=msg.get("name", f"Mensaje {i+1}"), padx=5, pady=5)
        msg_frame.pack(fill="x", padx=5, pady=5)
        # Checkbutton para activar/desactivar
        form["active_var"] = tk.BooleanVar(value=msg.get("active", True))
        tk.Checkbutton(msg_frame, text="Activo", variable=form["active_var"]).pack(anchor="w")
        # Desplegable para seleccionar modo de envío
        tk.Label(msg_frame, text="Modo de envío:").pack(side="left")
        form["mode_var"] = tk.StringVar(value=msg.get("mode", "Programado"))
        tk.OptionMenu(msg_frame, form["mode_var"], *modos).pack(side="left", padx=5)
        # Campo para tiempo (HH:MM:SS). Se usará para "Programado" (retraso relativo) o "Hora de sistema" (hora absoluta)
        tk.Label(msg_frame, text="Tiempo (HH:MM:SS):").pack(side="left")
        form["time_entry"] = tk.Entry(msg_frame, width=10)
        # Valor por defecto: si existe, usarlo; si no, "00:00:00"
        form["time_entry"].insert(0, msg.get("time", "00:00:00"))
        form["time_entry"].pack(side="left", padx=5)
        # Crear campos dinámicos para los datos del mensaje
        form["field_entries"] = {}
        fields = msg.get("fields", {})
        for key, value in fields.items():
            row = tk.Frame(msg_frame)
            row.pack(fill="x", padx=5, pady=2)
            tk.Label(row, text=f"{key}:", width=15, anchor="w").pack(side="left")
            ent = tk.Entry(row)
            ent.insert(0, str(value))
            ent.pack(side="left", fill="x", expand=True)
            form["field_entries"][key] = ent
        # Botón para enviar este mensaje (si está en modo On-demand)
        def send_this_message(form=form, m=msg):
            if not form["active_var"].get():
                messagebox.showinfo("Info", "Este mensaje está desactivado.")
                return
            mode = form["mode_var"].get()
            time_str = form["time_entry"].get()
            try:
                # Extraer los campos editados
                new_fields = {}
                for key, ent in form["field_entries"].items():
                    val = ent.get()
                    try:
                        if '.' in val:
                            new_fields[key] = float(val)
                        else:
                            new_fields[key] = int(val)
                    except:
                        new_fields[key] = val
            except Exception as e:
                messagebox.showerror("Error", f"Error al leer campos: {e}")
                return
            msg_to_send = {"name": m.get("name"), "fields": new_fields}
            send_topic = topic_entry.get().strip()
            if mode == "On-demand":
                # Enviar inmediatamente (o con delay si se especifica)
                delay_val = parse_time_to_seconds(time_str)  # si se desea considerar el tiempo también en on-demand
                send_message_now(send_topic, msg_to_send, delay=delay_val)
            else:
                messagebox.showinfo("Info", "Este botón solo funciona para mensajes On-demand.")
        tk.Button(msg_frame, text="Enviar Mensaje", command=send_this_message).pack(side="left", padx=5)
        multi_message_forms.append(form)

def parse_time_to_seconds(time_str):
    """Convierte una cadena HH:MM:SS a segundos (entero)."""
    try:
        h, m, s = map(int, time_str.strip().split(":"))
        return h * 3600 + m * 60 + s
    except:
        return 0

# Botón para iniciar el publicador.
def on_start():
    # Antes de iniciar, programar automáticamente los mensajes que no sean On-demand
    if not multi_message_forms:
        messagebox.showerror("Error", "Primero debe cargar y configurar al menos un mensaje.")
        return
    selected_realm = realm_var.get()
    selected_transport_label = transport_var.get()
    selected_topic = topic_entry.get().strip()
    if not selected_realm or not selected_transport_label or not selected_topic:
        messagebox.showerror("Error", "Complete todos los campos de configuración.")
        return
    # Buscar el transport
    selected_transport = None
    for t in transports:
        if t["label"] == selected_transport_label:
            selected_transport = t
            break
    if not selected_transport:
        messagebox.showerror("Error", "Transport seleccionado no encontrado.")
        return
    url = f"ws://{selected_transport['uri']}:{selected_transport['port']}{selected_transport['path']}"
    print("URL:", url)
    # Iniciar el publicador
    start_publisher(url, selected_realm, selected_topic)
    messagebox.showinfo("Info", f"Publicador iniciado en realm '{selected_realm}' con topic '{selected_topic}'\nConectado a: {url}")
    # Programar el envío automático de los mensajes (Programado y Hora de sistema)
    for form in multi_message_forms:
        if not form["active_var"].get():
            continue
        mode = form["mode_var"].get()
        time_str = form["time_entry"].get().strip()
        # Obtener los campos del mensaje
        new_fields = {}
        for key, ent in form["field_entries"].items():
            val = ent.get()
            try:
                if '.' in val:
                    new_fields[key] = float(val)
                else:
                    new_fields[key] = int(val)
            except:
                new_fields[key] = val
        msg_to_send = {"name": "Mensaje programado", "fields": new_fields}
        # Calcular el delay
        if mode == "Programado":
            delay_sec = parse_time_to_seconds(time_str)
        elif mode == "Hora de sistema":
            try:
                now = datetime.datetime.now()
                target = datetime.datetime.strptime(time_str, "%H:%M:%S")
                # Combina la fecha de hoy con la hora objetivo
                target = now.replace(hour=target.hour, minute=target.minute, second=target.second, microsecond=0)
                # Si el tiempo ya pasó, se programa para mañana
                if target <= now:
                    target += datetime.timedelta(days=1)
                delay_sec = (target - now).total_seconds()
            except Exception as e:
                messagebox.showerror("Error", f"Formato de hora de sistema inválido: {e}")
                continue
        else:
            # On-demand: no se programa automáticamente.
            continue
        # Programar el envío con el delay calculado.
        send_message_now(selected_topic, msg_to_send, delay=delay_sec)
    messagebox.showinfo("Info", "Los mensajes programados han sido configurados.")

tk.Button(root, text="Iniciar Publicador", command=on_start).pack(padx=10, pady=10)

root.mainloop()
