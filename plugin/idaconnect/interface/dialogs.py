import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QGridLayout,
    QWidget, QTableWidget, QTableWidgetItem,
    QGroupBox, QLabel, QPushButton)

from ..shared.models import Database


logger = logging.getLogger('IDAConnect.Interface')

# -----------------------------------------------------------------------------
# Dialogs
# -----------------------------------------------------------------------------


class OpenDialog(QDialog):

    def __init__(self, plugin, dbs, revs):
        super(OpenDialog, self).__init__()
        self._plugin = plugin
        self._dbs = dbs
        self._revs = revs

        # General setup
        logger.debug("Showing open database dialog")
        self.setWindowTitle("Open from Remote Server")
        iconPath = self._plugin.getResource('open.png')
        self.setWindowIcon(QIcon(iconPath))
        self.resize(900, 450)

        # Setup layout and widgets
        layout = QHBoxLayout(self)
        self._dbsTable = QTableWidget(len(dbs), 1, self)
        self._dbsTable.setHorizontalHeaderLabels(('Remote Databases',))
        for i, db in enumerate(dbs):
            item = QTableWidgetItem("%s (%s)" % (str(db.getFile()),
                                                 str(db.getHash())))
            item.setData(Qt.UserRole, db)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self._dbsTable.setItem(i, 0, item)
        self._dbsTable.horizontalHeader().setSectionsClickable(False)
        self._dbsTable.horizontalHeader().setStretchLastSection(True)
        self._dbsTable.verticalHeader().setVisible(False)
        self._dbsTable.setSelectionBehavior(QTableWidget.SelectRows)
        self._dbsTable.setSelectionMode(QTableWidget.SingleSelection)
        self._dbsTable.itemClicked.connect(self._dbClicked)
        minSZ = self._dbsTable.minimumSize()
        self._dbsTable.setMinimumSize(300, minSZ.height())
        maxSZ = self._dbsTable.maximumSize()
        self._dbsTable.setMaximumSize(300, maxSZ.height())
        layout.addWidget(self._dbsTable)

        rightSide = QWidget(self)
        rightLayout = QVBoxLayout(rightSide)
        infoGroup = QGroupBox("Information", rightSide)
        infoLayout = QGridLayout(infoGroup)
        self._fileLabel = QLabel('<b>File:</b>')
        infoLayout.addWidget(self._fileLabel, 0, 0)
        self._hashLabel = QLabel('<b>Hash:</b>')
        infoLayout.addWidget(self._hashLabel, 1, 0)
        infoLayout.setColumnStretch(0, 1)
        self._typeLabel = QLabel('<b>Type:</b>')
        infoLayout.addWidget(self._typeLabel, 0, 1)
        self._dateLabel = QLabel('<b>Date:</b>')
        infoLayout.addWidget(self._dateLabel, 1, 1)
        infoLayout.setColumnStretch(1, 1)
        rightLayout.addWidget(infoGroup)

        revsGroup = QGroupBox("Revisions", rightSide)
        revsLayout = QGridLayout(revsGroup)
        self._revsTable = QTableWidget(0, 2, revsGroup)
        self._revsTable.setHorizontalHeaderLabels(('Identifier', 'Date'))
        horizontalHeader = self._revsTable.horizontalHeader()
        horizontalHeader.setSectionsClickable(False)
        horizontalHeader.setSectionResizeMode(0, horizontalHeader.Stretch)
        self._revsTable.verticalHeader().setVisible(False)
        self._revsTable.setSelectionBehavior(QTableWidget.SelectRows)
        self._revsTable.setSelectionMode(QTableWidget.SingleSelection)
        self._revsTable.itemClicked.connect(self._revClicked)
        revsLayout.addWidget(self._revsTable, 0, 0)
        rightLayout.addWidget(revsGroup)

        buttonsWidget = QWidget(rightSide)
        buttonsLayout = QHBoxLayout(buttonsWidget)
        buttonsLayout.addStretch()
        self._openButton = QPushButton("Open")
        self._openButton.setEnabled(False)
        self._openButton.clicked.connect(self.accept)
        buttonsLayout.addWidget(self._openButton)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(cancelButton)
        rightLayout.addWidget(buttonsWidget)
        layout.addWidget(rightSide)

    # -------------------------------------------------------------------------
    # Internal Events
    # -------------------------------------------------------------------------

    def _dbClicked(self, item):
        # When a database is clicked, update display
        db = item.data(Qt.UserRole)
        self._fileLabel.setText('<b>File:</b> %s' % str(db.getFile()))
        self._hashLabel.setText('<b>Hash:</b> %s' % str(db.getHash()))
        self._typeLabel.setText('<b>Type:</b> %s' % str(db.getType()))
        self._dateLabel.setText('<b>Date:</b> %s' % str(db.getDate()))

        # Including its list of revisions
        revs = [rev for rev in self._revs if rev.getHash() == db.getHash()]
        self._revsTable.setRowCount(len(revs))
        for i, rev in enumerate(revs):
            item = QTableWidgetItem(str(rev.getUUID()))
            item.setData(Qt.UserRole, rev)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self._revsTable.setItem(i, 0, item)
            item = QTableWidgetItem(str(rev.getDate()))
            item.setData(Qt.UserRole, rev)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self._revsTable.setItem(i, 1, item)

    def _revClicked(self, item):
        # When a revision is clicked, we're all set
        self._openButton.setEnabled(True)

    # -------------------------------------------------------------------------
    # Getters/Setters
    # -------------------------------------------------------------------------

    def getResult(self):
        # Used to get the database and revision
        db = self._dbsTable.currentItem().data(Qt.UserRole)
        return db, self._revsTable.currentItem().data(Qt.UserRole)


class SaveDialog(QDialog):

    def __init__(self, plugin, dbs, revs):
        super(SaveDialog, self).__init__()
        self._plugin = plugin
        self._dbs = dbs
        self._revs = revs

        # General setup
        logger.debug("Showing save database dialog")
        self.setWindowTitle("Save to Remote Server")
        iconPath = self._plugin.getResource('save.png')
        self.setWindowIcon(QIcon(iconPath))
        self.resize(900, 450)

        # Setup layout and widgets
        layout = QHBoxLayout(self)
        self._dbsTable = QTableWidget(len(dbs) + 1, 1, self)
        self._dbsTable.setHorizontalHeaderLabels(('Remote Databases',))
        for i, db in enumerate(dbs):
            item = QTableWidgetItem("%s (%s)" % (str(db.getFile()),
                                                 str(db.getHash())))
            item.setData(Qt.UserRole, db)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self._dbsTable.setItem(i, 0, item)
        newItem = QTableWidgetItem("<new database>")
        newItem.setData(Qt.UserRole, None)
        newItem.setFlags(newItem.flags() & ~Qt.ItemIsEditable)
        self._dbsTable.setItem(len(dbs), 0, newItem)
        self._dbsTable.horizontalHeader().setSectionsClickable(False)
        self._dbsTable.horizontalHeader().setStretchLastSection(True)
        self._dbsTable.verticalHeader().setVisible(False)
        self._dbsTable.setSelectionBehavior(QTableWidget.SelectRows)
        self._dbsTable.setSelectionMode(QTableWidget.SingleSelection)
        self._dbsTable.itemClicked.connect(self._dbClicked)
        minSZ = self._dbsTable.minimumSize()
        self._dbsTable.setMinimumSize(300, minSZ.height())
        maxSZ = self._dbsTable.maximumSize()
        self._dbsTable.setMaximumSize(300, maxSZ.height())
        layout.addWidget(self._dbsTable)

        rightSide = QWidget(self)
        rightLayout = QVBoxLayout(rightSide)
        infoGroup = QGroupBox("Information", rightSide)
        infoLayout = QGridLayout(infoGroup)
        self._fileLabel = QLabel('<b>File:</b>')
        infoLayout.addWidget(self._fileLabel, 0, 0)
        self._hashLabel = QLabel('<b>Hash:</b>')
        infoLayout.addWidget(self._hashLabel, 1, 0)
        infoLayout.setColumnStretch(0, 1)
        self._typeLabel = QLabel('<b>Type:</b>')
        infoLayout.addWidget(self._typeLabel, 0, 1)
        self._dateLabel = QLabel('<b>Date:</b>')
        infoLayout.addWidget(self._dateLabel, 1, 1)
        infoLayout.setColumnStretch(1, 1)
        rightLayout.addWidget(infoGroup)

        revsGroup = QGroupBox("Revisions", rightSide)
        revsLayout = QGridLayout(revsGroup)
        self._revsTable = QTableWidget(0, 2, revsGroup)
        self._revsTable.setHorizontalHeaderLabels(('Identifier', 'Date'))
        horizontalHeader = self._revsTable.horizontalHeader()
        horizontalHeader.setSectionsClickable(False)
        horizontalHeader.setSectionResizeMode(0, horizontalHeader.Stretch)
        self._revsTable.verticalHeader().setVisible(False)
        self._revsTable.setSelectionBehavior(QTableWidget.SelectRows)
        self._revsTable.setSelectionMode(QTableWidget.SingleSelection)
        revsLayout.addWidget(self._revsTable, 0, 0)
        rightLayout.addWidget(revsGroup)

        buttonsWidget = QWidget(rightSide)
        buttonsLayout = QHBoxLayout(buttonsWidget)
        buttonsLayout.addStretch()
        self._saveButton = QPushButton("Save")
        self._saveButton.setEnabled(False)
        self._saveButton.clicked.connect(self.accept)
        buttonsLayout.addWidget(self._saveButton)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        buttonsLayout.addWidget(cancelButton)
        rightLayout.addWidget(buttonsWidget)
        layout.addWidget(rightSide)

    # -------------------------------------------------------------------------
    # Internal Events
    # -------------------------------------------------------------------------

    def _dbClicked(self, item):
        # When a database is clicked, update display
        db = item.data(Qt.UserRole)
        db = db if db else Database('', '', '', '')
        self._saveButton.setEnabled(True)
        self._fileLabel.setText('<b>File:</b> %s' % str(db.getFile()))
        self._hashLabel.setText('<b>Hash:</b> %s' % str(db.getHash()))
        self._typeLabel.setText('<b>Type:</b> %s' % str(db.getType()))
        self._dateLabel.setText('<b>Date:</b> %s' % str(db.getDate()))

        # Including its list of revisions
        revs = [rev for rev in self._revs if rev.getHash() == db.getHash()]
        self._revsTable.setRowCount(len(revs) + 1)
        for i, rev in enumerate(revs):
            item = QTableWidgetItem(str(rev.getUUID()))
            item.setData(Qt.UserRole, rev)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self._revsTable.setItem(i, 0, item)
            item = QTableWidgetItem(str(rev.getDate()))
            item.setData(Qt.UserRole, rev)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self._revsTable.setItem(i, 1, item)
        newItem = QTableWidgetItem("<new revision>")
        item.setData(Qt.UserRole, None)
        newItem.setFlags(newItem.flags() & ~Qt.ItemIsEditable)
        self._revsTable.setItem(len(revs), 0, newItem)
        newItem = QTableWidgetItem()
        item.setData(Qt.UserRole, None)
        newItem.setFlags(newItem.flags() & ~Qt.ItemIsEditable)
        self._revsTable.setItem(len(revs), 1, newItem)

    def _revClicked(self, item):
        # When a revision is clicked, we're all set
        self._saveButton.setEnabled(True)

    # -------------------------------------------------------------------------
    # Getters/Setters
    # -------------------------------------------------------------------------

    def getResult(self):
        # Used to get the database and revision
        db = self._dbsTable.currentItem().data(Qt.UserRole)
        return db, self._revsTable.currentItem().data(Qt.UserRole)