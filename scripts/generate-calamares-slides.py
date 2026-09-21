#!/usr/bin/env python3
"""
Generate NooreldeanOS Calamares Slideshow & Branding Artwork
Dimensions: 680x320 for slide banners, 128x128 for logo, 400x500 for welcome sidebar
"""

import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def get_fonts():
    fonts = {}
    try:
        fonts['bold_large'] = ImageFont.truetype("/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf", 26)
        fonts['bold_mid'] = ImageFont.truetype("/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf", 18)
        fonts['regular'] = ImageFont.truetype("/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf", 13)
        fonts['code'] = ImageFont.truetype("/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Medium.ttf", 12)
    except Exception:
        fallback = ImageFont.load_default()
        fonts['bold_large'] = fallback
        fonts['bold_mid'] = fallback
        fonts['regular'] = fallback
        fonts['code'] = fallback
    return fonts

def create_base_canvas(w=680, h=320, c_start=(15, 20, 30), c_end=(9, 11, 17)):
    img = Image.new("RGBA", (w, h), c_end)
    draw = ImageDraw.Draw(img)
    # Subtle gradient
    for y in range(h):
        ratio = y / h
        r = int(c_start[0] * (1 - ratio) + c_end[0] * ratio)
        g = int(c_start[1] * (1 - ratio) + c_end[1] * ratio)
        b = int(c_start[2] * (1 - ratio) + c_end[2] * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
    return img

def create_slide1(out_path, fonts):
    """Slide 1: Welcome & Zen Kernel."""
    w, h = 680, 320
    img = create_base_canvas(w, h, (18, 26, 44), (10, 12, 18))
    draw = ImageDraw.Draw(img)

    # Ambient glow on the right
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([460, 60, 620, 220], fill=(0, 242, 254, 45))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=40))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Decorative Badge
    draw.rounded_rectangle([44, 40, 200, 68], radius=6, fill=(0, 242, 254, 30), outline=(0, 242, 254, 180), width=1)
    draw.text((58, 47), "★ ARCH LINUX BASED", font=fonts['code'], fill=(0, 242, 254, 255))

    # Title & Subtitle
    draw.text((44, 88), "NooreldeanOS", font=fonts['bold_large'], fill=(255, 255, 255, 255))
    draw.text((44, 125), "Next-Generation Arch Linux Experience", font=fonts['bold_mid'], fill=(125, 211, 252, 255))
    draw.text((44, 160), "مرحباً بك في نظام لينكس فائق السرعة والمصمم لرفع إنتاجيتك إلى أقصى حد.", font=fonts['regular'], fill=(203, 213, 225, 240))
    draw.text((44, 185), "مزود بنواة linux-zen المهيأة لتقليل زمن الاستجابة ومنحك تجربة خالية من التقطيع.", font=fonts['regular'], fill=(148, 163, 184, 220))

    # Feature tags
    tags = ["✦ linux-zen Kernel", "✦ Zstd Compression", "✦ ZRAM Enabled", "✦ Calamares Installer"]
    for i, tag in enumerate(tags):
        tx = 44 + (i % 2) * 190
        ty = 225 + (i // 2) * 32
        draw.rounded_rectangle([tx, ty, tx + 175, ty + 26], radius=5, fill=(30, 41, 59, 180), outline=(56, 189, 248, 100), width=1)
        draw.text((tx + 12, ty + 6), tag, font=fonts['code'], fill=(224, 242, 254, 255))

    # Right Icon (Hexagon Emblem)
    cx, cy = 540, 140
    r = 55
    hex_pts = [(cx + r * math.cos(math.radians(60*i - 30)), cy + r * math.sin(math.radians(60*i - 30))) for i in range(6)]
    draw.polygon(hex_pts, outline=(0, 242, 254, 220), width=3)
    draw.line([(cx - 20, cy - 28), (cx - 20, cy + 28)], fill=(79, 172, 254, 255), width=5)
    draw.line([(cx + 20, cy - 28), (cx + 20, cy + 28)], fill=(0, 242, 254, 255), width=5)
    draw.line([(cx - 20, cy - 28), (cx + 20, cy + 28)], fill=(168, 85, 247, 255), width=5)

    img.save(out_path, "PNG")
    print(f"[✔] Slide 1 generated: {out_path}")

def create_slide2(out_path, fonts):
    """Slide 2: Hyprland & Pywal Dynamic Aesthetics."""
    w, h = 680, 320
    img = create_base_canvas(w, h, (30, 18, 42), (12, 10, 18))
    draw = ImageDraw.Draw(img)

    # Ambient glow on the right
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([460, 60, 620, 220], fill=(168, 85, 247, 50))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=40))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([44, 40, 220, 68], radius=6, fill=(168, 85, 247, 30), outline=(168, 85, 247, 180), width=1)
    draw.text((58, 47), "❖ HYPRLAND & PYWAL", font=fonts['code'], fill=(216, 180, 254, 255))

    draw.text((44, 88), "Dynamic Aesthetics", font=fonts['bold_large'], fill=(255, 255, 255, 255))
    draw.text((44, 125), "سحر الألوان التفاعلية وسلاسة Wayland", font=fonts['bold_mid'], fill=(244, 114, 182, 255))
    draw.text((44, 160), "محرك Pywal الذكي يقرأ ألوان أي خلفية تختارها في جزء من الثانية.", font=fonts['regular'], fill=(203, 213, 225, 240))
    draw.text((44, 185), "تنسيق شامل بين النوافذ، الشريط العلوي، مركز الإشعارات، والطرفية.", font=fonts['regular'], fill=(148, 163, 184, 220))

    tags = ["✦ Smooth Animations", "✦ Catppuccin Accents", "✦ 30+ 4K Wallpapers", "✦ Glassmorphism Blur"]
    for i, tag in enumerate(tags):
        tx = 44 + (i % 2) * 190
        ty = 225 + (i // 2) * 32
        draw.rounded_rectangle([tx, ty, tx + 175, ty + 26], radius=5, fill=(30, 41, 59, 180), outline=(216, 180, 254, 100), width=1)
        draw.text((tx + 12, ty + 6), tag, font=fonts['code'], fill=(245, 208, 254, 255))

    # Visual representation of color palette swatches
    cx, cy = 540, 140
    colors = [(239, 68, 68), (249, 115, 22), (234, 179, 8), (34, 197, 94), (6, 182, 212), (59, 130, 246), (168, 85, 247)]
    for i, c in enumerate(colors):
        sx = cx - 60 + (i % 4) * 32
        sy = cy - 30 + (i // 4) * 35
        draw.rounded_rectangle([sx, sy, sx + 24, sy + 24], radius=6, fill=c, outline=(255, 255, 255, 180), width=1)

    img.save(out_path, "PNG")
    print(f"[✔] Slide 2 generated: {out_path}")

def create_slide3(out_path, fonts):
    """Slide 3: PipeWire Audio & SwayNC Notification Center."""
    w, h = 680, 320
    img = create_base_canvas(w, h, (16, 32, 38), (9, 16, 20))
    draw = ImageDraw.Draw(img)

    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([460, 60, 620, 220], fill=(16, 185, 129, 45))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=40))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([44, 40, 220, 68], radius=6, fill=(16, 185, 129, 30), outline=(16, 185, 129, 180), width=1)
    draw.text((58, 47), "♫ PIPEWIRE & SWAYNC", font=fonts['code'], fill=(110, 231, 183, 255))

    draw.text((44, 88), "Pro Audio & Controls", font=fonts['bold_large'], fill=(255, 255, 255, 255))
    draw.text((44, 125), "هندسة الصوت الاحترافية ومركز الإشعارات", font=fonts['bold_mid'], fill=(52, 211, 153, 255))
    draw.text((44, 160), "تحكم فوري في مخارج الصوت وسماعات البلوتوث عبر اختصار Super + A.", font=fonts['regular'], fill=(203, 213, 225, 240))
    draw.text((44, 185), "مركز إشعارات SwayNC متطور مع سلايدرز الصوت والإضاءة ونغمات تنبيه هادئة.", font=fonts['regular'], fill=(148, 163, 184, 220))

    tags = ["✦ Super + A Switcher", "✦ 6-Button Quick Grid", "✦ PipeWire Low-Latency", "✦ Audio Chimes"]
    for i, tag in enumerate(tags):
        tx = 44 + (i % 2) * 190
        ty = 225 + (i // 2) * 32
        draw.rounded_rectangle([tx, ty, tx + 175, ty + 26], radius=5, fill=(30, 41, 59, 180), outline=(52, 211, 153, 100), width=1)
        draw.text((tx + 12, ty + 6), tag, font=fonts['code'], fill=(209, 250, 229, 255))

    # Audio Waveform Graphics
    cx, cy = 540, 140
    bars = [15, 32, 50, 24, 45, 60, 38, 55, 20, 42, 18]
    for i, bh in enumerate(bars):
        bx = cx - 55 + i * 11
        draw.rounded_rectangle([bx, cy - bh // 2, bx + 6, cy + bh // 2], radius=3, fill=(52, 211, 153, 240))

    img.save(out_path, "PNG")
    print(f"[✔] Slide 3 generated: {out_path}")

def create_slide4(out_path, fonts):
    """Slide 4: Developer & Productivity Tools."""
    w, h = 680, 320
    img = create_base_canvas(w, h, (35, 25, 15), (16, 12, 9))
    draw = ImageDraw.Draw(img)

    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([460, 60, 620, 220], fill=(245, 158, 11, 45))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=40))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([44, 40, 220, 68], radius=6, fill=(245, 158, 11, 30), outline=(245, 158, 11, 180), width=1)
    draw.text((58, 47), "⚡ DEVELOPER WORKFLOW", font=fonts['code'], fill=(252, 211, 77, 255))

    draw.text((44, 88), "Peak Productivity", font=fonts['bold_large'], fill=(255, 255, 255, 255))
    draw.text((44, 125), "أقصى كفاءة للمطورين وصناع المحتوى", font=fonts['bold_mid'], fill=(251, 191, 36, 255))
    draw.text((44, 160), "طرفية Kitty فائقة السرعة مع برومبت Starship الذكي وأداة Yazi.", font=fonts['regular'], fill=(203, 213, 225, 240))
    draw.text((44, 185), "أداة sys-clean لصيانة الكاش التلقائية وحذف الحزم المهملة بضغطة زر.", font=fonts['regular'], fill=(148, 163, 184, 220))

    tags = ["✦ Super + Return Kitty", "✦ Super + R Rofi Run", "✦ sys-clean Optimizer", "✦ Git & Fastfetch"]
    for i, tag in enumerate(tags):
        tx = 44 + (i % 2) * 190
        ty = 225 + (i // 2) * 32
        draw.rounded_rectangle([tx, ty, tx + 175, ty + 26], radius=5, fill=(30, 41, 59, 180), outline=(251, 191, 36, 100), width=1)
        draw.text((tx + 12, ty + 6), tag, font=fonts['code'], fill=(254, 243, 199, 255))

    # Mini Terminal Box
    cx, cy = 540, 140
    draw.rounded_rectangle([cx - 65, cy - 45, cx + 65, cy + 45], radius=6, fill=(15, 23, 42, 240), outline=(245, 158, 11, 180), width=1)
    # Traffic lights
    draw.ellipse([cx - 55, cy - 35, cx - 47, cy - 27], fill=(239, 68, 68, 255))
    draw.ellipse([cx - 42, cy - 35, cx - 34, cy - 27], fill=(245, 158, 11, 255))
    draw.ellipse([cx - 29, cy - 35, cx - 21, cy - 27], fill=(34, 197, 94, 255))
    draw.text((cx - 55, cy - 10), "➜ sys-clean", font=fonts['code'], fill=(56, 189, 248, 255))
    draw.text((cx - 55, cy + 8), "[✔] Cleaned!", font=fonts['code'], fill=(74, 222, 128, 255))

    img.save(out_path, "PNG")
    print(f"[✔] Slide 4 generated: {out_path}")

def create_branding_assets(target_dir):
    """Generate logo.png and welcome.png for Calamares."""
    # Logo: 128x128
    logo = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    ld = ImageDraw.Draw(logo)
    cx, cy = 64, 64
    r = 46
    hex_pts = [(cx + r * math.cos(math.radians(60*i - 30)), cy + r * math.sin(math.radians(60*i - 30))) for i in range(6)]
    ld.polygon(hex_pts, outline=(0, 242, 254, 255), width=3)
    ld.line([(cx - 16, cy - 22), (cx - 16, cy + 22)], fill=(79, 172, 254, 255), width=4)
    ld.line([(cx + 16, cy - 22), (cx + 16, cy + 22)], fill=(0, 242, 254, 255), width=4)
    ld.line([(cx - 16, cy - 22), (cx + 16, cy + 22)], fill=(168, 85, 247, 255), width=4)
    logo.save(os.path.join(target_dir, "logo.png"))
    print(f"[✔] Calamares logo generated: {os.path.join(target_dir, 'logo.png')}")

    # Welcome banner (240x480)
    w_banner = Image.new("RGBA", (240, 480), (15, 17, 24, 255))
    wd = ImageDraw.Draw(w_banner)
    wd.rectangle([0, 0, 239, 479], fill=(13, 16, 23, 255))
    # Glowing top emblem
    ecx, ecy = 120, 100
    er = 42
    pts = [(ecx + er * math.cos(math.radians(60*i - 30)), ecy + er * math.sin(math.radians(60*i - 30))) for i in range(6)]
    wd.polygon(pts, outline=(0, 242, 254, 220), width=3)
    wd.line([(ecx - 14, ecy - 18), (ecx - 14, ecy + 18)], fill=(79, 172, 254, 255), width=4)
    wd.line([(ecx + 14, ecy - 18), (ecx + 14, ecy + 18)], fill=(0, 242, 254, 255), width=4)
    wd.line([(ecx - 14, ecy - 18), (ecx + 14, ecy + 18)], fill=(168, 85, 247, 255), width=4)
    w_banner.save(os.path.join(target_dir, "welcome.png"))
    print(f"[✔] Calamares welcome banner generated: {os.path.join(target_dir, 'welcome.png')}")

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "./branding"
    os.makedirs(target_dir, exist_ok=True)
    fonts = get_fonts()

    create_branding_assets(target_dir)
    create_slide1(os.path.join(target_dir, "slide1_welcome.png"), fonts)
    create_slide2(os.path.join(target_dir, "slide2_hyprland.png"), fonts)
    create_slide3(os.path.join(target_dir, "slide3_audio.png"), fonts)
    create_slide4(os.path.join(target_dir, "slide4_dev.png"), fonts)
    print("\n[🎉] All Calamares Slide & Branding Assets created successfully!")

if __name__ == "__main__":
    main()
