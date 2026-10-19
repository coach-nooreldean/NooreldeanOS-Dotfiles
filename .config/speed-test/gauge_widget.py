#!/usr/bin/env python3
"""
Dynamic Speedometer Gauge Widget for NooreldeanOS Speed Test.
Features smooth 60 FPS easing animations, adaptive scale, antialiased gradients,
glowing needle and arc pointer, and high-DPI crystal clear typography.
"""

import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, 
    QLinearGradient, QRadialGradient, QPainterPath
)

class CircularGaugeWidget(QWidget):
    def __init__(self, parent=None, colors=None):
        super().__init__(parent)
        self.setMinimumSize(280, 280)
        self.colors = colors or {
            'bg': '#181b22',
            'fg': '#cdd6f4',
            'primary': '#38bdf8',
            'hover': '#818cf8',
            'surface': '#222733',
            'border': '#333b4d',
            'danger': '#f43f5e'
        }

        # Animated values
        self._target_value = 0.0
        self._current_value = 0.0
        self._max_scale = 100.0
        self._unit = "Mbps"
        self._phase_text = "جاهز للبدء"
        self._phase_sub = "READY"
        self._phase_color = self.colors['primary']

        # 60 FPS animation timer
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._animate_step)
        self._timer.start()

    def update_colors(self, colors):
        self.colors = colors
        self._phase_color = colors.get('primary', '#38bdf8')
        self.update()

    def set_speed(self, speed_mbps):
        self._target_value = max(0.0, float(speed_mbps))
        # Dynamically adjust max scale
        if self._target_value > 1000:
            self._max_scale = 2000.0
        elif self._target_value > 500:
            self._max_scale = 1000.0
        elif self._target_value > 250:
            self._max_scale = 500.0
        elif self._target_value > 100:
            self._max_scale = 250.0
        else:
            self._max_scale = 100.0

    def set_phase(self, ar_text, en_text, color=None, unit="Mbps"):
        self._phase_text = ar_text
        self._phase_sub = en_text
        self._unit = unit
        if color:
            self._phase_color = color
        else:
            self._phase_color = self.colors.get('primary', '#38bdf8')
        self.update()

    def reset(self):
        self._target_value = 0.0
        self._current_value = 0.0
        self._max_scale = 100.0
        self._phase_text = "جاهز للبدء"
        self._phase_sub = "READY"
        self._phase_color = self.colors.get('primary', '#38bdf8')
        self.update()

    def _animate_step(self):
        diff = self._target_value - self._current_value
        if abs(diff) > 0.05:
            # Smooth spring-like lerp
            self._current_value += diff * 0.12
            self.update()
        elif abs(diff) > 0.0:
            self._current_value = self._target_value
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = self.width()
        h = self.height()
        side = min(w, h)
        cx = w / 2.0
        cy = h / 2.0 + 10.0

        # Radius definitions
        radius = side * 0.40
        track_width = max(10.0, side * 0.055)
        rect = QRectF(cx - radius, cy - radius, radius * 2.0, radius * 2.0)

        # Base track (240 degree sweep from 210 deg counter-clockwise by -240 deg)
        # In Qt: 210 deg is bottom-left, -240 deg sweeps clockwise to -30 deg (bottom-right)
        track_pen = QPen(QColor(self.colors.get('surface', '#222733')))
        track_pen.setWidthF(track_width)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, int(210 * 16), int(-240 * 16))

        # Active progress arc
        frac = min(1.0, max(0.0, self._current_value / self._max_scale)) if self._max_scale > 0 else 0.0
        active_span = int(-240 * frac * 16)

        if abs(active_span) > 16:
            # Create colorful gradient for active arc
            grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
            c_start = QColor(self.colors.get('primary', '#38bdf8'))
            c_end = QColor(self._phase_color)
            grad.setColorAt(0.0, c_start)
            grad.setColorAt(1.0, c_end)

            active_pen = QPen(QBrush(grad), track_width)
            active_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(active_pen)
            painter.drawArc(rect, int(210 * 16), active_span)

        # Scale tick marks and numbers
        painter.save()
        num_ticks = 10
        tick_radius_outer = radius - track_width / 2.0 - 6.0
        tick_radius_inner = tick_radius_outer - 8.0
        text_radius = tick_radius_inner - 14.0

        font_ticks = QFont("Inter", max(8, int(side * 0.03)), QFont.Weight.Medium)
        painter.setFont(font_ticks)

        for i in range(num_ticks + 1):
            t_frac = i / float(num_ticks)
            # Angle: 150 deg (left) to 390 deg (right)
            angle_deg = 150.0 + t_frac * 240.0
            angle_rad = math.radians(angle_deg)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Tick lines
            p_outer = QPointF(cx + tick_radius_outer * cos_a, cy + tick_radius_outer * sin_a)
            p_inner = QPointF(cx + tick_radius_inner * cos_a, cy + tick_radius_inner * sin_a)

            is_major = (i % 2 == 0)
            t_color = QColor(self.colors.get('border', '#4c566a')) if not is_major else QColor(self.colors.get('fg', '#cdd6f4'))
            t_pen = QPen(t_color, 2.0 if is_major else 1.2)
            painter.setPen(t_pen)
            painter.drawLine(p_outer, p_inner)

            # Major tick label
            if is_major:
                val = int(round(t_frac * self._max_scale))
                val_str = str(val)
                tx = cx + text_radius * cos_a
                ty = cy + text_radius * sin_a
                painter.setPen(QColor(self.colors.get('fg', '#cdd6f4')).lighter(80))
                painter.drawText(QRectF(tx - 20, ty - 10, 40, 20), Qt.AlignmentFlag.AlignCenter, val_str)

        painter.restore()

        # Needle & Pointer Glow
        painter.save()
        current_deg = 150.0 + frac * 240.0
        current_rad = math.radians(current_deg)
        needle_len = radius - track_width / 2.0 - 10.0
        needle_x = cx + needle_len * math.cos(current_rad)
        needle_y = cy + needle_len * math.sin(current_rad)

        # Arc tip glowing dot
        tip_x = cx + radius * math.cos(current_rad)
        tip_y = cy + radius * math.sin(current_rad)
        glow_rad = track_width * 0.9

        glow_brush = QRadialGradient(tip_x, tip_y, glow_rad)
        glow_brush.setColorAt(0.0, QColor(self._phase_color).lighter(140))
        glow_brush.setColorAt(0.6, QColor(self._phase_color))
        glow_brush.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow_brush))
        painter.drawEllipse(QPointF(tip_x, tip_y), glow_rad, glow_rad)

        # Draw needle line
        needle_pen = QPen(QColor(self.colors.get('danger', '#f43f5e')), 3.0)
        needle_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(needle_pen)
        painter.drawLine(QPointF(cx, cy), QPointF(needle_x, needle_y))

        # Center metallic hub
        hub_outer = max(14.0, side * 0.065)
        hub_inner = hub_outer * 0.45
        painter.setPen(QPen(QColor(self.colors.get('border', '#333b4d')), 2.0))
        painter.setBrush(QBrush(QColor(self.colors.get('surface', '#222733'))))
        painter.drawEllipse(QPointF(cx, cy), hub_outer, hub_outer)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(self.colors.get('danger', '#f43f5e'))))
        painter.drawEllipse(QPointF(cx, cy), hub_inner, hub_inner)
        painter.restore()

        # Center Text (Big Speed Readout + Unit + Phase Pill)
        painter.save()
        # 1. Speed Number
        speed_font_size = max(24, int(side * 0.125))
        speed_font = QFont("Inter", speed_font_size, QFont.Weight.Bold)
        painter.setFont(speed_font)
        painter.setPen(QColor(self.colors.get('fg', '#ffffff')))

        val_display = f"{self._current_value:.1f}"
        text_y_center = cy + side * 0.08
        painter.drawText(QRectF(cx - 100, text_y_center - 35, 200, 45), Qt.AlignmentFlag.AlignCenter, val_display)

        # 2. Unit label (Mbps / ms)
        unit_font = QFont("JetBrainsMono Nerd Font", max(11, int(side * 0.045)), QFont.Weight.DemiBold)
        painter.setFont(unit_font)
        painter.setPen(QColor(self._phase_color))
        painter.drawText(QRectF(cx - 60, text_y_center + 12, 120, 22), Qt.AlignmentFlag.AlignCenter, self._unit)

        # 3. Phase Badge (Pill)
        pill_w = max(110.0, side * 0.44)
        pill_h = 24.0
        pill_rect = QRectF(cx - pill_w / 2.0, text_y_center + 38, pill_w, pill_h)

        bg_badge = QColor(self.colors.get('surface', '#222733'))
        bg_badge.setAlpha(220)
        border_badge = QColor(self._phase_color)
        border_badge.setAlpha(120)

        painter.setPen(QPen(border_badge, 1.2))
        painter.setBrush(QBrush(bg_badge))
        painter.drawRoundedRect(pill_rect, 12.0, 12.0)

        badge_font = QFont("Inter", max(9, int(side * 0.033)), QFont.Weight.Bold)
        painter.setFont(badge_font)
        painter.setPen(QColor(self.colors.get('fg', '#cdd6f4')))
        painter.drawText(pill_rect, Qt.AlignmentFlag.AlignCenter, f"{self._phase_text}  •  {self._phase_sub}")

        painter.restore()
