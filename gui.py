from os import path
from sys import argv
import json

from PyQt6.QtWidgets import QCheckBox, QDialog, QSpinBox, QDialogButtonBox, QLabel, QMessageBox, QWidget, QVBoxLayout, \
    QApplication, QMainWindow, QFileDialog, QHBoxLayout, QGridLayout, QAbstractSpinBox, QComboBox, QTabWidget, QFormLayout, \
    QColorDialog, QFrame, QDoubleSpinBox
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

        filters = 'CSV Files (*.csv);;Text Files (*.txt)'
        selectedFilter = settings['default_file_type']

        file_path, filter = QFileDialog.getOpenFileName(
            None, "Choose a filename", start_path,
            filters, selectedFilter)

        settings['recently_opened_folder'] = path.split(file_path)[0]
        with open('./settings.json', 'r+') as settings_json:
            settings_json.write(json.dumps(settings))


        print(file_path, filter)

        self.thermmap = new(file_path, path.split(file_path)[1][:-4])
        self.thermmap.get_data()
        self.thermmap.get_temperatures()

        self.canvas = MplCanvas(self)
        self.plot_toolbar = NavigationToolbar(self.canvas, self)

        list_of_colors = [
            "#E5EEFF",
            "#99B1D7",
            "#294D7F",
            "#287593",
            "#759387",
            "#BFA96D",
            "#B7925E",
            "#B37953",
            "#A64C4C",
            "#9E214B",
            "#460F26"
        ]
        from plotting import luminescence_dt
        self.canvas.axes = luminescence_dt(
            self.thermmap.data,
            self.thermmap.temperatures,
            self.canvas.axes,
            colormap=mpl.colors.LinearSegmentedColormap.from_list(name='', colors=list_of_colors, N=len(self.thermmap.get_temperatures()))
        )

        self.first_click = True
        self.second_click = False
        self.first_line = None
        self.second_line = None
        self.first_line_position = None
        self.second_line_position = None
        self.cid1 = self.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid2 = self.canvas.mpl_connect('pick_event', self.on_pick)
        self.resolution_of_x_data = abs(self.thermmap.data[-1, 0] - self.thermmap.data[-2, 0])

        layout_main = QHBoxLayout()
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.plot_toolbar)
        plot_layout.addWidget(self.canvas)
        layout_main.addLayout(plot_layout)

        layout_wavelengths_chooser = QFormLayout()

        self.first_value_widget = QDoubleSpinBox(
            minimum=self.thermmap.data[0, 0],
            maximum=self.thermmap.data[-1, 0],
            singleStep=self.resolution_of_x_data
        )
        self.first_value_widget.setKeyboardTracking(False)
        self.first_value_widget.setMinimumWidth(150)
        self.first_value_widget.valueChanged.connect(self.on_first_value_changed)
        layout_wavelengths_chooser.addRow(QLabel('Numerator: '), self.first_value_widget)
        self.second_value_widget = QDoubleSpinBox(
            minimum=self.thermmap.data[0, 0],
            maximum=self.thermmap.data[-1, 0],
            singleStep=self.resolution_of_x_data
        )
        self.second_value_widget.setKeyboardTracking(False)
        self.second_value_widget.setMinimumWidth(150)
        self.second_value_widget.valueChanged.connect(self.on_second_value_changed)
        layout_wavelengths_chooser.addRow(QLabel('Denominator: '), self.second_value_widget)

        layout_main.addLayout(layout_wavelengths_chooser)

        widget = QWidget()
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)
        self.canvas.draw()

    def on_click(self, event):
        if event.button == event.button.LEFT:
            if self.first_click:
                self.first_value_widget.setValue(event.xdata)
                self.second_click = True
            elif self.second_click:
                self.second_value_widget.setValue(event.xdata)
                self.second_click = False


    def on_pick(self, event):
        artist = event.artist
        mouse_event = event.mouseevent
        if (mouse_event.button == mouse_event.button.RIGHT) and (artist == self.first_line):
            artist.remove()
            self.first_line = None
            self.first_click = True
            self.first_line_position = None
            self.canvas.draw()
        elif (mouse_event.button == mouse_event.button.RIGHT) and (artist == self.second_line):
            artist.remove()
            self.second_line = None
            self.second_click = True
            self.second_line_position = None
            self.canvas.draw()

    def on_first_value_changed(self, value):
        if self.first_line is not None:
            self.first_line.remove()
        self.first_line = self.canvas.axes.axvline(
            value,
            ymin=0.1,
            ymax=0.9,
            linestyle='--',
            color='#6D597A',
            picker=True
        )
        self.first_line_position = value
        self.first_click = False
        self.canvas.draw()

    def on_second_value_changed(self, value):
        if self.second_line is not None:
            self.second_line.remove()
        self.second_line = self.canvas.axes.axvline(
            value,
            ymin=0.1,
            ymax=0.9,
            linestyle='--',
            color='#E56B6F',
            picker=True
        )
        self.second_line_position = value
        self.second_click = False
        self.canvas.draw()


def run_gui():
        # QApp
        app = QApplication(argv)
        # QWidget (MainWindow)
        window = MainWindow()
        window.show()
        app.exec()


run_gui()
