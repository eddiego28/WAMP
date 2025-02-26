#!/usr/bin/env python3
import sys, os, json, datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox,
                             QListWidget, QTextEdit, QFileDialog, QMessageBox,
                             QGroupBox, QFormLayout, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QTextCursor
import logging

# Configuración de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def format_json_as_table(msg):
    try:
        style = """
        <style>
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #000; padding: 5px; text-align: left; }
            th { background-color: #ccc; }
        </style>
        """
        html = style + "<table>"
        html += "<tr><th>Campo</th><th>Valor</th></tr>"
        for key, value in msg.items():
            html += f"<tr><td>{key}</td><td>{value}</td></tr>"
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

# ---------------- PublisherEditorWidget ----------------
class PublisherEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        modeLayout = QHBoxLayout()
        modeLayout.addWidget(QLabel("Editar en:"))
        self.editModeSelector = QComboBox()
        self.editModeSelector.addItems(["Formulario Dinámico", "JSON"])
        self.editModeSelector.currentTextChanged.connect(self.switchMode)
        modeLayout.addWidget(self.editModeSelector)
        layout.addLayout(modeLayout)
        
        self.importButton = QPushButton("Cargar JSON desde Archivo")
        self.importButton.clicked.connect(self.loadJSONFromFile)
        layout.addWidget(self.importButton)
        
        commonLayout = QHBoxLayout()
        commonLayout.addWidget(QLabel("Modo de envío:"))
        self.commonModeCombo = QComboBox()
        self.commonModeCombo.addItems(["Programado", "Hora de sistema", "On-demand"])
        commonLayout.addWidget(self.commonModeCombo)
        commonLayout.addWidget(QLabel("Tiempo (HH:MM:SS):"))
        self.commonTimeEdit = QLineEdit("00:00:00")
        commonLayout.addWidget(self.commonTimeEdit)
        layout.addLayout(commonLayout)
        
        self.dynamicWidget = DynamicPublisherMessageForm(parent=self)
        self.jsonEditor = QTextEdit()
        self.jsonEditor.setMinimumSize(600, 400)
        self.jsonEditor.hide()
        layout.addWidget(self.dynamicWidget)
        layout.addWidget(self.jsonEditor)
        
        self.setLayout(layout)
    
    def switchMode(self, mode):
        if mode == "Formulario Dinámico":
            self.jsonEditor.hide()
            self.dynamicWidget.show()
        else:
            self.dynamicWidget.hide()
            if not self.jsonEditor.toPlainText().strip():
                data = self.dynamicWidget.collect_form_data(self.dynamicWidget.formLayout)
                self.jsonEditor.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))
            self.jsonEditor.show()
    
    def loadJSONFromFile(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Seleccione un archivo JSON", "", "JSON Files (*.json);;All Files (*)")
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.jsonEditor.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el JSON:\n{e}")
    
    def send(self):
        if self.editModeSelector.currentText() == "Formulario Dinámico":
            self.dynamicWidget.sendJSON()
        else:
            try:
                data = json.loads(self.jsonEditor.toPlainText())
                topic = self.parent().topicEdit.text().strip() if hasattr(self.parent(), "topicEdit") else "com.ads.midshmi.topic"
                send_message_now(topic, data, delay=0)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"JSON inválido:\n{e}")

# ---------------- DynamicPublisherMessageForm ----------------
class DynamicPublisherMessageForm(QGroupBox):
    def __init__(self, default_json=None, parent=None):
        super().__init__("Mensaje (JSON dinámico)", parent)
        # Si no se proporciona JSON, se inicializa con un ejemplo complejo
        if default_json is None:
            self.default_json = {
                "config": {
                    "param1": "valor1",
                    "param2": 123,
                    "detalles": {
                        "subparam1": "dato1",
                        "subparam2": [1, 2, 3]
                    }
                },
                "lista": ["item1", "item2", "item3"]
            }
        else:
            self.default_json = default_json
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.formArea = QScrollArea()
        self.formArea.setMinimumSize(600, 400)
        self.formWidget = QWidget()
        self.formLayout = QFormLayout()
        self.formWidget.setLayout(self.formLayout)
        self.formArea.setWidget(self.formWidget)
        self.formArea.setWidgetResizable(True)
        layout.addWidget(QLabel("Campos a editar:"))
        layout.addWidget(self.formArea)
        self.setLayout(layout)
        self.build_form(self.default_json)
    
    def build_form(self, data):
        # Limpia el formulario antes de construirlo
        while self.formLayout.count():
            child = self.formLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._build_form_rec(data, self.formLayout)
    
    def _build_form_rec(self, data, layout, indent=0):
        # Si se desea, se puede usar el parámetro indent para modificar la apariencia (aumentando el margen)
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    group = QGroupBox(key)
                    # Aplicamos un estilo para indentarlo (aumentar margen izquierdo)
                    group.setStyleSheet(f"margin-left: {indent * 20}px;")
                    group_layout = QFormLayout()
                    group.setLayout(group_layout)
                    layout.addRow(group)
                    self._build_form_rec(value, group_layout, indent + 1)
                elif isinstance(value, list):
                    te = QTextEdit()
                    te.setPlainText(json.dumps(value, indent=2, ensure_ascii=False))
                    te.setStyleSheet(f"margin-left: {indent * 20}px;")
                    layout.addRow(QLabel(key), te)
                else:
                    le = QLineEdit(str(value))
                    le.setStyleSheet(f"margin-left: {indent * 20}px;")
                    layout.addRow(QLabel(key), le)
        else:
            le = QLineEdit(str(data))
            le.setStyleSheet(f"margin-left: {indent * 20}px;")
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
    
    def sendJSON(self):
        data = self.collect_form_data(self.formLayout)
        try:
            h, m, s = map(int, self.parent().commonTimeEdit.text().strip().split(":"))
            delay = h * 3600 + m * 60 + s
        except:
            delay = 0
        topic = self.parent().topicEdit.text().strip() if hasattr(self.parent(), "topicEdit") else "com.ads.midshmi.topic"
        send_message_now(topic, data, delay=delay)

# ---------------- MessageConfigWidget ----------------
class MessageConfigWidget(QGroupBox):
    def __init__(self, msg_id, parent=None):
        super().__init__(parent)
        self.msg_id = msg_id
        self.setTitle(f"Mensaje #{self.msg_id}")
        self.setCheckable(True)
        self.setChecked(True)
        self.toggled.connect(self.toggleContent)
        self.initUI()
    
    def initUI(self):
        self.contentWidget = QWidget()
        contentLayout = QVBoxLayout()
        
        formLayout = QFormLayout()
        self.realmCombo = QComboBox()
        self.realmCombo.addItems(["default", "ADS.MIDSHMI"])
        formLayout.addRow("Realm:", self.realmCombo)
        self.urlEdit = QLineEdit("ws://127.0.0.1:60001/ws")
        formLayout.addRow("Router URL:", self.urlEdit)
        self.topicEdit = QLineEdit("com.ads.midshmi.topic")
        formLayout.addRow("Topic:", self.topicEdit)
        contentLayout.addLayout(formLayout)
        
        self.editorWidget = PublisherEditorWidget(parent=self)
        self.editorWidget.commonModeCombo.currentTextChanged.connect(self.updateSendButtonState)
        contentLayout.addWidget(self.editorWidget)
        
        self.sendButton = QPushButton("Enviar")
        self.sendButton.clicked.connect(self.sendMessage)
        self.sendButton.setEnabled(self.editorWidget.commonModeCombo.currentText() == "On-demand")
        contentLayout.addWidget(self.sendButton)
        
        self.contentWidget.setLayout(contentLayout)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.contentWidget)
        self.setLayout(mainLayout)
    
    def updateSendButtonState(self, mode):
        self.sendButton.setEnabled(mode == "On-demand")
    
    def toggleContent(self, checked):
        self.contentWidget.setVisible(checked)
        if not checked:
            topic = self.topicEdit.text().strip()
            mode = self.editorWidget.commonModeCombo.currentText()
            time_val = self.editorWidget.commonTimeEdit.text()
            self.setTitle(f"Mensaje #{self.msg_id} - {topic} - {mode} - {time_val}")
        else:
            self.setTitle(f"Mensaje #{self.msg_id}")
    
    def sendMessage(self):
        mode = self.editorWidget.commonModeCombo.currentText()
        try:
            h, m, s = map(int, self.editorWidget.commonTimeEdit.text().strip().split(":"))
            delay = h * 3600 + m * 60 + s
        except:
            delay = 0
        topic = self.topicEdit.text().strip()
        if self.editorWidget.editModeSelector.currentText() == "Formulario Dinámico":
            data = self.editorWidget.dynamicWidget.collect_form_data(self.editorWidget.dynamicWidget.formLayout)
        else:
            try:
                data = json.loads(self.editorWidget.jsonEditor.toPlainText())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"JSON inválido:\n{e}")
                return
        send_message_now(topic, data, delay=(delay if mode != "On-demand" else 0))
        publish_time = datetime.datetime.now() + datetime.timedelta(seconds=delay)
        publish_time_str = publish_time.strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(self.parent(), "logText"):
            appendHtmlLog(self.parent().logText, f"<p><strong>[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Publicado: Topic: {topic}, Programado para: {publish_time_str}</strong></p>")
    
    def getConfig(self):
        return {
            "id": self.msg_id,
            "realm": self.realmCombo.currentText(),
            "router_url": self.urlEdit.text().strip(),
            "topic": self.topicEdit.text().strip(),
            "content": (self.editorWidget.dynamicWidget.collect_form_data(self.editorWidget.dynamicWidget.formLayout)
                        if self.editorWidget.editModeSelector.currentText() == "Formulario Dinámico"
                        else json.loads(self.editorWidget.jsonEditor.toPlainText()))
        }

# ---------------- PublisherTab (Múltiples Mensajes) ----------------
class PublisherTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.msgWidgets = []
        self.next_id = 1
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        topLayout = QHBoxLayout()
        self.addMsgButton = QPushButton("Agregar mensaje")
        self.addMsgButton.clicked.connect(self.addMessage)
        topLayout.addWidget(self.addMsgButton)
        layout.addLayout(topLayout)
        
        self.msgArea = QScrollArea()
        self.msgArea.setWidgetResizable(True)
        self.msgContainer = QWidget()
        self.msgLayout = QVBoxLayout()
        self.msgContainer.setLayout(self.msgLayout)
        self.msgArea.setWidget(self.msgContainer)
        layout.addWidget(self.msgArea)
        
        connLayout = QHBoxLayout()
        connLayout.addWidget(QLabel("Publicador Global (Conecta y publica todos los mensajes)"))
        self.globalStartButton = QPushButton("Iniciar Publicador")
        self.globalStartButton.clicked.connect(self.startPublisher)
        connLayout.addWidget(self.globalStartButton)
        layout.addLayout(connLayout)
        
        self.logText = QTextEdit()
        self.logText.setReadOnly(True)
        self.logText.setMinimumHeight(150)
        layout.addWidget(QLabel("Log Publicador:"))
        layout.addWidget(self.logText)
        
        self.setLayout(layout)
    
    def addMessage(self):
        widget = MessageConfigWidget(self.next_id, parent=self)
        self.msgLayout.addWidget(widget)
        self.msgWidgets.append(widget)
        self.next_id += 1
    
    def startPublisher(self):
        for widget in self.msgWidgets:
            config = widget.getConfig()
            start_publisher(config["router_url"], config["realm"], config["topic"])
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_html = (f"<p><strong>[{timestamp}] Publicador iniciado</strong><br/>"
                        f"Realm: {config['realm']}<br/>Topic: {config['topic']}<br/>URL: {config['router_url']}</p>")
            appendHtmlLog(self.logText, log_html)
            mode = widget.editorWidget.commonModeCombo.currentText()
            if mode in ["Programado", "Hora de sistema"]:
                try:
                    h, m, s = map(int, widget.editorWidget.commonTimeEdit.text().strip().split(":"))
                    delay = h * 3600 + m * 60 + s
                except:
                    delay = 0
                QTimer.singleShot(delay * 1000, widget.sendMessage)
    
    def sendTestMessage(self):
        for widget in self.msgWidgets:
            config = widget.getConfig()
            send_message_now(config["topic"], {"name": "Mensaje de prueba", "fields": {"valor": 123, "estado": "OK"}}, delay=0)
            formatted = format_json_as_table({"name": "Mensaje de prueba", "fields": {"valor": 123, "estado": "OK"}})
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            appendHtmlLog(self.logText, f"<p><strong>[{timestamp}] Stimulus message</strong><br/>{formatted}</p>")

# ---------------- SubscriberTab ----------------
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
        listLayout.addWidget(QLabel("Topics:"))
        self.topicsList = QListWidget()
        self.topicsList.setSelectionMode(QListWidget.MultiSelection)
        listLayout.addWidget(self.topicsList)
        btnLayout = QVBoxLayout()
        self.loadTopicsButton = QPushButton("Cargar Topics desde archivo")
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
        filepath, _ = QFileDialog.getOpenFileName(self, "Seleccione JSON de Topics", "", "JSON Files (*.json);;All Files (*)")
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{e}")
            return
        topics = data if isinstance(data, list) else data.get("topics", [])
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
        appendHtmlLog(self.logText, f"<p><strong>[{timestamp}] Subscriptor iniciado</strong><br/>Realm: {realm}<br/>Topics: {topics}</p>")
    
    def onMessageArrived(self, content):
        from PyQt5.QtCore import QMetaObject, Qt, Q_ARG
        QMetaObject.invokeMethod(self, "onMessageArrivedMainThread", Qt.QueuedConnection, Q_ARG(dict, content))
    
    @pyqtSlot(dict)
    def onMessageArrivedMainThread(self, content):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_table = format_json_as_table(content)
        appendHtmlLog(self.logText, f"<p><strong>[{timestamp}] Sys answer</strong><br/>{html_table}</p>")

# ---------------- Ventana Principal ----------------
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
