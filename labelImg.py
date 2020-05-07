#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os.path
import platform
import sys
import subprocess
from qtmodern import styles, windows

from functools import partial

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    if sys.version_info.major >= 3:
        import sip

        sip.setapi('QVariant', 2)
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from libs.resources import *
from libs.constants import *
from libs.utils import *
from libs.settings import Settings
from libs.shape import Shape, DEFAULT_LINE_COLOR, DEFAULT_FILL_COLOR
from libs.stringBundle import StringBundle
from libs.canvas import Canvas
from libs.zoomWidget import ZoomWidget
from libs.colorDialog import ColorDialog
from libs.toolBar import ToolBar
from libs.yolo_io import YoloReader
from libs.yolo_io import TXT_EXT
from libs.ustr import ustr
from libs.hashableQListWidgetItem import HashableQTreeWidgetItem
from libs.labelDialog2 import *
from libs import labelDialog2
from libs.custom_widget import QCustomQWidget
import dowloadAPI

# from libs.treeLabelWidget import TreeLabel

__appname__ = 'labelImg'
TXT_SUFFIX = '.txt'


class WindowMixin(object):

    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            addActions(toolbar, actions)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        return toolbar


class ThisPalette(QPalette):
    def __init__(self):
        super(ThisPalette, self).__init__()
        # palette.setColor(QPalette.Window, QColor (179, 200, 200))
        # palette.setColor(QPalette.Window, QColor (211, 238, 255))
        # self.setColor(QPalette.Window, QColor(150, 182, 197))
        # self.setColor(QPalette.Base, QColor(255, 255, 255))
        # selfsetColor(QPalette.AlternateBase, QColor(53, 53, 53))
        # selfsetColor(QPalette.ToolTipBase, QtCore.Qt.white)
        # selfsetColor(QPalette.Text, QtCore.Qt.white)
        # self.setColor(QPalette.Button, QColor(211, 238, 255))
        # self.setColor(QPalette.ButtonText, QtCore.Qt.black)
        # selfsetColor(QPalette.BrightText, QtCore.Qt.red)
        # self.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        # self.setColor(QPalette.HighlightedText, QtCore.Qt.black)


class MainWindow(QMainWindow, WindowMixin):
    FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = list(range(3))

    def __init__(self, defaultFilename=None, defaultPrefdefClassFile=None, defaultSaveDir=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle(__appname__)

        # Load setting in the main thread
        self.settings = Settings()
        self.settings.load()
        settings = self.settings

        palette = ThisPalette()
        self.setPalette(palette)

        # Load string bundle for i18n
        self.stringBundle = StringBundle.getBundle()
        getStr = lambda strId: self.stringBundle.getString(strId)

        # Save as Pascal voc xml
        self.defaultSaveDir = defaultSaveDir
        self.usingPascalVocFormat = True
        self.usingYoloFormat = False

        # For loading all image under a directory
        self.mImgList = []
        self.dirname = None
        self.labelHist = []
        self.lastOpenDir = None

        self.dataSublabel = self.load_dataSublabels()
        self.refDir = None
        self.shapesRefs = []
        self.brandHint = None
        self.brandlist = []
        self.notelist = []

        # Whether we need to save or not.
        self.dirty = False

        self._noSelectionSlot = False
        self._beginner = True
        # self.screencastViewer = self.getAvailableScreencastViewer()
        # self.screencast = "https://youtu.be/p0nR2YsCY_U"

        # Load predefined classes to the list
        self.loadPredefinedClasses(defaultPrefdefClassFile)
        if not os.path.exists(os.path.join(os.getcwd(), 'datasets')):
            os.mkdir(os.path.join(os.getcwd(), 'datasets'))
        if not os.path.exists(os.path.join(os.getcwd(), 'datasets/detect_label/')):
            os.mkdir(os.path.join(os.getcwd(), 'datasets/detect_label/'))

        # Main widgets and related state.
        self.labelDialog = LabelDialog(parent=self, label='here', subLabels=['here2', 'here3'])

        self.itemsToShapes = {}
        self.shapesToItems = {}
        self.prevLabelText = ''

        listLayout = QVBoxLayout()
        listLayout.setContentsMargins(0, 0, 0, 0)

        # Create a widget for using default label
        self.useDefaultLabelCheckbox = QCheckBox(getStr('useDefaultLabel'))
        self.useDefaultLabelCheckbox.setChecked(False)
        self.defaultLabelTextLine = QLineEdit()
        useDefaultLabelQHBoxLayout = QHBoxLayout()
        useDefaultLabelQHBoxLayout.addWidget(self.useDefaultLabelCheckbox)
        useDefaultLabelQHBoxLayout.addWidget(self.defaultLabelTextLine)
        useDefaultLabelContainer = QWidget()
        # useDefaultLabelContainer.setLayout(useDefaultLabelQHBoxLayout)

        # Create a widget for edit and diffc button
        # self.diffcButton = QCheckBox(getStr('useDifficult'))
        # self.diffcButton.setChecked(False)
        # self.diffcButton.stateChanged.connect(self.btnstate)
        self.editButton = QToolButton()
        self.editButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.saveFormatCBox = QCheckBox('Auto save format')
        self.saveFormatCBox.setChecked(False)

        # Add some of widgets to listLayout
        listLayout.addWidget(self.editButton)
        # listLayout.addWidget(self.diffcButton)
        listLayout.addWidget(self.saveFormatCBox)
        listLayout.addWidget(useDefaultLabelContainer)
        labelListContainer = QWidget()
        labelListContainer.setLayout(listLayout)

        # Create and add a widget for showing current label items
        self.labelList = QTreeWidget()
        self.labelList.itemActivated.connect(self.labelSelectionChanged)
        self.labelList.itemSelectionChanged.connect(self.labelSelectionChanged)
        self.labelList.itemDoubleClicked.connect(self.editLabel)
        # Connect to itemChanged to detect checkbox changes.
        self.labelList.itemChanged.connect(self.labelItemChanged)
        listLayout.addWidget(self.labelList)

        self.dock = QDockWidget(getStr('boxLabelText'), self)
        self.dock.setObjectName(getStr('labels'))
        self.dock.setWidget(labelListContainer)

        self.fileListWidget = QListWidget()
        self.fileListWidget.itemDoubleClicked.connect(self.fileitemDoubleClicked)
        filelistLayout = QVBoxLayout()
        filelistLayout.setContentsMargins(0, 0, 0, 0)
        filelistLayout.addWidget(self.fileListWidget)
        fileListContainer = QWidget()
        fileListContainer.setLayout(filelistLayout)
        self.filedock = QDockWidget(getStr('fileList'), self)
        self.filedock.setObjectName(getStr('files'))
        self.filedock.setWidget(fileListContainer)

        self.zoomWidget = ZoomWidget()
        self.colorDialog = ColorDialog(parent=self)

        self.canvas = Canvas(parent=self)
        self.canvas.zoomRequest.connect(self.zoomRequest)
        self.canvas.setDrawingShapeToSquare(settings.get(SETTING_DRAW_SQUARE, False))

        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        self.scrollBars = {
            Qt.Vertical: scroll.verticalScrollBar(),
            Qt.Horizontal: scroll.horizontalScrollBar()
        }
        self.scrollArea = scroll
        self.canvas.scrollRequest.connect(self.scrollRequest)

        self.canvas.newShape.connect(self.newShape)
        self.canvas.shapeMoved.connect(self.setDirty)
        self.canvas.selectionChanged.connect(self.shapeSelectionChanged)
        self.canvas.drawingPolygon.connect(self.toggleDrawingSensitive)

        self.setCentralWidget(scroll)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filedock)
        self.filedock.setFeatures(QDockWidget.DockWidgetFloatable)

        self.dockFeatures = QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable
        self.dock.setFeatures(self.dock.features() ^ self.dockFeatures)

        # Actions
        action = partial(newAction, self)
        quit = action(getStr('quit'), self.close,
                      'Ctrl+Q', 'quit', getStr('quitApp'))

        upLoadBtn = action('Upload', self.upLoadBtn,
                           'Ctrl+l', 'upload', 'completed upload to sever')

        download = action('hint', self.download,
                      'Ctrl+x', 'download', 'download hint from sever')

        train = action('train', self.train,
                       'Ctrl+t', 'train', 'choose data and train')

        trainStatus = action('train status', self.trainning_status,
                             'Ctrl+z', 'trainStatus', 'trainning status')

        checkpoint= action('switch_checkpoint', self.choose_checkpoint,
                      None, 'switch_checkpoint', 'choose checkpoint will use')

        downloadCheckpoint= action('download checkpoint', self.download_checkpoint,
                      None, 'download', 'choose checkpoint will download')


        opendir = action(getStr('openDir'), self.openDirDialog,
                         'Ctrl+u', 'open', getStr('openDir'))

        changeSavedir = action(getStr('changeSaveDir'), self.changeSavedirDialog,
                               'Ctrl+r', 'open', getStr('changeSavedAnnotationDir'))

        openAnnotation = action(getStr('openAnnotation'), self.openAnnotationDialog,
                                'Ctrl+Shift+O', 'open', getStr('openAnnotationDetail'))

        openNextImg = action(getStr('nextImg'), self.openNextImg,
                             'd', 'next', getStr('nextImgDetail'))

        openPrevImg = action(getStr('prevImg'), self.openPrevImg,
                             'a', 'prev', getStr('prevImgDetail'))

        save = action(getStr('save'), self.saveFile,
                      'Ctrl+S', 'save', getStr('saveDetail'), enabled=False)

        saveAs = action(getStr('saveAs'), self.saveFileAs,
                        'Ctrl+Shift+S', 'save-as', getStr('saveAsDetail'), enabled=False)

        close = action(getStr('closeCur'), self.closeFile, 'Ctrl+W', 'close', getStr('closeCurDetail'))

        resetAll = action(getStr('resetAll'), self.resetAll, None, 'resetall', getStr('resetAllDetail'))

        color1 = action(getStr('boxLineColor'), self.chooseColor1,
                        'Ctrl+L', 'color_line', getStr('boxLineColorDetail'))

        createMode = action(getStr('crtBox'), self.setCreateMode,
                            'w', 'new', getStr('crtBoxDetail'), enabled=False)
        editMode = action('&Edit\nRectBox', self.setEditMode,
                          'e', 'edit', u'Move and edit Boxs', enabled=False)

        create = action(getStr('crtBox'), self.createShape,
                        'w', 'new', getStr('crtBoxDetail'), enabled=False)
        delete = action(getStr('delBox'), self.deleteSelectedShape,
                        'Delete', 'delete', getStr('delBoxDetail'), enabled=False)
        copy = action(getStr('dupBox'), self.copySelectedShape,
                      'Ctrl+D', 'copy', getStr('dupBoxDetail'),
                      enabled=False)

        advancedMode = action(getStr('advancedMode'), self.toggleAdvancedMode,
                              'Ctrl+Shift+A', 'expert', getStr('advancedModeDetail'),
                              checkable=True)

        hideAll = action('&Hide\nRectBox', partial(self.togglePolygons, False),
                         'Ctrl+H', 'hide', getStr('hideAllBoxDetail'),
                         enabled=False)
        showAll = action('&Show\nRectBox', partial(self.togglePolygons, True),
                         'Ctrl+A', 'hide', getStr('showAllBoxDetail'),
                         enabled=False)

        help = action(getStr('tutorial'), self.showTutorialDialog, None, 'help', getStr('tutorialDetail'))
        showInfo = action(getStr('info'), self.showInfoDialog, None, 'help', getStr('info'))

        zoom = QWidgetAction(self)
        zoom.setDefaultWidget(self.zoomWidget)

        self.zoomWidget.setWhatsThis(
            u"Zoom in or out of the image. Also accessible with"
            " %s and %s from the canvas." % (fmtShortcut("Ctrl+[-+]"),
                                             fmtShortcut("Ctrl+Wheel")))
        self.zoomWidget.setEnabled(False)

        zoomIn = action(getStr('zoomin'), partial(self.addZoom, 10),
                        'Ctrl++', 'zoom-in', getStr('zoominDetail'), enabled=False)
        zoomOut = action(getStr('zoomout'), partial(self.addZoom, -10),
                         'Ctrl+-', 'zoom-out', getStr('zoomoutDetail'), enabled=False)
        zoomOrg = action(getStr('originalsize'), partial(self.setZoom, 100),
                         'Ctrl+=', 'zoom', getStr('originalsizeDetail'), enabled=False)
        fitWindow = action(getStr('fitWin'), self.setFitWindow,
                           'Ctrl+F', 'fit-window', getStr('fitWinDetail'),
                           checkable=True, enabled=False)
        fitWidth = action(getStr('fitWidth'), self.setFitWidth,
                          'Ctrl+Shift+F', 'fit-width', getStr('fitWidthDetail'),
                          checkable=True, enabled=False)
        # Group zoom controls into a list for easier toggling.
        zoomActions = (self.zoomWidget, zoomIn, zoomOut,
                       zoomOrg, fitWindow, fitWidth)
        self.zoomMode = self.MANUAL_ZOOM
        self.scalers = {
            self.FIT_WINDOW: self.scaleFitWindow,
            self.FIT_WIDTH: self.scaleFitWidth,
            # Set to one to scale to 100% when loading files.
            self.MANUAL_ZOOM: lambda: 1,
        }

        edit = action(getStr('editLabel'), self.editLabel,
                      'Ctrl+E', 'edit', getStr('editLabelDetail'),
                      enabled=False)
        self.editButton.setDefaultAction(edit)

        shapeLineColor = action(getStr('shapeLineColor'), self.chshapeLineColor,
                                icon='color_line', tip=getStr('shapeLineColorDetail'),
                                enabled=False)
        shapeFillColor = action(getStr('shapeFillColor'), self.chshapeFillColor,
                                icon='color', tip=getStr('shapeFillColorDetail'),
                                enabled=False)

        labels = self.dock.toggleViewAction()
        labels.setText(getStr('showHide'))
        labels.setShortcut('Ctrl+Shift+L')

        # Lavel list context menu.
        labelMenu = QMenu()
        addActions(labelMenu, (edit, delete))
        self.labelList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.labelList.customContextMenuRequested.connect(
            self.popLabelListMenu)

        # Draw squares/rectangles
        self.drawSquaresOption = QAction('Draw Squares', self)
        # self.drawSquaresOption.setShortcut('Ctrl+Shift+R')
        self.drawSquaresOption.setCheckable(True)
        self.drawSquaresOption.setChecked(settings.get(SETTING_DRAW_SQUARE, False))
        self.drawSquaresOption.triggered.connect(self.toogleDrawSquare)

        # Store actions for further handling.
        self.actions = struct(save=save, saveAs=saveAs, close=close, resetAll=resetAll,
                              lineColor=color1, create=create, delete=delete, edit=edit, copy=copy,
                              createMode=createMode, editMode=editMode, advancedMode=advancedMode,
                              shapeLineColor=shapeLineColor, shapeFillColor=shapeFillColor,
                              zoom=zoom, zoomIn=zoomIn, zoomOut=zoomOut, zoomOrg=zoomOrg,
                              fitWindow=fitWindow, fitWidth=fitWidth,
                              zoomActions=zoomActions,
                              fileMenuActions=(
                                  opendir, save, saveAs, close, resetAll, quit),
                              beginner=(), advanced=(),
                              editMenu=(edit, copy, delete,
                                        None, color1, self.drawSquaresOption),
                              beginnerContext=(create, edit, copy, delete),
                              advancedContext=(createMode, editMode, edit, copy,
                                               delete, shapeLineColor, shapeFillColor),
                              onLoadActive=(
                                  close, create, createMode, editMode),
                              onShapesPresent=(saveAs, hideAll, showAll))

        self.menus = struct(
            file=self.menu('&File'),
            edit=self.menu('&Edit'),
            sever=self.menu('&Sever'),
            view=self.menu('&View'),
            help=self.menu('&Help'),
            recentFiles=QMenu('Open &Recent'),
            labelList=labelMenu)

        # Auto saving : Enable auto saving if pressing next
        self.autoSaving = QAction(getStr('autoSaveMode'), self)
        self.autoSaving.setCheckable(True)
        self.autoSaving.setChecked(settings.get(SETTING_AUTO_SAVE, False))
        # Sync single class mode from PR#106
        self.singleClassMode = QAction(getStr('singleClsMode'), self)
        self.singleClassMode.setShortcut("Ctrl+Shift+S")
        self.singleClassMode.setCheckable(True)
        self.singleClassMode.setChecked(settings.get(SETTING_SINGLE_CLASS, False))
        self.lastLabel = None
        # Add option to enable/disable labels being displayed at the top of bounding boxes
        self.displayLabelOption = QAction(getStr('displayLabel'), self)
        self.displayLabelOption.setShortcut("Ctrl+Shift+P")
        self.displayLabelOption.setCheckable(True)
        self.displayLabelOption.setChecked(settings.get(SETTING_PAINT_LABEL, False))
        self.displayLabelOption.triggered.connect(self.togglePaintLabelsOption)

        addActions(self.menus.file,
                   (opendir, changeSavedir, openAnnotation, self.menus.recentFiles, save, saveAs, close, resetAll, quit))
        addActions(self.menus.help, (help, showInfo))
        addActions(self.menus.sever, (download, upLoadBtn, train, checkpoint, downloadCheckpoint, trainStatus))
        addActions(self.menus.view, (
            self.autoSaving,
            self.singleClassMode,
            self.displayLabelOption,
            labels, advancedMode, None,
            hideAll, showAll, None,
            zoomIn, zoomOut, zoomOrg, None,
            fitWindow, fitWidth))

        self.menus.file.aboutToShow.connect(self.updateFileMenu)

        # Custom context menu for the canvas widget:
        addActions(self.canvas.menus[0], self.actions.beginnerContext)
        addActions(self.canvas.menus[1], (
            action('&Copy here', self.copyShape),
            action('&Move here', self.moveShape)))

        self.tools = self.toolbar('Tools')
        self.actions.beginner = (
            opendir, changeSavedir, openNextImg, openPrevImg, save, download, upLoadBtn, train, trainStatus, create, None, copy, delete, None,
            zoomIn, zoom, zoomOut, fitWindow, fitWidth, checkpoint, downloadCheckpoint)

        self.actions.advanced = (
            opendir, changeSavedir, openNextImg, openPrevImg, save, download, upLoadBtn, train, trainStatus, createMode, None,
            editMode, None,
            hideAll, showAll, checkpoint, downloadCheckpoint)

        self.statusBar().showMessage('%s started.' % __appname__)
        self.statusBar().show()

        # Application state.
        self.image = QImage()
        self.filePath = ustr(defaultFilename)
        self.recentFiles = []
        self.maxRecent = 7
        self.lineColor = None
        self.fillColor = None
        self.zoom_level = 100
        self.fit_window = False

        ## Fix the compatible issue for qt4 and qt5. Convert the QStringList to python list
        if settings.get(SETTING_RECENT_FILES):
            if have_qstring():
                recentFileQStringList = settings.get(SETTING_RECENT_FILES)
                self.recentFiles = [ustr(i) for i in recentFileQStringList]
            else:
                self.recentFiles = recentFileQStringList = settings.get(SETTING_RECENT_FILES)

        size = settings.get(SETTING_WIN_SIZE, QSize(600, 500))
        position = QPoint(0, 0)
        saved_position = settings.get(SETTING_WIN_POSE, position)
        # Fix the multiple monitors issue
        for i in range(QApplication.desktop().screenCount()):
            if QApplication.desktop().availableGeometry(i).contains(saved_position):
                position = saved_position
                break
        self.resize(size)
        self.move(position)
        # saveDir = ustr(settings.get(SETTING_SAVE_DIR, None))
        # self.lastOpenDir = ustr(settings.get(SETTING_LAST_OPEN_DIR, None))
        # if self.defaultSaveDir is None and saveDir is not None and os.path.exists(saveDir):
        #     self.defaultSaveDir = saveDir
        #     self.statusBar().showMessage('%s started. Annotation will be saved to %s' %
        #                                  (__appname__, self.defaultSaveDir))
        #     self.statusBar().show()

        self.restoreState(settings.get(SETTING_WIN_STATE, QByteArray()))
        Shape.line_color = self.lineColor = QColor(settings.get(SETTING_LINE_COLOR, DEFAULT_LINE_COLOR))
        Shape.fill_color = self.fillColor = QColor(settings.get(SETTING_FILL_COLOR, DEFAULT_FILL_COLOR))
        self.canvas.setDrawingColor(self.lineColor)

        # Add chris
        # Shape.difficult = self.difficult

        def xbool(x):
            if isinstance(x, QVariant):
                return x.toBool()
            return bool(x)

        if xbool(settings.get(SETTING_ADVANCE_MODE, False)):
            self.actions.advancedMode.setChecked(True)
            self.toggleAdvancedMode()

        # Populate the File menu dynamically.
        self.updateFileMenu()

        # Since loading the file may take some time, make sure it runs in the background.
        if self.filePath and os.path.isdir(self.filePath):
            self.queueEvent(partial(self.importDirImages, self.filePath or ""))
        elif self.filePath:
            self.queueEvent(partial(self.loadFile, self.filePath or ""))

        # Callbacks:
        self.zoomWidget.valueChanged.connect(self.paintCanvas)

        self.populateModeActions()

        # Display cursor coordinates at the right of status bar
        self.labelCoordinates = QLabel('')
        self.statusBar().addPermanentWidget(self.labelCoordinates)

        # Open Dir if deafult file
        if self.filePath and os.path.isdir(self.filePath):
            self.openDirDialog(dirpath=self.filePath, silent=True)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.canvas.setDrawingShapeToSquare(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            # Draw rectangle if Ctrl is pressed
            self.canvas.setDrawingShapeToSquare(True)

    def noShapes(self):
        return not self.itemsToShapes

    def toggleAdvancedMode(self, value=True):
        self._beginner = not value
        self.canvas.setEditing(True)
        self.populateModeActions()
        self.editButton.setVisible(not value)
        if value:
            self.actions.createMode.setEnabled(True)
            self.actions.editMode.setEnabled(False)
            self.dock.setFeatures(self.dock.features() | self.dockFeatures)
        else:
            self.dock.setFeatures(self.dock.features() ^ self.dockFeatures)

    def populateModeActions(self):
        if self.beginner():
            tool, menu = self.actions.beginner, self.actions.beginnerContext
        else:
            tool, menu = self.actions.advanced, self.actions.advancedContext
        self.tools.clear()
        addActions(self.tools, tool)
        self.canvas.menus[0].clear()
        addActions(self.canvas.menus[0], menu)
        self.menus.edit.clear()
        actions = (self.actions.create,) if self.beginner() \
            else (self.actions.createMode, self.actions.editMode)
        addActions(self.menus.edit, actions + self.actions.editMenu)

    def setBeginner(self):
        self.tools.clear()
        addActions(self.tools, self.actions.beginner)

    def setAdvanced(self):
        self.tools.clear()
        addActions(self.tools, self.actions.advanced)

    def setDirty(self):
        self.dirty = True
        self.actions.save.setEnabled(True)

    def setClean(self):
        self.dirty = False
        self.actions.save.setEnabled(False)
        self.actions.create.setEnabled(True)

    def toggleActions(self, value=True):
        """Enable/Disable widgets which depend on an opened image."""
        for z in self.actions.zoomActions:
            z.setEnabled(value)
        for action in self.actions.onLoadActive:
            action.setEnabled(value)

    def queueEvent(self, function):
        QTimer.singleShot(0, function)

    def status(self, message, delay=5000):
        self.statusBar().showMessage(message, delay)

    def resetState(self):
        self.itemsToShapes.clear()
        self.shapesToItems.clear()
        self.labelList.clear()
        self.filePath = None
        self.imageData = None
        self.brandHint = None
        self.canvas.resetState()
        self.labelCoordinates.clear()

    def currentItem(self):
        items = self.labelList.selectedItems()
        if items:
            return items[0]
        return None

    def addRecentFile(self, filePath):
        if filePath in self.recentFiles:
            self.recentFiles.remove(filePath)
        elif len(self.recentFiles) >= self.maxRecent:
            self.recentFiles.pop()
        self.recentFiles.insert(0, filePath)

    def beginner(self):
        return self._beginner

    def advanced(self):
        return not self.beginner()

    def getAvailableScreencastViewer(self):
        osName = platform.system()

        if osName == 'Windows':
            return ['C:\\Program Files\\Internet Explorer\\iexplore.exe']
        elif osName == 'Linux':
            return ['xdg-open']
        elif osName == 'Darwin':
            return ['open']

    ## Callbacks ##
    def showTutorialDialog(self):
        # subprocess.Popen(self.screencastViewer + [self.screencast])
        print('test')

    def showInfoDialog(self):
        msg = u'Name:{0} \nApp Version:{1} \n{2} '.format(__appname__, __version__, sys.version_info)
        QMessageBox.information(self, u'Information', msg)

    def createShape(self):
        assert self.beginner()
        self.canvas.setEditing(False)
        self.actions.create.setEnabled(False)

    def toggleDrawingSensitive(self, drawing=True):
        """In the middle of drawing, toggling between modes should be disabled."""
        self.actions.editMode.setEnabled(not drawing)
        if not drawing and self.beginner():
            # Cancel creation.
            print('Cancel creation.')
            self.canvas.setEditing(True)
            self.canvas.restoreCursor()
            self.actions.create.setEnabled(True)

    def toggleDrawMode(self, edit=True):
        self.canvas.setEditing(edit)
        self.actions.createMode.setEnabled(edit)
        self.actions.editMode.setEnabled(not edit)

    def setCreateMode(self):
        assert self.advanced()
        self.toggleDrawMode(False)

    def setEditMode(self):
        assert self.advanced()
        self.toggleDrawMode(True)
        self.labelSelectionChanged()

    def updateFileMenu(self):
        currFilePath = self.filePath

        def exists(filename):
            return os.path.exists(filename)

        menu = self.menus.recentFiles
        menu.clear()
        files = [f for f in self.recentFiles if f !=
                 currFilePath and exists(f)]
        for i, f in enumerate(files):
            icon = newIcon('labels')
            action = QAction(
                icon, '&%d %s' % (i + 1, QFileInfo(f).fileName()), self)
            action.triggered.connect(partial(self.loadRecent, f))
            menu.addAction(action)

    def popLabelListMenu(self, point):
        self.menus.labelList.exec_(self.labelList.mapToGlobal(point))

    def editLabel(self):
        if not self.canvas.editing():
            return
        item = self.currentItem()
        if not item:
            return

        if item.childCount() == 0 and item.parent() is not None:
            # print('parent')
            item = item.parent()

        shape = self.itemsToShapes[item]
        dialog = LabelDialog(label=shape.label, subLabels=shape.subLabels)
        subLabels, saveData = dialog.popUp()
        # print(saveData)
        if subLabels is not None:
            text, sublabels = subLabels[0], subLabels[1:]
            if text is not None:
                item.setText(0, text)
                for i in reversed(range(item.childCount())):
                    item.removeChild(item.child(i))
                for sub in sublabels:
                    child = QTreeWidgetItem(item)
                    # child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    child.setText(0, sub)
                    child.setCheckState(0, Qt.Checked)

                item.setBackground(0, generateColorByText(text))
                shape.subLabels = sublabels
                shape.label = text
                self.setDirty()

                if saveData:
                    # print('save data')
                    self.dataSublabel[shape.label] = [shape.subLabels, self.convert_points_list(shape.points)]

    # Tzutalin 20160906 : Add file list and dock to move faster
    def fileitemDoubleClicked(self, item=None):
        # print(item)
        # item
        widget_item = self.fileListWidget.itemWidget(item)
        currIndex = self.mImgList.index(ustr(widget_item.getPath()))
        if currIndex < len(self.mImgList):
            filename = self.mImgList[currIndex]
            if filename:
                self.loadFile(filename)

    # Add chris
    # def btnstate(self, item= None):
    #     """ Function to handle difficult examples
    #     Update on each object """
    #     if not self.canvas.editing():
    #         return
    #
    #     item = self.currentItem()
    #     if not item: # If not selected Item, take the first one
    #         item = self.labelList.item(self.labelList.count()-1)
    #
    #     difficult = self.diffcButton.isChecked()
    #
    #     try:
    #         shape = self.itemsToShapes[item]
    #     except:
    #         pass
    #     # Checked and Update
    #     try:
    #         if difficult != shape.difficult:
    #             shape.difficult = difficult
    #             self.setDirty()
    #         else:  # User probably changed item visibility
    #             self.canvas.setShapeVisible(shape, item.checkState() == Qt.Checked)
    #     except:
    #         pass

    def scroll(self, item):
        self.labelList.scrollToItem(item, QAbstractItemView.PositionAtTop)

    # React to canvas signals.
    def shapeSelectionChanged(self, selected=False):
        if self._noSelectionSlot:
            self._noSelectionSlot = False
        else:
            shape = self.canvas.selectedShape
            if shape:
                self.shapesToItems[shape].setSelected(True)
                self.scroll(self.shapesToItems[shape])
            else:
                self.labelList.clearSelection()

        self.actions.delete.setEnabled(selected)
        self.actions.copy.setEnabled(selected)
        self.actions.edit.setEnabled(selected)
        self.actions.shapeLineColor.setEnabled(selected)
        self.actions.shapeFillColor.setEnabled(selected)

    def addLabel(self, shape):
        # print('addLabel')
        shape.paintLabel = self.displayLabelOption.isChecked()
        item = HashableQTreeWidgetItem(self.labelList)  # HashableQListWidgetItem(shape.label)

        item.setText(0, shape.label)
        item.setBackground(0, generateColorByText(shape.label))
        for sub in shape.subLabels:
            child = QTreeWidgetItem(item)
            child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
            child.setText(0, sub)
            child.setCheckState(0, Qt.Checked)

        self.itemsToShapes[item] = shape
        a = self.itemsToShapes[item]
        self.shapesToItems[shape] = item
        # self.canvas.setShapeVisible(shape, item.checkState(0) == Qt.Checked)
        # self.labelList.addItem(item)
        for action in self.actions.onShapesPresent:
            action.setEnabled(True)

    def remLabel(self, shape):
        if shape is None:
            # print('rm empty label')
            return
        item = self.shapesToItems[shape]
        self.labelList.takeTopLevelItem(self.labelList.indexOfTopLevelItem(item))
        self.canvas.selectedShape = None
        del self.shapesToItems[shape]
        del self.itemsToShapes[item]

    def loadLabels(self, shapes):
        s = []
        # for label, subLabel, points, line_color, fill_color, difficult in shapes:
        for label, subLabel, points, line_color, fill_color in shapes:
            # self.dataSublabel[label] = [subLabel, points]
            shape = Shape(label=label, subLabels=subLabel)
            for x, y in points:
                # Ensure the labels are within the bounds of the image. If not, fix them.
                x, y, snapped = self.canvas.snapPointToCanvas(x, y)
                if snapped:
                    self.setDirty()

                shape.addPoint(QPointF(x, y))
            # shape.difficult = difficult
            shape.close()
            s.append(shape)

            if line_color:
                shape.line_color = QColor(*line_color)
            else:
                shape.line_color = generateColorByText(label)

            if fill_color:
                shape.fill_color = QColor(*fill_color)
            else:
                shape.fill_color = generateColorByText(label)

            self.addLabel(shape)

        self.canvas.loadShapes(s)

    def saveLabels(self, annotationFilePath):
        annotationFilePath = ustr(annotationFilePath)

        def format_shape(s):
            return dict(label=s.label,
                        subLabels=s.subLabels,
                        line_color=s.line_color.getRgb(),
                        fill_color=s.fill_color.getRgb(),
                        points=[(p.x(), p.y()) for p in s.points]
                        )
            # # add chris
            #  difficult = s.difficult)

        shapes = [format_shape(shape) for shape in self.canvas.shapes]

        if annotationFilePath[-4:].lower() == ".xml":
            annotationFilePath = annotationFilePath[:-4]
            annotationFilePath += TXT_EXT
        elif annotationFilePath[-4:].lower() != ".xml" and annotationFilePath[-4:].lower() != ".txt":
            annotationFilePath += TXT_EXT

        f = open(annotationFilePath, 'w')
        for data in shapes:
            f.write('{0},{1},{2},{3},{4},{5},{6},{7},{8}|{9}\n'.format(int(data['points'][0][0]), int(data['points'][0][1]), \
                                                                       int(data['points'][1][0]), int(data['points'][1][1]), \
                                                                       int(data['points'][2][0]), int(data['points'][2][1]), \
                                                                       int(data['points'][3][0]), int(data['points'][3][1]), \
                                                                       data['label'], '|'.join(data['subLabels'])))
            if self.saveFormatCBox.checkState():
                # if data['label'] == 'MODEL':
                # print(data['label'] )
                # print([[int(data['points'][0][0]), int(data['points'][0][1])],
                #                                 [int(data['points'][1][0]), int(data['points'][1][1])],
                #                                 [int(data['points'][2][0]), int(data['points'][2][1])],
                #                                 [int(data['points'][3][0]), int(data['points'][3][1])]] )
                self.dataSublabel[data['label']] = [data['subLabels'],
                                                    [[int(data['points'][0][0]), int(data['points'][0][1])],
                                                     [int(data['points'][1][0]), int(data['points'][1][1])],
                                                     [int(data['points'][2][0]), int(data['points'][2][1])],
                                                     [int(data['points'][3][0]), int(data['points'][3][1])]]]
        f.close()

    def copySelectedShape(self):
        self.addLabel(self.canvas.copySelectedShape())
        # fix copy and delete
        self.shapeSelectionChanged(True)

    def labelSelectionChanged(self):
        # print('labelSelectionChanged')
        item = self.currentItem()

        if item and self.canvas.editing():
            if item.childCount() == 0 and item.parent() is not None:
                print('parent')
                item = item.parent()

            self._noSelectionSlot = True
            self.canvas.selectShape(self.itemsToShapes[item])
            # shape = self.itemsToShapes[item]
            # # Add Chris
            # self.diffcButton.setChecked(shape.difficult)

    def labelItemChanged(self, item):

        try:
            # print('labelItemChanged')
            shape = self.itemsToShapes[item]
        except:
            return
        label = item.text(0)
        # print(label)
        if label != shape.label:
            shape.label = item.text(0)
            shape.line_color = generateColorByText(shape.label)
            self.setDirty()
        else:  # User probably changed item visibility
            self.canvas.setShapeVisible(shape, item.checkState(0) == Qt.Checked)

    def convert_points_list(self, points1):
        xi1, yi1 = int(points1[0].x()), int(points1[0].y())
        xi2, yi2 = int(points1[1].x()), int(points1[1].y())
        xi3, yi3 = int(points1[2].x()), int(points1[2].y())
        xi4, yi4 = int(points1[3].x()), int(points1[3].y())

        plist = [[xi1, yi1], [xi2, yi2], [xi3, yi3], [xi4, yi4]]
        return plist

    def minEditdistanceLabel(self, label, listword=None):

        if listword is None:
            listword = ['JAPAN', 'NISSAN', 'TOYOTA', 'DAIHATSU', 'SUZUKI', 'CORPORATION', 'CO.,LTD.', \
                        'TRIM', 'COLOR', 'ENGINE', 'CHASSIS', 'CHASSIS NO.', 'MODEL', 'PLANT', 'PLANTA', 'TRANS', \
                        'TYPE', 'TIPO', 'MODELD', 'MOTOR']
        else:
            listword = list(listword)

        from editdistance import distance

        minedit = 100
        minIdx = -1
        for i, w in enumerate(listword):
            d = distance(w, label)
            if d < minedit and d <= len(w) / 4:
                minedit = d
                minIdx = i

        if minIdx > -1:
            return listword[minIdx]
        else:
            return label

    #
    # def get_this_reflabel(self):
    #     point = self.canvas.shapes[-1].points
    #     points = self.convert_points_list(point)
    #     x_begin = int(points[0][0])
    #     label = ''
    #     preNote = ''
    #     for shape in self.shapesRefs:
    #         if self.brandHint is None:
    #             self.brandHint = shape['brand']
    #         pointsRef = shape['points']
    #         if self.check_overlap(points, pointsRef, x_begin=x_begin):
    #             label += shape['label']
    #             x_begin = pointsRef[0][0]
    #             if preNote is None:
    #                 print('preNote is None')
    #                 preNote = shape['note']
    #             elif preNote == 'None':
    #                 print('preNote == None')
    #                 preNote = shape['note']
    #             elif preNote == '':
    #                 print('preNote == ')
    #                 preNote = shape['note']
    #
    #     if len(self.shapesRefs) < 1:
    #         self.brandHint = 'daihatsu'
    #     if label != '':
    #         return self.minEditdistanceLabel(label), preNote
    #     else:
    #         return self.prevLabelText, preNote

    # def leftKey(self):
    #     KEYS = ['CHASSIS', 'FRAME', 'MODEL', 'TYPE', 'COLOR', 'TRIM', 'ENGINE', 'TRANS']
    #     point = self.canvas.shapes[-1].points
    #     points = self.convert_points_list(point)
    #
    #     for shape in self.canvas.shapes[:-1]:
    #         point = shape.points
    #         points2 = self.convert_points_list(point)
    #
    #         inKey = False
    #         for k in KEYS:
    #             if shape.label in k or k in shape.label:
    #                 inKey = True
    #                 break
    #         if self.check_overlap(points, points2, end_x=points[0][0], only_line=True) and inKey:
    #             print('label', shape.label)
    #             return shape.label
    #     return None

    # Callback functions:

    def onlyPositionRefile(self, points):
        ret_subs = []
        ret_lb = ''
        points = self.convert_points_list(points)
        for shape in self.shapesRefs:
            ps = shape['points']
            if self.check_overlap(points, ps):
                ret_lb = shape['label']
                if ret_lb in self.dataSublabel:
                    ret_subs = self.dataSublabel[ret_lb][0]
                else:
                    ret_subs = shape['subLabel']
                return ret_subs, ret_lb
        return ret_subs, ret_lb

    def newShape(self):
        """Pop-up and give focus to the label editor.

        position MUST be in global coordinates.
        """
        # ref_label, preNote = self.get_this_reflabel()
        # if preNote == '' and secondPreNote is not None:
        #     preNote = secondPreNote
        #
        # if not self.useDefaultLabelCheckbox.isChecked() or not self.defaultLabelTextLine.text():
        #     if len(self.labelHist) > 0:
        #         self.labelDialog = LabelDialog(
        #             parent=self, listItem=self.labelHist, listItem2=self.brandlist, listItem3=self.notelist)
        #
        #     # Sync single class mode from PR#106
        #     if self.singleClassMode.isChecked() and self.lastLabel:
        #         text = self.lastLabel
        #         brand, note = '', ''
        #     else:
        #         if ref_label in self.refDict:
        #             self.labelDialog.addtextToList(texts=self.refDict[ref_label])
        #         if secondPreNote is not None:
        #             self.labelDialog.addtextToList(textsNote=[secondPreNote])
        #
        #         text, brand, note = self.labelDialog.popUp(text=ref_label, brand= self.brandHint, note=preNote)
        #         self.lastLabel = text
        # else:
        #     text = self.defaultLabelTextLine.text()
        #     brand, note = '', ''
        subLabels, ret_lb = self.onlyPosition(self.canvas.shapes[-1].points)
        if ret_lb == '' and subLabels == []:
            subLabels, ret_lb = self.onlyPositionRefile(self.canvas.shapes[-1].points)

        # if len(self.labelHist) > 0:
        self.labelDialog = LabelDialog(
            parent=self, label=ret_lb, subLabels=subLabels)

        subLabels, saveData = self.labelDialog.popUp()

        # Add Chris
        if subLabels is not None:
            text = subLabels[0]
            subLabels = subLabels[1:]
            # print('text:', text)
            self.lastLabel = text
            self.prevLabelText = text

            generate_color = generateColorByText(text)
            shape = self.canvas.setLastLabel(text=text, subLabels=subLabels, line_color=generate_color, fill_color=generate_color)
            self.addLabel(shape)

            if self.beginner():  # Switch to edit mode.
                self.canvas.setEditing(True)
                self.actions.create.setEnabled(True)
            else:
                self.actions.editMode.setEnabled(True)
            self.setDirty()

            if saveData:
                # print('save new data')
                self.dataSublabel[shape.label] = [shape.subLabels, self.convert_points_list(shape.points)]

        else:
            # print('canvas.resetAllLines()')
            # self.canvas.undoLastLine()
            self.canvas.resetAllLines()

    def scrollRequest(self, delta, orientation):
        units = - delta / (8 * 15)
        bar = self.scrollBars[orientation]
        bar.setValue(bar.value() + bar.singleStep() * units)

    def setZoom(self, value):
        self.actions.fitWidth.setChecked(False)
        self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.MANUAL_ZOOM
        self.zoomWidget.setValue(value)

    def addZoom(self, increment=10):
        self.setZoom(self.zoomWidget.value() + increment)

    def zoomRequest(self, delta):
        # get the current scrollbar positions
        # calculate the percentages ~ coordinates
        h_bar = self.scrollBars[Qt.Horizontal]
        v_bar = self.scrollBars[Qt.Vertical]

        # get the current maximum, to know the difference after zooming
        h_bar_max = h_bar.maximum()
        v_bar_max = v_bar.maximum()

        # get the cursor position and canvas size
        # calculate the desired movement from 0 to 1
        # where 0 = move left
        #       1 = move right
        # up and down analogous
        cursor = QCursor()
        pos = cursor.pos()
        relative_pos = QWidget.mapFromGlobal(self, pos)

        cursor_x = relative_pos.x()
        cursor_y = relative_pos.y()

        w = self.scrollArea.width()
        h = self.scrollArea.height()

        # the scaling from 0 to 1 has some padding
        # you don't have to hit the very leftmost pixel for a maximum-left movement
        margin = 0.1
        move_x = (cursor_x - margin * w) / (w - 2 * margin * w)
        move_y = (cursor_y - margin * h) / (h - 2 * margin * h)

        # clamp the values from 0 to 1
        move_x = min(max(move_x, 0), 1)
        move_y = min(max(move_y, 0), 1)

        # zoom in
        units = delta / (8 * 15)
        scale = 10
        self.addZoom(scale * units)

        # get the difference in scrollbar values
        # this is how far we can move
        d_h_bar_max = h_bar.maximum() - h_bar_max
        d_v_bar_max = v_bar.maximum() - v_bar_max

        # get the new scrollbar values
        new_h_bar_value = h_bar.value() + move_x * d_h_bar_max
        new_v_bar_value = v_bar.value() + move_y * d_v_bar_max

        h_bar.setValue(new_h_bar_value)
        v_bar.setValue(new_v_bar_value)

    def setFitWindow(self, value=True):
        if value:
            self.actions.fitWidth.setChecked(False)
        self.zoomMode = self.FIT_WINDOW if value else self.MANUAL_ZOOM
        self.adjustScale()

    def setFitWidth(self, value=True):
        if value:
            self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.FIT_WIDTH if value else self.MANUAL_ZOOM
        self.adjustScale()

    def togglePolygons(self, value):
        for item, shape in self.itemsToShapes.items():
            item.setCheckState(0, Qt.Checked if value else Qt.Unchecked)

    def loadFile(self, filePath=None):
        """Load the specified file, or the last opened file if None."""
        self.resetState()
        self.canvas.setEnabled(False)
        if filePath is None:
            filePath = self.settings.get(SETTING_FILENAME)

        # Make sure that filePath is a regular python string, rather than QString
        filePath = ustr(filePath)

        # Fix bug: An  index error after select a directory when open a new file.
        unicodeFilePath = ustr(filePath)
        unicodeFilePath = os.path.abspath(unicodeFilePath)
        # Tzutalin 20160906 : Add file list and dock to move faster
        # Highlight the file item
        if unicodeFilePath and self.fileListWidget.count() > 0:
            if unicodeFilePath in self.mImgList:
                index = self.mImgList.index(unicodeFilePath)
                fileWidgetItem = self.fileListWidget.item(index)
                fileWidgetItem.setSelected(True)
            else:
                self.fileListWidget.clear()
                self.mImgList.clear()

        if unicodeFilePath and os.path.exists(unicodeFilePath):
            # Load image:
            # read data first and store for saving into label file.
            self.imageData = read(unicodeFilePath, None)
            self.canvas.verified = False

            image = QImage.fromData(self.imageData)
            if image.isNull():
                self.errorMessage(u'Error opening file',
                                  u"<p>Make sure <i>%s</i> is a valid image file." % unicodeFilePath)
                self.status("Error reading %s" % unicodeFilePath)
                return False
            self.status("Loaded %s" % os.path.basename(unicodeFilePath))
            self.image = image
            self.filePath = unicodeFilePath
            self.canvas.loadPixmap(QPixmap.fromImage(image))
            self.setClean()
            self.canvas.setEnabled(True)
            self.adjustScale(initial=True)
            self.paintCanvas()
            self.addRecentFile(self.filePath)
            self.toggleActions(True)

            # Label xml file and show bound box according to its filename
            # if self.usingPascalVocFormat is True:
            self.loadRefFile(self.filePath)
            if self.defaultSaveDir is not None:
                basename = os.path.basename(
                    os.path.splitext(self.filePath)[0])
                # xmlPath = os.path.join(self.defaultSaveDir, basename + XML_EXT)
                txtPath = os.path.join(self.defaultSaveDir, basename + TXT_EXT)
                """Annotation file priority:
                PascalXML > YOLO
                """
                print(txtPath)
                if os.path.exists(txtPath):
                    self.loadYOLOTXTByFilename(txtPath)
                else:
                    print('beginFromRef')
                    self.beginFromRef(basename)
            else:
                txtPath = os.path.splitext(filePath)[0] + TXT_EXT
                print(txtPath)
                basename = os.path.basename(
                    os.path.splitext(self.filePath)[0])
                if os.path.exists(txtPath):
                    self.loadYOLOTXTByFilename(txtPath)
                else:
                    print('beginFromRef')
                    self.beginFromRef(basename)

            self.setWindowTitle(__appname__ + ' ' + filePath)

            # Default : select last item if there is at least one item
            if self.labelList.topLevelItemCount():
                self.labelList.setCurrentItem(self.labelList.topLevelItem(self.labelList.topLevelItemCount() - 1))
                self.labelList.topLevelItem(self.labelList.topLevelItemCount() - 1).setSelected(True)

            self.canvas.setFocus(True)
            return True
        return False

    def resizeEvent(self, event):
        if self.canvas and not self.image.isNull() \
                and self.zoomMode != self.MANUAL_ZOOM:
            self.adjustScale()
        super(MainWindow, self).resizeEvent(event)

    def paintCanvas(self):
        assert not self.image.isNull(), "cannot paint null image"
        self.canvas.scale = 0.01 * self.zoomWidget.value()
        self.canvas.adjustSize()
        self.canvas.update()

    def adjustScale(self, initial=False):
        value = self.scalers[self.FIT_WINDOW if initial else self.zoomMode]()
        self.zoomWidget.setValue(int(100 * value))

    def scaleFitWindow(self):
        """Figure out the size of the pixmap in order to fit the main widget."""
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.centralWidget().width() - e
        h1 = self.centralWidget().height() - e
        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.canvas.pixmap.width() - 0.0
        h2 = self.canvas.pixmap.height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def scaleFitWidth(self):
        # The epsilon does not seem to work too well here.
        w = self.centralWidget().width() - 2.0
        return w / self.canvas.pixmap.width()

    def closeEvent(self, event):
        if not self.mayContinue():
            event.ignore()
        settings = self.settings

        self.save_dataSublabels()

        # If it loads images from dir, don't load it at the begining
        if self.dirname is None:
            settings[SETTING_FILENAME] = self.filePath if self.filePath else ''
        else:
            settings[SETTING_FILENAME] = ''

        settings[SETTING_WIN_SIZE] = self.size()
        settings[SETTING_WIN_POSE] = self.pos()
        settings[SETTING_WIN_STATE] = self.saveState()
        settings[SETTING_LINE_COLOR] = self.lineColor
        settings[SETTING_FILL_COLOR] = self.fillColor
        settings[SETTING_RECENT_FILES] = self.recentFiles
        settings[SETTING_ADVANCE_MODE] = not self._beginner
        if self.defaultSaveDir and os.path.exists(self.defaultSaveDir):
            settings[SETTING_SAVE_DIR] = ustr(self.defaultSaveDir)
        else:
            settings[SETTING_SAVE_DIR] = ''

        if self.lastOpenDir and os.path.exists(self.lastOpenDir):
            settings[SETTING_LAST_OPEN_DIR] = self.lastOpenDir
        else:
            settings[SETTING_LAST_OPEN_DIR] = ''

        settings[SETTING_AUTO_SAVE] = self.autoSaving.isChecked()
        settings[SETTING_SINGLE_CLASS] = self.singleClassMode.isChecked()
        settings[SETTING_PAINT_LABEL] = self.displayLabelOption.isChecked()
        settings[SETTING_DRAW_SQUARE] = self.drawSquaresOption.isChecked()
        settings.save()

    def loadRecent(self, filename):
        if self.mayContinue():
            self.loadFile(filename)

    def scanAllImages(self, folderPath):
        extensions = ['.%s' % fmt.data().decode("ascii").lower() for fmt in QImageReader.supportedImageFormats()]
        images = []

        for root, dirs, files in os.walk(folderPath):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relativePath = os.path.join(root, file)
                    path = ustr(os.path.abspath(relativePath))
                    images.append(path)
        natural_sort(images, key=lambda x: x.lower())
        return images

    def changeSavedirDialog(self, _value=False):

        saveDir = ustr(self.settings.get(SETTING_SAVE_DIR, None))

        if self.defaultSaveDir is not None:
            path = ustr(self.defaultSaveDir)
        elif saveDir is not None and os.path.exists(saveDir):
            path = saveDir
        else:
            path = '.'

        dirpath = ustr(QFileDialog.getExistingDirectory(self,
                                                        '%s - Save annotations to the directory' % __appname__, path, QFileDialog.ShowDirsOnly
                                                        | QFileDialog.DontResolveSymlinks))

        if dirpath is not None and len(dirpath) > 1:
            self.defaultSaveDir = dirpath

        self.statusBar().showMessage('%s . Annotation will be saved to %s' %
                                     ('Change saved folder', self.defaultSaveDir))
        self.statusBar().show()

    def openAnnotationDialog(self, _value=False):
        if self.filePath is None:
            self.statusBar().showMessage('Please select image first')
            self.statusBar().show()
            return

        path = os.path.dirname(ustr(self.filePath)) \
            if self.filePath else '.'
        if self.usingPascalVocFormat:
            filters = "Open Annotation XML file (%s)" % ' '.join(['*.xml'])
            filename = ustr(QFileDialog.getOpenFileName(self, '%s - Choose a xml file' % __appname__, path, filters))
            if filename:
                if isinstance(filename, (tuple, list)):
                    filename = filename[0]
            self.loadPascalXMLByFilename(filename)

    def openDirDialog(self, _value=False, dirpath=None, silent=False):
        if not self.mayContinue():
            return

        lastDir = ustr(self.settings.get(SETTING_LAST_OPEN_DIR, None))

        defaultOpenDirPath = dirpath if dirpath else '.'
        if self.lastOpenDir and os.path.exists(self.lastOpenDir):
            defaultOpenDirPath = self.lastOpenDir
        elif lastDir and os.path.exists(lastDir):
            defaultOpenDirPath = lastDir
        else:
            defaultOpenDirPath = os.path.dirname(self.filePath) if self.filePath else '.'

        if silent != True:
            targetDirPath = ustr(QFileDialog.getExistingDirectory(self,
                                                                  '%s - Open Directory' % __appname__, defaultOpenDirPath,
                                                                  QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        else:
            targetDirPath = ustr(defaultOpenDirPath)

        self.importDirImages(targetDirPath)

    def isExistsRefDir(self):
        if not os.path.exists(self.refDir):
            return False
        list_imgs = os.listdir(self.lastOpenDir)
        list_refs = os.listdir(self.refDir)
        check = ['{}.txt'.format(os.path.splitext(fn)[0]) in list_refs for fn in list_imgs]
        if all(check):
            return True
        else:
            return False

    def importDirImages(self, dirpath):
        # if not self.mayContinue() or not dirpath:
        #     return
        if not dirpath:
            return

        self.lastOpenDir = dirpath

        output_dir = os.path.join(os.getcwd(), 'datasets/detect_label/')
        output_name = os.path.basename(os.path.abspath(self.lastOpenDir))
        self.refDir = os.path.join(output_dir, output_name)
        if not self.isExistsRefDir():
            self.download()

        self.dirname = dirpath
        self.defaultSaveDir = None
        self.filePath = None
        self.fileListWidget.clear()
        self.mImgList = self.scanAllImages(dirpath)
        self.dirty = False
        self.openNextImg()
        for imgPath in self.mImgList:
            myQCustomQWidget = QCustomQWidget(imgPath)
            item = QListWidgetItem()
            item.setSizeHint(myQCustomQWidget.sizeHint())
            self.fileListWidget.addItem(item)
            self.fileListWidget.setItemWidget(item, myQCustomQWidget)

            # item = QCustomQWidget()
            # item.setIcon(imgPath)
            # item.setTextUp(imgPath)
            # self.fileListWidget.addItem(item)

    # load file txt to ref label
    def loadRefFile(self, imgPath):
        self.shapesRefs = []
        baseName = os.path.splitext(os.path.basename(imgPath))[0] + '.txt'
        print('baseName', baseName)

        refPath = os.path.join(self.refDir, baseName)
        if os.path.exists(refPath):
            unicodeRefPath = ustr(refPath)
            unicodeFilePath = os.path.abspath(unicodeRefPath)
            with open(unicodeFilePath, 'r') as f:
                for line in f:
                    text = line.split('\n')[0]
                    x1, y1, x2, y2, x3, y3, x4, y4 = text.split(',')[:8]
                    labels = ''.join(text.split(',')[8:])
                    points = [(int(x1), int(y1)), (int(x2), int(y2)), (int(x3), int(y3)), (int(x4), int(y4))]

                    if len(labels.split('|')) >= 1:
                        label = labels.split('|')[0]
                        subLabel = labels.split('|')[1:]
                    else:
                        label = labels
                        subLabel = []

                    shape = {'points': points, 'label': label, 'subLabel': subLabel}
                    self.shapesRefs.append(shape)

        self.shapesRefs.sort(key=lambda x: x['points'][0])
        return

    def openPrevImg(self, _value=False):
        # Proceding prev image without dialog if having any label
        if self.autoSaving.isChecked():
            if self.defaultSaveDir is not None:
                if self.dirty is True:
                    self.saveFile()
            else:
                self.changeSavedirDialog()
                return

        if not self.mayContinue():
            return

        if len(self.mImgList) <= 0:
            return

        if self.filePath is None:
            return

        currIndex = self.mImgList.index(self.filePath)
        if currIndex - 1 >= 0:
            filename = self.mImgList[currIndex - 1]
            if filename:
                print(filename)
                self.loadRefFile(filename)
                self.loadFile(filename)

    def openNextImg(self, _value=False):
        # Proceding prev image without dialog if having any label
        if self.autoSaving.isChecked():
            if self.defaultSaveDir is not None:
                if self.dirty is True:
                    self.saveFile()
            else:
                self.changeSavedirDialog()
                return

        if not self.mayContinue():
            return

        if len(self.mImgList) <= 0:
            return

        filename = None
        if self.filePath is None:
            filename = self.mImgList[0]
        else:
            currIndex = self.mImgList.index(self.filePath)
            if currIndex + 1 < len(self.mImgList):
                filename = self.mImgList[currIndex + 1]

        if filename:
            self.loadRefFile(filename)
            self.loadFile(filename)

    def upLoadBtn(self, _value=False):
        if self.lastOpenDir is None or self.defaultSaveDir is None:
            mess = 'prerequisite, must open a folder and choose save folder'
            QMessageBox.information(self, "Message", mess)

            return
        elif not os.path.exists(self.lastOpenDir) or not os.path.exists(self.defaultSaveDir):
            mess = 'prerequisite, must open a folder and choose save folder'
            QMessageBox.information(self, "Message", mess)

            return
        upLoadWind = uploadDialog(self, name=os.path.basename(self.defaultSaveDir))
        newName = upLoadWind.get_name()
        try:
            if newName is not None:
                print(newName)
                wai = labelDialog2.waitDialog(title='uploading', txtt='wait awhile, until upload {} done\n folder path: {}'.format(newName, self.defaultSaveDir),
                                 num=0)
                dowloadAPI.upload_gt_dir(os.path.abspath(self.lastOpenDir), os.path.abspath(self.defaultSaveDir),
                                         newName=newName)
                wai.mess = 'upload completed'
                wai.done_close()
            else:
                print('newName is', newName)
        except:
            wai = labelDialog2.waitDialog('can not connect server', num=0)
            wai.delay(1000)
            wai.done_close()

    def download(self, _value=False):
        print('dir', self.lastOpenDir)
        if self.lastOpenDir is None:
            mess = 'prerequisite, must open a folder and choose save folder'
            QMessageBox.information(self, "Message", mess)
            return
        elif not os.path.exists(self.lastOpenDir):
            mess = 'prerequisite, must open a folder and choose save folder'
            QMessageBox.information(self, "Message", mess)
            return

        wai = labelDialog2.waitDialog(txtt='wait awhile, until download done \n folder path: {}'.format(self.lastOpenDir), num=0)
        output_dir = os.path.join(os.getcwd(), 'datasets/detect_label/')
        output_name = os.path.basename(os.path.abspath(self.lastOpenDir))
        self.refDir = os.path.join(output_dir, output_name)
        if not os.path.exists(self.refDir):
            os.mkdir(self.refDir)
        status_code = dowloadAPI.downloadHint(os.path.abspath(self.lastOpenDir), self.refDir, wai)
        if status_code == 200:
            wai.mess = 'load hint completed'
        else:
            wai.mess = 'An error occurred'
        wai.done_close()

    def train(self, _value=False):
        # try:
        content, mess = dowloadAPI.request_current_synDir()
        if mess is None:
            (current_synDir, pretrain_list, note_list) = content
            print(note_list)
            trainWind = trainDialog(parent=self, listData=current_synDir, listPretrain=pretrain_list, listnote=note_list, numEpoch=100)
            synDirs_chose, pretrain, numEpoch, prefixName = trainWind.get_synDir_chose()
            print(synDirs_chose, pretrain, numEpoch, prefixName)
            if synDirs_chose is not None:
                print('chose:', synDirs_chose)
                # sent list dirs to start train
                verify = dowloadAPI.sent_synDirs_chose(synDirs_chose, pretrain, numEpoch, prefixName)
            else:
                print('synDirs_chose is None')
        else:
            wai = labelDialog2.waitDialog(title='training', txtt=mess, num=0)
            wai.delay(1000)
            wai.done_close()
        # except:
        #     wai = waitDialog('can not connect server', num=0)
        #     wai.delay(1000)
        #     wai.done_close()


    def trainning_status(self, _value=False):

        checkpointDf, training_log, status_code = dowloadAPI.request_train_status()

        if status_code not in [201, 200]:
            wai = labelDialog2.waitDialog(txtt='error appeared', num=0)
            wai.delay(1000)
            wai.done_close()
            return

        win_status = TrainStatus(checkpointDf=checkpointDf, training_log=training_log)
        notes = win_status.get_note()

        if notes:
            print('notes:', notes)
            dowloadAPI.request_save_notes(notes, dir_path=None)
        else:
            print('notes is None:', notes)

    @staticmethod
    def train_history(cpt_name=None):
        checkpointDf, status_code = dowloadAPI.request_trainning_history(cpt_name)

        if status_code not in [200]:
            wai = labelDialog2.waitDialog(txtt='error appeared', num=0)
            wai.delay(1000)
            wai.done_close()

        win_status = labelDialog2.trainning_history_dialog(checkpointDf=checkpointDf)
        notes = win_status.get_note()

        if notes:
            print('notes:', notes)
            dir_path = os.path.dirname(os.path.dirname( checkpointDf['fullPath'][0])) if checkpointDf.shape[0]>0 else None
            dowloadAPI.request_save_notes(notes, dir_path=dir_path)
        else:
            print('notes is None:', notes)

    @staticmethod
    def current_trainning_log():
        checkpointDf, training_log, status_code = dowloadAPI.request_current_trainning_log()

        if status_code not in [200]:
            wai = labelDialog2.waitDialog(txtt='error appeared', num=0)
            wai.delay(1000)
            wai.done_close()
            return

        win_status = labelDialog2.trainning_log_dialog(checkpointDf=checkpointDf, training_log=training_log)

        isStop = win_status.chose_stop()

        if isStop:
            print('chose stop training:', isStop)
            dowloadAPI.request_stop_training()
        else:
            print('chose continue training:', isStop)


    def choose_checkpoint(self, _value=False):
        try:
            listcheck, status_code = dowloadAPI.request_all_checkpoints()
            chooseWind = labelDialog2.choose_checkpoint(parent=self, listcheck=listcheck)
            checkpoint_chose = chooseWind.get_chose()
            if checkpoint_chose is not None:
                print('synDirs_chose:', checkpoint_chose)
                verify = dowloadAPI.sent_checkpoint_chose(checkpoint_chose)
            else:
                print('synDirs_chose is None')
        except:
            wai = labelDialog2.waitDialog(txtt='can not connect server', num=0)
            wai.delay(1000)
            wai.done_close()

    def download_checkpoint(self, _value=False):
        # try:
        listcheck, status_code = dowloadAPI.request_all_checkpoints()
        print('listcheck', listcheck)
        chooseWind = download_checkpoint(parent=self, listcheck=listcheck)
        checkpoint_chose = chooseWind.get_chose()
        print('synDirs_chose:', checkpoint_chose)

        if checkpoint_chose is not None:
            print('synDirs_chose:', checkpoint_chose)
            wai = labelDialog2.waitDialog(txtt='wait awhile, until download done', num=0)

            zip_checkpoint, filename = dowloadAPI.down_checkpoint_chose(checkpoint_chose)
            wai.done_close()
            # save_path = self.saveCheckpointDialog(zip_file_name = 'zip_checkpoint.zip')
            save_path = self.saveCheckpointDialog(zip_file_name=filename)
            # zip_checkpoint.save(save_path)
            if save_path:
                with open(save_path, 'wb') as f:
                    for chunk in zip_checkpoint.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            # shutil.unpack_archive(out_dirr + '/test.zip', extract_dir=save_path)
        else:
            print('synDirs_chose is None')
        # except:
        #     wai = waitDialog('can not connect server', num=0)
        #     wai.delay(1000)
        #     wai.done_close()

    def saveCheckpointDialog(self, zip_file_name):
        caption = '%s - Choose path' % __appname__
        filters = 'File (*%s)' % '/'
        openDialogPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), zip_file_name)
        dlg = QFileDialog(self, caption, openDialogPath, filters)
        dlg.setDefaultSuffix(filters[1:])
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        # filenameWithoutExtension = os.path.splitext(self.filePath)[0]
        # dlg.selectFile(filenameWithoutExtension)
        dlg.setOption(QFileDialog.DontUseNativeDialog, False)
        if dlg.exec_():
            fullFilePath = ustr(dlg.selectedFiles()[0])
            return fullFilePath
        return ''

    def saveFile(self, _value=False):
        if self.defaultSaveDir is not None and len(ustr(self.defaultSaveDir)):
            if self.filePath:
                imgFileName = os.path.basename(self.filePath)
                savedFileName = os.path.splitext(imgFileName)[0]
                savedPath = os.path.join(ustr(self.defaultSaveDir), savedFileName)
                self._saveFile(savedPath)
        else:
            print('1611: saveFileDialog')
            savedPath = self.saveFileDialog(removeExt=True)
            self.defaultSaveDir = os.path.dirname(savedPath)
            self._saveFile(savedPath)

    def saveFileAs(self, _value=False):
        assert not self.image.isNull(), "cannot save empty image"
        savedPath = self.saveFileDialog(removeExt=True)
        self.defaultSaveDir = os.path.dirname(savedPath)
        self._saveFile(savedPath)

    def saveFileDialog(self, removeExt=True):
        caption = '%s - Choose File' % __appname__
        filters = 'File (*%s)' % TXT_SUFFIX
        openDialogPath = self.currentPath()
        dlg = QFileDialog(self, caption, openDialogPath, filters)
        dlg.setDefaultSuffix('txt')
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        filenameWithoutExtension = os.path.splitext(self.filePath)[0] + '.txt'
        dlg.selectFile(filenameWithoutExtension)
        dlg.setOption(QFileDialog.DontUseNativeDialog, False)
        if dlg.exec_():
            fullFilePath = ustr(dlg.selectedFiles()[0])
            if removeExt:
                return os.path.splitext(fullFilePath)[0]  # Return file path without the extension.
            else:
                return fullFilePath

        return ''

    def _saveFile(self, annotationFilePath):
        if annotationFilePath:
            self.saveLabels(annotationFilePath)
            self.setClean()
            self.statusBar().showMessage('Saved to  %s' % annotationFilePath)
            self.statusBar().show()

    def closeFile(self, _value=False):
        if not self.mayContinue():
            return
        self.resetState()
        self.setClean()
        self.toggleActions(False)
        self.canvas.setEnabled(False)
        self.actions.saveAs.setEnabled(False)

    def resetAll(self):
        self.settings.reset()
        self.close()
        proc = QProcess()
        proc.startDetached(os.path.abspath(__file__))

    def mayContinue(self):
        return not (self.dirty and not self.discardChangesDialog())

    def discardChangesDialog(self):
        yes, no = QMessageBox.Yes, QMessageBox.No
        msg = u'You have unsaved changes, proceed anyway?'
        return yes == QMessageBox.warning(self, u'Attention', msg, yes | no)

    def errorMessage(self, title, message):
        return QMessageBox.critical(self, title,
                                    '<p><b>%s</b></p>%s' % (title, message))

    def currentPath(self):
        return os.path.dirname(self.filePath) if self.filePath else '.'

    def chooseColor1(self):
        color = self.colorDialog.getColor(self.lineColor, u'Choose line color',
                                          default=DEFAULT_LINE_COLOR)
        if color:
            self.lineColor = color
            Shape.line_color = color
            self.canvas.setDrawingColor(color)
            self.canvas.update()
            self.setDirty()

    def deleteSelectedShape(self):
        self.remLabel(self.canvas.deleteSelected())
        self.setDirty()
        if self.noShapes():
            for action in self.actions.onShapesPresent:
                action.setEnabled(False)

    def chshapeLineColor(self):
        color = self.colorDialog.getColor(self.lineColor, u'Choose line color',
                                          default=DEFAULT_LINE_COLOR)
        if color:
            self.canvas.selectedShape.line_color = color
            self.canvas.update()
            self.setDirty()

    def chshapeFillColor(self):
        color = self.colorDialog.getColor(self.fillColor, u'Choose fill color',
                                          default=DEFAULT_FILL_COLOR)
        if color:
            self.canvas.selectedShape.fill_color = color
            self.canvas.update()
            self.setDirty()

    def copyShape(self):
        self.canvas.endMove(copy=True)
        self.addLabel(self.canvas.selectedShape)
        self.setDirty()

    def moveShape(self):
        self.canvas.endMove(copy=False)
        self.setDirty()

    def loadPredefinedClasses(self, predefClassesFile):
        if os.path.exists(predefClassesFile) is True:
            with codecs.open(predefClassesFile, 'r', 'utf8') as f:
                for line in f:
                    line = line.strip()
                    if self.labelHist is None:
                        self.labelHist = [line]
                    else:
                        self.labelHist.append(line)
        pwd = os.getcwd()
        brandfile = os.path.join(pwd, 'data', 'brand.txt')
        print('brandfile', brandfile)
        if os.path.exists(brandfile) is True:
            with codecs.open(brandfile, 'r', 'utf8') as f:
                for line in f:
                    line = line.strip()
                    if self.brandlist is None:
                        self.brandlist = [line]
                    else:
                        self.brandlist.append(line)

        pwd = os.getcwd()
        noteFile = os.path.join(pwd, 'data', 'note.txt')
        print('noteFile', noteFile)
        if os.path.exists(noteFile) is True:
            with codecs.open(noteFile, 'r', 'utf8') as f:
                for line in f:
                    line = line.strip()
                    if self.notelist is None:
                        self.notelist = [line]
                    else:
                        self.notelist.append(line)

    def loadYOLOTXTByFilename(self, txtPath):
        if self.filePath is None:
            return
        if os.path.isfile(txtPath) is False:
            return
        tYoloParseReader = YoloReader(txtPath, self.image)
        shapes = tYoloParseReader.getShapes()
        self.loadLabels(shapes)
        self.canvas.verified = tYoloParseReader.verified

    def check_overlap(self, points1, points2):
        merge_v = merge_h = False
        (xi1, yi1), (xi2, yi2), (xi3, yi3), (xi4, yi4) = points1

        (xj1, yj1), (xj2, yj2), (xj3, yj3), (xj4, yj4) = points2
        xj1, yj1, xj2, yj2, xj3, yj3, xj4, yj4 = int(xj1), int(yj1), int(xj2), int(yj2), int(xj3), int(yj3), int(xj4), int(yj4)

        h_max = max(yi4 - yi1, yj4 - yj1)
        h_min = min(yi4 - yi1, yj4 - yj1)
        overlap_h = min(yi4, yj4) - max(yi1, yj1)
        if overlap_h >= h_min * 0.8 and overlap_h >= h_max * 0.5:
            merge_h = True

        v_max = max(xi3 - xi1, xj3 - xj1)
        v_min = min(xi3 - xi1, xj3 - xj1)
        overlap_v = min(xi3, xj3) - max(xi1, xj1)
        if overlap_v >= v_min * 0.8 and overlap_v >= v_max * 0.5:
            merge_v = True
        return merge_v and merge_h

    def onlyPosition(self, points):
        ret_subs = []
        ret_lb = ''
        points = self.convert_points_list(points)
        for k in self.dataSublabel:
            # ps = self.convert_points_list(self.dataSublabel[k][1])

            ps = self.dataSublabel[k][1]
            if self.check_overlap(points, ps):
                ret_subs = self.dataSublabel[k][0]
                ret_lb = k
                return ret_subs, ret_lb
        return ret_subs, ret_lb

    def preDictSubLabel(self, label, points):
        if label in self.dataSublabel:
            ret_subs = self.dataSublabel[label][0]
        else:
            ret_subs, ret_lb = self.onlyPosition(points)
            rectify_label = self.minEditdistanceLabel(label, listword=self.dataSublabel.keys())
            if ret_lb != rectify_label:
                ret_subs = []

        return ret_subs

    def hint_shapes_from_shapesRefs(self, shapes):
        s = []
        for sshape in shapes:
            label = self.minEditdistanceLabel(sshape['label'])
            # line_color, fill_color, difficult = False, False, False
            line_color, fill_color = False, False
            points = []
            for x, y in sshape['points']:
                # Ensure the labels are within the bounds of the image. If not, fix them.
                x, y, snapped = self.canvas.snapPointToCanvas(x, y)
                if snapped:
                    self.setDirty()
                points.append(QPointF(x, y))

            subLabel = self.preDictSubLabel(label, points)

            shape = Shape(label=label, subLabels=subLabel)
            shape.points = points
            # shape.difficult = difficult
            shape.close()

            s.append(shape)

            if line_color:
                shape.line_color = QColor(*line_color)
            else:
                shape.line_color = generateColorByText(label)

            if fill_color:
                shape.fill_color = QColor(*fill_color)
            else:
                shape.fill_color = generateColorByText(label)

            self.addLabel(shape)

        self.canvas.loadShapes(s)
        self.setDirty()


    def beginFromRef(self, baseName):
        # print('beginFromRef')
        if os.path.isfile(os.path.join(self.refDir,'{}.txt'.format(baseName))):
            print()
            if self.shapesRefs:
                self.hint_shapes_from_shapesRefs(self.shapesRefs)
                self.canvas.verified = False
        return

    def togglePaintLabelsOption(self):
        for shape in self.canvas.shapes:
            shape.paintLabel = self.displayLabelOption.isChecked()

    def toogleDrawSquare(self):
        print(self.drawSquaresOption.isChecked())
        self.canvas.setDrawingShapeToSquare(self.drawSquaresOption.isChecked())

    def load_dataSublabels(self):
        import json
        import os
        refDict = {}
        fn = os.path.join(os.getcwd(), 'data/dataSublabel.json')
        if os.path.isfile(fn):
            with open(fn, 'r') as jsonr:
                refDict = json.load(jsonr)

        return refDict

    def save_dataSublabels(self):
        import json
        import os

        fn = os.path.join(os.path.abspath(os.getcwd()), 'data/dataSublabel.json')
        with open(fn, 'w') as jsonw:
            json.dump(self.dataSublabel, jsonw, ensure_ascii=False, indent=4)


def inverted(color):
    return QColor(*[255 - v for v in color.getRgb()])


def read(filename, default=None):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default


def get_main_app(argv=[]):
    """
    Standard boilerplate Qt application code.
    Do everything but app.exec_() -- so that we can test the application in one thread
    """
    app = QApplication(argv)
    styles.dark(app)
    app.setApplicationName(__appname__)
    app.setWindowIcon(newIcon("app"))
    # Tzutalin 201705+: Accept extra agruments to change predefined class file
    # Usage : labelImg.py image predefClassFile saveDir
    win = MainWindow(argv[1] if len(argv) >= 2 else None,
                     argv[2] if len(argv) >= 3 else os.path.join(
                         os.path.dirname(sys.argv[0]),
                         'data', 'predefined_classes.txt'),
                     argv[3] if len(argv) >= 4 else None)
    # g = windows.ModernWindow(win)
    win.show()
    return app, win


def main():
    '''construct main app and run it'''
    app, _win = get_main_app(sys.argv)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
