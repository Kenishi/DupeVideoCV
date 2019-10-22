import os
import sys
from threading import Thread
from ctypes import c_wchar_p
from multiprocessing import Condition, Value, Pool
from PyQt5 import *
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import ScanWorker

class ProgressTracker(Thread):
	def __init__(self):
		super().__init__()
		self.lock = Condition()
		self.done = Value("H", 0)
		self.file = Value(c_wchar_p, "")
		self.progress = Value("d", 0.0)
		self.callbacks = []

	def update(self, file, progress):
		with self.lock:
			self.file = file
			self.progress = progress
			self.lock.notifyAll()

	def complete(self):
		with self.done.get_lock():
			self.done.value = 1
		with self.lock:
			self.lock.notifyAll()

	def registerUpdateCallback(self, callback):
		self.callbacks.append(callback)

	def run(self):
		while True:
			with self.done.get_lock():
				if self.done.value:
					break
				self.lock.wait()
				with self.file.get_lock() and self.progress.get_lock():
					for callback in self.callbacks:
						callback(file.value, progress.value)



class TreeItem(QTreeWidgetItem):
	def __init__(self, path, status):
		super().__init__([path, status])
		self.path = path
		self.status = status


class OptionsDialog(QDialog):
	def __init__(self, config, parent=None):
		super().__init__(parent)

		self.setMinimumSize(QSize(500, 250))

		mainBox = QVBoxLayout()
		
		entryBox = QHBoxLayout()
		label = QLabel("File Exts")
		self.fileTypes = QLineEdit(",".join(config["filetypes"]))
		entryBox.addWidget(label)
		entryBox.addWidget(self.fileTypes)
		mainBox.addLayout(entryBox)

		buttonBox = QHBoxLayout()
		ok = QPushButton("Ok")
		ok.clicked.connect(self.onOK)
		buttonBox.addWidget(ok)

		cancel = QPushButton("Cancel")
		cancel.clicked.connect(self.reject)
		buttonBox.addWidget(cancel)

		mainBox.addLayout(buttonBox)
		self.setLayout(mainBox)

	def onOK(self):
		filetypes = self.fileTypes.text().split(",")
		config = {
			"filetypes" : filetypes
		}
		self.config = config
		self.accept()

class Application(QWidget):
	def __init__(self):
		super().__init__()

		self.setMinimumSize(QSize(1000,480))
		self.setWindowTitle("DupeVideoCV")
		self.isFindingDupes = False

		self.initView()

		self.config = {
			"filetypes" : ["mp4", "mpg", "wmv", "avi", "ts", "3pg", "mov"]
		}

	def createTreeView(self):
		treeView = QTreeWidget(self)
		treeView.setHeaderLabels(["Folder", "Status"])
		treeView.setColumnCount(2)

		treeView.header().setSectionResizeMode(0, QHeaderView.Stretch)

		return treeView
		pass

	def initView(self):
		self.treeView = self.createTreeView()

		addFolder = QPushButton("Add")
		addFolder.clicked.connect(self.onAddFolder)

		removeFolder = QPushButton("Remove")
		removeFolder.clicked.connect(self.onRemoveFolder)

		rescan = QPushButton("Rescan")
		rescan.clicked.connect(self.onRescan)

		options = QPushButton("Options")
		options.clicked.connect(self.onOptions)

		findDupes = QPushButton("Find Dupes")
		findDupes.clicked.connect(self.onFindDupes)

		mainLayout = QVBoxLayout()
		mainLayout.addWidget(self.treeView)

		buttonGroupLayout = QHBoxLayout()
		leftButtons = QHBoxLayout()
		leftButtons.addWidget(addFolder)
		leftButtons.addWidget(removeFolder)
		leftButtons.addWidget(rescan)
		leftButtons.addWidget(options)

		rightButtons = QHBoxLayout()
		rightButtons.addWidget(findDupes, alignment=Qt.AlignRight)

		buttonGroupLayout.addLayout(leftButtons)
		buttonGroupLayout.addLayout(rightButtons)
		mainLayout.addLayout(buttonGroupLayout)
		self.setLayout(mainLayout)

	def onAddFolder(self):
		path = QFileDialog.getExistingDirectory(self, caption="Add a folder")
		item = TreeItem(path, "")
		self.treeView.addTopLevelItem(item)
		self.scanFolderForVideo(path)

	def onRemoveFolder(self):
		items = self.treeView.selectedItems()
		for item in items:
			index = self.treeView.indexOfTopLevelItem(item)
			if index > -1:
				self.treeView.takeTopLevelItem(self.treeView.indexOfTopLevelItem(item))

	def onRescan(self):
		paths = [self.treeView.topLevelItem(i).path for i in range(self.treeView.topLevelItemCount())]
		self.treeView.clear()
		for path in paths:
			self.scanFolderForVideo(path)
		pass

	def onOptions(self):
		dlg = OptionsDialog(self.config)
		if dlg.exec_():
			self.config = dlg.config
			print(self.config)
		pass

	def onFindDupes(self):
		if not self.isFindingDupes:
			self.isFindingDupes = True

			with Pool(5) as pool:
				for file in self._nextFile():
					tracker = ProgressTracker()
					tracker.registerUpdateCallback(self.onProgress)

					future = pool.apply_async(ScanWorker.scan, (tracker,))
					tracker.start()

			self.isFindingDupes = False

		pass

	def onProgress(self, done, file, progress):
		print(file, progress)
		pass

	def onScanComplete(self, file, results):
		print(file, results)
		pass


	def _nextFile(self):
		for i in range(self.treeView.topLevelItemCount()):
			item = self.treeView.topLevelItem(i)
			for c in range(item.childCount()):
				child = item.child(c)
				path = item.path + "/" + child.path
				yield path

	def findFolderItem(self, folder):
		for i in range(self.treeView.topLevelItemCount()):
			item = self.treeView.topLevelItem(i)
			if item.path == folder:
				return item
		return None

	def scanFolderForVideo(self, folder):
		for (root, dirs, files) in os.walk(folder):
			for file in files:
				ext = os.path.splitext(file)[-1][1:]
				if ext in self.config["filetypes"]:
					item = self.findFolderItem(root)

					# Add the folder to the top if we don't have it
					if not item:
						item = TreeItem(root, "")
						self.treeView.addTopLevelItem(item)
					newItem = TreeItem(file, "")
					item.addChild(newItem)			


if __name__ == "__main__":
	app = QApplication(sys.argv)
	font = QFont("times", 8)
	app.setFont(font)
	mainWnd = Application()
	mainWnd.show()
	sys.exit(app.exec_())