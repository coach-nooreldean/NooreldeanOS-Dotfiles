import sys
import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QPushButton, 
                             QLineEdit, QMessageBox, QProgressBar, QInputDialog, QApplication)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from disk_manager import get_available_drives, format_drive

def load_pywal_colors():
    wal_cache = os.path.expanduser("~/.cache/wal/colors.json")
    if os.path.exists(wal_cache):
        try:
            with open(wal_cache, 'r') as f:
                data = json.load(f)
            return {
                'bg': data['special']['background'],
                'fg': data['special']['foreground'],
                'primary': data['colors']['color4'],
                'danger': data['colors']['color1'],
                'border': data['colors']['color8'],
                'hover': data['colors']['color2'],
                'surface': data['colors']['color0']
            }
        except Exception:
            pass
    # Fallback dark theme
    return {
        'bg': '#1e1e2e',
        'fg': '#cdd6f4',
        'primary': '#89b4fa',
        'danger': '#f38ba8',
        'border': '#45475a',
        'hover': '#a6e3a1',
        'surface': '#313244'
    }

def apply_dark_palette(app, colors):
    if not app:
        return
    palette = QPalette()
    bg = QColor(colors['bg'])
    fg = QColor(colors['fg'])
    surface = QColor(colors['surface'])
    
    palette.setColor(QPalette.ColorRole.Window, bg)
    palette.setColor(QPalette.ColorRole.WindowText, fg)
    palette.setColor(QPalette.ColorRole.Base, surface)
    palette.setColor(QPalette.ColorRole.AlternateBase, bg)
    palette.setColor(QPalette.ColorRole.ToolTipBase, fg)
    palette.setColor(QPalette.ColorRole.ToolTipText, bg)
    palette.setColor(QPalette.ColorRole.Text, fg)
    palette.setColor(QPalette.ColorRole.Button, surface)
    palette.setColor(QPalette.ColorRole.ButtonText, fg)
    palette.setColor(QPalette.ColorRole.BrightText, QColor(colors['danger']))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['primary']))
    palette.setColor(QPalette.ColorRole.HighlightedText, bg)
    
    app.setPalette(palette)

class RoundedComboBox(QComboBox):
    def showPopup(self):
        super().showPopup()
        popup = self.view().window()
        if popup:
            popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            popup.setObjectName("ComboPopup")
            popup.setStyleSheet("#ComboPopup { background: transparent; border: none; }")

def get_stylesheet(colors):
    return f"""
    QWidget {{
        background-color: {colors['bg']};
        color: {colors['fg']};
        font-family: 'Inter', 'JetBrainsMono Nerd Font', sans-serif;
        font-size: 14px;
        font-weight: 600;
    }}
    QLabel {{
        font-size: 14px;
    }}
    QComboBox, QLineEdit {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 8px 12px;
        color: {colors['fg']};
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox QAbstractItemView {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        selection-background-color: {colors['primary']};
        selection-color: {colors['bg']};
        outline: none;
        padding: 4px;
    }}
    QPushButton {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 8px 16px;
        color: {colors['fg']};
    }}
    QPushButton:hover {{
        background-color: {colors['primary']};
        color: {colors['bg']};
        border: 1px solid {colors['primary']};
    }}
    QPushButton:disabled {{
        background-color: {colors['bg']};
        color: {colors['border']};
    }}
    QPushButton#FormatBtn {{
        background-color: {colors['danger']};
        color: {colors['bg']};
        font-weight: bold;
        font-size: 15px;
        border: none;
        border-radius: 12px;
        padding: 12px;
    }}
    QPushButton#FormatBtn:hover {{
        background-color: {colors['fg']};
        color: {colors['danger']};
    }}
    QProgressBar {{
        border: 1px solid {colors['border']};
        border-radius: 12px;
        text-align: center;
        background-color: {colors['surface']};
        height: 12px;
    }}
    QProgressBar::chunk {{
        background-color: {colors['primary']};
        border-radius: 12px;
    }}
    QMessageBox {{
        background-color: {colors['bg']};
    }}
    QMessageBox QLabel {{
        color: {colors['fg']};
    }}
    QMessageBox QPushButton {{
        background-color: {colors['surface']};
        min-width: 80px;
    }}
    """

class FormatThread(QThread):
    finished = pyqtSignal(bool, str)
    
    def __init__(self, device_path, fs_type, label, password):
        super().__init__()
        self.device_path = device_path
        self.fs_type = fs_type
        self.label = label
        self.password = password
        
    def run(self):
        try:
            format_drive(self.device_path, self.fs_type, self.label, self.password)
            self.finished.emit(True, "Drive formatted successfully!")
        except Exception as e:
            self.finished.emit(False, str(e))

class FormatterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drive Formatter")
        self.setMinimumWidth(550)
        self.setMinimumHeight(350)
        
        self.colors = load_pywal_colors()
        self.setStyleSheet(get_stylesheet(self.colors))
        
        app = QApplication.instance()
        if app:
            apply_dark_palette(app, self.colors)
        
        self.drives = []
        self.setup_ui()
        self.refresh_drives()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        title = QLabel("Drive Formatter")
        title.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {self.colors['primary']};")
        layout.addWidget(title)
        
        # Drive Selection
        drive_layout = QHBoxLayout()
        drive_label = QLabel("Select Disk:")
        self.disk_combo = RoundedComboBox()
        self.disk_combo.currentIndexChanged.connect(self.on_disk_changed)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_drives)
        
        drive_layout.addWidget(drive_label)
        drive_layout.addWidget(self.disk_combo, stretch=1)
        drive_layout.addWidget(self.refresh_btn)
        
        # Partition Selection
        part_layout = QHBoxLayout()
        part_label = QLabel("Partition:")
        self.part_combo = RoundedComboBox()
        
        part_layout.addWidget(part_label)
        part_layout.addWidget(self.part_combo, stretch=1)
        
        # File System Selection
        fs_layout = QHBoxLayout()
        fs_label = QLabel("File System:")
        self.fs_combo = RoundedComboBox()
        self.fs_options = {
            "ext4 (Linux - خفيف وسريع)": "ext4",
            "FAT32 (متوافق مع جميع الأنظمة)": "FAT32",
            "NTFS (ويندوز)": "NTFS",
            "exFAT (للأجهزة الحديثة والملفات الكبيرة)": "exFAT"
        }
        self.fs_combo.addItems(self.fs_options.keys())
        
        fs_layout.addWidget(fs_label)
        fs_layout.addWidget(self.fs_combo, stretch=1)
        
        # Label Input
        label_layout = QHBoxLayout()
        label_label = QLabel("Volume Label:")
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("Optional name for the drive")
        
        label_layout.addWidget(label_label)
        label_layout.addWidget(self.label_input, stretch=1)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminate mode
        self.progress.hide()
        
        # Format Button
        self.format_btn = QPushButton("Format Drive")
        self.format_btn.setObjectName("FormatBtn")
        self.format_btn.clicked.connect(self.confirm_and_format)
        
        # Add to main layout
        layout.addLayout(drive_layout)
        layout.addLayout(part_layout)
        layout.addLayout(fs_layout)
        layout.addLayout(label_layout)
        layout.addStretch()
        layout.addWidget(self.progress)
        layout.addWidget(self.format_btn)
        
        self.setLayout(layout)
        
    def refresh_drives(self):
        self.disk_combo.blockSignals(True)
        self.disk_combo.clear()
        self.part_combo.clear()
        
        self.drives = get_available_drives()
        
        if not self.drives:
            self.disk_combo.addItem("No available drives found")
            self.format_btn.setEnabled(False)
            self.disk_combo.blockSignals(False)
            return
            
        self.format_btn.setEnabled(True)
        for i, disk in enumerate(self.drives):
            self.disk_combo.addItem(disk['display_name'], userData=i)
            
        self.disk_combo.blockSignals(False)
        self.on_disk_changed(0)
        
    def on_disk_changed(self, index):
        self.part_combo.clear()
        if index < 0 or index >= len(self.drives):
            return
            
        disk = self.drives[index]
        self.part_combo.addItem("Entire Disk (Wipe all partitions)", userData=disk['path'])
        
        for part in disk['partitions']:
            self.part_combo.addItem(part['display_name'], userData=part['path'])
            
    def confirm_and_format(self):
        drive_path = self.part_combo.currentData()
        if not drive_path:
            return
            
        display_text = self.fs_combo.currentText()
        fs_type = self.fs_options[display_text]
        label = self.label_input.text()
        
        # Confirmation Dialog
        reply = QMessageBox.warning(
            self, 'Confirm Format',
            f"Are you absolutely sure you want to format {drive_path} as {fs_type}?\n\n"
            "ALL DATA ON THIS DRIVE WILL BE PERMANENTLY LOST!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            password, ok = QInputDialog.getText(
                self, "Authentication Required", 
                "Enter your user password to format the drive:", 
                QLineEdit.EchoMode.Password
            )
            if ok and password:
                self.start_formatting(drive_path, fs_type, label, password)
            
    def start_formatting(self, device_path, fs_type, label, password):
        self.format_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.disk_combo.setEnabled(False)
        self.part_combo.setEnabled(False)
        self.fs_combo.setEnabled(False)
        self.label_input.setEnabled(False)
        
        self.progress.show()
        
        self.thread = FormatThread(device_path, fs_type, label, password)
        self.thread.finished.connect(self.on_format_finished)
        self.thread.start()
        
    def on_format_finished(self, success, message):
        self.progress.hide()
        
        self.format_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.disk_combo.setEnabled(True)
        self.part_combo.setEnabled(True)
        self.fs_combo.setEnabled(True)
        self.label_input.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.label_input.clear()
        else:
            QMessageBox.critical(self, "Error", f"Failed to format drive:\n{message}")
            
        self.refresh_drives()
