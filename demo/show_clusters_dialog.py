import matplotlib as mpl
mpl.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QDialog, QButtonGroup, QVBoxLayout, QRadioButton, QMessageBox

from demo.ui.show_clusters_dialog import Ui_ShowClustersDialog
from util.util import plot_flights

class ShowClustersDialog(QDialog):
    def __init__(self, filenames, labels, label_names, parent=None):
        super(ShowClustersDialog, self).__init__(parent)
        self.ui = Ui_ShowClustersDialog()
        self.filenames = filenames
        self.label_names = label_names
        self.labels = labels
        self.current_flight = 0
        self.current_cluster = 0

        # Shape of plots
        self.grid = (3, 2)
        self.num_flights = self.grid[0] * self.grid[1]

        self.ui.setupUi(self)

        # Create layout for canvas
        self.ui.widget.setLayout(QVBoxLayout())

        # Separate flights per cluster
        self.clusters = [[] for _ in label_names]
        for fn, lbl in zip(filenames, labels):
            self.clusters[lbl].append(fn)

        # Connect buttons
        self.ui.btnPrevCluster.clicked.connect(self.on_prev_cluster)
        self.ui.btnNextCluster.clicked.connect(self.on_next_cluster)
        self.ui.btnPrevPage.clicked.connect(self.on_prev_page)
        self.ui.btnNextPage.clicked.connect(self.on_next_page)

        self.update_screen()

    def on_prev_cluster(self):
        self.current_cluster -= 1
        self.current_flight = 0
        self.update_screen()

    def on_next_cluster(self):
        self.current_cluster += 1
        self.current_flight = 0
        self.update_screen()

    def on_prev_page(self):
        self.current_flight = max(0, self.current_flight - self.num_flights)
        self.update_screen()

    def on_next_page(self):
        self.current_flight = self.current_flight + self.num_flights
        self.update_screen()

    def update_screen(self):
        self.ui.lblCluster.setText("Cluster label: " + self.label_names[self.current_cluster])
        self.ui.lblWhich.setText("Cluster {} of {}\nShowing flights {} to {} of {}".format(
            self.current_cluster + 1,
            len(self.label_names),
            min(self.current_flight + 1, len(self.clusters[self.current_cluster])),
            min(self.current_flight + self.num_flights + 1, len(self.clusters[self.current_cluster])),
            len(self.clusters[self.current_cluster])
        ))

        # Update buttons
        if self.current_cluster == (len(self.label_names) - 1):
            self.ui.btnNextCluster.setEnabled(False)
        else:
            self.ui.btnNextCluster.setEnabled(True)

        if self.current_cluster == 0:
            self.ui.btnPrevCluster.setEnabled(False)
        else:
            self.ui.btnPrevCluster.setEnabled(True)

        if self.current_flight + self.num_flights >= len(self.clusters[self.current_cluster]):
            self.ui.btnNextPage.setEnabled(False)
        else:
            self.ui.btnNextPage.setEnabled(True)

        if self.current_flight == 0:
            self.ui.btnPrevPage.setEnabled(False)
        else:
            self.ui.btnPrevPage.setEnabled(True)

        # Plot the flights
        idx_start = self.current_flight
        idx_end = self.current_flight + self.num_flights
        flights_to_plot = self.clusters[self.current_cluster][idx_start:idx_end]
        figsize = (self.ui.widget.size().width(), self.ui.widget.size().height())
        fig = plot_flights(flights_to_plot, self.grid, figsize)

        # Display the flights
        canvas = FigureCanvas(fig)
        layout = self.ui.widget.layout()
        for i in range(layout.count()):
            layout.itemAt(i).widget().deleteLater()
        layout.addWidget(canvas)
