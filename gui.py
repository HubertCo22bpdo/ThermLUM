from os import path
from sys import argv
import json

from PyQt6.QtWidgets import QCheckBox, QDialog, QSpinBox, QDialogButtonBox, QLabel, QMessageBox, QWidget, QVBoxLayout, \
    QApplication, QMainWindow, QFileDialog, QHBoxLayout, QGridLayout, QAbstractSpinBox, QComboBox, QTabWidget, \
    QFormLayout, \
    QColorDialog, QFrame, QDoubleSpinBox, QPushButton, QStackedLayout
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
from utilities import quantization_to_resolution
from plotting import luminescence_dt

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

        self.thermmap = new(file_path, path.split(file_path)[1][:-4])
        self.thermmap.get_data()
        self.thermmap.get_temperatures()

        self.canvas = MplCanvas(self)
        self.plot_toolbar = NavigationToolbar(self.canvas, self)

        self.normalized_canvas = MplCanvas(self)
        self.normalized_plot_toolbar = NavigationToolbar(self.normalized_canvas, self)

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

        self.canvas.axes = luminescence_dt(
            self.thermmap.data,
            self.thermmap.temperatures,
            self.canvas.axes,
            colormap=mpl.colors.LinearSegmentedColormap.from_list(name='', colors=list_of_colors,
                                                                  N=len(self.thermmap.temperatures))
        )

        self.first_click = True
        self.second_click = False
        self.first_line = None
        self.second_line = None
        self.first_line_position = None
        self.second_line_position = None
        self.normalization_position = None
        self.normalization_line = None
        self.resolution_of_x_data = abs(self.thermmap.data[-1, 0] - self.thermmap.data[-2, 0])

        self.cid1 = self.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid2 = self.canvas.mpl_connect('pick_event', self.on_pick)

        layout_main = QHBoxLayout()
        self.layout_plots = QStackedLayout()
        layout_plot = QVBoxLayout()
        layout_plot.addWidget(self.plot_toolbar)
        layout_plot.addWidget(self.canvas)

        layout_normalized_plot = QVBoxLayout()
        layout_normalized_plot.addWidget(self.normalized_plot_toolbar)
        layout_normalized_plot.addWidget(self.normalized_canvas)

        container1 = QWidget()
        container1.setLayout(layout_plot)
        container2 = QWidget()
        container2.setLayout(layout_normalized_plot)
        self.layout_plots.addWidget(container1)
        self.layout_plots.addWidget(container2)
        layout_main.addLayout(self.layout_plots)
        layout_ribbon = QVBoxLayout()

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
        layout_ribbon.addLayout(layout_wavelengths_chooser)

        layout_normalization_widgets = QGridLayout()
        self.normalization_value_widget = QDoubleSpinBox(
            minimum=self.thermmap.data[0, 0],
            maximum=self.thermmap.data[-1, 0],
            singleStep=self.resolution_of_x_data
        )
        self.normalization_value_widget.setKeyboardTracking(False)
        self.normalization_value_widget.setMinimumWidth(150)
        self.normalization_value_widget.valueChanged.connect(self.on_normalization_value_changed)
        layout_normalization_widgets.addWidget(QLabel('Normalize to:'), 0, 0)
        layout_normalization_widgets.addWidget(self.normalization_value_widget, 0, 1)
        self.normalization_button = QPushButton('Normalize')
        self.normalization_button.setCheckable(True)
        self.normalization_button.clicked.connect(self.on_normalization_button_clicked)
        layout_normalization_widgets.addWidget(self.normalization_button, 1, 0, 1, 2)
        layout_ribbon.addLayout(layout_normalization_widgets)

        layout_main.addLayout(layout_ribbon)

        widget = QWidget()
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)
        self.canvas.draw()

    def on_click(self, event):
        if type(event.button) is str:
            return
        else:
            value = quantization_to_resolution(event.xdata, self.resolution_of_x_data)
        if event.button == event.button.LEFT:
            if self.first_click:
                self.first_value_widget.setValue(value)
                self.second_click = True
            elif self.second_click:
                self.second_value_widget.setValue(value)
                self.second_click = False
        elif event.button == event.button.MIDDLE:
            self.normalization_value_widget.setValue(value)

    def on_pick(self, event):
        if type(event.mouseevent.button) is str:
            return
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
        new_value = quantization_to_resolution(value, self.resolution_of_x_data)
        if new_value != value:
            self.first_value_widget.setValue(new_value)
            return
        if self.first_line is not None:
            self.first_line.remove()
        self.first_line = self.canvas.axes.axvline(
            value,
            ymin=0.02,
            ymax=0.9,
            linestyle='--',
            color='#6D597A',
            picker=True,
            zorder=0
        )
        self.first_line_position = value
        self.first_click = False
        self.canvas.draw()

    def on_second_value_changed(self, value):
        new_value = quantization_to_resolution(value, self.resolution_of_x_data)
        if new_value != value:
            self.second_value_widget.setValue(new_value)
            return
        if self.second_line is not None:
            self.second_line.remove()
        self.second_line = self.canvas.axes.axvline(
            value,
            ymin=0.02,
            ymax=0.9,
            linestyle='--',
            color='#E56B6F',
            picker=True,
            zorder=0
        )
        self.second_line_position = value
        self.second_click = False
        self.canvas.draw()

    def on_normalization_value_changed(self, value):
        new_value = quantization_to_resolution(value, self.resolution_of_x_data)
        if new_value != value:
            self.normalization_value_widget.setValue(new_value)
            return
        if self.normalization_line is not None:
            self.normalization_line.remove()
        self.normalization_line = self.canvas.axes.axvline(
            value,
            ymin=0,
            ymax=1,
            linestyle='-',
            color='#ffd656',
            picker=True,
            zorder=0
        )
        self.normalization_position = value
        self.canvas.draw()

    def on_normalization_button_clicked(self, checked):
        if self.normalization_position is not None:
            if checked:
                self.normalization_button.setText('Denormalize')
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
                self.normalized_canvas.axes.cla()
                self.normalized_canvas.axes = luminescence_dt(
                    self.thermmap.normalize(self.normalization_position),
                    self.thermmap.temperatures,
                    self.normalized_canvas.axes,
                    colormap=mpl.colors.LinearSegmentedColormap.from_list(
                        name='',
                        colors=list_of_colors,
                        N=len(self.thermmap.temperatures)
                    ))
                self.normalized_canvas.draw()
                self.layout_plots.setCurrentIndex(1)
            else:
                self.normalization_button.setText('Normalize')
                self.layout_plots.setCurrentIndex(0)
        else:
            self.normalization_button.setChecked(False)


def run_gui():
    # QApp
    app = QApplication(argv)
    # QWidget (MainWindow)
    window = MainWindow()
    window.show()
    app.exec()


run_gui()
