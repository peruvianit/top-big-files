import sys
import os

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction

from utils.FileHelper import FileDetails


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        exportAct = QAction(QIcon('export.png'), '&Exit', self)
        exportAct.setShortcut('Ctrl+Q')
        exportAct.setStatusTip('Export json')
        exportAct.triggered.connect(QApplication.instance().quit)

        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(QApplication.instance().quit)

        helpAct = QAction('&About', self)
        helpAct.setStatusTip('About')
        helpAct.triggered.connect(self.helpMenuClick)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        helpMenu = menubar.addMenu('&Help')
        fileMenu.addAction(exitAct)
        helpMenu.addAction(helpAct)

        # config windows
        self.setGeometry(300, 300, 800, 500)
        self.setWindowTitle('Top Big files')

        # GUI elements
        # Create central widget and layout
        self._centralWidget = QWidget()
        self._verticalLayout = QVBoxLayout()
        self._centralWidget.setLayout(self._verticalLayout)

        # Set central widget
        self.setCentralWidget(self._centralWidget)

        self.addForm()
        self.addCopyRight()

    def addForm(self):
        formLayout = QFormLayout()

        self.nameField = QLineEdit("c:\\")
        self.nameField.setDisabled(True)

        buttonPath = QPushButton("Change directory")
        buttonPath.clicked.connect(self.change_directory)

        buttonRun = QPushButton("Run")
        buttonRun.clicked.connect(self.run_analizer)

        self.buttonDelete = QPushButton("Delete selection")
        self.buttonDelete.clicked.connect(self.delete_files)
        self.buttonDelete.setDisabled(True)

        buttonGroup = QGroupBox()
        buttonGroup.setStyleSheet("QGroupBox { border: 0px;}")

        horizontalButtonLayout = QHBoxLayout()
        horizontalButtonLayout.addWidget(buttonRun)
        horizontalButtonLayout.addWidget(self.buttonDelete)
        buttonGroup.setLayout(horizontalButtonLayout)

        listLabel = QLabel('Files founds')
        self.listFileField = QListWidget()
        self.listFileField.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        listExternsionsLabel = QLabel('Extensions founds')
        self.listExtensionsField = QListWidget()

        self.workFileField = QLineEdit()
        self.workFileField.setDisabled(True)

        formLayout.addRow(buttonPath, self.nameField)
        formLayout.addRow(None, buttonGroup)
        formLayout.addRow(listLabel, self.listFileField)
        formLayout.addRow(listExternsionsLabel, self.listExtensionsField)
        formLayout.addRow(None, self.workFileField)

        self._verticalLayout.addLayout(formLayout)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)


    def addCopyRight(self):
        copyRight = QLabel(
            'Copyright © <a href="https://peruvianit.github.io/">Peruvianit</a> 2023')
        copyRight.setOpenExternalLinks(True)
        self._verticalLayout.addWidget(copyRight, alignment=Qt.AlignmentFlag.AlignRight)


    def helpMenuClick(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Author")
        dlg.setText('''Author : Peruvianit
Email  : sergioarellanodiaz@gmail.com
        ''')
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Ok:
            dlg.close()

    def change_directory(self):
        self.clear_controls()
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.nameField.setText(folderpath)

    def run_analizer(self):
        self.clear_controls()
        FileDetails.clear_list_file()
        verify_top_files_big_size(self, self.nameField.text())

    def delete_files(self):

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Delete files!")
        dlg.setText("Confirm to continue with the cancellation?")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Yes:
            for item in self.listFileField.selectedItems():
                try:
                    file_path = item.text().replace('/','\\').split("#-->")[0].strip()
                    print('la cancellazione fisica del file, è desattivata sul codice!!')
                    #os.remove(file_path)
                    FileDetails.remove_file(file_path)
                    self.listFileField.takeItem(self.listFileField.row(item))

                except OSError as e:
                    print(f'[{file_path}] {e.strerror}')

        self.refresh_list(FileDetails.get_list_file())

    def update_message(self, message):
        self.workFileField.setText(message)

    def clear_controls(self):
        self.listFileField.clear()
        self.listExtensionsField.clear()
        self.statusBar.clearMessage()
        self.workFileField.clear()

    def refresh_list(self, listFiles):
        self.clear_controls()

        # files founds
        for file in listFiles:
            item = QListWidgetItem(f"{file.name} #--> ( {file.size} bytes)")
            self.listFileField.addItem(item)

        # extensions founds
        for key, value in FileDetails.analizer_extensions().items():
            item = QListWidgetItem(f"{key} \t ({value}) concurrence")
            self.listExtensionsField.addItem(item)

        self.buttonDelete.setDisabled(False if len(listFiles) > 0 else True)

        self.statusBar.showMessage(f"File analyzer count {FileDetails.total_files_count()} with a total of ({FileDetails.total_size_analized()}) bytes")

def verify_top_files_big_size(mainWindows: MainWindow, path: str):
    try:
        for ele in os.listdir(path):
            path_directory = os.path.join(path, ele)

            if os.path.isdir(path_directory):
                verify_top_files_big_size(mainWindows, path_directory)
            else:
                try:
                    file_size = os.path.getsize(path_directory)
                    if FileDetails.add_file(FileDetails(path_directory, file_size)):
                        mainWindows.refresh_list(FileDetails.get_list_file())

                    mainWindows.update_message(path_directory)
                    mainWindows.repaint()
                except FileNotFoundError:
                    print(f"Problem read the file : {path_directory}")

    except PermissionError:
        print(f"Not permission for the folder : {path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()

    sys.exit(app.exec())