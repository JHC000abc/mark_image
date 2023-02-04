# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@contact: JHC000abc@gmail.com
@file: start.py
@time: 2023/2/4 13:03 $
@desc:

"""
import os
import re
import json
from queue import Queue
from threading import Thread
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication, Qt
from gui.control import ctrl_mark
import qdarkstyle


if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    Form = ctrl_mark.Mark()
    Form.show()
    sys.exit(app.exec_())