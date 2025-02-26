#!/usr/bin/env python3
import sys, os, json, datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QListWidget,
                             QListWidgetItem, QTextEdit, QFileDialog, QMessageBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QTextCursor
import logging

# Añadir la carpeta raíz del proyecto al sys.path
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

# ---------- Pestaña Publicador ----------
class PublisherMessageForm(QGroupBox):
    def __init__(self, message_data, parent=None):
        super().__init__(message_data.get("name", "Mensaje"), parent)
        self.message_data = message_data
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.activeButton = QPushButton("Activo")
        self.activeButton.setCheckable(True)
        self.activeButton.setChecked(self.message_data.get("active", True))
        layout.addWidget(self.activeButton)
        
        modeLayout = QHBoxLayout()
        modeLayout.addWidget(QLabel("Modo de envío:"))
        self.modeCombo = QComboBox()
        self.modeCombo.addItems(["Programado", "Hora de sistema", "On-demand"])
        self.modeCombo.setCurrentText(self.message_data.get("mode", "Programado"))
        modeLayout.addWidget(self.modeCombo)
        layout.addLayout(modeLayout)
        
        timeLayout = QHBoxLayout()
        timeLayout.addWidget(QLabel("Tiempo (HH:MM:SS):"))
        self.timeEdit = QLineEdit(self.message_data.get("time", "00:00:00"))
        timeLayout.addWidget(self.timeEdit)
        layout.addLayout(timeLayout)
        
        self.fieldsForm = QFormLayout()
        self.fieldEdits = {}
        fields = self.message_data.get("fields", {})
        for key, value in fields.items():
            lineEdit = QLineEdit(str(value))
            self.fieldsForm.addRow(QLabel(f"{key}:"), lineEdit)
            self.fieldEdits[key] = lineEdit
        layout.addLayout(self.fieldsForm)
        
        self.sendButton = QPushButton("Enviar Mensaje")
        self.sendButton.clicked.connect(self.sendMessage)
        layout.addWidget(self.sendButton)
        
        self.setLayout(layout)
    
    def getMessage(self):
        new_fields = {}
        for key, edit in self.fieldEdits.items():
            txt = edit.text()
            try:
                if '.' in txt:
                    new_fields[key] = float(txt)
                else:
                    new_fields[key] = int(txt)
            except:
                new_fields[key] = txt
        return {"name": self.message_data.get("name"), "fields": new_fields}
    
    def getDelay(self):
        try:
            h, m, s = map(int, self.timeEdit.text().strip().split(":"))
            return h * 3600 + m * 60 + s
        except:
            return 0
    
    def sendMessage(self):
        if not self.activeButton.isChecked():
            QMessageBox.information(self, "Info", "Este mensaje está desactivado.")
            return
        mode = self.modeCombo.currentText()
        delay = self.getDelay()
        msg = self.getMessage()
        topic = self.window().publisherTab.topicEdit.text().strip()
        if mode == "On-demand":
            send_message_now(topic, msg, delay=delay)
        else:
            QMessageBox.information(self, "Info", "Los mensajes programados se enviarán al iniciar el publicador.")

class PublisherTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messageForms = []
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        formLayout = QHBoxLayout()
        formLayout.addWidget(QLabel("Realm:"))
        self.realmCombo = QComboBox()
        self.realmCombo.addItems(["default", "ADS.MIDSHMI"])
        formLayout.addWidget(self.realmCombo)
        formLayout.addWidget(QLabel("Router URL:"))
        self.urlEdit = QLineEdit("ws://127.0.0.1:60001/ws")
        formLayout.addWidget(self.urlEdit)
        formLayout.addWidget(QLabel("Topic:"))
        self.topicEdit = QLineEdit("com.ads.midshmi.topic")
        formLayout.addWidget(self.topicEdit)
        layout.addLayout(formLayout)
        
        self.loadMessagesButton = QPushButton("Cargar Mensajes")
        self.loadMessagesButton.clicked.connect(self.loadMessages)
        layout.addWidget(self.loadMessagesButton)
        
        from PyQt5.QtWidgets import QScrollArea
        self.scrollAreaWidget = QWidget()
        self.scrollAreaLayout = QVBoxLayout()
        self.scrollAreaWidget.setLayout(self.scrollAreaLayout)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.scrollAreaWidget)
        self.scrollArea.setWidgetResizable(True)
        layout.addWidget(QLabel("Configurar Mensajes:"))
        layout.addWidget(self.scrollArea)
        
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
    
    def loadMessages(self):
        from PyQt5.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getOpenFileName(self, "Selecciona JSON de Mensajes", "", "JSON Files (*.json);;All Files (*)")
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{e}")
            return
        if isinstance(data, list):
            messages = data
        else:
            messages = data.get("messages", [])
        for i in reversed(range(self.scrollAreaLayout.count())):
            widget = self.scrollAreaLayout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.messageForms = []
        for msg in messages:
            form = PublisherMessageForm(msg, self)
            self.scrollAreaLayout.addWidget(form)
            self.messageForms.append(form)
    
    def startPublisher(self):
        from publisher.pubGUI import start_publisher, send_message_now
        url = self.urlEdit.text().strip()
        realm = self.realmCombo.currentText()
        topic = self.topicEdit.text().strip()
        if not url or not realm or not topic:
            QMessageBox.critical(self, "Error", "Complete todos los campos de configuración.")
            return
        start_publisher(url, realm, topic)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        appendHtmlLog(self.logText, f"<p>[{timestamp}] Publicador iniciado en realm '{realm}' con topic '{topic}'<br/>URL: {url}</p>")
        for form in self.messageForms:
            if not form.activeButton.isChecked():
                continue
            mode = form.modeCombo.currentText()
            if mode == "On-demand":
                continue
            delay = form.getDelay()
            msg = form.getMessage()
            send_message_now(topic, {"name": form.message_data.get("name"), "fields": msg["fields"]}, delay=delay)
            formatted = format_json_as_table({"name": form.message_data.get("name"), "fields": msg["fields"]})
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            appendHtmlLog(self.logText, f"<p>[{timestamp}] Stimulus message:<br/>{formatted}</p>")
    
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
        layout = QVBoxLayout()
        formLayout = QHBoxLayout()
        formLayout.addWidget(QLabel("Realm:"))
        self.realmCombo = QComboBox()
        self.realmCombo.addItems(["default", "ADS.MIDSHMI"])
        formLayout.addWidget(self.realmCombo)
        formLayout.addWidget(QLabel("Router URL:"))
        self.urlEdit = QLineEdit("ws://127.0.0.1:60001")
        formLayout.addWidget(self.urlEdit)
        layout.addLayout(formLayout)
        
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
        filepath, _ = QFileDialog.getOpenFileName(self, "Selecciona JSON de Tópicos", "", "JSON Files (*.json);;All Files (*)")
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
            item = QListWidgetItem(topic)
            self.topicsList.addItem(item)
    
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
            QMessageBox.critical(self, "Error", "Selecciona al menos un tópico.")
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
