#!/usr/bin/env python3
"""
Main User Interface for NooreldeanOS Speed Test.
Built with PyQt6, Pywal dynamic theming, and modern glassmorphism aesthetics.
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QComboBox, QProgressBar, 
    QFrame, QDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QToolTip
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import (
    QPalette, QColor, QFont, QIcon, QPixmap, QPainter, 
    QLinearGradient, QAction
)

from speed_engine import SpeedEngine
from gauge_widget import CircularGaugeWidget
from graph_widget import LiveGraphWidget

HISTORY_FILE = Path.home() / ".config" / "speed-test" / "history.json"

def load_pywal_colors():
    """Load colors dynamically from Pywal cache or return modern dark theme fallback."""
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
                'surface': data['colors'].get('color0', '#1f2430'),
                'border': data['colors'].get('color8', '#384152'),
                'card_bg': data['colors'].get('color0', '#1c212b')
            }
        except Exception:
            pass

    return {
        'bg': '#14171e',
        'fg': '#e2e8f0',
        'primary': '#38bdf8',
        'secondary': '#818cf8',
        'hover': '#34d399',
        'danger': '#f43f5e',
        'surface': '#1b202c',
        'border': '#2d3748',
        'card_bg': '#1e2433'
    }

class InfoFetcherThread(QThread):
    info_ready = pyqtSignal(dict)

    def run(self):
        try:
            info = SpeedEngine.get_network_info()
            self.info_ready.emit(info)
        except Exception:
            pass

class SpeedTestWorker(QThread):
    net_info_ready = pyqtSignal(dict)
    ping_progress = pyqtSignal(dict)
    ping_done = pyqtSignal(dict)
    download_progress = pyqtSignal(dict)
    download_done = pyqtSignal(dict)
    upload_progress = pyqtSignal(dict)
    upload_done = pyqtSignal(dict)
    test_finished = pyqtSignal(dict)
    test_error = pyqtSignal(str)

    def __init__(self, engine_mode="cloudflare"):
        super().__init__()
        self.engine_mode = engine_mode
        self.engine = SpeedEngine()

    def cancel(self):
        self.engine.cancel()

    def run(self):
        try:
            # 1. Network Info
            net_info = self.engine.get_network_info()
            self.net_info_ready.emit(net_info)

            if self.engine_mode == "ookla":
                # Run through speedtest-cli
                try:
                    res = self.engine.run_speedtest_cli()
                    self.test_finished.emit(res)
                    return
                except Exception as e:
                    self.test_error.emit(f"خطأ في Ookla CLI: {e}\nجاري التحويل للمحرك المدمج...")
                    time.sleep(1)

            # --- Built-in Cloudflare High-Speed Engine ---
            # 2. Ping & Jitter
            self.ping_progress.emit({"status": "measuring"})
            ping_res = self.engine.measure_ping_jitter(count=5)
            if self.engine.cancel_event.is_set():
                return
            if not ping_res:
                ping_res = {"ping": 0.0, "jitter": 0.0}
            self.ping_done.emit(ping_res)

            # 3. Download Speed Test (8 seconds multi-stream)
            def on_down_update(data):
                self.download_progress.emit(data)

            down_res = self.engine.measure_download(progress_callback=on_down_update, duration=8.0, threads_count=4)
            if self.engine.cancel_event.is_set():
                return
            self.download_done.emit(down_res)

            # Brief pause for aesthetic transition
            time.sleep(0.4)

            # 4. Upload Speed Test (7 seconds multi-stream)
            def on_up_update(data):
                self.upload_progress.emit(data)

            up_res = self.engine.measure_upload(progress_callback=on_up_update, duration=7.0, threads_count=4)
            if self.engine.cancel_event.is_set():
                return
            self.upload_done.emit(up_res)

            # 5. Compile Final Result
            final_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "ping": ping_res.get("ping", 0.0),
                "jitter": ping_res.get("jitter", 0.0),
                "download": down_res.get("avg_mbps", 0.0),
                "download_peak": down_res.get("peak_mbps", 0.0),
                "upload": up_res.get("avg_mbps", 0.0),
                "upload_peak": up_res.get("peak_mbps", 0.0),
                "ip": net_info.get("ip", "Unknown"),
                "isp": net_info.get("isp", "Unknown"),
                "city": net_info.get("city", ""),
                "country": net_info.get("country", ""),
                "server": net_info.get("server", "Cloudflare Edge")
            }
            self.test_finished.emit(final_data)

        except Exception as e:
            self.test_error.emit(str(e))

class MetricCard(QFrame):
    """Modern Glassmorphic Metric Display Card."""
    def __init__(self, title_ar, title_en, icon_symbol, unit="Mbps", colors=None, parent=None):
        super().__init__(parent)
        self.colors = colors or {}
        self.unit = unit
        self.accent_color = self.colors.get('primary', '#38bdf8')

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("MetricCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        # Header: Icon + Title
        hdr_box = QHBoxLayout()
        self.lbl_icon = QLabel(icon_symbol)
        self.lbl_icon.setFont(QFont("JetBrainsMono Nerd Font", 16))
        self.lbl_icon.setStyleSheet(f"color: {self.accent_color};")

        self.lbl_title = QLabel(f"{title_ar} • {title_en}")
        self.lbl_title.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet(f"color: {self.colors.get('fg', '#e2e8f0')}; opacity: 0.8;")

        hdr_box.addWidget(self.lbl_icon)
        hdr_box.addWidget(self.lbl_title)
        hdr_box.addStretch()

        # Value + Unit
        val_box = QHBoxLayout()
        val_box.setSpacing(6)
        self.lbl_value = QLabel("--")
        self.lbl_value.setFont(QFont("Inter", 22, QFont.Weight.Bold))
        self.lbl_value.setStyleSheet(f"color: {self.colors.get('fg', '#ffffff')};")

        self.lbl_unit = QLabel(self.unit)
        self.lbl_unit.setFont(QFont("Inter", 11, QFont.Weight.Medium))
        self.lbl_unit.setStyleSheet(f"color: {self.accent_color}; margin-top: 8px;")

        val_box.addWidget(self.lbl_value)
        val_box.addWidget(self.lbl_unit)
        val_box.addStretch()

        # Subtitle / status
        self.lbl_sub = QLabel("جاهز للقياس")
        self.lbl_sub.setFont(QFont("Inter", 9))
        self.lbl_sub.setStyleSheet("color: #718096;")

        layout.addLayout(hdr_box)
        layout.addLayout(val_box)
        layout.addWidget(self.lbl_sub)

        self.update_style(active=False)

    def set_value(self, val_str, sub_str=None, color=None):
        self.lbl_value.setText(val_str)
        if sub_str:
            self.lbl_sub.setText(sub_str)
        if color:
            self.lbl_value.setStyleSheet(f"color: {color};")
            self.lbl_icon.setStyleSheet(f"color: {color};")
            self.lbl_unit.setStyleSheet(f"color: {color}; margin-top: 8px;")

    def update_style(self, active=False):
        c_bg = self.colors.get('card_bg', '#1e2433')
        c_border = self.accent_color if active else self.colors.get('border', '#2d3748')
        glow = f"border: 1.5px solid {c_border};" if active else f"border: 1px solid {c_border};"
        self.setStyleSheet(f"""
            QFrame#MetricCard {{
                background-color: {c_bg};
                border-radius: 12px;
                {glow}
            }}
        """)

class HistoryDialog(QDialog):
    """Dialog showing previous speed test runs."""
    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
        self.setWindowTitle("سجل فحوصات السرعة | Test History")
        self.resize(650, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors.get('bg', '#14171e')};
                color: {colors.get('fg', '#e2e8f0')};
            }}
            QTableWidget {{
                background-color: {colors.get('surface', '#1b202c')};
                border: 1px solid {colors.get('border', '#2d3748')};
                border-radius: 10px;
                color: {colors.get('fg', '#e2e8f0')};
                gridline-color: {colors.get('border', '#2d3748')};
            }}
            QHeaderView::section {{
                background-color: {colors.get('card_bg', '#1e2433')};
                color: {colors.get('primary', '#38bdf8')};
                font-weight: bold;
                padding: 6px;
                border: none;
                border-bottom: 1px solid {colors.get('border', '#2d3748')};
            }}
            QPushButton {{
                background-color: {colors.get('surface', '#1b202c')};
                border: 1px solid {colors.get('border', '#2d3748')};
                border-radius: 8px;
                color: {colors.get('fg', '#e2e8f0')};
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors.get('primary', '#38bdf8')};
                color: {colors.get('bg', '#14171e')};
            }}
        """)

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["التاريخ | Date", "تحميل (Mbps)", "رفع (Mbps)", "Ping (ms)", "المزود | ISP"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        btn_box = QHBoxLayout()
        self.btn_clear = QPushButton("مسح السجل | Clear")
        self.btn_clear.clicked.connect(self.clear_history)
        self.btn_close = QPushButton("إغلاق | Close")
        self.btn_close.clicked.connect(self.accept)

        btn_box.addWidget(self.btn_clear)
        btn_box.addStretch()
        btn_box.addWidget(self.btn_close)
        layout.addLayout(btn_box)

        self.load_history()

    def load_history(self):
        self.table.setRowCount(0)
        if not HISTORY_FILE.exists():
            return
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
            records.reverse()
            for r in records[:50]:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(r.get("timestamp", "")))
                self.table.setItem(row, 1, QTableWidgetItem(f"{r.get('download', 0):.1f}"))
                self.table.setItem(row, 2, QTableWidgetItem(f"{r.get('upload', 0):.1f}"))
                self.table.setItem(row, 3, QTableWidgetItem(f"{r.get('ping', 0):.1f}"))
                self.table.setItem(row, 4, QTableWidgetItem(r.get("isp", "")))
        except Exception:
            pass

    def clear_history(self):
        if HISTORY_FILE.exists():
            try:
                HISTORY_FILE.unlink()
            except Exception:
                pass
        self.table.setRowCount(0)

class SpeedTestApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.colors = load_pywal_colors()
        self.setWindowTitle("NooreldeanOS Speed Test")
        self.resize(880, 680)
        self.setMinimumSize(820, 620)

        # Set App Icon
        icon_path = Path.home() / ".config" / "speed-test" / "assets" / "icon.svg"
        if not icon_path.exists():
            icon_path = Path(__file__).parent / "assets" / "icon.svg"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.worker = None
        self.latest_result = None
        self.is_testing = False

        self.setup_ui()
        self.apply_theme()

        # Load initial network info in background
        QTimer.singleShot(150, self.fetch_initial_info)

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # 1. Header Toolbar
        hdr_layout = QHBoxLayout()
        
        # Logo + Titles
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_app_title = QLabel("NooreldeanOS Speed Test")
        lbl_app_title.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        lbl_app_title.setStyleSheet(f"color: {self.colors['primary']};")

        lbl_app_desc = QLabel("أداة قياس سرعة واستقرار الاتصال بالإنترنت  •  Internet Bandwidth Benchmark")
        lbl_app_desc.setFont(QFont("Inter", 9))
        lbl_app_desc.setStyleSheet(f"color: {self.colors['fg']}; opacity: 0.7;")

        title_box.addWidget(lbl_app_title)
        title_box.addWidget(lbl_app_desc)
        hdr_layout.addLayout(title_box)
        hdr_layout.addStretch()

        # Engine Selector & Connection Badge
        engine_box = QHBoxLayout()
        engine_box.setSpacing(10)

        self.lbl_net_badge = QLabel("🟢 جاري التحقق من الشبكة...")
        self.lbl_net_badge.setFont(QFont("Inter", 9, QFont.Weight.DemiBold))
        self.lbl_net_badge.setStyleSheet(f"""
            background-color: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: 8px;
            padding: 4px 10px;
            color: {self.colors['fg']};
        """)

        self.combo_engine = QComboBox()
        self.combo_engine.setFont(QFont("Inter", 9, QFont.Weight.Medium))
        self.combo_engine.addItem("⚡ Cloudflare Edge Engine (مباشر وسريع)", "cloudflare")
        if SpeedEngine.is_speedtest_cli_available():
            self.combo_engine.addItem("🌐 Ookla Speedtest.net CLI", "ookla")
        self.combo_engine.setToolTip("اختر محرك القياس المناسب")

        engine_box.addWidget(self.lbl_net_badge)
        engine_box.addWidget(self.combo_engine)
        hdr_layout.addLayout(engine_box)
        main_layout.addLayout(hdr_layout)

        # 2. Network Info Strip (Glass Cards)
        info_strip = QHBoxLayout()
        info_strip.setSpacing(12)

        self.card_ip = self._create_info_box("🌐 عنوان IP والموقع", "جاري الكشف...", "IP & Location")
        self.card_isp = self._create_info_box("🏢 مزود الخدمة (ISP)", "جاري الكشف...", "Internet Provider")
        self.card_server = self._create_info_box("⚡ خادم الفحص", "Cloudflare Anycast", "Server Node")

        info_strip.addWidget(self.card_ip)
        info_strip.addWidget(self.card_isp)
        info_strip.addWidget(self.card_server)
        main_layout.addLayout(info_strip)

        # 3. Main Center Split Section (Gauge on Left, Live Graph on Right)
        center_layout = QHBoxLayout()
        center_layout.setSpacing(16)

        # Left: Circular Speedometer Gauge
        self.gauge = CircularGaugeWidget(self, self.colors)
        center_layout.addWidget(self.gauge, stretch=4)

        # Right: Live Graph & Realtime Indicators
        right_box = QVBoxLayout()
        right_box.setSpacing(12)

        self.graph = LiveGraphWidget(self, self.colors)
        right_box.addWidget(self.graph, stretch=3)

        # Realtime test status strip
        status_box = QHBoxLayout()
        self.lbl_status_msg = QLabel("اضغط على الزر أدناه لبدء الفحص الكامل")
        self.lbl_status_msg.setFont(QFont("Inter", 10, QFont.Weight.Medium))
        self.lbl_status_msg.setStyleSheet(f"color: {self.colors['fg']};")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['primary']};
                border-radius: 3px;
            }}
        """)

        status_box.addWidget(self.lbl_status_msg)
        right_box.addLayout(status_box)
        right_box.addWidget(self.progress_bar)

        center_layout.addLayout(right_box, stretch=5)
        main_layout.addLayout(center_layout)

        # 4. Metric Cards (4 Grid Cards)
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(12)

        self.card_ping = MetricCard("زمن الاستجابة", "Ping", "⚡", unit="ms", colors=self.colors)
        self.card_jitter = MetricCard("التذبذب", "Jitter", "〰️", unit="ms", colors=self.colors)
        self.card_download = MetricCard("سرعة التحميل", "Download", "⬇️", unit="Mbps", colors=self.colors)
        self.card_upload = MetricCard("سرعة الرفع", "Upload", "⬆️", unit="Mbps", colors=self.colors)

        metrics_layout.addWidget(self.card_ping, 0, 0)
        metrics_layout.addWidget(self.card_jitter, 0, 1)
        metrics_layout.addWidget(self.card_download, 0, 2)
        metrics_layout.addWidget(self.card_upload, 0, 3)
        main_layout.addLayout(metrics_layout)

        # 5. Bottom Action Controls
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(12)

        self.btn_start = QPushButton("🚀 بدء فحص السرعة  •  START TEST")
        self.btn_start.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        self.btn_start.setFixedHeight(48)
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.clicked.connect(self.toggle_test)

        self.btn_copy = QPushButton("📋 نسخ النتيجة")
        self.btn_copy.setFont(QFont("Inter", 10, QFont.Weight.DemiBold))
        self.btn_copy.setFixedHeight(48)
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.setEnabled(False)
        self.btn_copy.clicked.connect(self.copy_results)

        self.btn_history = QPushButton("📜 السجل")
        self.btn_history.setFont(QFont("Inter", 10, QFont.Weight.DemiBold))
        self.btn_history.setFixedHeight(48)
        self.btn_history.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_history.clicked.connect(self.show_history)

        self.btn_refresh = QPushButton("🔄 تحديث الشبكة")
        self.btn_refresh.setFont(QFont("Inter", 10, QFont.Weight.DemiBold))
        self.btn_refresh.setFixedHeight(48)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.fetch_initial_info)

        ctrl_layout.addWidget(self.btn_start, stretch=4)
        ctrl_layout.addWidget(self.btn_copy, stretch=1)
        ctrl_layout.addWidget(self.btn_history, stretch=1)
        ctrl_layout.addWidget(self.btn_refresh, stretch=1)
        main_layout.addLayout(ctrl_layout)

    def _create_info_box(self, title_ar, default_val, title_en):
        box = QFrame()
        box.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['surface']};
                border: 1px solid {self.colors['border']};
                border-radius: 10px;
                padding: 4px 10px;
            }}
        """)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        lbl_t = QLabel(f"{title_ar} • {title_en}")
        lbl_t.setFont(QFont("Inter", 8, QFont.Weight.Bold))
        lbl_t.setStyleSheet(f"color: {self.colors['primary']}; opacity: 0.85;")

        lbl_v = QLabel(default_val)
        lbl_v.setFont(QFont("Inter", 10, QFont.Weight.Medium))
        lbl_v.setStyleSheet(f"color: {self.colors['fg']};")
        lbl_v.setWordWrap(True)

        layout.addWidget(lbl_t)
        layout.addWidget(lbl_v)
        box.val_label = lbl_v
        return box

    def apply_theme(self):
        c = self.colors
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {c['bg']};
                color: {c['fg']};
                font-family: 'Inter', sans-serif;
            }}
            QComboBox {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding: 6px 12px;
                color: {c['fg']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QPushButton {{
                background-color: {c['surface']};
                border: 1px solid {c['border']};
                border-radius: 10px;
                color: {c['fg']};
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {c['border']};
                border-color: {c['primary']};
            }}
            QPushButton:disabled {{
                opacity: 0.4;
                color: {c['border']};
            }}
            QPushButton#StartBtnActive {{
                background-color: {c['primary']};
                color: {c['bg']};
                border: 1px solid {c['primary']};
                font-weight: bold;
            }}
            QPushButton#StartBtnActive:hover {{
                background-color: {c['hover']};
                border-color: {c['hover']};
            }}
            QPushButton#StopBtn {{
                background-color: {c['danger']};
                color: #ffffff;
                border: 1px solid {c['danger']};
                font-weight: bold;
            }}
        """)
        self.btn_start.setObjectName("StartBtnActive")
        self.btn_start.setStyle(self.btn_start.style())

    def fetch_initial_info(self):
        self.lbl_net_badge.setText("🔄 جاري الكشف...")
        self._info_fetcher = InfoFetcherThread(self)
        self._info_fetcher.info_ready.connect(self._update_net_ui)
        self._info_fetcher.start()

    def _update_net_ui(self, info):
        ip = info.get("ip", "Unknown")
        city = info.get("city", "")
        country = info.get("country", "")
        loc_str = f"{ip} ({city}, {country})" if city else ip
        self.card_ip.val_label.setText(loc_str)

        isp = info.get("isp", "Unknown ISP")
        self.card_isp.val_label.setText(isp)

        server = info.get("server", "Cloudflare Anycast")
        self.card_server.val_label.setText(server)

        iface = info.get("interface", "Default")
        self.lbl_net_badge.setText(f"🟢 متصل: {iface}")

    def toggle_test(self):
        if self.is_testing:
            self.stop_test()
        else:
            self.start_test()

    def start_test(self):
        self.is_testing = True
        self.latest_result = None
        self.btn_copy.setEnabled(False)

        # Update button to Stop style
        self.btn_start.setText("⏹ إيقاف الفحص  •  STOP")
        self.btn_start.setObjectName("StopBtn")
        self.btn_start.setStyleSheet(f"background-color: {self.colors['danger']}; color: white; border: none;")

        # Reset widgets
        self.gauge.reset()
        self.graph.clear()
        self.progress_bar.setValue(0)
        self.card_ping.set_value("--", "جاري الفحص...")
        self.card_jitter.set_value("--", "جاري الفحص...")
        self.card_download.set_value("--", "في الانتظار...")
        self.card_upload.set_value("--", "في الانتظار...")

        mode = self.combo_engine.currentData()
        self.worker = SpeedTestWorker(engine_mode=mode)
        self.worker.net_info_ready.connect(self._update_net_ui)
        self.worker.ping_progress.connect(self._on_ping_progress)
        self.worker.ping_done.connect(self._on_ping_done)
        self.worker.download_progress.connect(self._on_download_progress)
        self.worker.download_done.connect(self._on_download_done)
        self.worker.upload_progress.connect(self._on_upload_progress)
        self.worker.upload_done.connect(self._on_upload_done)
        self.worker.test_finished.connect(self._on_test_finished)
        self.worker.test_error.connect(self._on_test_error)
        self.worker.start()

    def stop_test(self):
        if self.worker and self.worker.isRunning():
            self.lbl_status_msg.setText("⚠️ جاري إلغاء الفحص...")
            self.worker.cancel()
            self.worker.wait(1000)
        self._test_ended_cleanup()
        self.lbl_status_msg.setText("تم إلغاء الفحص بواسطة المستخدم")
        self.gauge.set_phase("تم الإلغاء", "CANCELLED", color=self.colors['danger'])

    def _test_ended_cleanup(self):
        self.is_testing = False
        self.btn_start.setText("🚀 بدء فحص جديد  •  START TEST")
        self.btn_start.setObjectName("StartBtnActive")
        self.btn_start.setStyleSheet("")
        self.btn_start.setStyle(self.btn_start.style())
        self.card_ping.update_style(False)
        self.card_jitter.update_style(False)
        self.card_download.update_style(False)
        self.card_upload.update_style(False)

    def _on_ping_progress(self, data):
        self.lbl_status_msg.setText("⚡ جاري قياس زمن الاستجابة والتذبذب (Ping & Jitter)...")
        self.gauge.set_phase("فحص Ping", "TESTING LATENCY", color=self.colors['primary'], unit="ms")
        self.card_ping.update_style(True)
        self.card_jitter.update_style(True)

    def _on_ping_done(self, data):
        p = data.get("ping", 0.0)
        j = data.get("jitter", 0.0)
        status_ping = "ممتاز جداً" if p < 50 else ("جيد" if p < 100 else "مرتفع")
        status_jitter = "مستقر" if j < 5 else "متفاوت"

        self.card_ping.set_value(f"{p:.1f}", status_ping, color=self.colors['primary'])
        self.card_jitter.set_value(f"{j:.1f}", status_jitter, color=self.colors['secondary'])
        self.gauge.set_speed(p)
        self.card_ping.update_style(False)
        self.card_jitter.update_style(False)

    def _on_download_progress(self, data):
        spd = data.get("speed_mbps", 0.0)
        peak = data.get("peak_mbps", 0.0)
        mb = data.get("total_mb", 0.0)
        pct = data.get("progress_pct", 0.0)

        self.lbl_status_msg.setText(f"⬇️ جاري قياس سرعة التحميل... {spd:.1f} Mbps (تم نقل {mb:.1f} MB)")
        self.progress_bar.setValue(int(pct / 2.0))  # First half of progress bar
        self.gauge.set_phase("تحميل", "DOWNLOAD", color=self.colors['primary'], unit="Mbps")
        self.gauge.set_speed(spd)
        self.graph.set_accent_color(self.colors['primary'])
        self.graph.add_sample(spd)
        self.card_download.update_style(True)
        self.card_download.set_value(f"{spd:.1f}", f"أعلى سرعة: {peak:.1f} Mbps", color=self.colors['primary'])

    def _on_download_done(self, data):
        avg = data.get("avg_mbps", 0.0)
        peak = data.get("peak_mbps", 0.0)
        self.card_download.set_value(f"{avg:.1f}", f"القمة: {peak:.1f} Mbps", color=self.colors['primary'])
        self.card_download.update_style(False)
        self.graph.clear()

    def _on_upload_progress(self, data):
        spd = data.get("speed_mbps", 0.0)
        peak = data.get("peak_mbps", 0.0)
        mb = data.get("total_mb", 0.0)
        pct = data.get("progress_pct", 0.0)

        self.lbl_status_msg.setText(f"⬆️ جاري قياس سرعة الرفع... {spd:.1f} Mbps (تم نقل {mb:.1f} MB)")
        self.progress_bar.setValue(int(50 + pct / 2.0))  # Second half of progress bar
        self.gauge.set_phase("رفع", "UPLOAD", color=self.colors['secondary'], unit="Mbps")
        self.gauge.set_speed(spd)
        self.graph.set_accent_color(self.colors['secondary'])
        self.graph.add_sample(spd)
        self.card_upload.update_style(True)
        self.card_upload.set_value(f"{spd:.1f}", f"أعلى سرعة: {peak:.1f} Mbps", color=self.colors['secondary'])

    def _on_upload_done(self, data):
        avg = data.get("avg_mbps", 0.0)
        peak = data.get("peak_mbps", 0.0)
        self.card_upload.set_value(f"{avg:.1f}", f"القمة: {peak:.1f} Mbps", color=self.colors['secondary'])
        self.card_upload.update_style(False)

    def _on_test_finished(self, results):
        self._test_ended_cleanup()
        self.latest_result = results
        self.btn_copy.setEnabled(True)
        self.progress_bar.setValue(100)

        down = results.get("download", 0.0)
        up = results.get("upload", 0.0)
        ping = results.get("ping", 0.0)

        self.lbl_status_msg.setText(f"✅ اكتمل الفحص بنجاح! التحميل: {down:.1f} Mbps | الرفع: {up:.1f} Mbps")
        self.gauge.set_phase("اكتمل الفحص", "COMPLETED", color=self.colors['hover'])
        self.gauge.set_speed(down)

        # Save to history
        self.save_history(results)

    def _on_test_error(self, err_msg):
        self._test_ended_cleanup()
        self.lbl_status_msg.setText(f"❌ حدث خطأ: {err_msg}")
        QMessageBox.warning(self, "خطأ في الفحص", f"تعذر إكمال الفحص:\n{err_msg}")

    def save_history(self, record):
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        history = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append(record)
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def copy_results(self):
        if not self.latest_result:
            return
        r = self.latest_result
        text = (
            f"🚀 NooreldeanOS Speed Test Results:\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⬇️ التحميل (Download): {r.get('download', 0.0):.1f} Mbps (Peak: {r.get('download_peak', 0.0):.1f})\n"
            f"⬆️ الرفع (Upload):     {r.get('upload', 0.0):.1f} Mbps (Peak: {r.get('upload_peak', 0.0):.1f})\n"
            f"⚡ الاستجابة (Ping):    {r.get('ping', 0.0):.1f} ms\n"
            f"〰️ التذبذب (Jitter):   {r.get('jitter', 0.0):.1f} ms\n"
            f"🌐 المزود (ISP):        {r.get('isp', 'Unknown')}\n"
            f"📍 الموقع (Location):  {r.get('city', '')} {r.get('country', '')}\n"
            f"📅 التاريخ (Date):     {r.get('timestamp', '')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"تم الاختبار بواسطة توزيعة NooreldeanOS"
        )
        QApplication.clipboard().setText(text)
        self.lbl_status_msg.setText("📋 تم نسخ نتائج الفحص للحافظة بنجاح!")

    def show_history(self):
        dlg = HistoryDialog(self.colors, self)
        dlg.exec()
