from PyQt5.QtWidgets import QDialog, QListWidgetItem, QMessageBox, QInputDialog
from demo.ui.change_label_dialog import Ui_ChangeLabelDialog


class ChangeLabelDialog(QDialog):
    def __init__(self, labels, parent=None):
        super(ChangeLabelDialog, self).__init__(parent)
        self.ui = Ui_ChangeLabelDialog()
        self.labels = labels[:]

        self.ui.setupUi(self)

        # Set up labels
        for label in self.labels:
            item = QListWidgetItem(label)
            self.ui.listWidget.addItem(item)

        # Connect signals and slots
        self.ui.btnAdd.clicked.connect(self.on_add_label_clicked)
        self.ui.btnRename.clicked.connect(self.on_rename_label_clicked)
        self.ui.btnRemove.clicked.connect(self.on_remove_label_clicked)
        self.ui.listWidget.itemSelectionChanged.connect(self.on_item_selection_changed)
        self.ui.buttonBox.accepted.connect(self.on_ok_clicked)

    def on_ok_clicked(self):
        if self.ui.listWidget.count() >= 2:
            self.accept()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)

            msg.setText("Too few labels")
            msg.setInformativeText("You must specify at least 2 labels.")
            msg.setWindowTitle("Too few labels")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def on_item_selection_changed(self):
        if self.ui.listWidget.currentRow() >= 0:
            self.ui.btnRemove.setEnabled(True)
            self.ui.btnRename.setEnabled(True)
        else:
            self.ui.btnRemove.setEnabled(False)
            self.ui.btnRename.setEnabled(False)

    def on_add_label_clicked(self):
        text, ok = QInputDialog.getText(self, "Add Label...", "Enter the new label:")
        if ok and text:
            self.ui.listWidget.addItem(text)
            self.labels.append(text)

    def on_rename_label_clicked(self):
        row = self.ui.listWidget.currentRow()
        if 0 <= row < len(self.labels):
            text, ok = QInputDialog.getText(self, "Rename Label...", "Enter the new label name:",
                                            text=self.labels[row])
            if ok and text:
                self.ui.listWidget.item(row).setText(text)
                self.labels[row] = text

    def on_remove_label_clicked(self):
        row = self.ui.listWidget.currentRow()
        if 0 <= row < len(self.labels):
            del self.labels[row]
            self.ui.listWidget.takeItem(row)

    def get_labels(self):
        return self.labels[:]

