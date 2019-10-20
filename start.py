from wx import *
from wx import dataview

class FolderViewItem(dataview.DataViewItem):
	# Types: folder, file
	def __init__(self, itemType, label, parent, id=ID_ANY):
		super().__init__(id)
		self.itemType = itemType
		self.label = label
		self.status = ""
		self.parent = parent


class FolderViewModel(dataview.DataViewModel):
	def __init__(self):
		super().__init__()
		self.data = []
		self.root = FolderViewItem("root", "", None, ID_NONE)
		self.data.append(self.root)

	def IsContainer(self, item):
		if item is FolderViewItem:
			return len(item.children) > 0
		return False

	def GetParent(self, item):
		print("looking for", item.GetID())
		results = list(filter(lambda d: d.GetID().__eq__(item.GetID()), self.data))
		if not results[0].parent: return self.root
		else: return results[0].parent

	def GetChildren(self, item, childrenRet):
		print(item.Id)
		childrenRet = item.children
		return len(childrenRet)

	def GetColumnCount(self):
		return 2

	def GetColumnType(self, col):
		return "text"

	def GetValue(self, item, col):
		if col == 0: return item.label
		else: return item.status

	def addItem(self, item, parent):
		self.data.append(item)
		if not parent:
			self.ItemAdded(self.root, item)
		else:
			self.ItemAdded(parent, item)

class OptionDialog(Dialog):
	def __init__(self, parent, config):
		super().__init__(parent, title="Options")
		self.config = config

		fileTypeText = StaticText(self, label="File Exts")
		self.fileType = TextCtrl(self)
		self.fileType.SetValue(",".join(config["filetypes"]))

		ok = Button(self, label="Ok", id=ID_OK)
		cancel = Button(self, label="Cancel", id=ID_CANCEL)

		mainSizer = BoxSizer(VERTICAL)

		fileTypeSizer = BoxSizer(HORIZONTAL)
		fileTypeSizer.Add(fileTypeText, flag=EXPAND | LEFT | RIGHT | ALIGN_CENTER_VERTICAL, border=3)
		fileTypeSizer.Add(self.fileType, proportion=5, flag=EXPAND | RIGHT, border=3)

		exitSizer = BoxSizer(HORIZONTAL)
		exitSizer.Add(ok, flag=EXPAND | ALIGN_RIGHT)
		exitSizer.Add(cancel, flag=EXPAND | ALIGN_RIGHT)

		mainSizer.Add(fileTypeSizer, flag=EXPAND | ALL)
		mainSizer.Add(exitSizer, flag=EXPAND | ALIGN_RIGHT)

		self.SetSizer(mainSizer)

		ok.Bind(EVT_BUTTON, self.onBtn)
		cancel.Bind(EVT_BUTTON, self.onBtn)

		pass

	def onBtn(self, event):
		if self.IsModal():
			if event.EventObject.Id == ID_OK:
				self.config = {
					"filetypes" : self.fileType.GetValue().split(",")
				}
			self.EndModal(event.EventObject.Id)
		else:
			self.Close()


class MainWindow(Frame):
	def createScreen(self):
		self.folderView = self.createFolderView()

		addFolder = Button(self, label="Add Folder")
		addFolder.Bind(EVT_BUTTON, self.addFolder)

		rescan = Button(self, label="Rescan Folders")
		rescan.Bind(EVT_BUTTON, self.rescanFolders)

		options = Button(self, label="Options")
		options.Bind(EVT_BUTTON, self.showOptions)

		findDupes = Button(self, label="Find Dupes")
		findDupes.Bind(EVT_BUTTON, self.findDupes)
		
		mainSizer = BoxSizer(VERTICAL)
		buttonSizer = BoxSizer(HORIZONTAL)

		mainSizer.Add(self.folderView, proportion=5, flag=EXPAND | ALL, border=3)
		mainSizer.Add(buttonSizer, proportion=1, flag=EXPAND | ALL, border = 3)

		leftButtonSizer = BoxSizer(HORIZONTAL)
		leftButtonSizer.Add(addFolder)
		leftButtonSizer.Add(rescan)
		leftButtonSizer.Add(options)
		
		buttonSizer.Add(leftButtonSizer, proportion=1, flag=ALIGN_LEFT)
		buttonSizer.Add(findDupes, flag=ALIGN_RIGHT)

		self.SetSizer(mainSizer)

	def createFolderView(self):
		folderView = dataview.DataViewCtrl(self)
		folderView.AppendTextColumn("Files", 0)
		folderView.AppendTextColumn("Status", 1)

		folderViewModel = FolderViewModel()
		folderView.AssociateModel(folderViewModel)
		folderViewModel.DecRef()

		return folderView

	def addFolder(self, event):
		dlg = DirDialog(None, "Choose a folder to add", "", DD_DIR_MUST_EXIST | DD_DEFAULT_STYLE)
		if dlg.ShowModal() == ID_OK:
			path = dlg.GetPath()
			model = self.folderView.GetModel()
			item = FolderViewItem("folder", path, model.root)
			model.addItem(item, model.root)
		pass

	def rescanFolders(self, event):
		print("rescan")
		pass

	def showOptions(self, event):
		dlg = OptionDialog(self, self.config)
		if dlg.ShowModal() == ID_OK:
			print(dlg.config)
			self.config = dlg.config
		pass

	def findDupes(self, event):
		pass

	def __init__(self):
		super().__init__(None, title="DupeVideoCV")
		self.createScreen()

		self.config = {
			"filetypes" : ["mp4", "avi", "wmv", "3pg", "mpg", "ts", "mov"]
		}


app = App()
window = MainWindow()
window.Show()
app.MainLoop()