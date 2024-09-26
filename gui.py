from os import path
from sys import argv
import json
from inspect import signature
from functools import partial

from PyQt6.QtWidgets import QCheckBox, QDialog, QSpinBox, QDialogButtonBox, QLabel, QMessageBox, QWidget, QVBoxLayout, \
    QApplication, QMainWindow, QFileDialog, QHBoxLayout, QGridLayout, QAbstractSpinBox, QComboBox, QTabWidget, \
    QFormLayout, \
    QColorDialog, QFrame, QDoubleSpinBox, QPushButton, QStackedLayout, QSizePolicy
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
from fitting_functions import dict_of_fitting_functions, dict_of_fitting_limits

mpl.use("QtAgg")

with open('./settings.json', 'r') as settings_json:
    settings = json.load(settings_json)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=settings['plot_width'], height=settings['plot_height'],
                 dpi=settings['plot_dpi']):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.subplots_adjust(bottom=0.15, left=0.15)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class OutMplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=settings['plot_width'], height=settings['plot_height'],
                 dpi=settings['plot_dpi']):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.subplots_adjust(bottom=0.15, left=0.15)
        fig.tight_layout()
        self.parameter_axes = fig.add_subplot(3, 1, (1, 2))
        self.sensitivity_axes = self.parameter_axes.twinx()
        self.error_axes = fig.add_subplot(3, 1, 3)
        super(OutMplCanvas, self).__init__(fig)


class NumberedDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, *args, index, **kwargs):
        self.index = index
        super().__init__(*args, **kwargs)


class NumberedPushButton(QPushButton):
    def __init__(self, *args, index, **kwargs):
        self.index = index
        super().__init__(*args, **kwargs)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        start_path = path.expanduser(settings['recently_opened_folder'])

        filters = 'CSV Files (*.csv);;Text Files (*.txt);;Data Files (*.dat)'
        selectedFilter = settings['default_file_type']

        file_path, filter = QFileDialog.getOpenFileName(
            None, "Choose a filename", start_path,
            filters, selectedFilter)

        settings['recently_opened_folder'] = path.split(file_path)[0]
        with open('./settings.json', 'r+') as settings_json:
            settings_json.write(json.dumps(settings, indent=0))

        self.thermmap = new(file_path, path.split(file_path)[1][:-4])
        self.thermmap.get_data()
        self.thermmap.get_temperatures()

        self.canvas = MplCanvas(self)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.plot_toolbar = NavigationToolbar(self.canvas, self)

        self.normalized_canvas = MplCanvas(self)
        self.normalized_plot_toolbar = NavigationToolbar(self.normalized_canvas, self)

        self.fitting_canvas = None
        self.fitting_toolbar = None

        list_of_colors = settings["plot_colormap"]

        self.canvas.axes = luminescence_dt(
            self.thermmap.data,
            self.thermmap.temperatures,
            self.canvas.axes,
            colormap=mpl.colors.LinearSegmentedColormap.from_list(
                name='',
                colors=list_of_colors,
                N=len(self.thermmap.temperatures))
        )

        self.first_click = True
        self.second_click = False
        self.first_line = None
        self.second_line = None
        self.normalized_first_line = None
        self.normalized_second_line = None
        self.normalized_normalization_line = None
        self.first_line_position = None
        self.second_line_position = None
        self.normalization_position = None
        self.normalization_line = None
        self.resolution_of_x_data = abs(self.thermmap.data[-1, 0] - self.thermmap.data[-2, 0])

        self.cid1 = self.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid2 = self.canvas.mpl_connect('pick_event', self.on_pick)
        self.cid3 = self.normalized_canvas.mpl_connect('button_press_event', self.on_click)
        self.cid2 = self.normalized_canvas.mpl_connect('pick_event', self.on_pick)

        self.layout_main = QHBoxLayout()
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
        self.layout_main.addLayout(self.layout_plots)
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

        self.create_thermometric_parameter_button = QPushButton('Create thermometric parameter')
        self.create_thermometric_parameter_button.clicked.connect(self.create_thermometric_parameter)
        layout_ribbon.addWidget(self.create_thermometric_parameter_button)

        self.fitting_functions_widget = QComboBox()
        self.fitting_functions_layout = QStackedLayout()
        fitting_function_index = 0
        fitting_layouts = []
        fitting_containers = []
        fitting_buttons = []
        fitting_boxes = []
        self.blocked_parameters = []
        self.bounds_on_parameters = []
        self.initial_parameters = []
        for name, function in dict_of_fitting_functions.items():
            self.bounds_on_parameters.append(dict_of_fitting_limits[name])
            self.fitting_functions_widget.addItem(name)
            temporary_layout = QGridLayout()
            temporary_container = QWidget()
            fitting_buttons.append([])
            fitting_boxes.append([])
            self.blocked_parameters.append([])
            self.initial_parameters.append([])
            for index, argument in enumerate(signature(function).parameters):
                temporary_layout.addWidget(QLabel(f'{argument}'), index, 0)
                self.blocked_parameters[fitting_function_index].append(False)
                self.initial_parameters[fitting_function_index].append(None)
                temporary_spinbox = NumberedDoubleSpinBox(index=index)
                temporary_spinbox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
                temporary_spinbox.setKeyboardTracking(False)
                temporary_spinbox.setMinimumWidth(80)
                temporary_spinbox.setMaximum(1e18)
                temporary_spinbox.setDecimals(18)
                fitting_boxes[fitting_function_index].append(temporary_spinbox)
                fitting_boxes[fitting_function_index][index].valueChanged.connect(partial(self.on_set_starting_parameter, box=fitting_boxes[fitting_function_index][index], index=index ))
                temporary_layout.addWidget(fitting_boxes[fitting_function_index][index], index, 1)
                temporary_button = NumberedPushButton('Block', index=index)
                temporary_button.setCheckable(True)
                fitting_buttons[fitting_function_index].append(temporary_button)
                fitting_buttons[fitting_function_index][index].clicked.connect(partial(self.on_block_parameter, button=fitting_buttons[fitting_function_index][index], index=index))
                temporary_layout.addWidget(fitting_buttons[fitting_function_index][index], index, 2)


            temporary_container.setLayout(temporary_layout)
            fitting_layouts.append(temporary_layout)
            fitting_containers.append(temporary_container)
            self.fitting_functions_layout.addWidget(fitting_containers[fitting_function_index])
            fitting_function_index += 1

        self.fitting_functions_widget.currentIndexChanged.connect(self.on_fitting_function_changed)
        layout_ribbon.addWidget(self.fitting_functions_widget)
        layout_ribbon.addLayout(self.fitting_functions_layout)

        self.layout_main.addLayout(layout_ribbon)

        widget = QWidget()
        widget.setLayout(self.layout_main)
        self.setCentralWidget(widget)
        self.canvas.draw()
        self.move(0, 0)

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
        if (mouse_event.button == mouse_event.button.RIGHT) and (
                artist == self.first_line or artist == self.normalized_first_line):
            if self.normalized_first_line is not None:
                self.normalized_first_line.remove()
                self.normalized_first_line = None
            if self.first_line is not None:
                self.first_line.remove()
                self.first_line = None
            self.first_click = True
            self.first_line_position = None
            self.canvas.draw()
            self.normalized_canvas.draw()
        elif (mouse_event.button == mouse_event.button.RIGHT) and (
                artist == self.second_line or artist == self.normalized_second_line):
            if self.normalized_second_line is not None:
                self.normalized_second_line.remove()
                self.normalized_second_line = None
            if self.second_line is not None:
                self.second_line.remove()
                self.second_line = None
            self.second_click = True
            self.second_line_position = None
            self.canvas.draw()
            self.normalized_canvas.draw()

    def on_first_value_changed(self, value):
        new_value = quantization_to_resolution(value, self.resolution_of_x_data)
        if new_value != value:
            self.first_value_widget.setValue(new_value)
            return
        if self.first_line is not None:
            self.first_line.remove()
        if self.normalized_first_line is not None:
            self.normalized_first_line.remove()
        self.first_line = self.canvas.axes.axvline(
            value,
            ymin=0.02,
            ymax=0.9,
            linestyle='--',
            color='#6D597A',
            picker=True,
            zorder=0
        )
        self.normalized_first_line = self.normalized_canvas.axes.axvline(
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
        self.normalized_canvas.draw()

    def on_second_value_changed(self, value):
        new_value = quantization_to_resolution(value, self.resolution_of_x_data)
        if new_value != value:
            self.second_value_widget.setValue(new_value)
            return
        if self.second_line is not None:
            self.second_line.remove()
        if self.normalized_second_line is not None:
            self.normalized_second_line.remove()
        self.second_line = self.canvas.axes.axvline(
            value,
            ymin=0.02,
            ymax=0.9,
            linestyle='--',
            color='#E56B6F',
            picker=True,
            zorder=0
        )
        self.normalized_second_line = self.normalized_canvas.axes.axvline(
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
        self.normalized_canvas.draw()

    def on_normalization_value_changed(self, value):
        new_value = quantization_to_resolution(value, self.resolution_of_x_data)
        if new_value != value:
            self.normalization_value_widget.setValue(new_value)
            return
        if self.normalization_line is not None:
            self.normalization_line.remove()
        if self.normalized_normalization_line is not None:
            self.normalized_normalization_line.remove()
        self.normalization_line = self.canvas.axes.axvline(
            value,
            ymin=0,
            ymax=1,
            linestyle='-',
            color='#ffd656',
            picker=True,
            zorder=0
        )
        self.normalized_normalization_line = self.normalized_canvas.axes.axvline(
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
        self.normalized_canvas.draw()

    def on_normalization_button_clicked(self, checked):
        if self.normalization_position is not None:
            if checked:
                self.normalization_button.setText('Denormalize')
                list_of_colors = settings["plot_colormap"]
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
                if self.first_line_position is not None:
                    self.normalized_first_line = self.normalized_canvas.axes.axvline(
                        self.first_line_position,
                        ymin=0.02,
                        ymax=0.9,
                        linestyle='--',
                        color='#6D597A',
                        picker=True,
                        zorder=0
                    )
                if self.second_line_position is not None:
                    self.normalized_second_line = self.normalized_canvas.axes.axvline(
                        self.second_line_position,
                        ymin=0.02,
                        ymax=0.9,
                        linestyle='--',
                        color='#E56B6F',
                        picker=True,
                        zorder=0
                    )
                self.normalized_normalization_line = self.normalized_canvas.axes.axvline(
                    self.normalization_position,
                    ymin=0,
                    ymax=1,
                    linestyle='-',
                    color='#ffd656',
                    picker=True,
                    zorder=0
                )
                self.normalized_canvas.draw()
                self.layout_plots.setCurrentIndex(1)
            else:
                self.normalization_button.setText('Normalize')
                self.layout_plots.setCurrentIndex(0)
        else:
            self.normalization_button.setChecked(False)

    def create_thermometric_parameter(self):
        if self.first_line_position is None or self.second_line_position is None:
            return
        if self.fitting_canvas is None:
            self.fitting_canvas = OutMplCanvas()
            self.fitting_canvas.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            self.fitting_toolbar = NavigationToolbar(self.fitting_canvas, self)
            layout_fitting = QVBoxLayout()
            layout_fitting.addWidget(self.fitting_toolbar)
            layout_fitting.addWidget(self.fitting_canvas)
            self.layout_main.addLayout(layout_fitting)

        self.thermometric_parameter = self.thermmap.get_row_of_ydata(
            self.first_line_position) / self.thermmap.get_row_of_ydata(self.second_line_position)
        self.fitting_canvas.parameter_axes.cla()
        self.fitting_canvas.parameter_axes.scatter(
            self.thermmap.temperatures,
            self.thermometric_parameter,
            color='#6D597A',
            marker='o',
            facecolors='none'
        )
        self.fitting_canvas.parameter_axes.set_ylabel('Intensity ratio', color='#6D597A')
        self.fitting_canvas.parameter_axes.tick_params(axis='y', labelcolor='#6D597A')
        self.fitting_canvas.draw()
        # TODO: I will use scipy.optimisation.function_fit here
        pass

    def on_fitting_function_changed(self, index):
        self.fitting_functions_layout.setCurrentIndex(index)

    def on_set_starting_parameter(self, box, index):
        value = box.value()

    def on_block_parameter(self, button, index):
        checked = button.isChecked()
        self.blocked_parameters[self.fitting_functions_layout.currentIndex()][index] = True if checked else False


def run_gui():
    # QApp
    app = QApplication(argv)
    app.setApplicationName('ThermLUM')
    # QWidget (MainWindow)
    window = MainWindow()
    window.show()
    app.exec()


run_gui()
