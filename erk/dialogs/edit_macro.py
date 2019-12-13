#
#  Erk IRC Client
#  Copyright (C) 2019  Daniel Hetrick
#               _   _       _                         
#              | | (_)     | |                        
#   _ __  _   _| |_ _  ___ | |__                      
#  | '_ \| | | | __| |/ _ \| '_ \                     
#  | | | | |_| | |_| | (_) | |_) |                    
#  |_| |_|\__,_|\__| |\___/|_.__/ _                   
#  | |     | |    _/ |           | |                  
#  | | __ _| |__ |__/_  _ __ __ _| |_ ___  _ __ _   _ 
#  | |/ _` | '_ \ / _ \| '__/ _` | __/ _ \| '__| | | |
#  | | (_| | |_) | (_) | | | (_| | || (_) | |  | |_| |
#  |_|\__,_|_.__/ \___/|_|  \__,_|\__\___/|_|   \__, |
#                                                __/ |
#                                               |___/ 
#  https://github.com/nutjob-laboratories
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from erk.resources import *
from erk.strings import *
from erk.config import *

import erk.macro

class Dialog(QDialog):

	@staticmethod
	def get_macro_information(filename,parent=None):
		dialog = Dialog(filename,parent)
		r = dialog.exec_()
		if r:
			return dialog.return_info()
		return None

		self.close()

	def return_info(self):

		#retval = self.linecount.value()
		#retval = 1

		macro = {}
		macro["trigger"] = self.trigger.text()
		macro["arguments"] = {}
		macro["arguments"]["minimum"] = self.minargs.value()
		macro["arguments"]["maximum"] = self.maxargs.value()
		macro["output"] = self.output.text()

		with open(self.filename, "w") as write_data:
			json.dump(macro, write_data, indent=4, sort_keys=True)

		macro["filename"] = self.filename

		erk.macro.add_new_macro(macro)

		return True

	def minvaluechange(self):
		minargs = self.minargs.value()
		maxargs = self.maxargs.value()

		if maxargs<minargs and maxargs!=0: self.maxargs.setValue(minargs)

	def maxvaluechange(self):
		minargs = self.minargs.value()
		maxargs = self.maxargs.value()

		if maxargs<minargs and maxargs!=0: self.minargs.setValue(maxargs)

	def __init__(self,filename,parent=None):
		super(Dialog,self).__init__(parent)

		self.parent = parent
		self.filename = filename

		self.base = os.path.basename(filename)

		with open(filename, "r") as macrofile:
			self.macro = json.load(macrofile)

		self.setWindowTitle(self.macro["trigger"])
		self.setWindowIcon(QIcon(MACRO_ICON))

		triggerLayout = QHBoxLayout()
		# triggerLayout.addStretch()
		self.triggerLabel = QLabel("Trigger")
		self.trigger = QLineEdit(self.macro["trigger"])
		triggerLayout.addWidget(self.triggerLabel)
		triggerLayout.addWidget(self.trigger)
		# triggerLayout.addStretch()

		minargsLayout = QHBoxLayout()
		self.minargsLabel = QLabel("Minimum # of arguments")
		self.minargs = QSpinBox()
		self.minargs.setRange(0,10)
		self.minargs.setValue(self.macro["arguments"]["minimum"])
		minargsLayout.addWidget(self.minargsLabel)
		minargsLayout.addWidget(self.minargs)

		maxargsLayout = QHBoxLayout()
		self.maxargsLabel = QLabel("Maximum # of arguments")
		self.maxargs = QSpinBox()
		self.maxargs.setRange(0,10)
		self.maxargs.setValue(self.macro["arguments"]["maximum"])
		maxargsLayout.addWidget(self.maxargsLabel)
		maxargsLayout.addWidget(self.maxargs)

		self.minargs.valueChanged.connect(self.minvaluechange)
		self.maxargs.valueChanged.connect(self.maxvaluechange)

		outputLayout = QHBoxLayout()
		# outputLayout.addStretch()
		self.outputLabel = QLabel("Output")
		self.output = QLineEdit(self.macro["output"])
		outputLayout.addWidget(self.outputLabel)
		outputLayout.addWidget(self.output)
		# outputLayout.addStretch()

		# Buttons
		buttons = QDialogButtonBox(self)
		buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)

		buttons.button(QDialogButtonBox.Ok).setText("Save")

		# filedisplay = QLabel("<b><i>"+self.base+"</i></b>")
		# filedisplay.setAlignment(Qt.AlignCenter)

		fileBox = QGroupBox(self.base)
		fileBox.setAlignment(Qt.AlignHCenter)

		finalLayout = QVBoxLayout()
		#finalLayout.addWidget(filedisplay)
		finalLayout.addLayout(triggerLayout)
		finalLayout.addStretch()
		finalLayout.addWidget(QLabel('''
			<small><br>Every word typed after the macro's trigger is an<br>
			argument to the macro; arguments are delimited<br>
			by spaces.</small>
			'''))
		finalLayout.addLayout(minargsLayout)
		finalLayout.addStretch()
		finalLayout.addWidget(QLabel('''
			<small><br>Set maximum # of arguments to 0 (zero) to accept an<br>
			unlimited number of arguments</small>
			'''))
		finalLayout.addLayout(maxargsLayout)
		finalLayout.addStretch()
		finalLayout.addWidget(QLabel('''
			<small><br><b>$0</b> is replaced with all arguments to the macro.<br>
			For each subsequent argument, <b>$<i>n</i></b> is replaced with<br>
			the appropriate argument (<b>$1</b> for the first argument,<br>
			<b>$2</b> for the second argument, etc.)</small>
			'''))
		finalLayout.addLayout(outputLayout)
		finalLayout.addWidget(buttons)

		fileBox.setLayout(finalLayout)

		fileLayout = QVBoxLayout()
		fileLayout.addWidget(fileBox)

		self.setWindowFlags(self.windowFlags()
					^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(fileLayout)