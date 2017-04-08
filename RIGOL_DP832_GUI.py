import sys
import os
import time
import visa

from PyQt5.QtWidgets import (QRadioButton, QTextBrowser, QDialogButtonBox, QDialog, QAction, QMainWindow, QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox, QWidget, QPushButton, QApplication, QCheckBox, QGridLayout, QLineEdit, QLabel,QMessageBox)
from PyQt5.QtGui import (QIcon, QFont)
from PyQt5.QtCore import (Qt, QSize, QTimer, QT_VERSION_STR)
from PyQt5.Qt import PYQT_VERSION_STR
from sip import SIP_VERSION_STR

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as pyplot
import matplotlib.ticker as ticker
import matplotlib
import numpy

from datetime import (datetime)

class About_License(QDialog):
    def __init__(self, parent=None):
        super(About_License, self).__init__(parent)

        self.initUI()

    def initUI(self):
        mainLayout1 = QGridLayout()
        mainLayout2 = QGridLayout()
        self.groupBox = QGroupBox("License GPL")

        self.licence_txt = \
""" This file is part of RIGOL DP832 GUI.

    RIGOL DP832 GUI is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    RIGOL DP832 GUI is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with RIGOL DP832 GUI; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA"""
    
        self.licence = QLabel(self.licence_txt, self)
        mainLayout2.addWidget(self.licence, 2, 1, 1, 2)
        self.qt_ver = QLabel("Qt version: " + str(QT_VERSION_STR), self)
        mainLayout1.addWidget(self.qt_ver, 3, 1, 1, 2)
        self.sip_ver = QLabel("SIP version: " + str(SIP_VERSION_STR), self)
        mainLayout1.addWidget(self.sip_ver, 4, 1, 1, 2)
        self.pyqt_ver = QLabel("PyQt version: " + str(PYQT_VERSION_STR), self)
        mainLayout1.addWidget(self.pyqt_ver, 5, 1, 1, 2)
        self.matplot_ver = QLabel("Matplotlib version: " + str(matplotlib.__version__), self)
        mainLayout1.addWidget(self.matplot_ver, 6, 1, 1, 2)
        self.made_1 = QLabel("MADE BY kudl4t4", self)
        self.made_1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.made_1.setFont(QFont("Verdana", 10, QFont.Bold))
        mainLayout1.addWidget(self.made_1, 7, 1)
        self.made_2 = QLabel(self)
        self.made_2.setOpenExternalLinks(True)
        urlLink = "<a href=\"http://geeks24.eu\">geeks24.eu</a>"
        self.made_2.setText(urlLink)
        self.made_2.setFont(QFont("Verdana", 10, QFont.Bold))
        mainLayout1.addWidget(self.made_2, 7, 2)

        self.groupBox.setLayout(mainLayout2)
        mainLayout1.addWidget(self.groupBox, 1, 1, 1, 2)
        self.setLayout(mainLayout1)

class Plot(QMainWindow):
    def __init__(self, rigol_instt, channelNamestring, parent=None):
        super(Plot, self).__init__(parent)
        self.NO_CHANNELS = 3
        self.NO_MEASURES = 1024
        try:
            self.rigol = rigol_instt
        except Exception as ex:
            print(ex)
            self.close()

        self.ch_Names = channelNamestring

        self.plot_widget = QWidget()
        self.setCentralWidget(self.plot_widget)
    
        self.initUI()
        self.initPlot()
        self.plotOne()
        

    def initUI(self):
        self.figure = pyplot.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.plot_gb_channel = []
        plot_gb_channel_layout = []
        self.plot_gb_channel_chbox_volt = []
        self.plot_gb_channel_chbox_curr = []

        self.plot_cb_only_channel = []

        plot_le_autoread = QLabel('Time between measures: ')
        self.plot_spinbox_autoread = QDoubleSpinBox()
        self.plot_spinbox_autoread.setSuffix(" s")
        self.plot_spinbox_autoread.setPrefix("~ ")
        self.plot_spinbox_autoread.setSingleStep(1)
        self.plot_spinbox_autoread.setValue(1)
        self.plot_spinbox_autoread.setRange(1,20)

        for i in range(0,self.NO_CHANNELS):
            self.plot_gb_channel.append(QGroupBox("Channel"+str(i+1)))
            plot_gb_channel_layout.append(QGridLayout())
            self.plot_gb_channel[i].setLayout(plot_gb_channel_layout[i])
            self.plot_gb_channel_chbox_volt.append(QCheckBox('Voltage'))
            self.plot_gb_channel_chbox_curr.append(QCheckBox('Current'))
            plot_gb_channel_layout[i].addWidget(self.plot_gb_channel_chbox_volt[i])
            plot_gb_channel_layout[i].addWidget(self.plot_gb_channel_chbox_curr[i])
        self.plot_gb_channel_chbox_volt[0].toggled.connect(lambda:self.plotOneChange(0))
        self.plot_gb_channel_chbox_volt[1].toggled.connect(lambda:self.plotOneChange(1))
        self.plot_gb_channel_chbox_volt[2].toggled.connect(lambda:self.plotOneChange(2))
        self.plot_gb_channel_chbox_curr[0].toggled.connect(lambda:self.plotOneChange(3))
        self.plot_gb_channel_chbox_curr[1].toggled.connect(lambda:self.plotOneChange(4))
        self.plot_gb_channel_chbox_curr[2].toggled.connect(lambda:self.plotOneChange(5))

        self.plot_gb_only_channel = QGroupBox("From:")
        self.plot_gb_only_channel.setEnabled(False)
        plot_gb_only_channel_layout = QGridLayout()
        self.plot_gb_only_channel.setLayout(plot_gb_only_channel_layout)
        self.plot_gb_only_channel_rb_ch1 = QRadioButton("Channel1")
        self.plot_gb_only_channel_rb_ch1.setChecked(True)
        self.plot_gb_only_channel_rb_ch2 = QRadioButton('Channel2')
        self.plot_gb_only_channel_rb_ch3 = QRadioButton('Channel3')
        plot_gb_only_channel_layout.addWidget(self.plot_gb_only_channel_rb_ch1, 1,1)
        plot_gb_only_channel_layout.addWidget(self.plot_gb_only_channel_rb_ch2, 2,1)
        plot_gb_only_channel_layout.addWidget(self.plot_gb_only_channel_rb_ch3, 3,1)
        self.plot_gb_only_channel_rb_ch1.toggled.connect(lambda:self.plotTwoChange(1))
        self.plot_gb_only_channel_rb_ch2.toggled.connect(lambda:self.plotTwoChange(2))
        self.plot_gb_only_channel_rb_ch3.toggled.connect(lambda:self.plotTwoChange(3))

        self.plot_btn_startplot = QPushButton('Start')
        self.plot_btn_startplot.clicked.connect(lambda: self.startPlot())

        self.plot_btn_stopplot = QPushButton('Stop')
        self.plot_btn_stopplot.setEnabled(False)
        self.plot_btn_stopplot.clicked.connect(lambda: self.stopPlot())

        self.plot_gb_base = QGroupBox('Plot: ')
        plot_gb_base_layout = QGridLayout()
        self.plot_gb_base.setLayout(plot_gb_base_layout)
        self.plot_gb_base_rb_time = QRadioButton('[Y]: Voltage, Current [X]: Time')
        self.plot_gb_base_rb_time.setChecked(True)
        self.plot_gb_base_rb_voltage = QRadioButton('[Y]: Current [X]:Voltage')
        plot_gb_base_layout.addWidget(plot_le_autoread,1,1,1,3)
        plot_gb_base_layout.addWidget(self.plot_spinbox_autoread, 1,4)
        plot_gb_base_layout.addWidget(self.plot_gb_base_rb_time, 2, 1, 1, 4)
        for i in range(0,self.NO_CHANNELS):
            plot_gb_base_layout.addWidget(self.plot_gb_channel[i], 3,i+1)
        plot_gb_base_layout.addWidget(self.plot_gb_base_rb_voltage, 2, 5, 1, 4)
        plot_gb_base_layout.addWidget(self.plot_gb_only_channel, 3, 5)
        self.plot_gb_base_rb_time.toggled.connect(lambda:self.plotBase())
        self.plot_gb_base_rb_voltage.toggled.connect(lambda:self.plotBase())

        self.plot_gb_analyze = QGroupBox('Analyze: ')
        plot_gb_analyze_layout = QGridLayout()
        self.plot_gb_analyze.setLayout(plot_gb_analyze_layout)

        self.var_count = 0
        self.plot_gb_save_base = QGroupBox('Save ')
        plot_gb_save_base_layout = QGridLayout()
        self.plot_gb_save_base.setLayout(plot_gb_save_base_layout)
        self.save_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'values_no_'+str(self.var_count)+'.csv')
        self.plot_le_save = QLabel(str(self.save_path))
        self.plot_btn_clear = QPushButton('Clear')
        self.plot_btn_clear.clicked.connect(lambda: self.clear())
        self.plot_btn_save = QPushButton('Save to csv')
        self.plot_btn_save.setEnabled(False)
        self.plot_btn_save.clicked.connect(lambda: self.save())
        plot_gb_save_base_layout.addWidget(self.plot_le_save, 1, 1, 1, 2)
        plot_gb_save_base_layout.addWidget(self.plot_btn_save, 1, 3, 2, 1)
        plot_gb_save_base_layout.addWidget(self.plot_btn_clear, 2, 1, 1, 1)

        self.plot_le_start_time = QLabel('Start time: ')
        self.plot_le_start_time_val = QLabel()
        self.plot_le_time = QLabel('Time: ')
        self.plot_le_time_val = QLabel()
        self.plot_le_stop_time = QLabel('Stop time: ')
        self.plot_le_stop_time_val = QLabel()

        self.plot_gb_maximum_volt_base = QGroupBox('Voltage Maximum Value: ')
        plot_gb_maximum_volt_base_layout = QGridLayout()
        self.plot_gb_maximum_volt_base.setLayout(plot_gb_maximum_volt_base_layout)
        self.plot_le_max_volt = []
        self.plot_le_max_val_volt = []
        for i in range(0,self.NO_CHANNELS):
            self.plot_le_max_volt.append(QLabel("CH"+str(i+1)))
            self.plot_le_max_val_volt.append(QLabel())
            plot_gb_maximum_volt_base_layout.addWidget(self.plot_le_max_volt[i], 1, 1+(2*i))
            plot_gb_maximum_volt_base_layout.addWidget(self.plot_le_max_val_volt[i], 1, 2+(2*i))
        
        self.plot_gb_maximum_curr_base = QGroupBox('Current Maximum Value: ')
        plot_gb_maximum_curr_base_layout = QGridLayout()
        self.plot_gb_maximum_curr_base.setLayout(plot_gb_maximum_curr_base_layout)
        self.plot_le_max_curr = []
        self.plot_le_max_val_curr = []
        for i in range(0,self.NO_CHANNELS):
            self.plot_le_max_curr.append(QLabel("CH"+str(i+1)))
            self.plot_le_max_val_curr.append(QLabel())
            plot_gb_maximum_curr_base_layout.addWidget(self.plot_le_max_curr[i], 1, 1+(2*i))
            plot_gb_maximum_curr_base_layout.addWidget(self.plot_le_max_val_curr[i], 1, 2+(2*i))

        self.plot_gb_minimum_volt_base = QGroupBox('Voltage Minimum Value: ')
        plot_gb_minimum_volt_base_layout = QGridLayout()
        self.plot_gb_minimum_volt_base.setLayout(plot_gb_minimum_volt_base_layout)
        self.plot_le_min_volt = []
        self.plot_le_min_val_volt = []
        for i in range(0,self.NO_CHANNELS):
            self.plot_le_min_volt.append(QLabel("CH"+str(i+1)))
            self.plot_le_min_val_volt.append(QLabel())
            plot_gb_minimum_volt_base_layout.addWidget(self.plot_le_min_volt[i], 1, 1+(2*i))
            plot_gb_minimum_volt_base_layout.addWidget(self.plot_le_min_val_volt[i], 1, 2+(2*i))
        
        self.plot_gb_minimum_curr_base = QGroupBox('Current Minimum Value: ')
        plot_gb_minimum_curr_base_layout = QGridLayout()
        self.plot_gb_minimum_curr_base.setLayout(plot_gb_minimum_curr_base_layout)
        self.plot_le_min_curr = []
        self.plot_le_min_val_curr = []
        for i in range(0,self.NO_CHANNELS):
            self.plot_le_min_curr.append(QLabel("CH"+str(i+1)))
            self.plot_le_min_val_curr.append(QLabel())
            plot_gb_minimum_curr_base_layout.addWidget(self.plot_le_min_curr[i], 1, 1+(2*i))
            plot_gb_minimum_curr_base_layout.addWidget(self.plot_le_min_val_curr[i], 1, 2+(2*i))

        self.plot_gb_average_volt_base = QGroupBox('Voltage Average Value: ')
        plot_gb_average_volt_base_layout = QGridLayout()
        self.plot_gb_average_volt_base.setLayout(plot_gb_average_volt_base_layout)
        self.plot_le_avg_volt = []
        self.plot_le_avg_val_volt = []
        for i in range(0,self.NO_CHANNELS):
            self.plot_le_avg_volt.append(QLabel("CH"+str(i+1)))
            self.plot_le_avg_val_volt.append(QLabel())
            plot_gb_average_volt_base_layout.addWidget(self.plot_le_avg_volt[i], 1, 1+(2*i))
            plot_gb_average_volt_base_layout.addWidget(self.plot_le_avg_val_volt[i], 1, 2+(2*i))
        
        self.plot_gb_average_curr_base = QGroupBox('Current Average Value: ')
        plot_gb_average_curr_base_layout = QGridLayout()
        self.plot_gb_average_curr_base.setLayout(plot_gb_average_curr_base_layout)
        self.plot_le_avg_curr = []
        self.plot_le_avg_val_curr = []
        for i in range(0,self.NO_CHANNELS):
            self.plot_le_avg_curr.append(QLabel("CH"+str(i+1)))
            self.plot_le_avg_val_curr.append(QLabel())
            plot_gb_average_curr_base_layout.addWidget(self.plot_le_avg_curr[i], 1, 1+(2*i))
            plot_gb_average_curr_base_layout.addWidget(self.plot_le_avg_val_curr[i], 1, 2+(2*i))
            
        self.plot_le_min = QLabel('Minimum Value: ')
        self.plot_le_min_val = QLabel()
        self.plot_le_avg = QLabel('Average Value: ')
        self.plot_le_avg_val = QLabel()
        plot_gb_analyze_layout.addWidget(self.plot_le_start_time, 1, 1)
        plot_gb_analyze_layout.addWidget(self.plot_le_start_time_val, 1, 2)
        plot_gb_analyze_layout.addWidget(self.plot_le_stop_time, 1, 3)
        plot_gb_analyze_layout.addWidget(self.plot_le_stop_time_val, 1, 4)
        plot_gb_analyze_layout.addWidget(self.plot_le_time, 2, 1)
        plot_gb_analyze_layout.addWidget(self.plot_le_time_val, 2, 2)
        plot_gb_analyze_layout.addWidget(self.plot_gb_maximum_volt_base, 3, 1, 1, 2)
        plot_gb_analyze_layout.addWidget(self.plot_gb_maximum_curr_base, 3, 3, 1, 2)
        plot_gb_analyze_layout.addWidget(self.plot_gb_minimum_volt_base, 4, 1, 1, 2)
        plot_gb_analyze_layout.addWidget(self.plot_gb_minimum_curr_base, 4, 3, 1, 2)
        plot_gb_analyze_layout.addWidget(self.plot_gb_average_volt_base, 5, 1, 1, 2)
        plot_gb_analyze_layout.addWidget(self.plot_gb_average_curr_base, 5, 3, 1, 2)

        plot_layout = QGridLayout()
        plot_layout.addWidget(self.plot_gb_base, 1,1,2,2)
        plot_layout.addWidget(self.plot_gb_analyze, 1,3,1,3)
        plot_layout.addWidget(self.plot_gb_save_base, 2,3,2,3)
        plot_layout.addWidget(self.plot_btn_startplot, 3,1)
        plot_layout.addWidget(self.plot_btn_stopplot, 3,2)
        plot_layout.addWidget(self.toolbar, 4,1,1,5)
        plot_layout.addWidget(self.canvas, 5,1,5,5)

        self.plot_widget.setLayout(plot_layout)

    def initPlot(self):
        self.count = [0 for x in range(self.NO_CHANNELS)]
        self.timer_data = QTimer()
        self.timer_data.timeout.connect(lambda: self.dataForPlot())

        self.timer_data_analize = QTimer()
        self.timer_data_analize.timeout.connect(lambda: self.dataAnalize())

        self.timer_plotter_volt = []
        self.timer_plotter_curr = []
        for i in range(0,self.NO_CHANNELS):
            self.timer_plotter_volt.append(QTimer())
            self.timer_plotter_curr.append(QTimer())
        self.timer_plotter_volt[0].timeout.connect(lambda: self.plotterOne(0, 0))
        self.timer_plotter_volt[1].timeout.connect(lambda: self.plotterOne(1, 0))
        self.timer_plotter_volt[2].timeout.connect(lambda: self.plotterOne(2, 0))
        self.timer_plotter_curr[0].timeout.connect(lambda: self.plotterOne(0, 1))
        self.timer_plotter_curr[1].timeout.connect(lambda: self.plotterOne(1, 1))
        self.timer_plotter_curr[2].timeout.connect(lambda: self.plotterOne(2, 1))

        self.timer_plotter_ch = []
        for i in range(0,self.NO_CHANNELS):
            self.timer_plotter_ch.append(QTimer())
        self.timer_plotter_ch[0].timeout.connect(lambda: self.plotterTwo(0))
        self.timer_plotter_ch[1].timeout.connect(lambda: self.plotterTwo(1))
        self.timer_plotter_ch[2].timeout.connect(lambda: self.plotterTwo(2))
                
        self.volt_val = [[]]
        self.curr_val = [[]]
        self.xmin = 0
        
        self.figure.clear()

    def plotBase(self):
        pyplot.clf()
        self.canvas.draw()
        
        if self.plot_gb_base_rb_time.isChecked() == True:
            for i in range(0,self.NO_CHANNELS):
                self.plot_gb_channel[i].setEnabled(True)
            self.plot_gb_only_channel.setEnabled(False)
            self.plotOne()
        if self.plot_gb_base_rb_voltage.isChecked() == True:
            for i in range(0,self.NO_CHANNELS):
                self.plot_gb_channel[i].setEnabled(False)
            self.plot_gb_only_channel.setEnabled(True)
            self.plotTwo()

    def plotOne(self):
        if hasattr(Plot, 'volt_val'):
            del self.volt_val
        if hasattr(Plot, 'curr_val'):
            del self.curr_val
        
        self.volt_val = [[0 for x in range(self.NO_MEASURES)] for y in range(self.NO_CHANNELS)]
        self.curr_val = [[0 for x in range(self.NO_MEASURES)] for y in range(self.NO_CHANNELS)]
        self.xmin = 0
        self.timeAxis=numpy.arange(self.xmin-self.NO_MEASURES,len(self.volt_val[0])+self.xmin-self.NO_MEASURES,1)

        self.ch123 = self.figure.add_subplot(1,1,1)

        self.axes_ch123 = [self.ch123, self.ch123.twinx(), self.ch123.twinx(), self.ch123.twinx(), self.ch123.twinx(), self.ch123.twinx(), self.ch123.twinx()]
        
        self.axes_ch123[0].grid(False)
        self.axes_ch123[0].set_xlabel("* time between measures = Time [s]")
        self.axes_ch123[0].xaxis.set_major_locator(ticker.MultipleLocator(100))
        self.axes_ch123[0].get_yaxis().set_visible(False)
        self.axes_ch123[0].axis([0-self.NO_MEASURES,0,0,0.0])
        self.axes_ch123[1].grid(False)
        self.axes_ch123[1].set_ylabel("Voltage ch1 [V]")
        self.axes_ch123[1].axes.yaxis.set_ticks_position('left')
        self.axes_ch123[1].axes.yaxis.set_label_position('left')
        self.axes_ch123[1].axis([0-self.NO_MEASURES,0,0,33.0])
        self.axes_ch123[1].set_visible(False)
        self.axes_ch123[2].grid(False)
        self.axes_ch123[2].set_ylabel("Voltage ch2 [V]")
        self.axes_ch123[2].axis([0-self.NO_MEASURES,0,0,33.0])
        self.axes_ch123[2].set_visible(False)
        self.axes_ch123[3].grid(False)
        self.axes_ch123[3].set_ylabel("Voltage ch3 [V]")
        self.axes_ch123[3].axis([0-self.NO_MEASURES,0,0,5.5])
        self.axes_ch123[3].set_visible(False)
        self.axes_ch123[4].grid(False)
        self.axes_ch123[4].set_ylabel("Current ch1 [A]")
        self.axes_ch123[4].axis([0-self.NO_MEASURES,0,0,3.5])
        self.axes_ch123[4].set_visible(False)
        self.axes_ch123[5].grid(False)
        self.axes_ch123[5].set_ylabel("Current ch2 [A]")
        self.axes_ch123[5].axis([0-self.NO_MEASURES,0,0,3.5])
        self.axes_ch123[5].set_visible(False)
        self.axes_ch123[6].grid(False)
        self.axes_ch123[6].set_ylabel("Current ch3 [A]")
        self.axes_ch123[6].axis([0-self.NO_MEASURES,0,0,3.5])
        self.axes_ch123[6].set_visible(False)
        
        self.axes_ch123[1].spines['left'].set_position(('axes', 0))

        self.volt_line = []
        self.volt_line.append(self.axes_ch123[1].plot(0,0,'g-'))
        self.volt_line.append(self.axes_ch123[2].plot(0,0,'c-'))
        self.volt_line.append(self.axes_ch123[3].plot(0,0,'m-'))
        self.curr_line = []
        self.curr_line.append(self.axes_ch123[4].plot(0,0, 'b-'))
        self.curr_line.append(self.axes_ch123[5].plot(0,0, 'r-'))
        self.curr_line.append(self.axes_ch123[6].plot(0,0, 'y-'))
        
        self.axes_ch123[1].axes.yaxis.label.set_color(self.volt_line[0][0].get_color())
        self.axes_ch123[2].axes.yaxis.label.set_color(self.volt_line[1][0].get_color())
        self.axes_ch123[3].axes.yaxis.label.set_color(self.volt_line[2][0].get_color())
        
        self.axes_ch123[4].axes.yaxis.label.set_color(self.curr_line[0][0].get_color())
        self.axes_ch123[5].axes.yaxis.label.set_color(self.curr_line[1][0].get_color())
        self.axes_ch123[6].axes.yaxis.label.set_color(self.curr_line[2][0].get_color())

        self.canvas.draw()
        
    def plotOneChange(self, no):
        countVolt = 0
        countCurr = 0
        subplot_right_adjust = 0
        subplot_left_adjust = 0
        for i in range(1,4):
            if self.plot_gb_channel_chbox_volt[i-1].isChecked() == True:
                countVolt += 1
                self.axes_ch123[i].set_visible(True)
                subplot_left_adjust = ((countVolt-1)*0.0625)
                self.axes_ch123[i].spines['left'].set_position(('axes', -0.10*(countVolt-1)))
                self.axes_ch123[i].axes.yaxis.set_ticks_position('left')
                self.axes_ch123[i].axes.yaxis.set_label_position('left')
            else:
                self.axes_ch123[i].set_visible(False)
        for i in range(4,7):
            if self.plot_gb_channel_chbox_curr[i-4].isChecked() == True:
                countCurr += 1
                self.axes_ch123[i].set_visible(True)
                subplot_right_adjust = (0.15*(countCurr-1))
                self.axes_ch123[i].spines['right'].set_position(('axes', 1+subplot_right_adjust))
            else:
                self.axes_ch123[i].set_visible(False)

        self.figure.subplots_adjust(right=(0.9-subplot_right_adjust))
        self.figure.subplots_adjust(left=(0.125+subplot_left_adjust))

        if countVolt > 2 or countCurr > 1:
            self.axes_ch123[-1].set_frame_on(True)
            self.axes_ch123[-1].patch.set_visible(False)

        self.canvas.draw()

    def plotTwo(self):
        if hasattr(Plot, 'volt_val'):
            del self.volt_val
        if hasattr(Plot, 'curr_val'):
            del self.curr_val

        self.volt_val = [[0 for x in range(self.NO_MEASURES)] for y in range(self.NO_CHANNELS)]
        self.curr_val = [[0 for x in range(self.NO_MEASURES)] for y in range(self.NO_CHANNELS)]
        self.xmin = 0
        self.column = numpy.column_stack((self.volt_val[0], self.curr_val[0]))
        self.header = "voltage ch1, current ch1"

        self.figure.subplots_adjust(right=0.9)
        self.figure.subplots_adjust(left=0.125)
        
        self.ch123 = self.figure.add_subplot(1,1,1)
        
        self.ch123.grid(False)
        self.ch123.set_ylabel("Current ch1 [A]")
        self.ch123.set_xlabel("Voltage ch1 [V]")
        self.ch123.axis([0,33.0,0,3.3])

        self.line = self.ch123.plot(0,0,'g-')
        self.ch123.axes.yaxis.label.set_color(self.line[0].get_color())
        self.ch123.axes.xaxis.label.set_color(self.line[0].get_color())

        self.canvas.draw()

    def plotTwoChange(self, no):
        pyplot.clf()
        self.canvas.draw()

        self.ch123 = self.figure.add_subplot(1,1,1)
        
        self.ch123.grid(False)
        self.ch123.set_ylabel("Current ch"+str(no)+" [A]")
        self.ch123.set_xlabel("Voltage ch"+str(no)+" [V]")
        if no != 3:
            self.ch123.axis([0,33.0,0,3.3])
        else:
            self.ch123.axis([0,5.5,0,3.3])

        self.line = self.ch123.plot(0,0,'go')
        self.ch123.axes.yaxis.label.set_color(self.line[0].get_color())
        self.ch123.axes.xaxis.label.set_color(self.line[0].get_color())

        self.column = numpy.column_stack((self.volt_val[no-1], self.curr_val[no-1]))
        self.header = "voltage ch"+str(no)+", current ch"+str(no)

        self.canvas.draw()
        

    def startPlot(self):
        if hasattr(Plot, 'self.volt_val'):
            del self.volt_val
        if hasattr(Plot, 'self.curr_val'):
            del self.curr_val
            
        self.plot_le_max_val_volt[0].setText("")
        self.plot_le_min_val_volt[0].setText("")
        self.plot_le_avg_val_volt[0].setText("")
        self.plot_le_max_val_curr[0].setText("")
        self.plot_le_min_val_curr[0].setText("")
        self.plot_le_avg_val_curr[0].setText("")
        self.plot_le_max_val_volt[1].setText("")
        self.plot_le_min_val_volt[1].setText("")
        self.plot_le_avg_val_volt[1].setText("")
        self.plot_le_max_val_curr[1].setText("")
        self.plot_le_min_val_curr[1].setText("")
        self.plot_le_avg_val_curr[1].setText("")
        self.plot_le_max_val_volt[2].setText("")
        self.plot_le_min_val_volt[2].setText("")
        self.plot_le_avg_val_volt[2].setText("")
        self.plot_le_max_val_curr[2].setText("")
        self.plot_le_min_val_curr[2].setText("")
        self.plot_le_avg_val_curr[2].setText("")

        self.volt_val = [[0 for x in range(self.NO_MEASURES)] for y in range(self.NO_CHANNELS)]
        self.curr_val = [[0 for x in range(self.NO_MEASURES)] for y in range(self.NO_CHANNELS)]
        self.xmin = 0

        self.plot_le_start_time_val.setText("")
        self.plot_le_time_val.setText("")
        self.plot_le_stop_time_val.setText("")
        
        self.timer_data.setInterval(1000*self.plot_spinbox_autoread.value())
        self.timer_data.start()

        if self.plot_gb_base_rb_time.isChecked() == True:
            if self.plot_gb_channel_chbox_volt[0].isChecked() == False and self.plot_gb_channel_chbox_curr[0].isChecked() == False and self.plot_gb_channel_chbox_curr[1].isChecked() == False and self.plot_gb_channel_chbox_volt[1].isChecked() == False and self.plot_gb_channel_chbox_curr[2].isChecked() == False and self.plot_gb_channel_chbox_volt[2].isChecked() == False:
                self.showWarning("from start", "NO data selected!")
                self.timer_data.stop()
                self.plot_gb_base.setEnabled(True)
                self.plot_btn_startplot.setEnabled(True)
                self.plot_btn_stopplot.setEnabled(False)
                return
            
            for i in range(0,self.NO_CHANNELS):
                self.timer_plotter_volt[i].setInterval(1000*self.plot_spinbox_autoread.value())
                self.timer_plotter_curr[i].setInterval(1000*self.plot_spinbox_autoread.value())
                
            if self.plot_gb_channel_chbox_volt[0].isChecked() == True:
                self.timer_plotter_volt[0].start()
            if self.plot_gb_channel_chbox_curr[0].isChecked() == True:
                self.timer_plotter_curr[0].start()
            if self.plot_gb_channel_chbox_volt[1].isChecked() == True:
                self.timer_plotter_volt[1].start()
            if self.plot_gb_channel_chbox_curr[1].isChecked() == True:
                self.timer_plotter_curr[1].start()
            if self.plot_gb_channel_chbox_volt[2].isChecked() == True:
                self.timer_plotter_volt[2].start()
            if self.plot_gb_channel_chbox_curr[2].isChecked() == True:
                self.timer_plotter_curr[2].start()

        if self.plot_gb_base_rb_voltage.isChecked() == True:
            if self.plot_gb_only_channel_rb_ch1.isChecked() == True:
                self.timer_plotter_ch[0].setInterval(1000*self.plot_spinbox_autoread.value())
                self.timer_plotter_ch[0].start()
            if self.plot_gb_only_channel_rb_ch2.isChecked() == True:
                self.timer_plotter_ch[1].setInterval(1000*self.plot_spinbox_autoread.value())
                self.timer_plotter_ch[1].start()
            if self.plot_gb_only_channel_rb_ch3.isChecked() == True:
                self.timer_plotter_ch[2].setInterval(1000*self.plot_spinbox_autoread.value())
                self.timer_plotter_ch[2].start()

        self.timer_data_analize.setInterval(1000*self.plot_spinbox_autoread.value())
        self.timer_data_analize.start()

        self.plot_le_start_time_val.setText(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        self.plot_btn_save.setEnabled(False)
        self.plot_gb_base.setEnabled(False)
        self.plot_btn_startplot.setEnabled(False)
        self.plot_btn_stopplot.setEnabled(True)

    def stopPlot(self):
        self.timer_data_analize.stop()
        if self.plot_gb_base_rb_time.isChecked() == True:
            for i in range(0,self.NO_CHANNELS):
                self.timer_plotter_volt[i].stop()
                self.timer_plotter_curr[i].stop()
        if self.plot_gb_base_rb_voltage.isChecked() == True:
            for i in range(0,self.NO_CHANNELS):
                self.timer_plotter_ch[i].stop()
        self.timer_data.stop()

        self.plot_le_stop_time_val.setText(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        if self.xmin > 0:
            self.plot_btn_save.setEnabled(True)
        self.plot_gb_base.setEnabled(True)
        self.plot_btn_startplot.setEnabled(True)
        self.plot_btn_stopplot.setEnabled(False)

    def dataForPlot(self):
        for i in range(0,self.NO_CHANNELS):
            try:
                parts = self.rigol.query(':MEASure:ALL? CH'+str(i+1)+'; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            parts = parts.rsplit(';')
            if parts[1] == '1\n':
                data = parts[0].rsplit(',')
                #workaround: doing ALL command gives strange values / CURR shows 0.000
                if float(data[1]) == 429496.719 and float(data[2]) == 429496.719:
                    data[1] = '0.000'
                    data[2] = '0.000'
                if float(data[0]) > 500 or float(data[1]) > 500:
                    self.showWarning("too big number", "Something wrong with measure!")
                    self.stopPlot()
                    return
                self.volt_val[i].append(float(data[0]))
                self.curr_val[i].append(float(data[1]))
                self.volt_val[i].pop(0)
                self.curr_val[i].pop(0)
            else:
                data = self.rigol.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
        self.xmin +=1
        self.plot_le_time_val.setText(str(self.xmin*self.plot_spinbox_autoread.value()))

    def dataAnalize(self):
        if self.xmin > self.NO_MEASURES:
            range = 0
        elif self.xmin < 1:
            range = self.NO_MEASURES - 1
        else:
            range = self.NO_MEASURES - self.xmin

        if self.plot_gb_base_rb_time.isChecked() == True:
            if self.plot_gb_channel_chbox_volt[0].isChecked() == True:
                self.plot_le_max_val_volt[0].setText("{:.3f}".format(max(self.volt_val[0][range:])))
                self.plot_le_min_val_volt[0].setText("{:.3f}".format(min(self.volt_val[0][range:])))
                self.plot_le_avg_val_volt[0].setText("{:.3f}".format(numpy.average(self.volt_val[0][range:])))
            if self.plot_gb_channel_chbox_curr[0].isChecked() == True:
                self.plot_le_max_val_curr[0].setText("{:.3f}".format(max(self.curr_val[0][range:])))
                self.plot_le_min_val_curr[0].setText("{:.3f}".format(min(self.curr_val[0][range:])))
                self.plot_le_avg_val_curr[0].setText("{:.3f}".format(numpy.average(self.curr_val[0][range:])))
            if self.plot_gb_channel_chbox_volt[1].isChecked() == True:
                self.plot_le_max_val_volt[1].setText("{:.3f}".format(max(self.volt_val[1][range:])))
                self.plot_le_min_val_volt[1].setText("{:.3f}".format(min(self.volt_val[1][range:])))
                self.plot_le_avg_val_volt[1].setText("{:.3f}".format(numpy.average(self.volt_val[1][range:])))
            if self.plot_gb_channel_chbox_curr[1].isChecked() == True:
                self.plot_le_max_val_curr[1].setText("{:.3f}".format(max(self.curr_val[1][range:])))
                self.plot_le_min_val_curr[1].setText("{:.3f}".format(min(self.curr_val[1][range:])))
                self.plot_le_avg_val_curr[1].setText("{:.3f}".format(numpy.average(self.curr_val[1][range:])))
            if self.plot_gb_channel_chbox_volt[2].isChecked() == True:
                self.plot_le_max_val_volt[2].setText("{:.3f}".format(max(self.volt_val[2][range:])))
                self.plot_le_min_val_volt[2].setText("{:.3f}".format(min(self.volt_val[2][range:])))
                self.plot_le_avg_val_volt[2].setText("{:.3f}".format(numpy.average(self.volt_val[2][range:])))
            if self.plot_gb_channel_chbox_curr[2].isChecked() == True:
                self.plot_le_max_val_curr[2].setText("{:.3f}".format(max(self.curr_val[2][range:])))
                self.plot_le_min_val_curr[2].setText("{:.3f}".format(min(self.curr_val[2][range:])))
                self.plot_le_avg_val_curr[2].setText("{:.3f}".format(numpy.average(self.curr_val[2][range:])))

        if self.plot_gb_base_rb_voltage.isChecked() == True:
            if self.plot_gb_only_channel_rb_ch1.isChecked() == True:
                self.plot_le_max_val_volt[0].setText("{:.3f}".format(max(self.volt_val[0][range:])))
                self.plot_le_min_val_volt[0].setText("{:.3f}".format(min(self.volt_val[0][range:])))
                self.plot_le_avg_val_volt[0].setText("{:.3f}".format(numpy.average(self.volt_val[0][range:])))
                self.plot_le_max_val_curr[0].setText("{:.3f}".format(max(self.curr_val[0][range:])))
                self.plot_le_min_val_curr[0].setText("{:.3f}".format(min(self.curr_val[0][range:])))
                self.plot_le_avg_val_curr[0].setText("{:.3f}".format(numpy.average(self.curr_val[0][range:])))
            if self.plot_gb_only_channel_rb_ch2.isChecked() == True:
                self.plot_le_max_val_volt[1].setText("{:.3f}".format(max(self.volt_val[1][range:])))
                self.plot_le_min_val_volt[1].setText("{:.3f}".format(min(self.volt_val[1][range:])))
                self.plot_le_avg_val_volt[1].setText("{:.3f}".format(numpy.average(self.volt_val[1][range:])))
                self.plot_le_max_val_curr[1].setText("{:.3f}".format(max(self.curr_val[1][range:])))
                self.plot_le_min_val_curr[1].setText("{:.3f}".format(min(self.curr_val[1][range:])))
                self.plot_le_avg_val_curr[1].setText("{:.3f}".format(numpy.average(self.curr_val[1][range:])))
            if self.plot_gb_only_channel_rb_ch3.isChecked() == True:
                self.plot_le_max_val_volt[2].setText("{:.3f}".format(max(self.volt_val[2][range:])))
                self.plot_le_min_val_volt[2].setText("{:.3f}".format(min(self.volt_val[2][range:])))
                self.plot_le_avg_val_volt[2].setText("{:.3f}".format(numpy.average(self.volt_val[2][range:])))
                self.plot_le_max_val_curr[2].setText("{:.3f}".format(max(self.curr_val[2][range:])))
                self.plot_le_min_val_curr[2].setText("{:.3f}".format(min(self.curr_val[2][range:])))
                self.plot_le_avg_val_curr[2].setText("{:.3f}".format(numpy.average(self.curr_val[2][range:])))

    def plotterOne(self, no, what):
        self.timeAxis=numpy.arange(self.xmin-self.NO_MEASURES,len(self.volt_val[no])+self.xmin-self.NO_MEASURES,1)
        if what == 0:
            self.volt_line[no][0].set_data(self.timeAxis,self.volt_val[no])
            self.axes_ch123[no+1].axis([self.timeAxis.min(),self.timeAxis.max(),0,max(self.volt_val[no])+0.1])
        else:
            self.curr_line[no][0].set_data(self.timeAxis,self.curr_val[no])
            self.axes_ch123[no+4].axis([self.timeAxis.min(),self.timeAxis.max(),0,max(self.curr_val[no])+0.1])
        self.canvas.draw()

    def plotterTwo(self, no):
        if self.xmin <= self.NO_MEASURES:
            self.line[0].set_data(self.volt_val[no][self.NO_MEASURES-self.xmin:],self.curr_val[no][self.NO_MEASURES-self.xmin:])
        else:
            self.line[0].set_data(self.volt_val[no],self.curr_val[no])
        self.ch123.axis([0,max(self.volt_val[no])+0.1,0,max(self.curr_val[no])+0.1])
        self.canvas.draw()

    def clear(self):
        self.var_count=0
        self.save_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'values_no_'+str(self.var_count)+'.csv')
        self.plot_le_save.setText(str(self.save_path))

    def save(self):
        self.header=""
        if self.xmin > self.NO_MEASURES:
            range = 0
        else:
            range = self.NO_MEASURES - self.xmin
        if self.plot_gb_base_rb_time.isChecked() == True:
            if self.plot_gb_channel_chbox_volt[0].isChecked() == True:
                if self.header.find("time") == 0:
                    self.column = numpy.column_stack((self.column, self.volt_val[0][range:]))
                    self.header = self.header + ", voltage ch1"
                else:
                    self.column = numpy.column_stack((self.timeAxis[range:], self.volt_val[0][range:]))
                    self.header = "time, voltage ch1"
            if self.plot_gb_channel_chbox_curr[0].isChecked() == True:
                if self.header.find("time") == 0:
                    self.column = numpy.column_stack((self.column, self.curr_val[0][range:]))
                    self.header = self.header + ", current ch1"
                else:
                    self.column = numpy.column_stack((self.timeAxis[range:], self.curr_val[0][range:]))
                    self.header = "time, current ch1"
            if self.plot_gb_channel_chbox_volt[1].isChecked() == True:
                if self.header.find("time") == 0:
                    self.column = numpy.column_stack((self.column, self.volt_val[1][range:]))
                    self.header = self.header + ", voltage ch2"
                else:
                    self.column = numpy.column_stack((self.timeAxis[range:], self.volt_val[1][range:]))
                    self.header = "time, voltage ch2"
            if self.plot_gb_channel_chbox_curr[1].isChecked() == True:
                if self.header.find("time") == 0:
                    self.column = numpy.column_stack((self.column, self.curr_val[1][range:]))
                    self.header = self.header + ", current ch2"
                else:
                    self.column = numpy.column_stack((self.timeAxis[range:], self.curr_val[1][range:]))
                    self.header = "time, current ch2"
            if self.plot_gb_channel_chbox_volt[2].isChecked() == True:
                if self.header.find("time") == 0:
                    self.column = numpy.column_stack((self.column, self.volt_val[2][range:]))
                    self.header = self.header + ", voltage ch3"
                else:
                    self.column = numpy.column_stack((self.timeAxis[range:], self.volt_val[2][range:]))
                    self.header = "time, voltage ch3"
            if self.plot_gb_channel_chbox_curr[2].isChecked() == True:
                if self.header.find("time") == 0:
                    self.column = numpy.column_stack((self.column, self.curr_val[2][range:]))
                    self.header = self.header + ", current ch3"
                else:
                    self.column = numpy.column_stack((self.timeAxis[range:], self.curr_val[2][range:]))
                    self.header = "time, current ch3"
        numpy.savetxt(self.plot_le_save.text(), self.column, delimiter=",", fmt='%s', header=self.header)

        self.var_count += 1
        self.save_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'values_no_'+str(self.var_count)+'.csv')
        self.plot_le_save.setText(str(self.save_path))

        del self.column
        del self.header

    def showWarning(self, string1, string2):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("WARNING: "+string1)
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(string2)
        msgBox.exec_();

    def closeEvent(self, evnt):
        if hasattr(Plot, 'pyplot'):
            pyplot.close(self.figure)
            pyplot.gcf()
        if hasattr(Plot, 'self.timer_plotter_volt') and hasattr(Plot, 'self.timer_plotter_curr'):
            for i in range(0,self.NO_CHANNELS):
                self.timer_plotter_volt[i].stop()
                self.timer_plotter_curr[i].stop()
        if hasattr(Plot, 'self.timer_plotter_ch'):
            for i in range(0,self.NO_CHANNELS):
                self.timer_plotter_ch[i].stop()
        if hasattr(Plot, 'self.timer_data'):
            self.timer_data.stop()

class DP832(QMainWindow):
    
    def __init__(self):
        super(DP832, self).__init__()

        aboutAction = QAction('&License', self)
        aboutAction.triggered.connect(lambda: self.menu_about())
        
        self.mainMenu = self.menuBar()
        about = self.mainMenu.addMenu('About')
        about.addAction(aboutAction)

        self.dp832_widget = QWidget()
        self.setCentralWidget(self.dp832_widget)
        self.initUI()

    def menu_about(self):
        self.about_license = About_License(self)
        self.about_license.setGeometry(200, 200, 400, 300)
        self.about_license.setSizeGripEnabled(False)
        self.about_license.setWindowTitle('About')
        self.about_license.setWindowIcon(QIcon('DP832.jpg'))
        self.about_license.show()    

    def plot(self):
        self.plot = Plot(self.main_rigol_inst, self.ch_string)
        self.plot.setGeometry(200, 200, 1450, 850)
        self.plot.setWindowTitle('Plot')
        self.plot.setWindowIcon(QIcon('DP832.jpg'))
        self.plot.show()
        
    def initUI(self):
        self.NO_CHANNELS = 3
        mainLayout = QGridLayout()
        self.ch_groupBox = []
        self.ch_string = []
        ch_layout = []
        ch_layout_overvolt = []
        ch_layout_overcurr = []
        ch_layout_track = []
        self.timer = []

        for i in range(0,self.NO_CHANNELS):
            self.ch_groupBox.append(QGroupBox("Channel" + str(i+1)))
            self.ch_groupBox[i].setEnabled(False)
            self.ch_groupBox[i].setCheckable(True)
            self.ch_groupBox[i].setChecked(False)
            self.ch_string.append("CH"+str(i+1))
            self.timer.append(QTimer())
            ch_layout.append(QGridLayout())

        self.ch_groupBox[0].clicked.connect(lambda: self.ch_set(0, self.ch_string[0]))
        self.ch_groupBox[1].clicked.connect(lambda: self.ch_set(1, self.ch_string[1]))
        self.ch_groupBox[2].clicked.connect(lambda: self.ch_set(2, self.ch_string[2]))

        self.timer[0].timeout.connect(lambda: self.ch_read(0, self.ch_string[0]))
        self.timer[1].timeout.connect(lambda: self.ch_read(1, self.ch_string[1]))
        self.timer[2].timeout.connect(lambda: self.ch_read(2, self.ch_string[2]))

        main_lbl_ipaddr = QLabel('IP:')
        mainLayout.addWidget(main_lbl_ipaddr,1,1)

        self.main_le_ipaddr = QLineEdit()
        self.main_le_ipaddr.setText("192.168.134.193")
        mainLayout.addWidget(self.main_le_ipaddr,1,2)

        self.main_btn_connect = QPushButton('Connect', self)
        self.main_btn_connect.setEnabled(True)
        self.main_btn_connect.clicked.connect(lambda:self.main_connect())
        mainLayout.addWidget(self.main_btn_connect, 3,2)

        self.main_btn_disconnect = QPushButton('Disconnect', self)
        self.main_btn_disconnect.setEnabled(False)
        self.main_btn_disconnect.clicked.connect(lambda:self.main_disconnect())
        mainLayout.addWidget(self.main_btn_disconnect, 3,3)

        self.main_btn_plot = QPushButton('Plot', self)
        self.main_btn_plot.setEnabled(False)
        self.main_btn_plot.clicked.connect(self.plot)
        mainLayout.addWidget(self.main_btn_plot, 3,6)

        self.main_lbl_instr = QLabel(self)
        self.main_lbl_instr.setText("Disconnected")
        mainLayout.addWidget(self.main_lbl_instr,10,1,1,3)

#======== Channel LAYOUT - READ
        self.ch_btn_read = []
        
        self.ch_chbox_autoread = []
        self.ch_spinbox_autoread = []
        self.ch_le_autoread = []
        
        ch_lbl_state = []
        self.ch_le_state = []
        ch_lbl_volt = []
        self.ch_le_volt = []
        ch_lbl_curr = []
        self.ch_le_curr = []
        ch_lbl_power = []
        self.ch_le_power = []
        
        self.ch_groupBox_overvolt = []
        ch_lbl_overvolt_state = []
        self.ch_le_overvolt_state = []
        ch_lbl_overvolt_volt = []
        self.ch_le_overvolt_volt = []
        ch_lbl_overvolt_volt_test = []
        self.ch_le_overvolt_volt_test = []
        self.ch_btn_overvolt_volt_test_clear = []
        
        self.ch_groupBox_overcurr = []
        ch_lbl_overcurr_state = []
        self.ch_le_overcurr_state = []
        ch_lbl_overcurr_curr = []
        self.ch_le_overcurr_curr = []
        ch_lbl_overcurr_curr_test = []
        self.ch_le_overcurr_curr_test = []
        self.ch_btn_overcurr_curr_test_clear = []

        self.ch_groupBox_track = []
        ch_lbl_track_state = []
        self.ch_le_track_state = []
        ch_lbl_track_mode = []
        self.ch_le_track_mode = []
        
        for i in range(0,self.NO_CHANNELS):       
            self.ch_btn_read.append(QPushButton('READ', self))
            ch_layout[i].addWidget(self.ch_btn_read[i],1,1,1,2)

            self.ch_chbox_autoread.append(QCheckBox("Autoread:"))
            ch_layout[i].addWidget(self.ch_chbox_autoread[i],2,1)

            self.ch_spinbox_autoread.append(QSpinBox())
            self.ch_spinbox_autoread[i].setSuffix(" s")
            self.ch_spinbox_autoread[i].setPrefix("~ ")
            self.ch_spinbox_autoread[i].setSingleStep(1)
            self.ch_spinbox_autoread[i].setValue(1)
            ch_layout[i].addWidget(self.ch_spinbox_autoread[i],2,2)

            self.ch_le_autoread.append(QLabel(''))
            ch_layout[i].addWidget(self.ch_le_autoread[i],2,3,1,2)

            ch_lbl_state.append(QLabel('State:'))
            ch_layout[i].addWidget(ch_lbl_state[i],3,1)

            self.ch_le_state.append(QLineEdit())
            self.ch_le_state[i].setText("---")
            self.ch_le_state[i].setReadOnly(1)
            ch_layout[i].addWidget(self.ch_le_state[i],3,2)

            ch_lbl_volt.append(QLabel('Voltage [V]:'))
            ch_layout[i].addWidget(ch_lbl_volt[i],4,1)

            self.ch_le_volt.append(QLineEdit())
            self.ch_le_volt[i].setText("---")
            self.ch_le_volt[i].setReadOnly(1)
            ch_layout[i].addWidget(self.ch_le_volt[i],4,2)

            ch_lbl_curr.append(QLabel('Current [A]:'))
            ch_layout[i].addWidget(ch_lbl_curr[i],5,1)

            self.ch_le_curr.append(QLineEdit())
            self.ch_le_curr[i].setText("---")
            self.ch_le_curr[i].setReadOnly(1)
            ch_layout[i].addWidget(self.ch_le_curr[i],5,2)

            ch_lbl_power.append(QLabel('Power [W]:'))
            ch_layout[i].addWidget(ch_lbl_power[i],6,1)

            self.ch_le_power.append(QLineEdit())
            self.ch_le_power[i].setText("---")
            self.ch_le_power[i].setReadOnly(1)
            ch_layout[i].addWidget(self.ch_le_power[i],6,2)

            self.ch_groupBox_overvolt.append(QGroupBox("Overvoltage protection"))
            self.ch_groupBox_overvolt[i].setCheckable(False)
            ch_layout_overvolt.append(QGridLayout())
            
            ch_lbl_overvolt_state.append(QLabel('State:'))
            ch_layout_overvolt[i].addWidget(ch_lbl_overvolt_state[i], 1,1)

            self.ch_le_overvolt_state.append(QLineEdit())
            self.ch_le_overvolt_state[i].setText("---")
            self.ch_le_overvolt_state[i].setReadOnly(1)
            ch_layout_overvolt[i].addWidget(self.ch_le_overvolt_state[i],1,2)

            ch_lbl_overvolt_volt.append(QLabel('Voltage[V]:'))
            ch_layout_overvolt[i].addWidget(ch_lbl_overvolt_volt[i], 2,1)

            self.ch_le_overvolt_volt.append(QLineEdit())
            self.ch_le_overvolt_volt[i].setText("---")
            self.ch_le_overvolt_volt[i].setReadOnly(1)
            ch_layout_overvolt[i].addWidget(self.ch_le_overvolt_volt[i],2,2)

            ch_lbl_overvolt_volt_test.append(QLabel('Alarm:'))
            ch_layout_overvolt[i].addWidget(ch_lbl_overvolt_volt_test[i], 3,1)

            self.ch_le_overvolt_volt_test.append(QLineEdit())
            self.ch_le_overvolt_volt_test[i].setText("---")
            self.ch_le_overvolt_volt_test[i].setReadOnly(1)
            ch_layout_overvolt[i].addWidget(self.ch_le_overvolt_volt_test[i],3,2)
            
            self.ch_btn_overvolt_volt_test_clear.append(QPushButton('CLEAR', self))
            ch_layout_overvolt[i].addWidget(self.ch_btn_overvolt_volt_test_clear[i],3,3,1,2)

            self.ch_groupBox_overcurr.append(QGroupBox("Overcurrent protection"))
            self.ch_groupBox_overcurr[i].setCheckable(False)
            ch_layout_overcurr.append(QGridLayout())
            
            ch_lbl_overcurr_state.append(QLabel('State:'))
            ch_layout_overcurr[i].addWidget(ch_lbl_overcurr_state[i], 1,1)

            self.ch_le_overcurr_state.append(QLineEdit())
            self.ch_le_overcurr_state[i].setText("---")
            self.ch_le_overcurr_state[i].setReadOnly(1)
            ch_layout_overcurr[i].addWidget(self.ch_le_overcurr_state[i],1,2)

            ch_lbl_overcurr_curr.append(QLabel('Current[A]:'))
            ch_layout_overcurr[i].addWidget(ch_lbl_overcurr_curr[i], 2,1)

            self.ch_le_overcurr_curr.append(QLineEdit())
            self.ch_le_overcurr_curr[i].setText("---")
            self.ch_le_overcurr_curr[i].setReadOnly(1)
            ch_layout_overcurr[i].addWidget(self.ch_le_overcurr_curr[i],2,2)

            ch_lbl_overcurr_curr_test.append(QLabel('Alarm:'))
            ch_layout_overcurr[i].addWidget(ch_lbl_overcurr_curr_test[i], 3,1)

            self.ch_le_overcurr_curr_test.append(QLineEdit())
            self.ch_le_overcurr_curr_test[i].setText("---")
            self.ch_le_overcurr_curr_test[i].setReadOnly(1)
            ch_layout_overcurr[i].addWidget(self.ch_le_overcurr_curr_test[i],3,2)
            
            self.ch_btn_overcurr_curr_test_clear.append(QPushButton('CLEAR', self))
            ch_layout_overcurr[i].addWidget(self.ch_btn_overcurr_curr_test_clear[i],3,3,1,2)
            
            if i != 2:
                self.ch_groupBox_track.append(QGroupBox("Track function"))
                self.ch_groupBox_track[i].setCheckable(False)
                ch_layout_track.append(QGridLayout())

                ch_lbl_track_state.append(QLabel('State:         '))
                ch_layout_track[i].addWidget(ch_lbl_track_state[i], 1,1)

                self.ch_le_track_state.append(QLineEdit())
                self.ch_le_track_state[i].setText("---")
                self.ch_le_track_state[i].setReadOnly(1)
                ch_layout_track[i].addWidget(self.ch_le_track_state[i],1,2)

                ch_lbl_track_mode.append(QLabel('Mode:         '))
                ch_layout_track[i].addWidget(ch_lbl_track_mode[i], 2,1)

                self.ch_le_track_mode.append(QLineEdit())
                self.ch_le_track_mode[i].setText("---")
                self.ch_le_track_mode[i].setReadOnly(1)
                ch_layout_track[i].addWidget(self.ch_le_track_mode[i],2,2)

#===========
        self.ch_btn_read[0].clicked.connect(lambda: self.ch_read(0, self.ch_string[0]))
        self.ch_btn_read[1].clicked.connect(lambda: self.ch_read(1, self.ch_string[1]))
        self.ch_btn_read[2].clicked.connect(lambda: self.ch_read(2, self.ch_string[2]))
        self.ch_btn_overvolt_volt_test_clear[0].clicked.connect(lambda: self.ch_alarm_ovp_clean(0, self.ch_string[0]))
        self.ch_btn_overvolt_volt_test_clear[1].clicked.connect(lambda: self.ch_alarm_ovp_clean(1, self.ch_string[1]))
        self.ch_btn_overvolt_volt_test_clear[2].clicked.connect(lambda: self.ch_alarm_ovp_clean(2, self.ch_string[2]))
        self.ch_btn_overcurr_curr_test_clear[0].clicked.connect(lambda: self.ch_alarm_ocp_clean(0, self.ch_string[0]))
        self.ch_btn_overcurr_curr_test_clear[1].clicked.connect(lambda: self.ch_alarm_ocp_clean(1, self.ch_string[1]))
        self.ch_btn_overcurr_curr_test_clear[2].clicked.connect(lambda: self.ch_alarm_ocp_clean(2, self.ch_string[2]))
        self.ch_chbox_autoread[0].stateChanged.connect(lambda: self.ch_autoreadset(0, self.ch_string[0]))
        self.ch_chbox_autoread[1].stateChanged.connect(lambda: self.ch_autoreadset(1, self.ch_string[1]))
        self.ch_chbox_autoread[2].stateChanged.connect(lambda: self.ch_autoreadset(2, self.ch_string[2]))
#========  Channel LAYOUT - SET
        self.ch_btn_write = []
        self.ch_chbox_state = []
        self.ch_combo_state = []
        self.ch_chbox_volt = []
        self.ch_dspinbox_volt = []
        self.ch_chbox_curr = []
        self.ch_dspinbox_curr = []

        self.ch_chbox_overvolt_state = []
        self.ch_combo_overvolt_state = []
        self.ch_chbox_overvolt_volt = []
        self.ch_dspinbox_overvolt_volt = []

        self.ch_chbox_overcurr_state = []
        self.ch_combo_overcurr_state = []
        self.ch_chbox_overcurr_curr = []
        self.ch_dspinbox_overcurr_curr = []
     
        self.ch_chbox_track_state = []
        self.ch_combo_track_state = []
        self.ch_chbox_track_mode = []
        self.ch_combo_track_mode = []
        
        for i in range(0,self.NO_CHANNELS):
            self.ch_btn_write.append(QPushButton('SET', self))
            ch_layout[i].addWidget(self.ch_btn_write[i],1,3,1,2)

            self.ch_chbox_state.append(QCheckBox("State:"))
            self.ch_chbox_state[i].setChecked(False)
            ch_layout[i].addWidget(self.ch_chbox_state[i],3,3)

            self.ch_combo_state.append(QComboBox())
            self.ch_combo_state[i].addItem("OFF")
            self.ch_combo_state[i].addItem("ON")
            ch_layout[i].addWidget(self.ch_combo_state[i],3,4)
        
            self.ch_chbox_volt.append(QCheckBox('Voltage [V]:'))
            ch_layout[i].addWidget(self.ch_chbox_volt[i],4,3)

            self.ch_dspinbox_volt.append(QDoubleSpinBox())
            if i == 2:
                self.ch_dspinbox_volt[i].setRange(0,5)
            else:
                self.ch_dspinbox_volt[i].setRange(0,30)
            self.ch_dspinbox_volt[i].setSingleStep(0.01)
            self.ch_dspinbox_volt[i].setDecimals(2)
            ch_layout[i].addWidget(self.ch_dspinbox_volt[i],4,4)

            self.ch_chbox_curr.append(QCheckBox('Current [A]:'))
            ch_layout[i].addWidget(self.ch_chbox_curr[i],5,3)

            self.ch_dspinbox_curr.append(QDoubleSpinBox())
            self.ch_dspinbox_curr[i].setRange(0,3)
            self.ch_dspinbox_curr[i].setSingleStep(0.001)
            self.ch_dspinbox_curr[i].setDecimals(3)
            ch_layout[i].addWidget(self.ch_dspinbox_curr[i],5,4)

            self.ch_chbox_overvolt_state.append(QCheckBox("State:"))
            self.ch_chbox_overvolt_state[i].setChecked(False)
            ch_layout_overvolt[i].addWidget(self.ch_chbox_overvolt_state[i], 1,3)

            self.ch_combo_overvolt_state.append(QComboBox())
            self.ch_combo_overvolt_state[i].addItem("OFF")
            self.ch_combo_overvolt_state[i].addItem("ON")
            ch_layout_overvolt[i].addWidget(self.ch_combo_overvolt_state[i], 1,4)

            self.ch_chbox_overvolt_volt.append(QCheckBox("Voltage[V]:"))
            self.ch_chbox_overvolt_volt[i].setChecked(False)
            ch_layout_overvolt[i].addWidget(self.ch_chbox_overvolt_volt[i], 2,3)

            self.ch_dspinbox_overvolt_volt.append(QDoubleSpinBox())
            if i == 2:
                self.ch_dspinbox_overvolt_volt[i].setRange(0,5.5)
            else:
                self.ch_dspinbox_overvolt_volt[i].setRange(0,33)
            self.ch_dspinbox_overvolt_volt[i].setSingleStep(0.01)
            self.ch_dspinbox_overvolt_volt[i].setDecimals(2)
            ch_layout_overvolt[i].addWidget(self.ch_dspinbox_overvolt_volt[i],2,4)

            self.ch_chbox_overcurr_state.append(QCheckBox("State:"))
            self.ch_chbox_overcurr_state[i].setChecked(False)
            ch_layout_overcurr[i].addWidget(self.ch_chbox_overcurr_state[i], 1,3)

            self.ch_combo_overcurr_state.append(QComboBox())
            self.ch_combo_overcurr_state[i].addItem("OFF")
            self.ch_combo_overcurr_state[i].addItem("ON")
            ch_layout_overcurr[i].addWidget(self.ch_combo_overcurr_state[i], 1,4)

            self.ch_chbox_overcurr_curr.append(QCheckBox("Current[A]:"))
            self.ch_chbox_overcurr_curr[i].setChecked(False)
            ch_layout_overcurr[i].addWidget(self.ch_chbox_overcurr_curr[i], 2,3)

            self.ch_dspinbox_overcurr_curr.append(QDoubleSpinBox())
            self.ch_dspinbox_overcurr_curr[i].setRange(0,3.3)
            self.ch_dspinbox_overcurr_curr[i].setSingleStep(0.001)
            self.ch_dspinbox_overcurr_curr[i].setDecimals(3)
            ch_layout_overcurr[i].addWidget(self.ch_dspinbox_overcurr_curr[i],2,4)

            if i != 2:
                self.ch_chbox_track_state.append(QCheckBox("State:        "))
                self.ch_chbox_track_state[i].setChecked(False)
                ch_layout_track[i].addWidget(self.ch_chbox_track_state[i],1,3)

                self.ch_combo_track_state.append(QComboBox())
                self.ch_combo_track_state[i].addItem("OFF")
                self.ch_combo_track_state[i].addItem("ON")
                ch_layout_track[i].addWidget(self.ch_combo_track_state[i],1,4)

                self.ch_chbox_track_mode.append(QCheckBox("Mode:        "))
                self.ch_chbox_track_mode[i].setChecked(False)
                ch_layout_track[i].addWidget(self.ch_chbox_track_mode[i],2,3)

                self.ch_combo_track_mode.append(QComboBox())
                self.ch_combo_track_mode[i].addItem("SYNC")
                self.ch_combo_track_mode[i].addItem("INDE")
                ch_layout_track[i].addWidget(self.ch_combo_track_mode[i],2,4)
#===========
        self.ch_btn_write[0].clicked.connect(lambda: self.ch_write(0, self.ch_string[0]))
        self.ch_btn_write[1].clicked.connect(lambda: self.ch_write(1, self.ch_string[1]))
        self.ch_btn_write[2].clicked.connect(lambda: self.ch_write(2, self.ch_string[2]))
        for i in range(0,self.NO_CHANNELS):
            self.ch_groupBox_overvolt[i].setLayout(ch_layout_overvolt[i])
            self.ch_groupBox_overcurr[i].setLayout(ch_layout_overcurr[i])
            ch_layout[i].addWidget(self.ch_groupBox_overvolt[i], 7, 1, 1,4) ## 6,1; 6,5; 6,9
            ch_layout[i].addWidget(self.ch_groupBox_overcurr[i], 8, 1, 1,4) ## 7,1; 7,5; 7,9
            if i != 2:
                self.ch_groupBox_track[i].setLayout(ch_layout_track[i])
                ch_layout[i].addWidget(self.ch_groupBox_track[i], 9, 1, 1, 4) 
            self.ch_groupBox[i].setLayout(ch_layout[i])
#======== Channel LAYOUT END
        for i in range(0,self.NO_CHANNELS):
            mainLayout.addWidget(self.ch_groupBox[i],4,(i*2)+1,1,2)
        self.dp832_widget.setLayout(mainLayout)
        #self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('RIGOL DP832 GUI')
        self.setWindowIcon(QIcon('DP832.jpg'))
   
    def closeEvent(self, event):
        if hasattr(DP832, 'self.main_rigol_inst'):
            try:
                self.main_rigol_inst.close()
            except Exception as ex:
                self.showWarning("from close", str(ex))
                print(ex)
        if hasattr(DP832, 'self.main_rigol_rm'):
            try:
                self.main_rigol_rm.close()
            except Exception as ex:
                self.showWarning("from close", str(ex))
                print(ex)
                
    def ch_autoreadset(self, no, string):
        time = self.ch_spinbox_autoread[no].value() * 1000
        self.timer[no].setInterval(time)
        if self.ch_chbox_autoread[no].isChecked() == True:
            self.timer[no].start(0)
            self.ch_spinbox_autoread[no].setEnabled(False)
            self.ch_btn_read[no].setEnabled(False)
            self.ch_btn_write[no].setEnabled(False)
        else:
            self.timer[no].stop()
            self.ch_spinbox_autoread[no].setEnabled(True)
            self.ch_btn_read[no].setEnabled(True)
            self.ch_btn_write[no].setEnabled(True)
            self.ch_le_autoread[no].setText('')

    def ch_set(self, no, string):
        for i in range(0,self.NO_CHANNELS):
            if i != no:
                self.ch_groupBox[i].setChecked(False)
        try:
            data = self.main_rigol_inst.query(':APPL '+ string +'; *OPC?')
        except Exception as ex:
            self.showWarning("from query", str(ex))
            print(ex)
            return
        if data != '1\n':
            data = self.main_rigol_inst.query(':SYSTem:ERRor?')
            self.showWarning("from reading", str(data))
            print(data)
            return
        
    def ch_read(self, no, string):
        time = "("+ datetime.now().strftime('%Y-%m-%d %H:%M:%S') +")"
        if self.ch_chbox_autoread[no].isChecked() == False:
            self.ch_btn_read[no].setText("READ "+time)
        else:
            self.ch_le_autoread[no].setText(time)
        
        try:
            data = self.main_rigol_inst.query(':OUTP? '+ string +'; *OPC?')
        except Exception as ex:
            self.showWarning("from query", str(ex))
            print(ex)
            return
        data = data.rsplit(';')

        if data[1] == '1\n':
            self.ch_le_state[no].setText(data[0])
        else:
            data = self.main_rigol_inst.query(':SYSTem:ERRor?')
            self.showWarning("from reading", str(data))
            print(data)
            return

        if data[0] == "ON":
            try:
                parts = self.main_rigol_inst.query(':MEASure:ALL? ' + string +'; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            parts = parts.rsplit(';')
            if parts[1] == '1\n':
                data = parts[0].rsplit(',')
                #workaround: doing ALL command gives strange values / CURR shows 0.000
                if float(data[1]) == 429496.719 and float(data[2]) == 429496.719:
                    data[1] = '0.000'
                    data[2] = '0.000'
                self.ch_le_volt[no].setText(data[0])
                self.ch_le_curr[no].setText(data[1])
                self.ch_le_power[no].setText(data[2])
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return

            try:
                data = self.main_rigol_inst.query(':APPL? '+ string +',VOLTage; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            data = data.rsplit(';')
            if data[1] == '1\n':
                self.ch_dspinbox_volt[no].setValue(float(data[0]))
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return

            try:
                data = self.main_rigol_inst.query(':APPL? '+ string +',CURRent; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            data = data.rsplit(';')
            if data[1] == '1\n':
                self.ch_dspinbox_curr[no].setValue(float(data[0]))
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return
        else:
            self.ch_le_volt[no].setText("---")
            self.ch_le_curr[no].setText("---")
            self.ch_le_power[no].setText("---")
            self.ch_dspinbox_volt[no].setValue(0.00)
            self.ch_dspinbox_curr[no].setValue(0.000)

        try:
            data = self.main_rigol_inst.query(':OUTP:OVP? '+ string +'; *OPC?')
        except Exception as ex:
            self.showWarning("from query", str(ex))
            print(ex)
            return
        data = data.rsplit(';')
        if data[1] == '1\n':
            self.ch_le_overvolt_state[no].setText(data[0])
        else:
            data = self.main_rigol_inst.query(':SYSTem:ERRor?')
            self.showWarning("from reading", str(data))
            print(data)
            return

        if data[0] == "ON":
            try:
                data = self.main_rigol_inst.query(':OUTP:OVP:VAL? '+ string +'; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            data = data.rsplit(';')
            
            if data[1] == '1\n':
                self.ch_le_overvolt_volt[no].setText(data[0])
                self.ch_dspinbox_overvolt_volt[no].setValue(float(data[0]))
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return

            try:
                data = self.main_rigol_inst.query(':OUTP:OVP:ALAR? '+ string +'; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            data = data.rsplit(';')
            
            if data[1] == '1\n':
                self.ch_le_overvolt_volt_test[no].setText(data[0])
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return
        else:
            self.ch_le_overvolt_volt[no].setText("---")
            self.ch_le_overvolt_volt_test[no].setText("---")
        
        data = self.main_rigol_inst.query(':OUTP:OCP? '+ string +'; *OPC?')
        data = data.rsplit(';')
        if data[1] == '1\n':
            self.ch_le_overcurr_state[no].setText(data[0])
        else:
            data = self.main_rigol_inst.query(':SYSTem:ERRor?')
            self.showWarning("from reading", str(data))
            print(data)
            return

        if data[0] == "ON":
            try:
                data = self.main_rigol_inst.query(':OUTP:OCP:VAL? '+ string +'; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            data = data.rsplit(';')
            if data[1] == '1\n':
                self.ch_le_overcurr_curr[no].setText(data[0])
                self.ch_dspinbox_overcurr_curr[no].setValue(float(data[0]))
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return

            try:
                data = self.main_rigol_inst.query(':OUTP:OCP:ALAR? '+ string +'; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            data = data.rsplit(';')
            if data[1] == '1\n':
                self.ch_le_overcurr_curr_test[no].setText(data[0])
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return
        else:
            self.ch_le_overcurr_curr[no].setText("---")
            self.ch_le_overcurr_curr_test[no].setText("---")

        if no != 2:
            try:
                data = self.main_rigol_inst.query(':OUTP:TRAC? '+ string +'; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            data = data.rsplit(';')
            #workaround for error
            if len(data) == 3:
                data.remove('')
            if data[1] == '1\n':
                self.ch_le_track_state[no].setText(data[0])
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return

            try:
                data = self.main_rigol_inst.query(':SYST:TRACKM?; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            data = data.rsplit(';')
            if data[1] == '1\n':
                self.ch_le_track_mode[no].setText(data[0])
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return
        

    def ch_write(self, no, string):
        button_newText = "SET "+"("+ datetime.now().strftime('%H:%M:%S') +")"
        self.ch_btn_write[no].setText(button_newText)
        
        if self.ch_chbox_state[no].isChecked() == True:
            if self.ch_combo_state[no].currentText() == "ON":
                try:
                    data = self.main_rigol_inst.query(':OUTP '+ string +',ON; *OPC?')
                except Exception as ex:
                    self.showWarning("from query", str(ex))
                    print(ex)
                    return
                if data != '1\n':
                    return
                time.sleep(1)
                self.ch_le_state[no].setText("ON")
                    
                try:
                    parts = self.main_rigol_inst.query(':MEASure:ALL? ' + string +'; *OPC?')
                except Exception as ex:
                    self.showWarning("from query", str(ex))
                    print(ex)
                    return
                parts = parts.rsplit(';')
                if parts[1] == '1\n':
                    data = parts[0].rsplit(',')
                    #workaround: doing ALL command gives strange values / CURR shows 0.000
                    if float(data[1]) == 429496.719 and float(data[2]) == 429496.719:
                        data[1] = '0.000'
                        data[2] = '0.000'
                    self.ch_le_volt[no].setText(data[0])
                    self.ch_le_curr[no].setText(data[1])
                    self.ch_le_power[no].setText(data[2])
                    self.ch_dspinbox_volt[no].setValue(float(data[0]))
                    self.ch_dspinbox_curr[no].setValue(float(data[1]))
                else:
                    data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                    self.showWarning("from reading", str(data))
                    print(data)
                    return
            else:
                try:
                    data = self.main_rigol_inst.query(':OUTP '+ string +',OFF; *OPC?')
                except Exception as ex:
                    self.showWarning("from query", str(ex))
                    print(ex)
                    return
                if data != '1\n':
                    return
                self.ch_le_state[no].setText("OFF")
                self.ch_le_volt[no].setText("---")
                self.ch_le_curr[no].setText("---")
                self.ch_le_power[no].setText("---")
                self.ch_dspinbox_volt[no].setValue(0.00)
                self.ch_dspinbox_curr[no].setValue(0.000)
        
        if self.ch_chbox_volt[no].isChecked() == True:
            try:
                data = self.main_rigol_inst.query(':APPL? '+ string +',CURRent; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            data = data.rsplit(';')
            if data[1] == '1\n':
                voltage = ":APPL {:3},{:.2f},{:.3f}".format(string, self.ch_dspinbox_volt[no].value(), float(data[0]))
                self.main_rigol_inst.write(voltage)
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return

        if self.ch_chbox_curr[no].isChecked() == True:
            try:
                data = self.main_rigol_inst.query(':APPL? '+ string +',VOLTage; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            data = data.rsplit(';')
            if data[1] == '1\n':
                current = ":APPL {:3},{:.2f},{:.3f}".format(string, float(data[0]), self.ch_dspinbox_curr[no].value())
                self.main_rigol_inst.write(current)
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return

        if self.ch_chbox_overvolt_state[no].isChecked() == True:
            if self.ch_combo_overvolt_state[no].currentText() == "ON":
                try:
                    data = self.main_rigol_inst.query(':OUTP:OVP '+ string +',ON; *OPC?')
                except Exception as ex:
                    self.showWarning("from query", str(ex))
                    print(ex)
                    return
                if data != '1\n':
                    return
                time.sleep(1)
                self.ch_le_overvolt_state[no].setText("ON")
                try:
                    data = self.main_rigol_inst.query(':OUTP:OVP:VAL? '+ string +'; *OPC?')
                except Exception as ex:
                    self.showWarning("from query", str(ex))
                    print(ex)
                    return
                data = data.rsplit(';')
                
                if data[1] == '1\n':
                    self.ch_le_overvolt_volt[no].setText(data[0])
                    self.ch_dspinbox_overvolt_volt[no].setValue(float(data[0]))
                else:
                    data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                    self.showWarning("from reading", str(data))
                    print(data)
                    return
                try:
                    data = self.main_rigol_inst.query(':OUTP:OVP:ALAR? '+ string +'; *OPC?')
                except Exception as ex:
                    self.showWarning("from query", str(ex))
                    print(ex)
                    return
                data = data.rsplit(';')
                if data[1] == '1\n':
                    self.ch_le_overvolt_volt_test[no].setText(data[0])
                else:
                    data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                    self.showWarning("from reading", str(data))
                    print(data)
                    return
            else:
                try:
                    data = self.main_rigol_inst.query(':OUTP:OVP '+ string +',OFF; *OPC?')
                except Exception as ex:
                    self.showWarning("from query", str(ex))
                    print(ex)
                    return
                if data != '1\n':
                    return
                self.ch_le_overvolt_state[no].setText("OFF")
                self.ch_le_overvolt_volt[no].setText("---")
                self.ch_le_overvolt_volt_test[no].setText("---")
                self.ch_dspinbox_overvolt_volt[no].setValue(0.00)

        if self.ch_chbox_overvolt_volt[no].isChecked() == True:
            ovp = ":OUTP:OVP:VAL {:3},{:.2f}; *OPC?".format(string, self.ch_dspinbox_overvolt_volt[no].value())
            try:
                data = self.main_rigol_inst.query(ovp);
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            if data != '1\n':
                return
            time.sleep(1)
            try:
                data = self.main_rigol_inst.query(':OUTP:OVP:VAL? '+ string +'; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            data = data.rsplit(';')
            
            if data[1] == '1\n':
                self.ch_le_overvolt_volt[no].setText(data[0])
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return

        if self.ch_chbox_overcurr_state[no].isChecked() == True:
            if self.ch_combo_overcurr_state[no].currentText() == "ON":
                try:
                    data = self.main_rigol_inst.query(':OUTP:OCP '+ string +',ON; *OPC?')
                except Exception as ex:
                    self.showWarning("from query", str(ex))
                    print(ex)
                    return
                if data != '1\n':
                    return
                time.sleep(1)
                self.ch_le_overcurr_state[no].setText("ON")
                try:
                    data = self.main_rigol_inst.query(':OUTP:OCP:VAL? '+ string +'; *OPC?')
                except Exception as ex:
                    self.showWarning("from query", str(ex))
                    print(ex)
                    return
                data = data.rsplit(';')
                if data[1] == '1\n':
                    self.ch_le_overcurr_curr[no].setText(data[0])
                    self.ch_dspinbox_overcurr_curr[no].setValue(float(data[0]))
                else:
                    data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                    self.showWarning("from reading", str(data))
                    print(data)
                    return

                try:
                    data = self.main_rigol_inst.query(':OUTP:OCP:ALAR? '+ string +'; *OPC?')
                except Exception as ex:
                    self.showWarning("from query", str(ex))
                    print(ex)
                    return
                data = data.rsplit(';')
                if data[1] == '1\n':
                    self.ch_le_overcurr_curr_test[no].setText(data[0])
                else:
                    data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                    self.showWarning("from reading", str(data))
                    print(data)
                    return
            else:
                try:
                    data = self.main_rigol_inst.query(':OUTP:OCP '+ string +',OFF; *OPC?')
                except Exception as ex:
                    self.showWarning("from query", str(ex))
                    print(ex)
                    return
                if data != '1\n':
                    return
                self.ch_le_overcurr_state[no].setText("OFF")
                self.ch_le_overcurr_curr[no].setText("---")
                self.ch_le_overcurr_curr_test[no].setText("---")
                self.ch_dspinbox_overcurr_curr[no].setValue(0.000)

        if self.ch_chbox_overcurr_curr[no].isChecked() == True:
            ocp = ":OUTP:OCP:VAL {:3},{:.3f}; *OPC?".format(string, self.ch_dspinbox_overcurr_curr[no].value())
            try:
                data = self.main_rigol_inst.query(ovp);
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            if data != '1\n':
                return
            time.sleep(1)
            try:
                data = self.main_rigol_inst.query(':OUTP:OCP:VAL? '+ string +'; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            data = data.rsplit(';')
            
            if data[1] == '1\n':
                self.ch_le_overcurr_curr[no].setText(data[0])
            else:
                data = self.main_rigol_inst.query(':SYSTem:ERRor?')
                self.showWarning("from reading", str(data))
                print(data)
                return

        if no != 2:
            if self.ch_chbox_track_state[no].isChecked() == True:
                if self.ch_combo_track_state[no].currentText() == "ON":
                    try:
                        data = self.main_rigol_inst.query(':OUTP:TRAC '+ string +',ON; *OPC?')
                    except Exception as ex:
                        self.showWarning("from query", str(ex))
                        print(ex)
                        return
                    if data != '1\n':
                        return
                    self.ch_le_track_state[no].setText("ON")
                else:
                    try:
                        data = self.main_rigol_inst.query(':OUTP:TRAC '+ string +',OFF; *OPC?')
                    except Exception as ex:
                        self.showWarning("from query", str(ex))
                        print(ex)
                        return
                    if data != '1\n':
                        return
                    self.ch_le_track_state[no].setText("OFF")

            if self.ch_chbox_track_mode[no].isChecked() == True:
                if self.ch_combo_track_mode[no].currentText() == "SYNC":
                    try:
                        data = self.main_rigol_inst.query(':SYST:TRACKM SYNC; *OPC?')
                    except Exception as ex:
                        self.showWarning("from query", str(ex))
                        print(ex)
                        return
                    if data != '1\n':
                        return
                    self.ch_le_track_mode[no].setText("SYNC")
                else:
                    try:
                        data = self.main_rigol_inst.query(':SYST:TRACKM INDE; *OPC?')
                    except Exception as ex:
                        self.showWarning("from query", str(ex))
                        print(ex)
                        return
                    if data != '1\n':
                        return
                    self.ch_le_track_mode[no].setText("INDE")

    def ch_alarm_ovp_clean(self, no, string):
        try:
            data = self.main_rigol_inst.query(':OUTPut:OVP:CLEAR '+ string +'; *OPC?')
        except Exception as ex:
            self.showWarning("from query", str(ex))
            print(ex)
            return
        if data != '1\n':
            return
        self.ch_le_overvolt_volt_test[no].setText("NO")
                
    def ch_alarm_ocp_clean(self, no, string):
        try:
            data = self.main_rigol_inst.query(':OUTPut:OCP:CLEAR '+ string +'; *OPC?')
        except Exception as ex:
            self.showWarning("from query", str(ex))
            print(ex)
            return
        if data != '1\n':
            return
        self.ch_le_overcurr_curr_test[no].setText("NO")

    def main_connect(self):
        #visa.log_to_screen()
        try: 
            self.main_rigol_rm = visa.ResourceManager()
        except Exception as ex:
            self.showWarning("from ResourceManager", str(ex))
            print(ex)
            return
        if self.main_rigol_rm.last_status == 0:
            self.main_rigol_hosting = "TCPIP::" + self.main_le_ipaddr.text() + "::inst0::INSTR"
            try:
                self.main_rigol_inst = self.main_rigol_rm.open_resource(self.main_rigol_hosting)
            except Exception as ex:
                self.showWarning("from open_resource", str(ex))
                self.main_rigol_rm.close()
                print(ex)
                return
            inst = self.main_rigol_inst.write('*CLS')
            inst = self.main_rigol_inst.query('*IDN?')
            self.main_rigol_connected = "Connected: "+str(inst.rstrip('\n'))+" ("+ datetime.now().strftime('%Y-%m-%d %H:%M:%S') +") "
            self.main_btn_connect.setEnabled(False)
            self.main_btn_disconnect.setEnabled(True)
            self.main_btn_plot.setEnabled(True)
            for i in range(0,self.NO_CHANNELS):
                self.ch_groupBox[i].setEnabled(True)
            self.ch_groupBox[0].setChecked(True)
            try:
                data = self.main_rigol_inst.query(':APPL CH1; *OPC?')
            except Exception as ex:
                self.showWarning("from query", str(ex))
                print(ex)
                return
            if data != '1\n':
                return
            self.main_lbl_instr.setText(self.main_rigol_connected)
        else:
            self.main_lbl_instr.setText("Disconnected: " + str(self.main_rigol_rm.last_status) )

        self.main_rigol_inst.chunk_size = 2048

    def main_disconnect(self):
        self.main_btn_connect.setEnabled(True)
        self.main_btn_disconnect.setEnabled(False)
        self.main_btn_plot.setEnabled(False)
        for i in range(0,self.NO_CHANNELS):
            self.ch_groupBox[i].setChecked(False)
            self.ch_groupBox[i].setEnabled(False)
            self.timer[i].stop()
            self.ch_le_autoread[i].setText('')
            self.ch_chbox_autoread[i].setChecked(False)
        self.main_lbl_instr.setText("Disconnected "+" ("+ datetime.now().strftime('%Y-%m-%d %H:%M:%S') +") ")
        try:
            self.main_rigol_inst.close()
        except Exception as ex:
            self.showWarning("from disconnecting", str(ex))
            print(ex)
        try:
            self.main_rigol_rm.close()
        except Exception as ex:
            self.showWarning("from disconnecting", str(ex))
            print(ex)
            
    def showWarning(self, string1, string2):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("WARNING: "+string1)
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(string2)
        msgBox.exec_();
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = DP832()
    ex.show()
    sys.exit(app.exec_())  
