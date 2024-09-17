from os import path
from sys import argv
import json

from PyQt6.QtWidgets import QCheckBox, QDialog, QSpinBox, QDialogButtonBox, QLabel, QMessageBox, QWidget, QVBoxLayout, \
    QApplication, QMainWindow, QFileDialog, QHBoxLayout, QGridLayout, QAbstractSpinBox, QComboBox, QTabWidget, QFormLayout, \
    QColorDialog
from PyQt6.QtGui import QAction, QCloseEvent, QIcon, QFont, QColor
from PyQt6.QtCore import QSize, Qt, pyqtSignal

import matplotlib as mpl  # import matplotlib after PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qtagg import (
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.pyplot import close

from creation import new

mpl.use("QtAgg")

with open('./settings.json', 'r') as settings_json:
    settings = json.load(settings_json)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=150):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        start_path = path.expanduser(settings['recently_opened_folder'])
        sorted_filetypes = [('CSV', '.csv'), ('Text Files', '.txt')]
        default_file_type = settings['default_file_type']

        filters = 'CSV Files (*.csv);;Text Files (*.txt)'
        selectedFilter = None

        file_path, filter = QFileDialog.getOpenFileName(
            None, "Choose a filename", start_path,
            filters, selectedFilter)

        print(file_path, filter)

        self.thermmap = new(file_path, path.split(file_path)[1][:-4])

        self.canvas = MplCanvas(self)
        self.plot_toolbar = NavigationToolbar(self.canvas, self)

        list_of_colors = [
            "#ff0000",
            "#ff8700",
            "#ffd300",
            "#deff0a",
            "#a1ff0a",
            "#0aff99",
            "#0aefff",
            "#147df5",
            "#580aff",
            "#be0aff",
        ]
        from plotting import luminescence_dt
        self.canvas.axes = luminescence_dt(self.thermmap.get_data(), self.thermmap.get_temperatures(), self.canvas.axes, colormap=mpl.colors.LinearSegmentedColormap.from_list(name='', colors=list_of_colors, N=len(self.thermmap.get_temperatures())))

        layout_main = QVBoxLayout()
        layout_main.addWidget(self.plot_toolbar)
        layout_ribbons = QHBoxLayout()
        layout_ribbons.addWidget(self.canvas)
        layout_main.addLayout(layout_ribbons)

        widget = QWidget()
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)
        self.canvas.draw()


def run_gui():
        # QApp
        app = QApplication(argv)
        # QWidget (MainWindow)
        window = MainWindow()
        window.show()
        app.exec()


run_gui()
