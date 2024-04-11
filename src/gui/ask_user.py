from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class AskUserDialog(QDialog):
    def __init__(self, title, message):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 300, 100)

        # Layout
        layout = QVBoxLayout()

        # Label
        self.label = QLabel(message)
        layout.addWidget(self.label)

        # Text Edit
        self.lineEdit = QLineEdit()
        layout.addWidget(self.lineEdit)

        # Button
        self.button = QPushButton("OK")
        self.button.clicked.connect(self.on_ok_clicked)
        layout.addWidget(self.button)

        self.setLayout(layout)
    
    def on_ok_clicked(self):
        self.user_input = self.lineEdit.text()
        self.accept()  # Closes the dialog and sets result to Accepted
