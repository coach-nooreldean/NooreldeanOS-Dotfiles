#!/usr/bin/env python3
"""
Entry point for NooreldeanOS Bluetooth Manager Application.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QPalette, QColor
from ui import BluetoothManagerApp, load_pywal_colors

def apply_global_palette(app, colors):
    palette = QPalette()
    bg = QColor(colors['bg'])
    fg = QColor(colors['fg'])
    surface = QColor(colors['surface'])

    palette.setColor(QPalette.ColorRole.Window, bg)
    palette.setColor(QPalette.ColorRole.WindowText, fg)
    palette.setColor(QPalette.ColorRole.Base, surface)
    palette.setColor(QPalette.ColorRole.AlternateBase, bg)
    palette.setColor(QPalette.ColorRole.ToolTipBase, surface)
    palette.setColor(QPalette.ColorRole.ToolTipText, fg)
    palette.setColor(QPalette.ColorRole.Text, fg)
    palette.setColor(QPalette.ColorRole.Button, surface)
    palette.setColor(QPalette.ColorRole.ButtonText, fg)
    palette.setColor(QPalette.ColorRole.BrightText, QColor(colors['danger']))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['primary']))
    palette.setColor(QPalette.ColorRole.HighlightedText, bg)

    app.setPalette(palette)

def main():
    # Force Wayland or auto-detect
    if "WAYLAND_DISPLAY" in os.environ and "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"

    app = QApplication(sys.argv)
    app.setApplicationName("NooreldeanOS Bluetooth")
    app.setApplicationDisplayName("NooreldeanOS Bluetooth")

    font = QFont("Cairo", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)

    colors = load_pywal_colors()
    apply_global_palette(app, colors)

    window = BluetoothManagerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
