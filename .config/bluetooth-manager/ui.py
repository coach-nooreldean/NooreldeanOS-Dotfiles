#!/usr/bin/env python3
"""
Main User Interface for NooreldeanOS Bluetooth Manager.
Built with PyQt6, Pywal dynamic theming, and native BlueZ D-Bus integration + Agent Session.
Includes real-time interactive pairing guide and passkey confirmation dialogs.
"""

import sys
import os
import json
import time
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QProgressBar, QFrame,
    QScrollArea, QTabWidget, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QKeySequence, QShortcut
)

from bluetooth_engine import BluetoothEngine

def load_pywal_colors():
    wal_cache = Path.home() / ".cache" / "wal" / "colors.json"
    if wal_cache.exists():
        try:
            with open(wal_cache, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {
                'bg': data['special']['background'],
                'fg': data['special']['foreground'],
                'primary': data['colors'].get('color4', '#38bdf8'),
                'secondary': data['colors'].get('color5', '#818cf8'),
                'hover': data['colors'].get('color2', '#34d399'),
                'danger': data['colors'].get('color1', '#f43f5e'),
                'surface': data['colors'].get('color0', '#181b22'),
                'border': data['colors'].get('color8', '#384152'),
                'card_bg': data['colors'].get('color0', '#14171f')
            }
        except Exception:
            pass

    return {
        'bg': '#10131a',
        'fg': '#e2e8f0',
        'primary': '#38bdf8',
        'secondary': '#818cf8',
        'hover': '#34d399',
        'danger': '#f43f5e',
        'surface': '#181d27',
        'border': '#2d3748',
        'card_bg': '#141822'
    }

class PairingInstructionDialog(QDialog):
    """Dialog showing step-by-step instructions on what to do on the physical device itself."""
    def __init__(self, parent, dev_name, mac, dev_icon="", colors=None):
        super().__init__(parent)
        self.setWindowTitle("خطوات الاقتران بالجهاز")
        self.resize(520, 420)
        self.colors = colors or load_pywal_colors()
        self.dev_name = dev_name or mac
        self.mac = mac
        self.dev_icon = dev_icon

        self.init_ui()

    def init_ui(self):
        c = self.colors
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {c['bg']};
                color: {c['fg']};
                font-family: 'Cairo', 'Inter', sans-serif;
            }}
            QFrame.Card {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border']};
                border-radius: 12px;
                padding: 14px;
            }}
            QPushButton {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                color: {c['fg']};
                padding: 8px 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {c['border']};
                border-color: {c['primary']};
            }}
            QPushButton.PrimaryBtn {{
                background-color: {c['primary']};
                color: {c['bg']};
                border: 1px solid {c['primary']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header with icon
        header_h = QHBoxLayout()
        glyph = BluetoothEngine.get_glyph_for_icon(self.dev_icon, self.dev_name)
        icon_lbl = QLabel(glyph)
        icon_lbl.setFont(QFont("JetBrainsMono Nerd Font", 24))
        icon_lbl.setStyleSheet(f"color: {c['primary']};")
        header_h.addWidget(icon_lbl)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)
        dev_title = QLabel(f"جاري الاقتران بـ: {self.dev_name}")
        dev_title.setFont(QFont("Cairo", 13, QFont.Weight.Bold))
        mac_lbl = QLabel(f"العنوان: {self.mac}")
        mac_lbl.setFont(QFont("Cairo", 8))
        mac_lbl.setStyleSheet(f"color: {c['fg']}; opacity: 0.6;")
        title_vbox.addWidget(dev_title)
        title_vbox.addWidget(mac_lbl)
        header_h.addLayout(title_vbox)
        header_h.addStretch()

        layout.addLayout(header_h)

        # Progress bar
        self.prog = QProgressBar()
        self.prog.setFixedHeight(4)
        self.prog.setTextVisible(False)
        self.prog.setRange(0, 0) # infinite pulse
        layout.addWidget(self.prog)

        # Instruction card
        card = QFrame()
        card.setProperty("class", "Card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)

        card_title = QLabel("📱 ماذا يجب أن تفعل في الجهاز نفسه الآن؟")
        card_title.setFont(QFont("Cairo", 11, QFont.Weight.Bold))
        card_title.setStyleSheet(f"color: {c['hover']};")
        card_layout.addWidget(card_title)

        is_audio = any(k in (self.dev_icon + self.dev_name).lower() for k in ["headset", "headphone", "buds", "airplus", "speaker", "audio"])

        if is_audio:
            t1 = "1. <b>تفعيل وضع الاقتران (Pairing Mode):</b> اضغط مطولاً على زر التشغيل في السماعة (5 إلى 7 ثوانٍ) حتى يومض ضوء الـ LED باللونين الأزرق والأحمر بسرعة."
            t2 = "2. <b>سماعات العلبة (TWS):</b> ضع السماعتين بالعلبة، افتح الغطاء، واضغط مطولاً على الزر الخلفي حتى يبدأ المؤشر بالوميض."
            t3 = "3. <b>رمز التوثيق PIN:</b> إذا طُلب منك رمز PIN، فإن الرمز الافتراضي هو <b>0000</b> أو <b>1234</b>."
        else:
            t1 = "1. <b>افحص شاشة هاتفك الآن:</b> ستظهر لك نافذة منبثقة بعنوان <i>طلب اقتران Bluetooth</i>."
            t2 = "2. <b>الموافقة:</b> اضغط على <b>اقتران (Pair)</b> أو <b>موافق (OK)</b> في شاشة هاتفك فور ظهورها."
            t3 = "3. <b>الرمز التلقائي:</b> إذا ظهر لك كود أمان، تأكد من مطابقته واضغط موافق، أو أدخل <b>0000</b> إذا طُلب PIN."

        for t in [t1, t2, t3]:
            lbl = QLabel(t)
            lbl.setFont(QFont("Cairo", 9))
            lbl.setWordWrap(True)
            lbl.setStyleSheet(f"color: {c['fg']};")
            card_layout.addWidget(lbl)

        self.passkey_box = QFrame()
        self.passkey_box.setStyleSheet(f"background-color: {c['surface']}; border-radius: 8px; padding: 8px;")
        pk_layout = QVBoxLayout(self.passkey_box)
        pk_layout.setSpacing(2)
        self.lbl_pk_title = QLabel("رمز التحقق الظاهر على جهازك (Passkey):")
        self.lbl_pk_title.setFont(QFont("Cairo", 8))
        self.lbl_pk_val = QLabel("------")
        self.lbl_pk_val.setFont(QFont("JetBrainsMono Nerd Font", 16, QFont.Weight.Bold))
        self.lbl_pk_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_pk_val.setStyleSheet(f"color: {c['primary']}; letter-spacing: 4px;")
        pk_layout.addWidget(self.lbl_pk_title)
        pk_layout.addWidget(self.lbl_pk_val)
        card_layout.addWidget(self.passkey_box)
        self.passkey_box.hide()

        layout.addWidget(card)

        # Status text
        self.lbl_status = QLabel("جاري إرسال إشارة الاتصال والمصادقة...")
        self.lbl_status.setFont(QFont("Cairo", 9))
        self.lbl_status.setStyleSheet(f"color: {c['primary']};")
        layout.addWidget(self.lbl_status)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_done = QPushButton("إغلاق")
        self.btn_done.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_done.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_done)

        layout.addLayout(btn_layout)

    def show_passkey(self, code):
        self.passkey_box.show()
        self.lbl_pk_val.setText(code)
        self.lbl_status.setText("📱 تحقق من مطابقة هذا الرمز على شاشة هاتفك واضغط موافق في الهاتف!")

    def set_result(self, ok, msg):
        self.prog.hide()
        if ok:
            self.lbl_status.setText("🎉 تم الاقتران والاتصال بالجهاز بنجاح!")
            self.lbl_status.setStyleSheet(f"color: {self.colors['hover']}; font-weight: bold;")
            self.btn_done.setText("تم بنجاح ✔")
            self.btn_done.setProperty("class", "PrimaryBtn")
            self.btn_done.setStyle(self.btn_done.style())
        else:
            self.lbl_status.setText(f"تعذر الاتصال: {msg}")
            self.lbl_status.setStyleSheet(f"color: {self.colors['danger']};")
            self.btn_done.setText("إغلاق")


class ScanWorker(QThread):
    devices_updated = pyqtSignal(list, list)
    scan_status = pyqtSignal(bool, str)

    def __init__(self):
        super().__init__()
        self._running = True

    def stop(self):
        self._running = False
        BluetoothEngine.stop_discovery()

    def run(self):
        started = BluetoothEngine.start_discovery()
        if not started:
            self.scan_status.emit(False, "تعذر بدء البحث. تأكد من تشغيل البلوتوث.")
            return

        self.scan_status.emit(True, "جاري فحص النطاق والبحث عن الأجهزة المحيطة...")

        while self._running:
            try:
                paired, discovered = BluetoothEngine.get_all_devices()
                self.devices_updated.emit(paired, discovered)
            except Exception:
                pass
            time.sleep(1.0)

        BluetoothEngine.stop_discovery()
        self.scan_status.emit(False, "تم إيقاف البحث")


class ActionWorker(QThread):
    finished = pyqtSignal(str, bool, str, str)

    def __init__(self, action, mac, extra=None):
        super().__init__()
        self.action = action
        self.mac = mac
        self.extra = extra

    def run(self):
        if self.action == "connect":
            ok, msg = BluetoothEngine.connect(self.mac)
            self.finished.emit("connect", ok, self.mac, msg)
        elif self.action == "disconnect":
            ok, msg = BluetoothEngine.disconnect(self.mac)
            self.finished.emit("disconnect", ok, self.mac, msg)
        elif self.action == "pair":
            ok, msg = BluetoothEngine.pair_and_connect(self.mac)
            self.finished.emit("pair", ok, self.mac, msg)
        elif self.action == "remove":
            ok, msg = BluetoothEngine.remove(self.mac)
            self.finished.emit("remove", ok, self.mac, msg)
        elif self.action == "power":
            state = bool(self.extra)
            ok = BluetoothEngine.set_power(state)
            self.finished.emit("power", ok, "", "on" if state else "off")
        elif self.action == "discoverable":
            state = bool(self.extra)
            ok = BluetoothEngine.set_discoverable(state)
            self.finished.emit("discoverable", ok, "", "on" if state else "off")


class BluetoothManagerApp(QMainWindow):
    passkey_received = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NooreldeanOS Bluetooth")
        self.resize(840, 640)
        self.setMinimumSize(740, 540)

        self.colors = load_pywal_colors()
        self.scan_worker = None
        self.action_workers = []
        self.paired_devices = []
        self.discovered_devices = []
        self.is_discoverable = True
        self.current_pairing_dialog = None

        self.passkey_received.connect(self.on_passkey_received)

        self.init_ui()
        self.apply_theme()

        # Connect Agent callbacks to UI signals
        session = BluetoothEngine.get_agent_session()
        session.set_prompt_callback(self.agent_prompt_handler)

        # Keyboard shortcuts
        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("F5"), self, self.refresh_all)
        QShortcut(QKeySequence("Ctrl+R"), self, self.refresh_all)

        # Initial refresh
        QTimer.singleShot(150, self.refresh_all)

        # Periodic background poll (every 3 seconds) for incoming connections & audio routing
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.periodic_poll)
        self.poll_timer.start(3000)

    def agent_prompt_handler(self, event_type, val):
        if event_type == "passkey":
            self.passkey_received.emit("passkey", val)
        elif event_type == "pin":
            self.passkey_received.emit("pin", val)

    def on_passkey_received(self, event_type, val):
        if self.current_pairing_dialog and self.current_pairing_dialog.isVisible():
            self.current_pairing_dialog.show_passkey(val)
        else:
            # Incoming pairing request from phone/tablet
            self.set_status(f"📱 طلب اقتران من جهاز محيط! رمز الأمان: {val} (تمت الموافقة التلقائية)")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        # 1. Header Bar
        header_layout = QHBoxLayout()
        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(3)

        title_label = QLabel("󰂯 إدارة أجهزة البلوتوث (Bluetooth Control)")
        title_label.setFont(QFont("Cairo", 15, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {self.colors['fg']};")

        subtitle_label = QLabel("مركز التحكم بالأجهزة اللاسلكية والاقتران السريع لـ NooreldeanOS")
        subtitle_label.setFont(QFont("Cairo", 9, QFont.Weight.Normal))
        subtitle_label.setStyleSheet(f"color: {self.colors['fg']}; opacity: 0.7;")

        header_text_layout.addWidget(title_label)
        header_text_layout.addWidget(subtitle_label)

        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()

        self.btn_refresh = QPushButton("🔄 تحديث")
        self.btn_refresh.setFont(QFont("Cairo", 9, QFont.Weight.Bold))
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.refresh_all)
        header_layout.addWidget(self.btn_refresh)

        main_layout.addLayout(header_layout)

        # 2. Controller & Power Card
        self.ctrl_card = QFrame()
        self.ctrl_card.setObjectName("ControllerCard")
        ctrl_card_layout = QHBoxLayout(self.ctrl_card)
        ctrl_card_layout.setContentsMargins(18, 14, 18, 14)
        ctrl_card_layout.setSpacing(12)

        # Adapter info
        adapter_vbox = QVBoxLayout()
        adapter_vbox.setSpacing(2)
        self.lbl_adapter_name = QLabel("󰂯 محول البلوتوث: جاري التحقق...")
        self.lbl_adapter_name.setFont(QFont("Cairo", 11, QFont.Weight.Bold))
        self.lbl_adapter_name.setStyleSheet(f"color: {self.colors['fg']};")

        self.lbl_adapter_mac = QLabel("العنوان: --:--:--:--:--:--")
        self.lbl_adapter_mac.setFont(QFont("Cairo", 9))
        self.lbl_adapter_mac.setStyleSheet(f"color: {self.colors['fg']}; opacity: 0.65;")

        adapter_vbox.addWidget(self.lbl_adapter_name)
        adapter_vbox.addWidget(self.lbl_adapter_mac)
        ctrl_card_layout.addLayout(adapter_vbox)

        ctrl_card_layout.addStretch()

        # Action Buttons on controller card
        self.btn_discoverable = QPushButton("󰈈 مرئي للأجهزة (Visible)")
        self.btn_discoverable.setFont(QFont("Cairo", 9, QFont.Weight.Medium))
        self.btn_discoverable.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_discoverable.clicked.connect(self.toggle_discoverable)
        ctrl_card_layout.addWidget(self.btn_discoverable)

        self.btn_power = QPushButton("󰂯 تشغيل البلوتوث")
        self.btn_power.setFont(QFont("Cairo", 9, QFont.Weight.Bold))
        self.btn_power.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_power.clicked.connect(self.toggle_power)
        ctrl_card_layout.addWidget(self.btn_power)

        self.btn_scan = QPushButton("󰍉 بحث عن أجهزة")
        self.btn_scan.setFont(QFont("Cairo", 9, QFont.Weight.Bold))
        self.btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_scan.clicked.connect(self.toggle_scan)
        ctrl_card_layout.addWidget(self.btn_scan)

        main_layout.addWidget(self.ctrl_card)

        # 3. Connection Instructions Banner
        self.guide_box = QFrame()
        self.guide_box.setObjectName("GuideBox")
        guide_layout = QHBoxLayout(self.guide_box)
        guide_layout.setContentsMargins(14, 8, 14, 8)
        guide_layout.setSpacing(10)

        guide_icon = QLabel("💡")
        guide_icon.setFont(QFont("Cairo", 12))
        guide_layout.addWidget(guide_icon)

        guide_txt = QLabel("<b>دليل الاقتران:</b> لتوصيل الهاتف؛ افتح البلوتوث بهاتفك واضغط على اسم الكمبيوتر. لتوصيل سماعة؛ اضغط مطولاً على زر التشغيل حتى يومض الـ LED ثم اضغط 'اقتران وتوصيل'.")
        guide_txt.setFont(QFont("Cairo", 8))
        guide_txt.setWordWrap(True)
        guide_txt.setStyleSheet(f"color: {self.colors['fg']}; opacity: 0.85;")
        guide_layout.addWidget(guide_txt, stretch=1)

        main_layout.addWidget(self.guide_box)

        # 4. Tabs for Paired and Available Devices
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Cairo", 10, QFont.Weight.Bold))

        # --- Tab 1: Paired Devices ---
        self.tab_paired = QWidget()
        tab_paired_layout = QVBoxLayout(self.tab_paired)
        tab_paired_layout.setContentsMargins(8, 12, 8, 8)

        self.scroll_paired = QScrollArea()
        self.scroll_paired.setWidgetResizable(True)
        self.scroll_paired.setFrameShape(QFrame.Shape.NoFrame)

        self.container_paired = QWidget()
        self.layout_paired = QVBoxLayout(self.container_paired)
        self.layout_paired.setContentsMargins(4, 4, 4, 4)
        self.layout_paired.setSpacing(10)
        self.layout_paired.addStretch()

        self.scroll_paired.setWidget(self.container_paired)
        tab_paired_layout.addWidget(self.scroll_paired)

        self.tabs.addTab(self.tab_paired, "الأجهزة المقترنة (Paired)")

        # --- Tab 2: Discovered / Available Devices ---
        self.tab_discovered = QWidget()
        tab_disc_layout = QVBoxLayout(self.tab_discovered)
        tab_disc_layout.setContentsMargins(8, 12, 8, 8)

        self.scroll_disc = QScrollArea()
        self.scroll_disc.setWidgetResizable(True)
        self.scroll_disc.setFrameShape(QFrame.Shape.NoFrame)

        self.container_disc = QWidget()
        self.layout_disc = QVBoxLayout(self.container_disc)
        self.layout_disc.setContentsMargins(4, 4, 4, 4)
        self.layout_disc.setSpacing(10)
        self.layout_disc.addStretch()

        self.scroll_disc.setWidget(self.container_disc)
        tab_disc_layout.addWidget(self.scroll_disc)

        self.tabs.addTab(self.tab_discovered, "الأجهزة المتاحة بالقرب (Available)")

        main_layout.addWidget(self.tabs, stretch=1)

        # 5. Bottom Status & Notification Bar
        self.bottom_bar = QFrame()
        self.bottom_bar.setObjectName("BottomBar")
        bottom_layout = QHBoxLayout(self.bottom_bar)
        bottom_layout.setContentsMargins(14, 8, 14, 8)

        self.lbl_status = QLabel("جاهز والاقتران متاح")
        self.lbl_status.setFont(QFont("Cairo", 9, QFont.Weight.Normal))
        self.lbl_status.setStyleSheet(f"color: {self.colors['fg']}; opacity: 0.85;")

        self.status_progress = QProgressBar()
        self.status_progress.setFixedHeight(4)
        self.status_progress.setTextVisible(False)
        self.status_progress.setRange(0, 0)
        self.status_progress.hide()

        bottom_layout.addWidget(self.lbl_status, stretch=1)
        bottom_layout.addWidget(self.status_progress)

        main_layout.addWidget(self.bottom_bar)

    def apply_theme(self):
        c = self.colors
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {c['bg']};
                color: {c['fg']};
                font-family: 'Cairo', 'Inter', sans-serif;
            }}
            QWidget {{
                color: {c['fg']};
            }}
            QFrame#ControllerCard {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border']};
                border-radius: 12px;
            }}
            QFrame#GuideBox {{
                background-color: {c['surface']};
                border: 1px solid {c['primary']};
                border-radius: 8px;
            }}
            QFrame#BottomBar {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 8px;
            }}
            QFrame.DeviceCard {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 10px;
                padding: 10px;
            }}
            QFrame.DeviceCard:hover {{
                border: 1px solid {c['primary']};
                background-color: {c['card_bg']};
            }}
            QTabWidget::pane {{
                border: 1px solid {c['border']};
                border-radius: 12px;
                background-color: {c['bg']};
                padding: 6px;
            }}
            QTabBar::tab {{
                background-color: {c['surface']};
                color: {c['fg']};
                border: 1px solid {c['border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 18px;
                margin-right: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {c['primary']};
                color: {c['bg']};
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                color: {c['fg']};
                padding: 7px 14px;
            }}
            QPushButton:hover {{
                background-color: {c['border']};
                border-color: {c['primary']};
            }}
            QPushButton.PrimaryBtn {{
                background-color: {c['primary']};
                color: {c['bg']};
                border: 1px solid {c['primary']};
                font-weight: bold;
            }}
            QPushButton.PrimaryBtn:hover {{
                background-color: {c['hover']};
                border-color: {c['hover']};
            }}
            QPushButton.DangerBtn {{
                background-color: transparent;
                color: {c['danger']};
                border: 1px solid {c['danger']};
            }}
            QPushButton.DangerBtn:hover {{
                background-color: {c['danger']};
                color: #ffffff;
            }}
            QPushButton.ActiveToggle {{
                background-color: {c['surface']};
                color: {c['hover']};
                border: 1px solid {c['hover']};
                font-weight: bold;
            }}
            QProgressBar {{
                background-color: {c['surface']};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {c['primary']};
                border-radius: 2px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {c['border']};
                min-height: 25px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {c['primary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

    def set_status(self, text, busy=False):
        self.lbl_status.setText(text)
        if busy:
            self.status_progress.show()
        else:
            self.status_progress.hide()

    def periodic_poll(self):
        if self.is_scanning or (self.current_pairing_dialog and self.current_pairing_dialog.isVisible()):
            return
        BluetoothEngine.auto_route_incoming_audio()
        try:
            paired, discovered = BluetoothEngine.get_all_devices()
            self.on_devices_updated(paired, discovered)
        except Exception:
            pass

    def refresh_all(self):
        self.set_status("جاري تحديث بيانات البلوتوث...", busy=True)
        ctrl = BluetoothEngine.get_controller()
        if not ctrl["available"]:
            self.lbl_adapter_name.setText("󰂲 البلوتوث غير متوفر أو غير مفعل")
            self.lbl_adapter_mac.setText(ctrl.get("error", "تأكد من تشغيل bluetooth.service"))
            self.btn_power.setEnabled(False)
            self.btn_scan.setEnabled(False)
            self.btn_discoverable.setEnabled(False)
            self.set_status("خدمة البلوتوث غير نشطة")
            return

        self.btn_power.setEnabled(True)
        is_powered = ctrl["powered"]

        if is_powered:
            self.lbl_adapter_name.setText(f"󰂯 {ctrl['name']} (نشط)")
            self.btn_power.setText("󰂲 إيقاف البلوتوث")
            self.btn_power.setProperty("class", "DangerBtn")
            self.btn_scan.setEnabled(True)
            self.btn_discoverable.setEnabled(True)
        else:
            self.lbl_adapter_name.setText(f"󰂲 {ctrl['name']} (متوقف)")
            self.btn_power.setText("󰂯 تشغيل البلوتوث")
            self.btn_power.setProperty("class", "PrimaryBtn")
            self.btn_scan.setEnabled(False)
            self.btn_discoverable.setEnabled(False)

        self.btn_power.setStyle(self.btn_power.style())
        self.lbl_adapter_mac.setText(f"العنوان: {ctrl['mac'] or 'N/A'}")

        self.is_discoverable = ctrl.get("discoverable", True)
        self.update_discoverable_btn_ui()

        # Automatically route incoming audio from connected phones/tablets
        BluetoothEngine.auto_route_incoming_audio()

        paired, discovered = BluetoothEngine.get_all_devices()
        self.on_devices_updated(paired, discovered)
        self.set_status("جاهز والاقتران متاح", busy=False)

    def update_discoverable_btn_ui(self):
        if self.is_discoverable:
            self.btn_discoverable.setText("󰈈 مرئي للأجهزة: نعم")
            self.btn_discoverable.setProperty("class", "ActiveToggle")
        else:
            self.btn_discoverable.setText("󰈉 غير مرئي (مخفي)")
            self.btn_discoverable.setProperty("class", "")
        self.btn_discoverable.setStyle(self.btn_discoverable.style())

    def toggle_discoverable(self):
        new_state = not self.is_discoverable
        self.is_discoverable = new_state
        self.update_discoverable_btn_ui()
        worker = ActionWorker("discoverable", "", extra=new_state)
        worker.finished.connect(self.on_action_finished)
        self.action_workers.append(worker)
        worker.start()

    def on_devices_updated(self, paired, discovered):
        self.paired_devices = paired
        self.discovered_devices = discovered
        self.render_paired_devices()
        self.render_discovered_devices()
        self.tabs.setTabText(0, f"الأجهزة المقترنة ({len(self.paired_devices)})")
        self.tabs.setTabText(1, f"الأجهزة المتاحة بالقرب ({len(self.discovered_devices)})")

    def render_paired_devices(self):
        while self.layout_paired.count() > 1:
            item = self.layout_paired.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.paired_devices:
            empty_lbl = QLabel("لا توجد أجهزة مقترنة حالياً.\nاضغط على 'بحث عن أجهزة' لاكتشاف الأجهزة المحيطة والاقتران بها.")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setFont(QFont("Cairo", 10))
            empty_lbl.setStyleSheet(f"color: {self.colors['fg']}; opacity: 0.6; padding: 40px;")
            self.layout_paired.insertWidget(0, empty_lbl)
            return

        for dev in self.paired_devices:
            card = self.create_device_card(dev, is_paired=True)
            self.layout_paired.insertWidget(self.layout_paired.count() - 1, card)

    def render_discovered_devices(self):
        while self.layout_disc.count() > 1:
            item = self.layout_disc.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.discovered_devices:
            msg = "لا توجد أجهزة قريبة مكتشفة حالياً."
            if self.scan_worker and self.scan_worker.isRunning():
                msg = "󰑮 جاري البحث عن الأجهزة القريبة... تأكد من تفعيل وضع الاقتران في جهازك"
            empty_lbl = QLabel(msg)
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_lbl.setFont(QFont("Cairo", 10))
            empty_lbl.setStyleSheet(f"color: {self.colors['fg']}; opacity: 0.6; padding: 40px;")
            self.layout_disc.insertWidget(0, empty_lbl)
            return

        for dev in self.discovered_devices:
            card = self.create_device_card(dev, is_paired=False)
            self.layout_disc.insertWidget(self.layout_disc.count() - 1, card)

    def create_device_card(self, dev, is_paired=True):
        card = QFrame()
        card.setProperty("class", "DeviceCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(14)

        # Icon
        glyph = BluetoothEngine.get_glyph_for_icon(dev.get("icon", ""), dev.get("name", ""))
        icon_lbl = QLabel(glyph)
        icon_lbl.setFont(QFont("JetBrainsMono Nerd Font", 18))
        icon_lbl.setStyleSheet(f"color: {self.colors['primary']};")
        icon_lbl.setFixedWidth(36)
        layout.addWidget(icon_lbl)

        # Name and Details
        info_vbox = QVBoxLayout()
        info_vbox.setSpacing(2)

        name_str = dev.get("name", "Unnamed Device")
        lbl_name = QLabel(name_str)
        lbl_name.setFont(QFont("Cairo", 11, QFont.Weight.Bold))
        lbl_name.setStyleSheet(f"color: {self.colors['fg']};")

        # Subtitle info: MAC + Status + Battery + RSSI
        sub_layout = QHBoxLayout()
        sub_layout.setSpacing(10)

        lbl_mac = QLabel(dev.get("mac", ""))
        lbl_mac.setFont(QFont("Cairo", 8))
        lbl_mac.setStyleSheet(f"color: {self.colors['fg']}; opacity: 0.6;")
        sub_layout.addWidget(lbl_mac)

        if is_paired:
            is_conn = dev.get("connected", False)
            status_text = "󰂱 متصل" if is_conn else "󰂯 مقترن"
            status_color = self.colors['hover'] if is_conn else self.colors['border']
            lbl_conn = QLabel(status_text)
            lbl_conn.setFont(QFont("Cairo", 8, QFont.Weight.Bold))
            lbl_conn.setStyleSheet(f"color: {status_color};")
            sub_layout.addWidget(lbl_conn)

        if dev.get("battery") is not None:
            lbl_bat = QLabel(f"󰁹 {dev['battery']}%")
            lbl_bat.setFont(QFont("Cairo", 8, QFont.Weight.Bold))
            lbl_bat.setStyleSheet(f"color: {self.colors['primary']};")
            sub_layout.addWidget(lbl_bat)

        if dev.get("rssi") is not None:
            lbl_rssi = QLabel(f"إشارة: {dev['rssi']} dBm")
            lbl_rssi.setFont(QFont("Cairo", 8))
            lbl_rssi.setStyleSheet(f"color: {self.colors['fg']}; opacity: 0.5;")
            sub_layout.addWidget(lbl_rssi)

        sub_layout.addStretch()

        info_vbox.addWidget(lbl_name)
        info_vbox.addLayout(sub_layout)
        layout.addLayout(info_vbox, stretch=1)

        # Actions
        mac = dev.get("mac", "")
        icon_name = dev.get("icon", "")
        if is_paired:
            if dev.get("connected", False):
                btn_disc = QPushButton("قطع الاتصال")
                btn_disc.setFont(QFont("Cairo", 8))
                btn_disc.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_disc.clicked.connect(lambda _, m=mac: self.do_disconnect(m))
                layout.addWidget(btn_disc)
            else:
                btn_conn = QPushButton("اتصال")
                btn_conn.setProperty("class", "PrimaryBtn")
                btn_conn.setFont(QFont("Cairo", 8, QFont.Weight.Bold))
                btn_conn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_conn.clicked.connect(lambda _, m=mac: self.do_connect(m))
                layout.addWidget(btn_conn)

            btn_rm = QPushButton("إلغاء الاقتران")
            btn_rm.setProperty("class", "DangerBtn")
            btn_rm.setFont(QFont("Cairo", 8))
            btn_rm.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_rm.clicked.connect(lambda _, m=mac: self.do_remove(m))
            layout.addWidget(btn_rm)
        else:
            btn_pair = QPushButton("اقتران وتوصيل")
            btn_pair.setProperty("class", "PrimaryBtn")
            btn_pair.setFont(QFont("Cairo", 8, QFont.Weight.Bold))
            btn_pair.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_pair.clicked.connect(lambda _, m=mac, n=name_str, ic=icon_name: self.do_pair(m, n, ic))
            layout.addWidget(btn_pair)

        return card

    def toggle_power(self):
        ctrl = BluetoothEngine.get_controller()
        new_state = not ctrl.get("powered", False)
        self.set_status("جاري تغيير حالة الطاقة للبلوتوث...", busy=True)
        worker = ActionWorker("power", "", extra=new_state)
        worker.finished.connect(self.on_action_finished)
        self.action_workers.append(worker)
        worker.start()

    def toggle_scan(self):
        if self.scan_worker and self.scan_worker.isRunning():
            self.btn_scan.setText("󰍉 بحث عن أجهزة")
            self.set_status("جاري إيقاف البحث...")
            self.scan_worker.stop()
            self.status_progress.hide()
        else:
            self.btn_scan.setText("󰑮 إيقاف البحث")
            self.status_progress.show()
            self.tabs.setCurrentIndex(1)
            self.scan_worker = ScanWorker()
            self.scan_worker.devices_updated.connect(self.on_devices_updated)
            self.scan_worker.scan_status.connect(self.on_scan_status)
            self.scan_worker.start()

    def on_scan_status(self, is_scanning, msg):
        self.set_status(msg, busy=is_scanning)
        if not is_scanning:
            self.btn_scan.setText("󰍉 بحث عن أجهزة")
            self.status_progress.hide()

    def do_connect(self, mac):
        self.set_status(f"جاري الاتصال بـ {mac}...", busy=True)
        worker = ActionWorker("connect", mac)
        worker.finished.connect(self.on_action_finished)
        self.action_workers.append(worker)
        worker.start()

    def do_disconnect(self, mac):
        self.set_status(f"جاري قطع الاتصال بـ {mac}...", busy=True)
        worker = ActionWorker("disconnect", mac)
        worker.finished.connect(self.on_action_finished)
        self.action_workers.append(worker)
        worker.start()

    def do_pair(self, mac, name="", icon=""):
        display_name = name or mac
        self.set_status(f"جاري الاقتران بـ {display_name} والاتصال به...", busy=True)

        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.stop()

        # Show the step-by-step instruction dialog!
        self.current_pairing_dialog = PairingInstructionDialog(self, display_name, mac, icon, self.colors)
        self.current_pairing_dialog.show()

        worker = ActionWorker("pair", mac)
        worker.finished.connect(self.on_action_finished)
        self.action_workers.append(worker)
        worker.start()

    def do_remove(self, mac):
        self.set_status(f"جاري إلغاء اقتران {mac}...", busy=True)
        worker = ActionWorker("remove", mac)
        worker.finished.connect(self.on_action_finished)
        self.action_workers.append(worker)
        worker.start()

    def on_action_finished(self, action, ok, mac, msg):
        if action == "connect":
            if ok:
                self.set_status(f"تم الاتصال بنجاح بـ {mac} ✔")
            else:
                self.set_status(f"فشل الاتصال: {msg}")
        elif action == "disconnect":
            self.set_status("تم قطع الاتصال")
        elif action == "pair":
            if self.current_pairing_dialog and self.current_pairing_dialog.isVisible():
                self.current_pairing_dialog.set_result(ok, msg)
            if ok:
                self.set_status(f"تم الاقتران والاتصال بنجاح بـ {mac} 🎉")
                self.tabs.setCurrentIndex(0)
            else:
                self.set_status(f"تعذر الاقتران: {msg}")
        elif action == "remove":
            self.set_status("تم إلغاء اقتران الجهاز بنجاح")
        elif action == "power":
            self.set_status("تم تغيير حالة البلوتوث")
        elif action == "discoverable":
            state_text = "الكمبيوتر الآن مرئي لجميع الأجهزة المحيطة (هواتف وسماعات)" if self.is_discoverable else "تم إخفاء الكمبيوتر عن الأجهزة المحيطة"
            self.set_status(state_text)

        self.refresh_all()

    def closeEvent(self, event):
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.stop()
        event.accept()
