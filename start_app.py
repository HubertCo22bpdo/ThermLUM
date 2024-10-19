# ThermLUM - luminescent thermometry data analysis application
# Copyright (C) 2024  Hubert Dzielak 

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
import sys
from gui import run_gui
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QIcon
import requests #type: ignore
from webbrowser import open

class Launcher(QApplication):
    """Checks if installed ThermLUM version is actual. Helps install the latest version. Credit to relACs:  
    """
    def __init__(self, sys_argv:list[str]):
        super(Launcher, self).__init__(sys_argv)
        self.window = QWidget()
        app_icon: QIcon = QIcon(r'.\icon\app_icon.tiff')
        Launcher.setWindowIcon(app_icon)
        launcher_layout = QVBoxLayout()
        launcher_layout.addWidget(QLabel(f"New ThermLUM version {latest_relase} is available."))
        install_button = QPushButton("Install new version")
        install_button.clicked.connect(lambda: open(f"https://github.com/HubertCo22bpdo/ThermLUM/tag/{latest_relase}")) #type: ignore
        skip_button: QPushButton = QPushButton("Continue using old version")
        skip_button.clicked.connect(Launcher.closeAllWindows) #type: ignore
        launcher_layout.addWidget(install_button)
        launcher_layout.addWidget(skip_button)
        self.window.setLayout(launcher_layout)
        self.window.show()

response = requests.get("https://api.github.com/repos/HubertCo22bpdo/ThermLUM/releases")
if response.ok:
    release = "1.0.5" #VERSION
    latest_relase= response.json()[0]["tag_name"]
    if latest_relase != release:
        launcher = Launcher(sys.argv)
        launcher.exec()
run_gui()
