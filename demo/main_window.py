import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QLabel, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt
from demo.ui.main_window import Ui_MainWindow
from demo.change_label_dialog import ChangeLabelDialog
from demo.label_flights_dialog import LabelFlightsDialog
from demo.show_clusters_dialog import ShowClustersDialog

class MainWindow(QMainWindow):
    def __init__(self, model, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.model = model

        self.ui.setupUi(self)

        # Create QLabels for the flight labels
        self.setup_labels()

        self.ui.btnStart.setDefault(True)
        try:
            self.model.load_validation("./validation.csv")
        except:
            pass

        # Connect buttons
        self.ui.btnChangeLabels.clicked.connect(self.on_change_labels_clicked)
        self.ui.btnStart.clicked.connect(self.on_start_clicked)
        self.ui.btnLabelMore.clicked.connect(self.on_label_more_clicked)
        self.ui.btnShowClusters.clicked.connect(self.on_show_clusters_clicked)
        self.ui.btnSave.clicked.connect(self.on_save_clicked)
        self.ui.btnLoad.clicked.connect(self.on_load_clicked)

    def on_save_clicked(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save training data", filter="CSV Files (*.csv)")

        # No input, nothing to do
        if not filename:
            return

        # Make sure we have a .csv extension
        if not filename.endswith(".csv"):
            filename += ".csv"

        self.model.save_to_csv(filename)


    def on_load_clicked(self):

        # TODO: Warning of reset

        filename, _ = QFileDialog.getOpenFileName(self, "Load training data", filter="CSV Files (*.csv)")

        # No input, notothing to do
        if not filename:
            return

        if self.model.load_from_csv(filename):
            self.setup_labels()
            self.ui.btnStart.setText("Stop")
            self.ui.btnLabelMore.setEnabled(True)
            self.ui.btnShowClusters.setEnabled(True)
            self.ui.btnChangeLabels.setEnabled(False)
            self.ui.btnSave.setEnabled(True)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Enter or QKeyEvent.key() == Qt.Key_Return:
            if self.ui.btnLabelMore.isEnabled():
                self.ui.btnLabelMore.click()
            else:
                if self.ui.btnStart.isDefault():
                    self.ui.btnStart.click()
                else:
                    self.ui.btnShowClusters.click()
        else:
            super(MainWindow, self).keyPressEvent(QKeyEvent)

    def setup_labels(self):
        # First, clear all current labels
        while self.ui.layoutLabels.count():
            item = self.ui.layoutLabels.takeAt(0)
            item.widget().deleteLater()

        # Now, set it with the model labels
        if not self.model.get_label_names():
            self.ui.layoutLabels.addWidget(QLabel("-- None --", parent=self))
            self.ui.btnStart.setEnabled(False)
        else:
            for label in self.model.get_label_names():
                self.ui.layoutLabels.addWidget(QLabel(label, parent=self))
            self.ui.btnStart.setEnabled(True)

    def on_change_labels_clicked(self):
        change_dialog = ChangeLabelDialog(self.model.get_label_names())

        if self.ui.btnShowClusters.isEnabled():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Are you sure?")
            msg.setInformativeText("Changing the labels will restart the "
                                   "clustering process, you will loose all"
                                   " work so far. Do you want to continue?")
            msg.setWindowTitle("Restart clustering")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            if msg.exec_() == QMessageBox.No:
                return
            self.ui.btnSave.setEnabled(False)

        if change_dialog.exec_():
            self.model.set_label_names(change_dialog.get_labels())
            self.setup_labels()
            self.ui.btnShowClusters.setEnabled(False)

    def on_start_clicked(self):
        if self.ui.btnStart.text() == "Start":
            centroids = self.model.get_centroids()
            dialog = LabelFlightsDialog(centroids, self.model.get_label_names(), ensure_two=True)
            if dialog.exec_():
                self.model.restart()
                centroid_labels = dialog.get_labels()
                self.model.label_flights([(c, l) for c, l in  zip(centroids, centroid_labels)])

                self.ui.btnStart.setText("Stop")
                self.ui.btnLabelMore.setEnabled(True)
                self.ui.btnShowClusters.setEnabled(True)
                self.ui.btnChangeLabels.setEnabled(False)
                self.ui.btnSave.setEnabled(True)

                self.ui.btnStart.setDefault(False)
                self.ui.btnShowClusters.setDefault(False)
                self.ui.btnLabelMore.setDefault(True)

                self.update_labels()
        else:
            self.ui.btnStart.setText("Start")
            self.ui.btnLabelMore.setEnabled(False)
            self.ui.btnShowClusters.setEnabled(True)
            self.ui.btnChangeLabels.setEnabled(True)

            self.ui.btnLabelMore.setDefault(False)
            self.ui.btnShowClusters.setDefault(True)

    def on_label_more_clicked(self):
        flights_to_label = self.model.get_flights_to_label()
        dialog = LabelFlightsDialog(flights_to_label, self.model.get_label_names())
        if dialog.exec_():
            labels = dialog.get_labels()
            self.model.label_flights([(f, l) for f, l in zip(flights_to_label, labels)])
            self.update_labels()

    def on_show_clusters_clicked(self):
        training_filename, training_label = self.model.get_labeled_training()
        test_filename, test_label = self.model.get_labeled_test()

        file_names = list(test_filename) + list(training_filename)
        labels = list(test_label) + list(training_label)

        dialog = ShowClustersDialog(file_names, labels, self.model.get_label_names())
        dialog.exec_()

    def update_labels(self):
        distrib = self.model.get_label_distribution()

        for i, (name, amount) in enumerate(zip(self.model.get_label_names(), distrib)):
            self.ui.layoutLabels.itemAt(i).widget().setText("{} ({})".format(name, amount))
