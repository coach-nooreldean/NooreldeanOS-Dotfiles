#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import subprocess
import os

class WallpaperChooserWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="تغيير الخلفية والألوان")
        
        dialog = Gtk.FileChooserDialog(
            title="اختر الخلفية ليتم تطبيقها واستخراج ألوانها",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        # فلاتر الصور
        filter_images = Gtk.FileFilter()
        filter_images.set_name("الصور")
        filter_images.add_mime_type("image/png")
        filter_images.add_mime_type("image/jpeg")
        filter_images.add_mime_type("image/jpg")
        filter_images.add_mime_type("image/webp")
        dialog.add_filter(filter_images)
        
        # نافذة معاينة الصورة
        self.preview = Gtk.Image()
        dialog.set_preview_widget(self.preview)
        dialog.connect("update-preview", self.update_preview_cb)

        # المجلد الافتراضي
        if os.path.exists(os.path.expanduser("~/Pictures")):
            dialog.set_current_folder(os.path.expanduser("~/Pictures"))
        else:
            dialog.set_current_folder(os.path.expanduser("~/"))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            dialog.destroy()
            self.set_wallpaper(filename)
        else:
            dialog.destroy()
            Gtk.main_quit()

    def update_preview_cb(self, dialog):
        filename = dialog.get_preview_filename()
        try:
            if filename and os.path.isfile(filename):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename, 250, 250, True)
                self.preview.set_from_pixbuf(pixbuf)
                dialog.set_preview_widget_active(True)
            else:
                dialog.set_preview_widget_active(False)
        except Exception:
            dialog.set_preview_widget_active(False)

    def set_wallpaper(self, filepath):
        script_path = os.path.expanduser("~/.config/hypr/scripts/set_wallpaper.sh")
        subprocess.Popen([script_path, filepath])
        Gtk.main_quit()

if __name__ == "__main__":
    win = WallpaperChooserWindow()
    Gtk.main()
