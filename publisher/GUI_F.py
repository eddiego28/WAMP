#!/usr/bin/env python3
import sys, json, datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox,
                             QFileDialog, QMessageBox, QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt
import pubGUI
from pubGUI import start_publisher, send_message_now

def parseTimeToSeconds(time_str):
    try:
        h, m, s = map(int, time_str.strip().split(":"))
        return h * 3600 + m * 60 + s
    except:
        return 0

class MessageForm(QGroupBox):
    def __init__(self, message_data, parent=None):
        super().__init__(message_data.get("name", "Mensaje"), parent)
        self.message_data = message_data
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        # Check para activar/desactivar
        self.activeCheck = QCheckBox("Activo")
        self.activeCheck.setChecked(self.message_data.get("active", True))
        layout.addWidget(self.activeCheck)
        
        # Desplegable para seleccionar el modo de envío
        hMode = QHBoxLayout()
        hMode.addWidget(QLabel("Modo de envío:"))
        self.modeCombo = QComboBox()
        self.modeCombo.addItems(["Programado", "Hora de sistema", "On-demand"])
        self.modeCombo.setCurrentText(self.message_data.get("mode", "Programado"))
        hMode.addWidget(self.modeCombo)
        layout.addLayout(hMode)
        
        # Campo para tiempo (HH:MM:SS)
        hTime = QHBoxLayout()
        hTime.addWidget(QLabel("Tiempo (HH:MM:SS):"))
        self.timeEdit = QLineEdit(self.message_data.get("time", "00:00:00"))
        hTime.addWidget(self.timeEdit)
        layout.addLayout(hTime)
        
        # Formulario para los campos del mensaje
        self.fieldsForm = QFormLayout()
        self.fieldEdits = {}
        fields = self.message_data.get("fields", {})
        for key, value in fields.items():
            lineEdit = QLineEdit(str(value))
            self.fieldsForm.addRow(QLabel(key + ":"), lineEdit)
            self.fieldEdits[key] = lineEdit
        layout.addLayout(self.fieldsForm)
        
        # Botón para enviar este mensaje (On-demand)
        self.sendButton = QPushButton("Enviar Mensaje")
        self.sendButton.clicked.connect(self.sendMessage)
        layout.addWidget(self.sendButton)
        
        self.setLayout(layout)
    
    def getMessage(self):
        new_fields = {}
        for key, edit in self.fieldEdits.items():
            text = edit.text()
            try:
                if '.' in text:
                    new_fields[key] = float(text)
                else:
                    new_fields[key] = int(text)
            except:
                new_fields[key] = text
        return {"name": self.message_data.get("name"), "fields": new_fields}
    
    def getDelay(self):
        return parseTimeToSeconds(self.timeEdit.text())
    
    def sendMessage(self):
        # Usar self.window() para obtener la ventana principal y acceder a topicEdit
        mainWindow = self.window()
        if not hasattr(mainWindow, "topicEdit"):
            QMessageBox.critical(self, "Error", "No se encontró la configuración del topic.")
            return
        topic = mainWindow.topicEdit.text().strip()
        if not self.activeCheck.isChecked():
            QMessageBox.information(self, "Info", "Este mensaje está desactivado.")
            return
        mode = self.modeCombo.currentText()
        delay_val = self.getDelay()
        msg = self.getMessage()
        if mode == "On-demand":
            send_message_now(topic, msg, delay=delay_val)
        else:
            QMessageBox.information(self, "Info", "Este botón solo envía mensajes en modo On-demand.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración WAMP - Publicador")
        self.initUI()
    
    def initUI(self):
        central = QWidget()
        self.setCentralWidget(central)
        mainLayout = QVBoxLayout()
        
        # Configuración básica
        formLayout = QFormLayout()
        self.realmCombo = QComboBox()
        self.transportCombo = QComboBox()
        self.topicEdit = QLineEdit("com.ads.midshmi.topic")
        # Cargar configuración desde archivo
        try:
            with open(r"C:\Users\ededi\Documents\PROYECTOS\WAMP\.crossbar\config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", "No se pudo cargar la configuración:\n" + str(e))
            sys.exit(1)
        realms = []
        transports = []
        for worker in config.get("workers", []):
            for realm in worker.get("realms", []):
                name = realm.get("name", "")
                if name and name not in realms:
                    realms.append(name)
            for transport in worker.get("transports", []):
                if transport.get("type") == "websocket":
                    endpoint = transport.get("endpoint", {})
                    port = endpoint.get("port")
                    uri = "127.0.0.1"
                    path = transport.get("path", "")
                    if path and not path.startswith("/"):
                        path = "/" + path
                    label = f"websocket@{uri}:{port}{path}"
                    transports.append({"label": label, "uri": uri, "port": port, "path": path})
        self.realmCombo.addItems(realms)
        self.transportCombo.addItems([t["label"] for t in transports])
        self.transports = transports
        formLayout.addRow("Elige Realm:", self.realmCombo)
        formLayout.addRow("Elige Transport:", self.transportCombo)
        formLayout.addRow("Ingresa Topic:", self.topicEdit)
        mainLayout.addLayout(formLayout)
        
        # Botón para cargar mensajes
        self.loadMessagesButton = QPushButton("Cargar Mensajes")
        self.loadMessagesButton.clicked.connect(self.loadMessages)
        mainLayout.addWidget(self.loadMessagesButton)
        
        # Área para formularios de mensajes (scrollable)
        self.scrollArea = QScrollArea()
        self.scrollAreaWidget = QWidget()
        self.scrollAreaLayout = QVBoxLayout()
        self.scrollAreaWidget.setLayout(self.scrollAreaLayout)
        self.scrollArea.setWidget(self.scrollAreaWidget)
        self.scrollArea.setWidgetResizable(True)
        mainLayout.addWidget(self.scrollArea)
        
        # Botón para iniciar el publicador
        self.startPublisherButton = QPushButton("Iniciar Publicador")
        self.startPublisherButton.clicked.connect(self.startPublisher)
        mainLayout.addWidget(self.startPublisherButton)
        
        central.setLayout(mainLayout)
        self.messageForms = []
    
    def loadMessages(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Selecciona JSON con mensajes", "", "JSON Files (*.json);;All Files (*)")
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{e}")
            return
        messages = data.get("messages", [])
        self.buildMessagesForm(messages)
    
    def buildMessagesForm(self, messages):
        # Limpiar área
        for i in reversed(range(self.scrollAreaLayout.count())):
            widget = self.scrollAreaLayout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.messageForms = []
        for msg in messages:
            form = MessageForm(msg, self)
            self.scrollAreaLayout.addWidget(form)
            self.messageForms.append(form)
    
    def startPublisher(self):
        if not self.messageForms:
            QMessageBox.critical(self, "Error", "Primero debe cargar y configurar al menos un mensaje.")
            return
        realm = self.realmCombo.currentText()
        transport_label = self.transportCombo.currentText()
        topic = self.topicEdit.text().strip()
        if not realm or not transport_label or not topic:
            QMessageBox.critical(self, "Error", "Complete todos los campos de configuración.")
            return
        selected_transport = None
        for t in self.transports:
            if t["label"] == transport_label:
                selected_transport = t
                break
        if not selected_transport:
            QMessageBox.critical(self, "Error", "Transport seleccionado no encontrado.")
            return
        url = f"ws://{selected_transport['uri']}:{selected_transport['port']}{selected_transport['path']}"
        start_publisher(url, realm, topic)
        QMessageBox.information(self, "Info", f"Publicador iniciado en realm '{realm}' con topic '{topic}'\nConectado a: {url}")
        # Programar el envío automático de mensajes en modo Programado o Hora de sistema
        for form in self.messageForms:
            if not form.activeCheck.isChecked():
                continue
            mode = form.modeCombo.currentText()
            time_str = form.timeEdit.text().strip()
            msg = form.getMessage()
            if mode == "Programado":
                delay_sec = parseTimeToSeconds(time_str)
            elif mode == "Hora de sistema":
                try:
                    now = datetime.datetime.now()
                    target = datetime.datetime.strptime(time_str, "%H:%M:%S")
                    target = now.replace(hour=target.hour, minute=target.minute, second=target.second, microsecond=0)
                    if target <= now:
                        target += datetime.timedelta(days=1)
                    delay_sec = (target - now).total_seconds()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Formato de hora inválido: {e}")
                    continue
            else:
                continue
            send_message_now(topic, {"name": form.message_data.get("name"), "fields": msg["fields"]}, delay=delay_sec)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
