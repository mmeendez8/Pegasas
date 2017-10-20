#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
sys.path.insert(0, os.path.abspath("../../"))

import numpy as np
import sys
from PyQt5.QtWidgets import QApplication
from demo.main_window import MainWindow
from active_learning import ActiveLearning

np.random.seed(26)

# ==========================

LABELS = ["Pattern Work", "Local Maneuvers", "Cross-Country"]
HOW_MANY = 10

# ==========================

# -------------------------- #

if __name__ == '__main__':
    model = ActiveLearning(
        labels=LABELS,
        feature_file="~/Desktop/Thesis/Classification/train_data_AltGPS_new3.csv",
        data_dir="~/Desktop/Thesis/Data",
        amount_to_label=3
    )

    # Start application
    app = QApplication(sys.argv)
    win = MainWindow(model)
    win.show()
    sys.exit(app.exec_())

# ==========================

# import matplotlib
# # matplotlib.rcParams['backend.qt4']='PySide'
# matplotlib.use('Qt5Agg')
#
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure

# # generate the plot
# fig = Figure(figsize=(600,600), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
# ax = fig.add_subplot(111)
# ax.plot([0,1])
# # generate the canvas to display the plot
# canvas = FigureCanvas(fig)
