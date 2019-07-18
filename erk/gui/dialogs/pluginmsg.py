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

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from erk.common import *

class Dialog(QDialog):

	@staticmethod
	def get_cmd_information(ctype,parent=None):
		dialog = Dialog(ctype,parent)
		r = dialog.exec_()
		if r:
			return dialog.return_list()
		return None

	def return_list(self):
		target = str(self.name.text())
		msg = str(self.msg.text())
		sid = str(self.sid.text())

		return [target,msg,sid]

	def __init__(self,ctype,parent=None):
		super(Dialog,self).__init__(parent)

		self.parent = parent

		if ctype=="msg":
			self.setWindowTitle(f"Plugin.msg()")
		elif ctype=="notice":
			self.setWindowTitle(f"Plugin.notice()")
		elif ctype=="action":
			self.setWindowTitle(f"Plugin.action()")
		
		self.setWindowIcon(QIcon(EDIT_ICON))

		nameLayout = QHBoxLayout()
		self.nameLabel = QLabel("<b>Target</b>")
		self.name = QLineEdit()
		nameLayout.addWidget(self.nameLabel)
		nameLayout.addWidget(self.name)

		msgLayout = QHBoxLayout()
		self.msgLabel = QLabel("<b>Message</b>")
		self.msg = QLineEdit()
		msgLayout.addWidget(self.msgLabel)
		msgLayout.addWidget(self.msg)

		sidLayout = QHBoxLayout()
		self.sidLabel = QLabel("<i>Server ID</i>")
		self.sid = QLineEdit()
		sidLayout.addWidget(self.sidLabel)
		sidLayout.addWidget(self.sid)

		# Buttons
		buttons = QDialogButtonBox(self)
		buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)

		self.optLabel = QLabel("Arguments in <i>italics</i> are optional")

		finalLayout = QVBoxLayout()
		finalLayout.addLayout(nameLayout)
		finalLayout.addLayout(msgLayout)
		finalLayout.addLayout(sidLayout)
		finalLayout.addStretch()
		finalLayout.addWidget(self.optLabel)
		finalLayout.addWidget(buttons)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)
