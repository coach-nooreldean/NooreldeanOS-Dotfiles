import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QRadioButton, QButtonGroup, 
    QProgressBar, QTextEdit, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDir
from converter import convert_video, get_convertible_files

class ConverterThread(QThread):
    file_progress_update = pyqtSignal(int)
    total_progress_update = pyqtSignal(int)
    log_update = pyqtSignal(str)
    finished = pyqtSignal(bool)
    
    def __init__(self, mode, input_type, path):
        super().__init__()
        self.mode = mode # 'mp4_to_mov' or 'mov_to_mp4'
        self.input_type = input_type # 'file' or 'folder'
        self.path = path
        
    def run(self):
        try:
            if self.mode == 'mp4_to_mov_linux':
                from_format = 'mp4'
                to_format = 'mov'
                codec_mode = 'dnxhr'
            elif self.mode == 'mp4_to_mov_mpeg4':
                from_format = 'mp4'
                to_format = 'mov'
                codec_mode = 'mpeg4'
            elif self.mode == 'mov_to_mp4_h264':
                from_format = 'mov'
                to_format = 'mp4'
                codec_mode = 'h264'
            else:
                from_format = 'mov'
                to_format = 'mp4'
                codec_mode = 'copy'
            
            
            def progress_callback(percent):
                self.file_progress_update.emit(percent)
                
            if self.input_type == 'file':
                self.log_update.emit(f"جاري تحويل الملف: {self.path}")
                self.total_progress_update.emit(0)
                
                output_path = convert_video(self.path, to_format, progress_callback, codec_mode=codec_mode)
                
                self.file_progress_update.emit(100)
                self.total_progress_update.emit(100)
                self.log_update.emit(f"✅ تم التحويل بنجاح:\n{output_path}\n")
            else:
                files = get_convertible_files(self.path, from_format)
                if not files:
                    self.log_update.emit(f"لم يتم العثور على ملفات بصيغة {from_format} في المجلد.")
                    self.finished.emit(False)
                    return
                
                total = len(files)
                self.log_update.emit(f"تم العثور على {total} ملفات. جاري بدء التحويل...")
                self.total_progress_update.emit(0)
                
                for i, file in enumerate(files):
                    self.log_update.emit(f"جاري تحويل: {file.name}...")
                    self.file_progress_update.emit(0)
                    
                    try:
                        output_path = convert_video(file, to_format, progress_callback, codec_mode=codec_mode)
                        self.log_update.emit(f"✅ اكتمل: {Path(output_path).name}")
                        self.file_progress_update.emit(100)
                    except Exception as e:
                        self.log_update.emit(f"⚠️ خطأ في {file.name}: {str(e)}")
                        self.file_progress_update.emit(0)
                    
                    # Update total progress
                    progress = int(((i + 1) / total) * 100)
                    self.total_progress_update.emit(progress)
                    
                self.log_update.emit("\n🎉 تم الانتهاء من جميع الملفات بنجاح!")
            
            self.finished.emit(True)
        except Exception as e:
            self.log_update.emit(f"❌ حدث خطأ:\n{str(e)}")
            self.finished.emit(False)


class VideoConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("محول صيغ الفيديو السريع (MP4 <-> MOV)")
        self.setMinimumSize(650, 600)
        
        # Set RTL direction for Arabic UI
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        self.init_ui()
        self.selected_path = None
        
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 1. Conversion Mode Selection
        mode_group = QGroupBox("نوع التحويل")
        mode_layout = QVBoxLayout()
        self.radio_mp4_to_mov_linux = QRadioButton("من MP4 إلى MOV (لدافنشي لينكس - DNxHR) [يحافظ على الجودة - بطيء وحجم كبير]")
        self.radio_mp4_to_mov_mpeg4 = QRadioButton("من MP4 إلى MOV (لدافنشي لينكس - MPEG-4) [سريع وحجمه أصغر - جودة أقل قليلاً]")
        self.radio_mov_to_mp4 = QRadioButton("من MOV إلى MP4 (نسخ الحاوية سريعاً - لا يدعم ProRes)")
        self.radio_mov_to_mp4_h264 = QRadioButton("من MOV إلى MP4 (إلى كوديك H.264 - متوافق كلياً مع جميع الأجهزة)")
        self.radio_mp4_to_mov_linux.setChecked(True)
        
        mode_layout.addWidget(self.radio_mp4_to_mov_linux)
        mode_layout.addWidget(self.radio_mp4_to_mov_mpeg4)
        mode_layout.addWidget(self.radio_mov_to_mp4)
        mode_layout.addWidget(self.radio_mov_to_mp4_h264)
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # 2. Input Type Selection
        input_type_group = QGroupBox("طريقة التحديد")
        input_type_layout = QHBoxLayout()
        self.radio_single_file = QRadioButton("ملف واحد")
        self.radio_folder = QRadioButton("مجلد كامل")
        self.radio_single_file.setChecked(True)
        
        input_type_layout.addWidget(self.radio_single_file)
        input_type_layout.addWidget(self.radio_folder)
        input_type_group.setLayout(input_type_layout)
        layout.addWidget(input_type_group)
        
        # 3. File/Folder Selection
        selection_layout = QHBoxLayout()
        self.btn_browse = QPushButton("استعراض...")
        self.btn_browse.setMinimumHeight(40)
        self.btn_browse.clicked.connect(self.browse)
        
        self.lbl_path = QLabel("لم يتم تحديد شيء بعد")
        self.lbl_path.setWordWrap(True)
        self.lbl_path.setStyleSheet("color: #666; font-style: italic;")
        
        selection_layout.addWidget(self.btn_browse)
        selection_layout.addWidget(self.lbl_path, stretch=1)
        layout.addLayout(selection_layout)
        
        # 4. Progress Bars
        progress_group = QGroupBox("التقدم")
        progress_layout = QVBoxLayout()
        
        lbl_file = QLabel("تقدم الفيديو الحالي:")
        self.file_progress_bar = QProgressBar()
        self.file_progress_bar.setValue(0)
        self.file_progress_bar.setTextVisible(True)
        
        lbl_total = QLabel("التقدم الإجمالي:")
        self.total_progress_bar = QProgressBar()
        self.total_progress_bar.setValue(0)
        self.total_progress_bar.setTextVisible(True)
        
        progress_layout.addWidget(lbl_file)
        progress_layout.addWidget(self.file_progress_bar)
        progress_layout.addWidget(lbl_total)
        progress_layout.addWidget(self.total_progress_bar)
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 5. Convert Button
        self.btn_convert = QPushButton("بدء التحويل السريع")
        self.btn_convert.setMinimumHeight(50)
        self.btn_convert.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        self.btn_convert.clicked.connect(self.start_conversion)
        layout.addWidget(self.btn_convert)
        
        # 6. Log Console
        log_label = QLabel("سجل العمليات:")
        layout.addWidget(log_label)
        
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        # Force text color to black and background to white for high contrast
        self.text_log.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff; 
                color: #000000; 
                font-family: monospace;
                border: 1px solid #cccccc;
            }
        """)
        layout.addWidget(self.text_log)

    def log(self, message):
        self.text_log.append(message)
        # Scroll to bottom
        scrollbar = self.text_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def browse(self):
        is_file_mode = self.radio_single_file.isChecked()
        is_mp4_to_mov = self.radio_mp4_to_mov_linux.isChecked() or self.radio_mp4_to_mov_mpeg4.isChecked()
        
        filter_str = "MP4 Files (*.mp4)" if is_mp4_to_mov else "MOV Files (*.mov)"
        
        if is_file_mode:
            path, _ = QFileDialog.getOpenFileName(
                self, 
                "اختر ملف الفيديو", 
                QDir.homePath(),
                f"Video Files ({'*.mp4' if is_mp4_to_mov else '*.mov'});;All Files (*)"
            )
        else:
            path = QFileDialog.getExistingDirectory(
                self,
                "اختر المجلد",
                QDir.homePath()
            )
            
        if path:
            self.selected_path = path
            self.lbl_path.setText(path)
            self.lbl_path.setStyleSheet("color: black;")
            
            if not is_file_mode:
                from_format = 'mp4' if is_mp4_to_mov else 'mov'
                files = get_convertible_files(path, from_format)
                self.log(f"تم تحديد المجلد. يحتوي على {len(files)} ملف بصيغة {from_format}.")

    def start_conversion(self):
        if not self.selected_path:
            QMessageBox.warning(self, "تنبيه", "الرجاء تحديد ملف أو مجلد أولاً.")
            return
            
        # Verify if path still exists
        if not os.path.exists(self.selected_path):
            QMessageBox.critical(self, "خطأ", "المسار المحدد لم يعد موجوداً.")
            self.selected_path = None
            self.lbl_path.setText("لم يتم تحديد شيء بعد")
            return
            
        self.btn_convert.setEnabled(False)
        self.btn_browse.setEnabled(False)
        self.file_progress_bar.setValue(0)
        self.total_progress_bar.setValue(0)
        self.text_log.clear()
        
        if self.radio_mp4_to_mov_linux.isChecked():
            mode = 'mp4_to_mov_linux'
            self.log("جاري بدء التحويل باستخدام كوديك DNxHR (قد يستغرق بعض الوقت، وسيكون حجم الملف كبيراً)...")
        elif self.radio_mp4_to_mov_mpeg4.isChecked():
            mode = 'mp4_to_mov_mpeg4'
            self.log("جاري بدء التحويل السريع باستخدام كوديك MPEG-4 (حجم أصغر)...")
        elif self.radio_mov_to_mp4_h264.isChecked():
            mode = 'mov_to_mp4_h264'
            self.log("جاري بدء تحويل الكوديك إلى H.264 (قد يستغرق وقتاً أطول، لكنه متوافق كلياً)...")
        else:
            mode = 'mov_to_mp4'
            self.log("جاري بدء التحويل السريع (تغيير الحاوية فقط)...")
            
        input_type = 'file' if self.radio_single_file.isChecked() else 'folder'
        
        self.thread = ConverterThread(mode, input_type, self.selected_path)
        self.thread.file_progress_update.connect(self.file_progress_bar.setValue)
        self.thread.total_progress_update.connect(self.total_progress_bar.setValue)
        self.thread.log_update.connect(self.log)
        self.thread.finished.connect(self.conversion_finished)
        self.thread.start()
        
    def conversion_finished(self, success):
        self.btn_convert.setEnabled(True)
        self.btn_browse.setEnabled(True)
        if success:
            QMessageBox.information(self, "نجاح", "تمت عملية التحويل بنجاح!")
        else:
            QMessageBox.critical(self, "فشل", "حدثت مشكلة أثناء التحويل. راجع السجل.")

def main():
    app = QApplication(sys.argv)
    
    # Set default font for better Arabic rendering
    font = app.font()
    font.setPointSize(11)
    app.setFont(font)
    
    window = VideoConverterApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
