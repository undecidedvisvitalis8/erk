from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

import os
import uuid

from ..syntax import *
from ..files import *
from ..resources import *
from ..strings import *
from ..widgets.action import MenuAction,insertNoTextSeparator
from .. import userinput

class Window(QMainWindow):

	def doRun(self):
		if self.current_client!=None:
			code = self.editor.toPlainText()
			userinput.execute_code(code,self.current_client,self.scriptError)

	def scriptError(self,error):
		e = error[1]
		ep = e.split(':')
		if len(ep)==2:
			if "wait" in ep[0]:
				# wrong arg to /wait
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Critical)
				msg.setText("Script error")
				msg.setInformativeText(ep[1])
				msg.setWindowTitle("/wait")
				msg.exec_()
			elif 'argcount' in ep[0]:
				# wrong arg to /argcount
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Critical)
				msg.setText("Script error")
				msg.setInformativeText(ep[1])
				msg.setWindowTitle("/argcount")
				msg.exec_()
			elif 'alias' in ep[0]:
				# wrong arg to /argcount
				msg = QMessageBox()
				msg.setIcon(QMessageBox.Critical)
				msg.setText("Script error")
				msg.setInformativeText(ep[1])
				msg.setWindowTitle("/alias")
				msg.exec_()

	def closeEvent(self, event):

		if self.changed:
			options = QFileDialog.Options()
			options |= QFileDialog.DontUseNativeDialog
			fileName, _ = QFileDialog.getSaveFileName(self,"Save Script As...",self.parent.scriptsdir,f"{APPLICATION_NAME} Script (*.{SCRIPT_FILE_EXTENSION});;All Files (*)", options=options)
			if fileName:
				efl = len(SCRIPT_FILE_EXTENSION)+1
				if fileName[-efl:].lower()!=f".{SCRIPT_FILE_EXTENSION}": fileName = fileName+f".{SCRIPT_FILE_EXTENSION}"
				self.filename = fileName
				code = open(self.filename,"w")
				code.write(self.editor.toPlainText())
				code.close()

		self.parent.seditors = None
		event.accept()
		self.close()

	def clientsRefreshed(self,clients):
		if len(clients)!=len(self.clients):
			self.clients = list(clients)

		if len(self.clients)==0:
			self.current_client = None

		found = False
		for c in self.clients:
			if c!=None:
				if self.current_client!=None:
					if c.id==self.current_client.id: found = True

		if not found: self.current_client = None

		if self.current_client == None:
			if len(self.clients)>0:
				self.current_client = self.clients[0]
				self.status_client.setText(  "&nbsp;<small><i>"+self.clients[0].server+":"+str(self.clients[0].port)+" ("+self.clients[0].nickname+")</i></small>"    )

		self.servers.clear()
		i = -1
		selected = None
		for c in self.clients:
			i = i + 1
			if self.current_client!=None:
				if c.id==self.current_client.id: selected = i
			if c.hostname:
				servername = c.hostname
			else:
				servername = c.server+":"+str(c.port)
			self.servers.addItem(servername+" ("+c.nickname+")")

		if selected!=None:
			self.servers.setCurrentIndex(selected)

		if self.current_client==None:
			self.status_client.setText("&nbsp;<small><i>&nbsp;</i></small>")
			self.runButton.setEnabled(False)
			self.servers.setEnabled(False)
		else:
			self.runButton.setEnabled(True)
			self.servers.setEnabled(True)

		self.generateFileMenu()

	def setServer(self):

		index = self.servers.currentIndex()

		if len(self.clients)>0:
			self.current_client = self.clients[index]
			self.status_client.setText(  "&nbsp;<small><i>"+self.clients[index].server+":"+str(self.clients[index].port)+" ("+self.clients[index].nickname+")</i></small>"    )
			self.servers.setCurrentIndex(index)

		self.generateFileMenu()

	def __init__(self,filename=None,parent=None):
		super(Window, self).__init__(parent)

		self.filename = filename
		self.parent = parent

		self.changed = False

		self.id = uuid.uuid1()

		self.clients = []
		self.current_client = None

		self.editor = QPlainTextEdit(self)
		self.highlight = ErkScriptHighlighter(self.editor.document())

		self.setWindowIcon(QIcon(SCRIPT_ICON))

		self.editor.textChanged.connect(self.docModified)
		self.editor.redoAvailable.connect(self.hasRedo)
		self.editor.undoAvailable.connect(self.hasUndo)
		self.editor.copyAvailable.connect(self.hasCopy)

		if self.filename:
			f = find_script_file(self.filename,self.parent.scriptsdir)
			if f!=None:
				x = open(f,mode="r",encoding="latin-1")
				source_code = str(x.read())
				x.close()
				self.editor.setPlainText(source_code)

		self.menubar = self.menuBar()

		self.status = self.statusBar()
		self.status.setStyleSheet('QStatusBar::item {border: None;}')

		self.status_client = QLabel("&nbsp;<small><i>&nbsp;</i></small>")
		self.status.addPermanentWidget(self.status_client,0)

		self.status_spacer = QLabel("")
		self.status.addPermanentWidget(self.status_spacer,1)

		self.servers = QComboBox(self)
		self.servers.activated.connect(self.setServer)

		runIcon = QIcon(RUN_ICON)

		self.runButton = QPushButton(runIcon,'')
		self.runButton.clicked.connect(self.doRun)
		self.runButton.setEnabled(False)

		height = self.servers.frameGeometry().height()

		self.runButton.setFixedSize(height,height)
		self.runButton.setIconSize(QSize(height,height))
		self.runButton.setStyleSheet("border: none;")

		self.fileMenu = self.menubar.addMenu("File")

		self.generateFileMenu()

		editMenu = self.menubar.addMenu("Edit")

		entry = QAction(QIcon(SELECTALL_ICON),"Select All",self)
		entry.triggered.connect(self.editor.selectAll)
		entry.setShortcut("Ctrl+A")
		editMenu.addAction(entry)

		insertNoTextSeparator(self.parent,editMenu)

		self.menuUndo = QAction(QIcon(UNDO_ICON),"Undo",self)
		self.menuUndo.triggered.connect(self.editor.undo)
		self.menuUndo.setShortcut("Ctrl+Z")
		editMenu.addAction(self.menuUndo)
		self.menuUndo.setEnabled(False)

		self.menuRedo = QAction(QIcon(REDO_ICON),"Redo",self)
		self.menuRedo.triggered.connect(self.editor.redo)
		self.menuRedo.setShortcut("Ctrl+Y")
		editMenu.addAction(self.menuRedo)
		self.menuRedo.setEnabled(False)

		insertNoTextSeparator(self.parent,editMenu)

		self.menuCut = QAction(QIcon(CUT_ICON),"Cut",self)
		self.menuCut.triggered.connect(self.editor.cut)
		self.menuCut.setShortcut("Ctrl+X")
		editMenu.addAction(self.menuCut)
		self.menuCut.setEnabled(False)

		self.menuCopy = QAction(QIcon(COPY_ICON),"Copy",self)
		self.menuCopy.triggered.connect(self.editor.copy)
		self.menuCopy.setShortcut("Ctrl+C")
		editMenu.addAction(self.menuCopy)
		self.menuCopy.setEnabled(False)

		self.menuPaste = QAction(QIcon(CLIPBOARD_ICON),"Paste",self)
		self.menuPaste.triggered.connect(self.editor.paste)
		self.menuPaste.setShortcut("Ctrl+V")
		editMenu.addAction(self.menuPaste)

		insertNoTextSeparator(self.parent,editMenu)

		self.menuZoomIn = QAction(QIcon(PLUS_ICON),"Zoom in",self)
		self.menuZoomIn.triggered.connect(self.editor.zoomIn)
		self.menuZoomIn.setShortcut("Ctrl++")
		editMenu.addAction(self.menuZoomIn)

		self.menuZoomOut = QAction(QIcon(MINUS_ICON),"Zoom out",self)
		self.menuZoomOut.triggered.connect(self.editor.zoomOut)
		self.menuZoomOut.setShortcut("Ctrl+-")
		editMenu.addAction(self.menuZoomOut)

		self.updateApplicationTitle()

		barLayout = QHBoxLayout()

		barLayout.setSpacing(0)
		barLayout.setContentsMargins(0,0,0,0)
			

		barLayout.addWidget(self.runButton)
		barLayout.addWidget(self.servers)

		layout = QVBoxLayout()
		layout.setSpacing(2)
		layout.setContentsMargins(2,2,2,2)
		layout.addLayout(barLayout)
		layout.addWidget(self.editor)

		fL = QWidget()
		fL.setLayout(layout)
		self.setCentralWidget(fL)

	def generateFileMenu(self):

		self.fileMenu.clear()

		entry = QAction(QIcon(NEWFILE_ICON),"New file",self)
		entry.triggered.connect(self.doNewFile)
		entry.setShortcut("Ctrl+N")
		self.fileMenu.addAction(entry)

		entry = QAction(QIcon(OPENFILE_ICON),"Open file",self)
		entry.triggered.connect(self.doFileOpen)
		entry.setShortcut("Ctrl+O")
		self.fileMenu.addAction(entry)

		self.menuSave = QAction(QIcon(SAVEFILE_ICON),"Save file",self)
		self.menuSave.triggered.connect(self.doFileSave)
		self.menuSave.setShortcut("Ctrl+S")
		self.fileMenu.addAction(self.menuSave)

		if self.filename==None:
			self.menuSave.setEnabled(False)

		entry = QAction(QIcon(SAVEASFILE_ICON),"Save as...",self)
		entry.triggered.connect(self.doFileSaveAs)
		self.fileMenu.addAction(entry)

		insertNoTextSeparator(self.parent,self.fileMenu)

		entry = QAction(QIcon(EXIT_ICON),"Exit",self)
		entry.triggered.connect(self.close)
		self.fileMenu.addAction(entry)

	def updateApplicationTitle(self):
		if self.filename!=None:
			base = os.path.basename(self.filename)
			if self.changed:
				self.setWindowTitle("* "+base)
			else:
				self.setWindowTitle(base)
		else:
			self.setWindowTitle(f"Unnamed {APPLICATION_NAME} script")

	def docModified(self):
		if self.changed: return
		self.changed = True
		self.updateApplicationTitle()

	def hasUndo(self,avail):
		if avail:
			self.menuUndo.setEnabled(True)
		else:
			self.menuUndo.setEnabled(False)

	def hasRedo(self,avail):
		if avail:
			self.menuRedo.setEnabled(True)
		else:
			self.menuRedo.setEnabled(False)

	def hasCopy(self,avail):
		if avail:
			self.menuCopy.setEnabled(True)
			self.menuCut.setEnabled(True)
		else:
			self.menuCopy.setEnabled(False)
			self.menuCut.setEnabled(False)

	def doFileSaveAs(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"Save Script As...",self.parent.scriptsdir,f"{APPLICATION_NAME} Script (*.{SCRIPT_FILE_EXTENSION});;All Files (*)", options=options)
		if fileName:
			efl = len(SCRIPT_FILE_EXTENSION)+1
			if fileName[-efl:].lower()!=f".{SCRIPT_FILE_EXTENSION}": fileName = fileName+f".{SCRIPT_FILE_EXTENSION}"
			self.filename = fileName
			code = open(self.filename,"w")
			code.write(self.editor.toPlainText())
			code.close()
			self.changed = False
			self.menuSave.setEnabled(False)
			self.updateApplicationTitle()

	def doNewFile(self):
		self.filename = None
		self.editor.clear()
		self.menuSave.setEnabled(False)

	def openFile(self,filename):
		x = open(filename,mode="r",encoding="latin-1")
		source_code = str(x.read())
		x.close()
		self.editor.setPlainText(source_code)
		self.filename = filename
		self.changed = False
		self.updateApplicationTitle()
		self.menuSave.setEnabled(True)

	def doFileOpen(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(self,"Open Script", self.parent.scriptsdir, f"{APPLICATION_NAME} Script (*.{SCRIPT_FILE_EXTENSION});;All Files (*)", options=options)
		if fileName:
			script = open(fileName,"r")
			self.editor.setPlainText(script.read())
			script.close()
			self.filename = fileName
			self.changed = False
			self.updateApplicationTitle()
			self.menuSave.setEnabled(True)

	def doFileSave(self):
		code = open(self.filename,"w")
		code.write(self.editor.toPlainText())
		code.close()
		self.changed = False
		self.updateApplicationTitle()