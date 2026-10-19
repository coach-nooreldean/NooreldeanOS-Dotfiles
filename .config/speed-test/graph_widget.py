#!/usr/bin/env python3
"""
Live Bandwidth Graph / Sparkline Widget for NooreldeanOS Speed Test.
Displays real-time throughput curves with smooth gradient fills and peak indicators.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, 
    QLinearGradient, QPainterPath
)

class LiveGraphWidget(QWidget):
    def __init__(self, parent=None, colors=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.colors = colors or {
            'bg': '#181b22',
            'fg': '#cdd6f4',
            'primary': '#38bdf8',
            'surface': '#222733',
            'border': '#333b4d'
        }
        self.samples = []  # list of speed values (Mbps)
        self.max_samples = 40
        self.peak_value = 0.0
        self.accent_color = self.colors.get('primary', '#38bdf8')

    def update_colors(self, colors):
        self.colors = colors
        self.accent_color = colors.get('primary', '#38bdf8')
        self.update()

    def set_accent_color(self, hex_color):
        self.accent_color = hex_color
        self.update()

    def add_sample(self, speed_mbps):
        val = max(0.0, float(speed_mbps))
        self.samples.append(val)
        if len(self.samples) > self.max_samples:
            self.samples.pop(0)
        if val > self.peak_value:
            self.peak_value = val
        self.update()

    def clear(self):
        self.samples.clear()
        self.peak_value = 0.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()

        # Background card
        card_rect = QRectF(0, 0, w, h)
        bg_col = QColor(self.colors.get('surface', '#222733'))
        bg_col.setAlpha(160)
        painter.setPen(QPen(QColor(self.colors.get('border', '#333b4d')), 1.0))
        painter.setBrush(QBrush(bg_col))
        painter.drawRoundedRect(card_rect, 12.0, 12.0)

        # Inner graph padding
        pad_x = 24.0
        pad_top = 34.0
        pad_bottom = 20.0
        gw = w - (pad_x * 2.0)
        gh = h - pad_top - pad_bottom

        # Graph Header
        title_font = QFont("Inter", 10, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor(self.colors.get('fg', '#cdd6f4')))
        painter.drawText(QRectF(pad_x, 10, gw, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "مخطط السرعة المباشر  •  Live Bandwidth")

        peak_font = QFont("JetBrainsMono Nerd Font", 9, QFont.Weight.DemiBold)
        painter.setFont(peak_font)
        painter.setPen(QColor(self.accent_color))
        painter.drawText(QRectF(pad_x, 10, gw, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"Peak: {self.peak_value:.1f} Mbps")

        # Determine y-axis max scale
        chart_max = max(10.0, self.peak_value * 1.15)

        # Draw subtle grid lines (25%, 50%, 75%, 100%)
        grid_pen = QPen(QColor(self.colors.get('border', '#333b4d')), 0.8, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        grid_font = QFont("Inter", 8)
        painter.setFont(grid_font)

        for step in [0.25, 0.50, 0.75, 1.0]:
            y_pos = pad_top + gh * (1.0 - step)
            painter.drawLine(QPointF(pad_x, y_pos), QPointF(pad_x + gw, y_pos))
            val_label = f"{int(chart_max * step)}"
            painter.setPen(QColor(self.colors.get('fg', '#cdd6f4')).lighter(60))
            painter.drawText(QRectF(w - pad_x - 35, y_pos - 12, 35, 12), Qt.AlignmentFlag.AlignRight, val_label)
            painter.setPen(grid_pen)

        if len(self.samples) < 2:
            # Idle placeholder text
            painter.setPen(QColor(self.colors.get('border', '#666e7f')))
            painter.setFont(QFont("Inter", 10, QFont.Weight.Medium))
            painter.drawText(QRectF(pad_x, pad_top, gw, gh), Qt.AlignmentFlag.AlignCenter, "بانتظار بدء الفحص... | Waiting to start...")
            return

        # Build polyline and area path
        step_x = gw / float(self.max_samples - 1)
        start_idx = self.max_samples - len(self.samples)

        path_line = QPainterPath()
        first_pt = None

        for i, val in enumerate(self.samples):
            plot_idx = start_idx + i
            px = pad_x + plot_idx * step_x
            y_norm = min(1.0, val / chart_max)
            py = pad_top + gh * (1.0 - y_norm)

            pt = QPointF(px, py)
            if i == 0:
                path_line.moveTo(pt)
                first_pt = pt
            else:
                path_line.lineTo(pt)

        # Area under curve
        path_area = QPainterPath(path_line)
        last_pt = path_line.currentPosition()
        path_area.lineTo(last_pt.x(), pad_top + gh)
        path_area.lineTo(first_pt.x(), pad_top + gh)
        path_area.closeSubpath()

        # Gradient fill
        fill_grad = QLinearGradient(0, pad_top, 0, pad_top + gh)
        c_fill_top = QColor(self.accent_color)
        c_fill_top.setAlpha(90)
        c_fill_bottom = QColor(self.accent_color)
        c_fill_bottom.setAlpha(5)
        fill_grad.setColorAt(0.0, c_fill_top)
        fill_grad.setColorAt(1.0, c_fill_bottom)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(fill_grad))
        painter.drawPath(path_area)

        # Draw glowing line
        line_pen = QPen(QColor(self.accent_color), 2.4)
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(line_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path_line)

        # Tip glowing circle
        painter.setPen(QPen(QColor(self.colors.get('bg', '#181b22')), 2.0))
        painter.setBrush(QBrush(QColor(self.accent_color).lighter(120)))
        painter.drawEllipse(last_pt, 4.5, 4.5)
