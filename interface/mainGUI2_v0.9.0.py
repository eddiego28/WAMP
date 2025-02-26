#!/usr/bin/env python3
import sys, os, json, datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox,
                             QListWidget, QListWidgetItem, QTextEdit, QFileDialog,
                             QMessageBox, QGroupBox, QFormLayout, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QTextCursor
import logging

# Añadir la carpeta raíz del proyecto al sys.path (ajusta según tu estructura)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from publisher.pubGUI import start_publisher, send_message_now
from subscriber.subGUI import start_subscriber

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def format_json_as_table(msg):
    try:
        html = "<table border='1' cellspacing='0' cellpadding='4' style='border-collapse:collapse;'>"
        for key, value in msg.items():
            html += f"<tr><td><b>{key}</b></td><td>{value}</td></tr>"
        html += "</table>"
        return html
    except Exception:
        return f"<p>{msg}</p>"

def appendHtmlLog(widget, html):
    cursor = widget.textCursor()
    cursor.movePosition(QTextCursor.End)
    cursor.insertHtml(html)
    cursor.insertBlock()
    widget.setTextCursor(cursor)
    widget.ensureCursorVisible()

# ---------- Formulario Dinámico para JSON (con estructura jerárquica) ----------
class DynamicPublisherMessageForm(QGroupBox):
    def __init__(self, default_json=None, parent=None):
        super().__init__("Mensaje (JSON dinámico)", parent)
        self.default_json = default_json  # JSON precargado (opcional)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        # Controles de modo y tiempo
        controlLayout = QHBoxLayout()
        controlLayout.addWidget(QLabel("Modo:"))
        self.modeCombo = QComboBox()
        self.modeCombo.addItems(["Programado", "Hora de sistema", "On-demand"])
        controlLayout.addWidget(self.modeCombo)
        controlLayout.addWidget(QLabel("Tiempo (HH:MM:SS):"))
        self.timeEdit = QLineEdit("00:00:00")
        controlLayout.addWidget(self.timeEdit)
        layout.addLayout(controlLayout)
        
        # Botón para cargar JSON desde archivo
        self.loadButton = QPushButton("Cargar JSON desde Archivo")
        self.loadButton.clicked.connect(self.loadJSON)
        layout.addWidget(self.loadButton)
        
        # Área donde se genera el formulario dinámico
        self.formArea = QScrollArea()
        self.formArea.setMinimumSize(600, 400)
        self.formWidget = QWidget()
        self.formLayout = QFormLayout()
        self.formWidget.setLayout(self.formLayout)
        self.formArea.setWidget(self.formWidget)
        self.formArea.setWidgetResizable(True)
        layout.addWidget(QLabel("Campos a editar:"))
        layout.addWidget(self.formArea)
        
        # Botón para previsualizar el JSON resultante
        self.previewButton = QPushButton("Previsualizar")
        self.previewButton.clicked.connect(self.previewJSON)
        layout.addWidget(self.previewButton)
        
        # Área de previsualización
        self.previewArea = QTextEdit()
        self.previewArea.setReadOnly(True)
        self.previewArea.setMinimumSize(600, 200)
        layout.addWidget(QLabel("Previsualización JSON:"))
        layout.addWidget(self.previewArea)
        
        # Botón para enviar el mensaje
        self.sendButton = QPushButton("Enviar JSON")
        self.sendButton.clicked.connect(self.sendJSON)
        layout.addWidget(self.sendButton)
        
        self.setLayout(layout)
        if self.default_json:
            self.build_form(self.default_json)
    
    def loadJSON(self):
        from PyQt5.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getOpenFileName(self, "Seleccione un archivo JSON", "", "JSON Files (*.json);;All Files (*)")
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.default_json = data
            self.build_form(data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el JSON:\n{e}")
    
    def build_form(self, data):
        # Limpia el layout actual
        while self.formLayout.count():
            child = self.formLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._build_form_rec(data, self.formLayout)
    
    def _build_form_rec(self, data, layout):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    # Creamos un grupo y agregamos una fila con el label y el grupo
                    group = QGroupBox()
                    group.setTitle(key)
                    group_layout = QFormLayout()
                    group.setLayout(group_layout)
                    layout.addRow(QLabel(key), group)
                    self._build_form_rec(value, group_layout)
                elif isinstance(value, list):
                    # Para listas, usamos un QTextEdit para editar el JSON de la lista
                    te = QTextEdit()
                    te.setPlainText(json.dumps(value, indent=2, ensure_ascii=False))
                    layout.addRow(QLabel(key), te)
                else:
                    le = QLineEdit(str(value))
                    layout.addRow(QLabel(key), le)
        else:
            le = QLineEdit(str(data))
            layout.addRow(QLabel("Valor"), le)
    
    def collect_form_data(self, layout):
        data = {}
        for row in range(layout.rowCount()):
            label_item = layout.itemAt(row, QFormLayout.LabelRole)
            field_item = layout.itemAt(row, QFormLayout.FieldRole)
            if label_item is None or field_item is None:
                continue
            key = label_item.widget().text()
            widget = field_item.widget()
            if isinstance(widget, QGroupBox):
                data[key] = self.collect_form_data(widget.layout())
            elif isinstance(widget, QTextEdit):
                try:
                    data[key] = json.loads(widget.toPlainText())
                except:
                    data[key] = widget.toPlainText()
            elif isinstance(widget, QLineEdit):
                data[key] = widget.text()
        return data
    
    def previewJSON(self):
        form_data = self.collect_form_data(self.formLayout)
        formatted = json.dumps(form_data, indent=2, ensure_ascii=False)
        self.previewArea.setPlainText(formatted)
    
    def getDelay(self):
        try:
            h, m, s = map(int, self.timeEdit.text().strip().split(":"))
            return h * 3600 + m * 60 + s
        except:
            return 0
    
    def sendJSON(self):
        form_data = self.collect_form_data(self.formLayout)
        delay = self.getDelay()
        topic = self.parent().topicEdit.text().strip() if hasattr(self.parent(), "topicEdit") else "com.ads.midshmi.topic"
        send_message_now(topic, form_data, delay=delay)
        QMessageBox.information(self, "Info", "Mensaje enviado.")

# ---------- Pestaña Publicador (Controles de conexión + formulario dinámico) ----------
class PublisherTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        # Controles de conexión
        connLayout = QHBoxLayout()
        connLayout.addWidget(QLabel("Realm:"))
        self.realmCombo = QComboBox()
        self.realmCombo.addItems(["default", "ADS.MIDSHMI"])
        connLayout.addWidget(self.realmCombo)
        connLayout.addWidget(QLabel("Router URL:"))
        self.urlEdit = QLineEdit("ws://127.0.0.1:60001/ws")
        connLayout.addWidget(self.urlEdit)
        connLayout.addWidget(QLabel("Topic:"))
        self.topicEdit = QLineEdit("com.ads.midshmi.topic")
        connLayout.addWidget(self.topicEdit)
        layout.addLayout(connLayout)
        
        # Agregar el formulario dinámico para JSON
        self.dynamicForm = DynamicPublisherMessageForm(parent=self)
        layout.addWidget(self.dynamicForm)
        
        btnLayout = QHBoxLayout()
        self.startButton = QPushButton("Iniciar Publicador")
        self.startButton.clicked.connect(self.startPublisher)
        btnLayout.addWidget(self.startButton)
        self.testButton = QPushButton("Enviar Mensaje de Prueba")
        self.testButton.clicked.connect(self.sendTestMessage)
        btnLayout.addWidget(self.testButton)
        layout.addLayout(btnLayout)
        
        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        layout.addWidget(QLabel("Log Publicador:"))
        layout.addWidget(self.logText)
        
        self.setLayout(layout)
    
    def startPublisher(self):
        from publisher.pubGUI import start_publisher
        url = self.urlEdit.text().strip()
        realm = self.realmCombo.currentText()
        topic = self.topicEdit.text().strip()
        if not url or not realm or not topic:
            QMessageBox.critical(self, "Error", "Complete todos los campos de conexión.")
            return
        start_publisher(url, realm, topic)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        appendHtmlLog(self.logText, f"<p>[{timestamp}] Publicador iniciado en realm '{realm}' con topic '{topic}'<br/>URL: {url}</p>")
    
    def sendTestMessage(self):
        from publisher.pubGUI import send_message_now
        topic = self.topicEdit.text().strip()
        message = {"name": "Mensaje de prueba", "fields": {"valor": 123, "estado": "OK"}}
        send_message_now(topic, message, delay=0)
        formatted = format_json_as_table(message)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        appendHtmlLog(self.logText, f"<p>[{timestamp}] Stimulus message:<br/>{formatted}</p>")

# ---------- Pestaña Subscriptor ----------
class SubscriberTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        from PyQt5.QtWidgets import QListWidget
        layout = QVBoxLayout()
        connLayout = QHBoxLayout()
        connLayout.addWidget(QLabel("Realm:"))
        self.realmCombo = QComboBox()
        self.realmCombo.addItems(["default", "ADS.MIDSHMI"])
        connLayout.addWidget(self.realmCombo)
        connLayout.addWidget(QLabel("Router URL:"))
        self.urlEdit = QLineEdit("ws://127.0.0.1:60001/ws")
        connLayout.addWidget(self.urlEdit)
        layout.addLayout(connLayout)
        
        listLayout = QHBoxLayout()
        listLayout.addWidget(QLabel("Tópicos:"))
        self.topicsList = QListWidget()
        self.topicsList.setSelectionMode(QListWidget.MultiSelection)
        listLayout.addWidget(self.topicsList)
        btnLayout = QVBoxLayout()
        self.loadTopicsButton = QPushButton("Cargar Tópicos desde Archivo")
        self.loadTopicsButton.clicked.connect(self.loadTopics)
        btnLayout.addWidget(self.loadTopicsButton)
        self.newTopicEdit = QLineEdit()
        self.newTopicEdit.setPlaceholderText("Añadir nuevo tópico...")
        btnLayout.addWidget(self.newTopicEdit)
        self.addTopicButton = QPushButton("Agregar")
        self.addTopicButton.clicked.connect(self.addTopic)
        btnLayout.addWidget(self.addTopicButton)
        listLayout.addLayout(btnLayout)
        layout.addLayout(listLayout)
        
        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        layout.addWidget(QLabel("Log Subscriptor:"))
        layout.addWidget(self.logText)
        
        self.startButton = QPushButton("Iniciar Suscripción")
        self.startButton.clicked.connect(self.startSubscription)
        layout.addWidget(self.startButton)
        
        self.setLayout(layout)
    
    def loadTopics(self):
        from PyQt5.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getOpenFileName(self, "Seleccione JSON de Tópicos", "", "JSON Files (*.json);;All Files (*)")
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{e}")
            return
        if isinstance(data, list):
            topics = data
        else:
            topics = data.get("topics", [])
        self.topicsList.clear()
        for topic in topics:
            self.topicsList.addItem(topic)
    
    def addTopic(self):
        new_topic = self.newTopicEdit.text().strip()
        if new_topic:
            self.topicsList.addItem(new_topic)
            self.newTopicEdit.clear()
    
    def startSubscription(self):
        from subscriber.subGUI import start_subscriber
        realm = self.realmCombo.currentText()
        url = self.urlEdit.text().strip()
        selected_items = self.topicsList.selectedItems()
        if not selected_items:
            QMessageBox.critical(self, "Error", "Seleccione al menos un tópico.")
            return
        topics = [item.text() for item in selected_items]
        start_subscriber(url, realm, topics, on_message_callback=self.onMessageArrived)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        appendHtmlLog(self.logText, f"<p>[{timestamp}] Subscriptor iniciado en realm '{realm}' para tópicos: {topics}</p>")
    
    def onMessageArrived(self, content):
        from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
        QMetaObject.invokeMethod(self, "onMessageArrivedMainThread", Qt.QueuedConnection, Q_ARG(dict, content))
    
    @pyqtSlot(dict)
    def onMessageArrivedMainThread(self, content):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_table = format_json_as_table(content)
        appendHtmlLog(self.logText, f"<p>[{timestamp}] Sys answer:<br/>{html_table}</p>")

# ---------- Ventana Principal ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema WAMP: Publicador y Subscriptor")
        self.resize(900, 700)
        self.initUI()
    
    def initUI(self):
        tabs = QTabWidget()
        self.publisherTab = PublisherTab(self)
        self.subscriberTab = SubscriberTab(self)
        tabs.addTab(self.publisherTab, "Publicador")
        tabs.addTab(self.subscriberTab, "Subscriptor")
        self.setCentralWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
