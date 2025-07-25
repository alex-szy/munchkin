from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from api import watch


class WatchPage(QWidget):
    """Add & show folders that the backend will watch."""

    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(18)

        title = QLabel("Add Watch Folders")
        root.addWidget(title)

        # ---- input row ---------------------------------------------------
        row = QHBoxLayout()
        self.path_edit = QLineEdit(placeholderText="Enter folder path …")
        self.path_edit.setMinimumWidth(350)
        row.addWidget(self.path_edit, 1)

        buttons = [
            (QPushButton("Add"), self.handle_add),
            (QPushButton("Browse"), self.handle_browse),
        ]

        for button, handler in buttons:
            button.clicked.connect(handler)
            row.addWidget(button)

        root.addLayout(row)

        # ---- table of paths ---------------------------------------------
        self.table = QTableWidget(0, 1)
        self.table.setHorizontalHeaderLabels(["Path"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.handle_remove)
        root.addWidget(self.table, 1)

        self.update()

    def update(self, *args, **kwargs):
        """Reload previously watched paths and display them."""
        super().update(*args, **kwargs)
        self.table.setRowCount(0)
        for path in watch.list():
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(path))

    def handle_browse(self):
        """Invoke file chooser and add the path"""
        path = QFileDialog.getExistingDirectory(self, "Choose a folder to watch")
        if path:
            self._add_path(path)

    def handle_add(self):
        """Handle adding a path typed in from the text input"""
        raw = self.path_edit.text().strip()
        if not raw:
            return
        cleaned = str(Path(raw).expanduser().resolve())
        if self._add_path(cleaned):
            self.path_edit.clear()

    def _add_path(self, path):
        """Calls the API to add a watch path and displays an error box if failed"""
        ok, err = watch.add(path)
        if err:
            QMessageBox.critical(
                self, "Add watch path failed", f"Adding watch path failed: {err}"
            )
        else:
            self.update()
        return ok

    def handle_remove(self, item: QTableWidgetItem):
        """Prompts the user for removal of an entry"""
        path_cell = self.table.item(item.row(), 0)
        if not path_cell:
            return
        path = path_cell.text()
        button = QMessageBox.question(
            self,
            "Remove watch folder",
            f"Stop watching the folder '{path}'?",
        )
        if button == QMessageBox.StandardButton.Yes:
            watch.remove(path_cell.text())
            self.update()
