#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import pubGUI  # Para actualizar pubGUI.global_message_data
from pubGUI import start_publisher

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

# Extraer realms: recorrer cada worker y sus realms
realms = []
for worker in config.get("workers", []):
    for realm in worker.get("realms", []):
        name = realm.get("name", "")
        if name and name not in realms:
            realms.append(name)

# Extraer transports: listar solo los de tipo "websocket"
transports = []
for worker in config.get("workers", []):
    for transport in worker.get("transports", []):
        if transport.get("type") == "websocket":
            endpoint = transport.get("endpoint", {})
            port = endpoint.get("port")
            uri = "127.0.0.1"  # Asumimos localhost si no se especifica
            path = transport.get("path", "")
            if path and not path.startswith("/"):
                path = "/" + path
            label = f"websocket@{uri}:{port}{path}"
            transports.append({
                "label": label,
                "type": "websocket",
                "uri": uri,
                "port": port,
                "path": path
            })

# Interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Configuración WAMP - Publicador")

# Sección para seleccionar Realm, Transport y Topic
tk.Label(root, text="Elige Realm:").pack(padx=10, pady=5)
realm_var = tk.StringVar(root)
if realms:
    realm_var.set(realms[0])
realm_menu = tk.OptionMenu(root, realm_var, *realms)
realm_menu.pack(padx=10, pady=5)

tk.Label(root, text="Elige Transport:").pack(padx=10, pady=5)
transport_var = tk.StringVar(root)
transport_labels = [t["label"] for t in transports]
if transport_labels:
    transport_var.set(transport_labels[0])
transport_menu = tk.OptionMenu(root, transport_var, *transport_labels)
transport_menu.pack(padx=10, pady=5)

tk.Label(root, text="Ingresa Topic:").pack(padx=10, pady=5)
topic_entry = tk.Entry(root, width=40)
topic_entry.pack(padx=10, pady=5)
topic_entry.insert(0, "com.ads.midshmi.topic")

# Botón para seleccionar el archivo JSON a personalizar
def select_json_file():
    filepath = filedialog.askopenfilename(
        title="Selecciona el archivo JSON",
        filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
    )
    if filepath:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el JSON:\n{e}")
            return
        # Guardar el filepath para referencia (opcional)
        json_file_var.set(filepath)
        build_form(data)

# Variable para almacenar la ruta del JSON seleccionado (opcional)
json_file_var = tk.StringVar(root, value="")

select_button = tk.Button(root, text="Seleccionar JSON", command=select_json_file)
select_button.pack(padx=10, pady=5)

# Frame para el formulario dinámico
frame_message = tk.LabelFrame(root, text="Personalizar mensaje JSON", padx=10, pady=10)
frame_message.pack(padx=10, pady=10, fill="both", expand=True)

# Diccionario para guardar las entradas dinámicas
dynamic_entries = {}

def build_form(data):
    # Limpia el frame si ya tiene widgets
    for widget in frame_message.winfo_children():
        widget.destroy()
    dynamic_entries.clear()
    # Si data es un diccionario, crea un campo para cada clave
    if isinstance(data, dict):
        for key, value in data.items():
            row = tk.Frame(frame_message)
            row.pack(fill="x", padx=5, pady=2)
            label = tk.Label(row, text=str(key) + ":", width=15, anchor="w")
            label.pack(side="left")
            entry = tk.Entry(row)
            # Si el valor no es una cadena, se convierte a cadena
            entry.insert(0, str(value))
            entry.pack(side="right", expand=True, fill="x")
            dynamic_entries[key] = entry
    else:
        # Si el JSON no es un diccionario, simplemente lo mostramos
        row = tk.Frame(frame_message)
        row.pack(fill="x", padx=5, pady=2)
        label = tk.Label(row, text="Contenido:", width=15, anchor="w")
        label.pack(side="left")
        entry = tk.Entry(row)
        entry.insert(0, str(data))
        entry.pack(side="right", expand=True, fill="x")
        dynamic_entries["contenido"] = entry

# Botón para actualizar el mensaje personalizado usando los valores del formulario
def update_message():
    if not dynamic_entries:
        messagebox.showerror("Error", "No hay datos para actualizar. Selecciona un JSON primero.")
        return
    try:
        new_message = {}
        for key, entry in dynamic_entries.items():
            # Se intenta interpretar el valor numérico si es posible; sino se queda como cadena.
            val = entry.get()
            try:
                # Primero intenta entero, luego flotante
                if '.' in val:
                    new_message[key] = float(val)
                else:
                    new_message[key] = int(val)
            except ValueError:
                new_message[key] = val
    except Exception as e:
        messagebox.showerror("Error", f"Error al actualizar mensaje: {e}")
        return
    pubGUI.global_message_data = new_message
    messagebox.showinfo("Información", "Mensaje JSON actualizado.")

update_button = tk.Button(frame_message, text="Actualizar Mensaje", command=update_message)
update_button.pack(pady=5)

def on_start():
    selected_realm = realm_var.get()
    selected_transport_label = transport_var.get()
    selected_topic = topic_entry.get().strip()
    if not selected_realm or not selected_transport_label or not selected_topic:
        messagebox.showerror("Error", "Por favor, complete todos los campos de configuración.")
        return
    # Buscar la configuración del transport seleccionado
    selected_transport = None
    for t in transports:
        if t["label"] == selected_transport_label:
            selected_transport = t
            break
    if not selected_transport:
        messagebox.showerror("Error", "Transport seleccionado no encontrado.")
        return
    # Construir la URL de conexión
    url = f"ws://{selected_transport['uri']}:{selected_transport['port']}{selected_transport['path']}"
    print("URL:", url)
    start_publisher(url, selected_realm, selected_topic)
    messagebox.showinfo("Info", f"Publicador iniciado en el realm '{selected_realm}' con topic '{selected_topic}'\nConectado a: {url}")

start_button = tk.Button(root, text="Iniciar Publicador", command=on_start)
start_button.pack(padx=10, pady=10)

root.mainloop()
