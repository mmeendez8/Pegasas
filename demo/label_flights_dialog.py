import matplotlib as mpl
mpl.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QDialog, QButtonGroup, QVBoxLayout, QRadioButton, QMessageBox
from PyQt5.QtCore import Qt
import numpy as np

from demo.ui.label_flights_dialog import Ui_LabelFlightsDialog
from util.util import plot_flight_to_label

class LabelFlightsDialog(QDialog):
    def __init__(self, filenames, labels, parent=None, ensure_two=False):
        super(LabelFlightsDialog, self).__init__(parent)
        self.ui = Ui_LabelFlightsDialog()
        self.filenames = filenames
        self.label_names = labels
        self.labels = [0 for _ in filenames]
        self.seen = [False for _ in filenames]
        self.current_flight = 0
        self.ensure_two = ensure_two

        self.ui.setupUi(self)

        # Create layout for widgets
        self.ui.widgetLarge.setLayout(QVBoxLayout())
        self.ui.widgetSmall.setLayout(QVBoxLayout())

        # Create an array of radio buttons and lay them out in the Group Box
        label_rbns = [QRadioButton("{}: {}".format(i+1, label)) for i, label in enumerate(self.label_names)]
        button_layout = QVBoxLayout()
        self.ui.button_group = QButtonGroup()
        for i, btn in enumerate(label_rbns):
            button_layout.addWidget(btn)
            self.ui.button_group.addButton(btn, i)
            btn.clicked.connect(self.on_select_label)
        self.ui.groupBox.setLayout(button_layout)

        # Connect signals
        self.ui.btnNext.clicked.connect(self.on_next_clicked)
        self.ui.btnPrev.clicked.connect(self.on_prev_clicked)

        # Update the interface with the current flight
        self.update_current_flight()

        # Grab keyboard to detect arrow key
        self.grabKeyboard()

    def keyPressEvent(self, QKeyEvent):
        key = QKeyEvent.key()
        if Qt.Key_1 <= key <= Qt.Key_9:
            which = key - Qt.Key_1
            button = self.ui.button_group.button(which)
            if button:
                button.click()

        elif key == Qt.Key_Left:
            self.ui.btnPrev.click()
        elif key == Qt.Key_Right:
            self.ui.btnNext.click()
        else:
            super(LabelFlightsDialog, self).keyPressEvent(QKeyEvent)

    def get_labels(self):
        return self.labels[:]
        # return [i % 2 for i in range(len(self.filenames))]

    def on_select_label(self):
        self.labels[self.current_flight] = self.ui.button_group.checkedId()

    def on_next_clicked(self):
        self.current_flight += 1
        self.update_current_flight()

    def on_prev_clicked(self):
        self.current_flight -= 1
        self.update_current_flight()

    def accept(self):
        if self.ensure_two and len(set(self.labels)) < 2:
            self.releaseKeyboard()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)

            msg.setText("Not enough examples with different labels")
            msg.setInformativeText("We need examples of more than just one label. At least one flight must have a different label.")
            msg.setWindowTitle("Not enough examples")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            self.grabKeyboard()
        elif not np.all(self.seen):
                self.releaseKeyboard()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)

                msg.setText("There are still more flights")
                msg.setInformativeText("You did not go through all the flights. The default label '{}' will be applied to the unseen flights. Do you want to continue?".format(self.label_names[0]))
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                code = msg.exec_()
                self.grabKeyboard()
                if code == QMessageBox.Yes:
                    super(LabelFlightsDialog, self).accept()
        else:
            super(LabelFlightsDialog, self).accept()

    def update_current_flight(self):
        # Update label with number of flights and filename
        self.ui.lblWhich.setText("Flight {} of {}".format(self.current_flight + 1, len(self.filenames)))
        self.ui.lblFilename.setText(self.filenames[self.current_flight])

        # Mark the current label
        self.ui.button_group.button(self.labels[self.current_flight]).setChecked(True)

        # Enable/Disable the navigation buttons as needed
        self.ui.btnPrev.setEnabled(self.current_flight > 0)
        self.ui.btnNext.setEnabled(self.current_flight < len(self.filenames) - 1)

        # Plot the flight
        size_large = (self.ui.widgetLarge.size().width(), self.ui.widgetLarge.size().height())
        size_small = (self.ui.widgetSmall.size().width(), self.ui.widgetSmall.size().height())
        fig_ts, fig_lat_lon = plot_flight_to_label(
            self.filenames[self.current_flight],
            size_large,
            size_small
        )

        # Display Time Series
        canvas = FigureCanvas(fig_ts)
        layout = self.ui.widgetLarge.layout()
        for i in range(layout.count()):
            layout.itemAt(i).widget().deleteLater()
        layout.addWidget(canvas)

        # Display Lat/Lon
        canvas = FigureCanvas(fig_lat_lon)
        layout = self.ui.widgetSmall.layout()
        for i in range(layout.count()):
            layout.itemAt(i).widget().deleteLater()
        layout.addWidget(canvas)

        self.seen[self.current_flight] = True
