import backendMethods
from usefulVariables import *  # local variables
import PyQt5.QtWidgets as Qt
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from pathlib import Path
import shutil
import json
import glob


class SeparationLine(Qt.QFrame):
    def __init__(self):
        """a horizontal separation line"""
        super().__init__()
        self.setFrameShape(Qt.QFrame.HLine)
        self.setFrameShadow(Qt.QFrame.Sunken)
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.setFixedHeight(10)

class ProfileSelect(Qt.QFrame):
    wasSelected = QtCore.pyqtSignal(str)
    def __init__(self, properties:dict):
        """a button to select the profile to launch or modify"""
        super().__init__()
        self.mainLayout = Qt.QHBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(self.mainLayout)

        self.name = properties["name"]
        self.modloader = properties["modloader"]
        self.version = properties["version"]
        self.isSelected = False

        # modloader icon
        modloaderIcon = QtGui.QIcon(str(iconsAssetsDir/f"{self.modloader.lower()}.png"))
        self.modloaderIconLabel = Qt.QLabel()
        self.modloaderIconLabel.setPixmap(modloaderIcon.pixmap(64, 64))
        self.mainLayout.addWidget(self.modloaderIconLabel)

        # widget containing the informations about the profile
        self.informationsWidget = Qt.QWidget()
        self.informationsLayout = Qt.QVBoxLayout()
        self.informationsWidget.setLayout(self.informationsLayout)
        self.mainLayout.addWidget(self.informationsWidget, 1)  # the 1 makes the widget expandable

        self.nameLabel = Qt.QLabel(self.name)
        self.nameLabel.setFont(Fonts.smallTitleFont)
        self.informationsLayout.addWidget(self.nameLabel)

        self.versionLabel = Qt.QLabel(f"{self.modloader} {self.version}")
        self.versionLabel.setFont(Fonts.textFont)
        self.informationsLayout.addWidget(self.versionLabel)

        # mouse tracking
        self.setMouseTracking(True)
        self.enterEvent = self.onEnter
        self.leaveEvent = self.onLeave

        self.mousePressEvent = self.onMousePress

    def onMousePress(self, event):
        if not self.isSelected:
            self.setSelected(True)
        event.accept()

    def onEnter(self, event):
        self.setHovered(True)
        event.accept()

    def onLeave(self, event):
        self.setHovered(False)
        event.accept()
    
    def setHovered(self, hovered:bool):
        """gray out the frame on hover"""
        if hovered:
            self.setStyleSheet("background-color: rgba(0, 0, 0, 64);")
            for widget in (self.nameLabel, self.versionLabel, self.modloaderIconLabel, self.informationsWidget):  # avoid applying shadow to inner widgets
                widget.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        else:
            self.setStyleSheet("")

    def setSelected(self, selected:bool):
        """outline the frame if selected"""
        if selected:
            self.setFrameShape(Qt.QFrame.Box)
            self.isSelected = True
            self.wasSelected.emit(self.name)
        else:
            self.setFrameShape(Qt.QFrame.NoFrame)
            self.isSelected = False

class ModSelect(Qt.QFrame):
    wasSelected = QtCore.pyqtSignal(object)
    def __init__(self, modData:dict):
        """a button to select the mod to view or modify"""
        super().__init__()
        self.mainLayout = Qt.QHBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.mainLayout)
        self.isSelected = False

        if isinstance(modData, str):  # if it's a custom jar mod
            self.isCustom = True
            self.fileName = modData
        else:
            self.isCustom = False
            self.modData = modData
            self.name = modData["modName"]
            self.modId = modData["modId"]
            self.fileName = modData["fileName"]
            self.version = modData["versionName"]
            self.iconPath = cacheDir/"modIcons"/modData["platform"].lower()/f"{self.modId}.png"
            self.versionId = modData["versionId"]

        # mod icon
        self.iconLabel = Qt.QLabel()
        self.updateIcon()
        self.mainLayout.addWidget(self.iconLabel)

        self.textWidget = Qt.QWidget()
        self.textLayout = Qt.QVBoxLayout()
        self.textWidget.setLayout(self.textLayout)
        self.mainLayout.addWidget(self.textWidget, 1)

        self.nameLabel = Qt.QLabel(self.name if not self.isCustom else self.fileName)
        self.nameLabel.setFont(Fonts.smallTitleFont)
        self.nameLabel.setWordWrap(True)
        self.textLayout.addWidget(self.nameLabel)

        self.versionLabel = Qt.QLabel()
        if not self.isCustom:
            if self.version:
                self.versionLabel.setText(self.version)
                self.versionLabel.setFont(Fonts.textFont)
                self.versionLabel.setWordWrap(True)
                self.textLayout.addWidget(self.versionLabel)

        # mouse tracking
        self.setMouseTracking(True)
        self.enterEvent = self.onEnter
        self.leaveEvent = self.onLeave

        self.mousePressEvent = self.onMousePress
    
    def updateIcon(self):
        """update the icon from the iconPath if it exists"""
        if self.isCustom:
            self.iconLabel.setPixmap(QtGui.QPixmap(str(iconsAssetsDir/"jar.png")).scaled(64, 64))
        else:
            if os.path.exists(self.iconPath):
                self.iconLabel.setPixmap(QtGui.QPixmap(str(self.iconPath)).scaled(64, 64))
            else:
                self.iconLabel.setPixmap(QtGui.QPixmap(str(iconsAssetsDir/"noMedia.png")).scaled(64, 64))

    def onMousePress(self, event):
        if not self.isSelected:
            self.setSelected(True)
        event.accept()

    def onEnter(self, event):
        self.setHovered(True)
        event.accept()

    def onLeave(self, event):
        self.setHovered(False)
        event.accept()
    
    def setHovered(self, hovered:bool):
        """gray out the frame on hover"""
        if hovered:
            self.setStyleSheet("background-color: rgba(0, 0, 0, 64);")
            for widget in (self.textWidget, self.nameLabel, self.versionLabel, self.iconLabel):  # avoid applying shadow to inner widgets
                widget.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        else:
            self.setStyleSheet("")

    def setSelected(self, selected:bool):
        """outline the frame if selected"""
        if selected:
            if not self.isCustom:
                self.setFrameShape(Qt.QFrame.Box)
                self.isSelected = True
                self.wasSelected.emit(self.modData)
            else:
                self.wasSelected.emit(self.fileName)
                
        else:
            self.setFrameShape(Qt.QFrame.NoFrame)
            self.isSelected = False

class SearchModSelect(Qt.QFrame):
    wasSelected = QtCore.pyqtSignal(dict)
    def __init__(self, modData:dict):
        """a button to select the mod to view and install"""
        super().__init__()
        self.mainLayout = Qt.QHBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(self.mainLayout)

        self.modData = modData
        self.name = modData["name"]
        self.author = modData["author"]
        self.iconPath = modData["icon"]
        self.modId = modData["id"]
        self.platform = modData["platform"]
        self.isSelected = False

        # mod icon
        self.iconLabel = Qt.QLabel()
        self.updateIcon()
        self.mainLayout.addWidget(self.iconLabel)

        # widget containing the informations about the mod
        self.textWidget = Qt.QWidget()
        self.textLayout = Qt.QVBoxLayout()
        self.textWidget.setLayout(self.textLayout)
        self.mainLayout.addWidget(self.textWidget, 1)  # the 1 makes the widget expandable

        self.nameLabel = Qt.QLabel(self.name)
        self.nameLabel.setFont(Fonts.smallTitleFont)
        self.nameLabel.setWordWrap(True)
        self.textLayout.addWidget(self.nameLabel)

        self.authorLabel = Qt.QLabel(f"by {self.author}")
        self.authorLabel.setFont(Fonts.textFont)
        self.authorLabel.setWordWrap(True)
        self.textLayout.addWidget(self.authorLabel)

        # mouse tracking
        self.setMouseTracking(True)
        self.enterEvent = self.onEnter
        self.leaveEvent = self.onLeave

        self.mousePressEvent = self.onMousePress
    
    def updateIcon(self):
        """update the icon from the iconPath if it exists"""
        if os.path.exists(self.iconPath):
            self.iconLabel.setPixmap(QtGui.QPixmap(str(self.iconPath)).scaled(64, 64))
        else:
            self.iconLabel.setPixmap(QtGui.QPixmap(str(iconsAssetsDir/"noMedia.png")).scaled(64, 64))

    def onMousePress(self, event):
        if not self.isSelected:
            self.setSelected(True)
        event.accept()

    def onEnter(self, event):
        self.setHovered(True)
        event.accept()

    def onLeave(self, event):
        self.setHovered(False)
        event.accept()
    
    def setHovered(self, hovered:bool):
        """gray out the frame on hover"""
        if hovered:
            self.setStyleSheet("background-color: rgba(0, 0, 0, 64);")
            for widget in (self.textWidget, self.nameLabel, self.iconLabel):  # avoid applying shadow to inner widgets
                widget.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        else:
            self.setStyleSheet("")

    def setSelected(self, selected:bool):
        """outline the frame if selected"""
        if selected:
            self.setFrameShape(Qt.QFrame.Box)
            self.isSelected = True
            self.wasSelected.emit(self.modData)
        else:
            self.setFrameShape(Qt.QFrame.NoFrame)
            self.isSelected = False

class ModVersionRadio(Qt.QWidget):
    def __init__(self):
        """a serie of radio buttons to select the mod version, given a list of versions with their properties"""
        super().__init__()
        self.versions = {}
        self.radioButtons = []
        self.mainLayout = Qt.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.radioGroup = Qt.QButtonGroup(self)
    
    def setVersions(self, versions:dict, gameVersion:str):
        """update the radio buttons with the new versions"""
        self.versions = versions
        # clear previous radio buttons
        for radioButton in self.radioButtons:
            self.radioGroup.removeButton(radioButton)
        self.radioButtons = []
        for i in reversed(range(self.mainLayout.count())):
            self.mainLayout.itemAt(i).widget().deleteLater()
        
        # create new radio buttons
        foundRecommended = False
        isFirst = True
        for version, properties in self.versions.items():
            text = f"{properties['releaseType']} - {version}"
            if isFirst:
                text = f"(latest) {text}"
            if not foundRecommended and properties['releaseType'] == "release" and gameVersion in properties['mcVersions']:
                text = f"(recommended) {text}"
                foundRecommended = True
            radioButton = Qt.QRadioButton(text)
            radioButton.setFont(Fonts.subtitleFont)
            self.radioGroup.addButton(radioButton)
            self.radioButtons.append(radioButton)
            self.mainLayout.addWidget(radioButton)
            isFirst = False
        
    def getSelectionData(self) -> dict:
        """return the version data of the selected radio button"""
        for radioButton in self.radioButtons:
            if radioButton.isChecked():
                version = radioButton.text()
                cleanVersion = version
                for prefix in ["(latest) ", "(recommended) ", "release - ", "beta - ", "alpha - "]:
                    cleanVersion = cleanVersion.replace(prefix, "", 1)  # remove the prefix
                return self.versions[cleanVersion]
        return None  # if no version selected
    
    def getCheckedVersion(self):
        """return the version data of the checked radio button"""
        for radioButton in self.radioGroup.buttons():
            if radioButton.isChecked():
                version = radioButton.text()
                return version, self.versions[version]
        return None


class addProfilePopup(Qt.QDialog):
    """popup to create a new profile"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle(lang("addProfile"))
        self.mainLayout = Qt.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # profile name
        self.profileNameWidget = Qt.QWidget()
        self.profileNameLayout = Qt.QHBoxLayout()
        self.profileNameWidget.setLayout(self.profileNameLayout)
        self.mainLayout.addWidget(self.profileNameWidget)

        self.profileNameLabel = Qt.QLabel(lang("profileName"))
        self.profileNameLabel.setFont(Fonts.titleFont)
        self.profileNameLayout.addWidget(self.profileNameLabel)

        self.profileNameInput = Qt.QLineEdit()
        self.profileNameInput.setPlaceholderText(lang("profileNameHere"))
        self.profileNameInput.setFixedHeight(40)
        self.profileNameInput.setFont(Fonts.titleFont)
        self.profileNameInput.setMaxLength(64)
        self.profileNameInput.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[a-zA-Z0-9_ .-]+")))  # filter out invalid characters
        self.profileNameLayout.addWidget(self.profileNameInput)

        # minecraft version
        self.mcVersionWidget = Qt.QWidget()
        self.mcVersionLayout = Qt.QHBoxLayout()
        self.mcVersionWidget.setLayout(self.mcVersionLayout)
        self.mainLayout.addWidget(self.mcVersionWidget)

        self.mcVersionLabel = Qt.QLabel(lang("mcVersion"))
        self.mcVersionLabel.setFont(Fonts.titleFont)
        self.mcVersionLayout.addWidget(self.mcVersionLabel)
        
        self.mcVersionSelectWidget = Qt.QWidget()
        self.mcVersionSelectLayout = Qt.QVBoxLayout()
        self.mcVersionSelectWidget.setLayout(self.mcVersionSelectLayout)
        self.mcVersionLayout.addWidget(self.mcVersionSelectWidget)

        self.showReleaseCheck = Qt.QCheckBox(lang("onlyShowReleases"))
        self.showReleaseCheck.setFont(Fonts.bigTextFont)
        self.showReleaseCheck.setChecked(True)
        self.showReleaseCheck.stateChanged.connect(self.showReleaseChange)
        self.mcVersionSelectLayout.addWidget(self.showReleaseCheck)

        self.versionSelect = Qt.QComboBox()
        self.versionSelect.setFont(Fonts.titleFont)
        self.versionSelect.addItems(backendMethods.Methods.listMcVersions(backendMethods.Methods, onlyReleases=True))
        self.mcVersionSelectLayout.addWidget(self.versionSelect)

        # modloader
        self.modloaderWidget = Qt.QWidget()
        self.modloaderLayout = Qt.QHBoxLayout()
        self.modloaderWidget.setLayout(self.modloaderLayout)
        self.mainLayout.addWidget(self.modloaderWidget)

        self.modloaderLabel = Qt.QLabel(lang("modloader"))
        self.modloaderLabel.setFont(Fonts.titleFont)
        self.modloaderLayout.addWidget(self.modloaderLabel)

        self.modloaderSelect = Qt.QComboBox()
        self.modloaderSelect.setFont(Fonts.titleFont)
        self.modloaderSelect.addItems(["Fabric", "Forge", "NeoForge", "Quilt"])
        self.modloaderLayout.addWidget(self.modloaderSelect)

        self.buttonsWidget = Qt.QWidget()
        self.buttonsLayout = Qt.QHBoxLayout()
        self.buttonsWidget.setLayout(self.buttonsLayout)
        self.mainLayout.addWidget(self.buttonsWidget)

        # buttons
        self.cancelButton = Qt.QPushButton(lang("cancel"))
        self.cancelButton.setFont(Fonts.titleFont)
        self.cancelButton.setFixedHeight(50)
        self.cancelButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cancelButton.clicked.connect(self.close)
        self.buttonsLayout.addWidget(self.cancelButton)

        self.createButton = Qt.QPushButton(lang("create"))
        self.createButton.setFont(Fonts.titleFont)
        self.createButton.setFixedHeight(50)
        self.createButton.clicked.connect(self.createProfile)
        self.buttonsLayout.addWidget(self.createButton)
    
    def showReleaseChange(self):
        """change the minecraft version list to only show releases or not"""
        self.versionSelect.clear()
        if self.showReleaseCheck.isChecked():
            self.versionSelect.addItems(backendMethods.Methods.listMcVersions(backendMethods.Methods, onlyReleases=True))
        else:
            self.versionSelect.addItems(backendMethods.Methods.listMcVersions(backendMethods.Methods, onlyReleases=False))
    
    def createProfile(self):
        """create a new profile based on the user input"""
        self.profileName = self.profileNameInput.text().strip()
        if not self.profileName:
            QMessageBox.critical(self, lang("error"), lang("profileNameEmptyError"))
            return
        self.existingProfiles = [Path(item).name for item in glob.glob(str(profilesDir/"*"))]
        if self.profileName in self.existingProfiles:
            QMessageBox.critical(self, lang("error"), lang("profileNameExistsError"))
            return
        
        self.mcVersion = self.versionSelect.currentText()
        self.modloader = self.modloaderSelect.currentText()
        self.profilePath = profilesDir/self.profileName
        self.profilePath.mkdir(parents=True, exist_ok=False)
        self.profilePropertiesPath = self.profilePath/"properties.json"
        
        with open(self.profilePropertiesPath, "w", encoding="utf-8") as f:
            # write the profile properties to the file
            json.dump({"name": self.profileName, "version": self.mcVersion, "modloader": self.modloader}, f, indent=4)
        
        QMessageBox.information(self, lang("success"), lang("profileCreationSuccess"))
        
        self.close()


class CustomModMenu(Qt.QWidget):
    needRefresh = QtCore.pyqtSignal()
    def __init__(self, modFileName:str, modFilePath:Path):
        """opens a popup menu to do actions on custom jar mods"""
        self.modFileName = modFileName
        self.modFilePath = modFilePath
        super().__init__()
        self.mainLayout = Qt.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # mod name
        self.modNameLabel = Qt.QLabel(self.modFileName)
        self.modNameLabel.setFont(Fonts.titleFont)
        self.modNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.modNameLabel.setWordWrap(True)
        self.mainLayout.addWidget(self.modNameLabel)

        # buttons
        self.buttonsWidget = Qt.QWidget()
        self.buttonsLayout = Qt.QHBoxLayout()
        self.buttonsWidget.setLayout(self.buttonsLayout)
        self.mainLayout.addWidget(self.buttonsWidget)

        # remove button
        self.removeButton = Qt.QPushButton(lang("remove"))
        self.removeButton.setFont(Fonts.titleFont)
        self.removeButton.setFixedHeight(50)
        self.removeButton.clicked.connect(self.removeMod)
        self.buttonsLayout.addWidget(self.removeButton)

        # rename button
        self.renameButton = Qt.QPushButton(lang("rename"))
        self.renameButton.setFont(Fonts.titleFont)
        self.renameButton.setFixedHeight(50)
        self.renameButton.clicked.connect(self.renameMod)
        self.buttonsLayout.addWidget(self.renameButton)

        # close button
        self.closeButton = Qt.QPushButton(lang("close"))
        self.closeButton.setFont(Fonts.titleFont)
        self.closeButton.setFixedHeight(50)
        self.closeButton.clicked.connect(self.close)
        self.buttonsLayout.addWidget(self.closeButton)

    def removeMod(self):
        """remove the mod file and close the popup"""
        confirm = QMessageBox.question(self, lang("removeMod"), lang("removeModConfirm"), QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            os.remove(self.modFilePath)
            QMessageBox.information(self, lang("success"), lang("modRemoved"))
            self.needRefresh.emit()
            self.close()
    
    def renameMod(self):
        """rename the mod file"""
        newName, ok = Qt.QInputDialog.getText(self, lang("renameMod"), lang("newName"))
        if ok:
            if not newName:
                QMessageBox.warning(self, lang("error"), lang("modNameEmptyError"))
                return
            ext = self.modFilePath.name.split(".")[-1]
            newFilePath = self.modFilePath.parent/f"{newName}.{ext}"
            if newFilePath.exists():
                QMessageBox.warning(self, lang("error"), lang("modNameExistsError"))
                return
            os.rename(self.modFilePath, newFilePath)
            QMessageBox.information(self, lang("success"), lang("modRenamed"))
            self.needRefresh.emit()
            self.close()


class configureProfilePopup(Qt.QWidget):
    renameProfile = QtCore.pyqtSignal(str)
    removeProfile = QtCore.pyqtSignal()
    def __init__(self, profileName:str):
        """popup to modify the profile properties"""
        self.profileName = profileName
        self.profilePath = profilesDir/self.profileName
        
        super().__init__()
        self.mainLayout = Qt.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # profile name
        self.profileNameLabel = Qt.QLabel(self.profileName)
        self.profileNameLabel.setFont(Fonts.titleFont)
        self.profileNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.profileNameLabel.setWordWrap(True)
        self.mainLayout.addWidget(self.profileNameLabel)

        # buttons
        self.buttonsWidget = Qt.QWidget()
        self.buttonsLayout = Qt.QHBoxLayout()
        self.buttonsWidget.setLayout(self.buttonsLayout)
        self.mainLayout.addWidget(self.buttonsWidget)
        
        # rename button
        self.renameButton = Qt.QPushButton(lang("rename"))
        self.renameButton.setFont(Fonts.titleFont)
        self.renameButton.setFixedHeight(50)
        self.renameButton.clicked.connect(self.askRename)
        self.buttonsLayout.addWidget(self.renameButton)

        # remove button
        self.removeButton = Qt.QPushButton(lang("removeProfile"))
        self.removeButton.setFont(Fonts.titleFont)
        self.removeButton.setFixedHeight(50)
        self.removeButton.clicked.connect(self.askRemove)
        self.buttonsLayout.addWidget(self.removeButton)

        # close button
        self.closeButton = Qt.QPushButton(lang("close"))
        self.closeButton.setFont(Fonts.titleFont)
        self.closeButton.setFixedHeight(50)
        self.closeButton.clicked.connect(self.close)
        self.buttonsLayout.addWidget(self.closeButton)
    
    def askRename(self):
        """ask the user for the new profile name"""
        newName, ok = Qt.QInputDialog.getText(self, lang("rename"), lang("newName"))
        if ok:
            if not newName:
                QMessageBox.warning(self, lang("error"), lang("profileNameEmptyError"))
                return
            otherNames = [Path(item).name for item in glob.glob(str(profilesDir/"*")) if Path(item).name != self.profileName]
            if newName in otherNames:
                QMessageBox.warning(self, lang("error"), lang("profileNameExistsError"))
                return
            self.renameProfile.emit(newName)
            self.close()
    
    def askRemove(self):
        """ask the user to confirm the profile removal"""
        confirm = QMessageBox.question(self, lang("removeProfile"), lang("removeProfileConfirm"), QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.removeProfile.emit()
            self.close()
