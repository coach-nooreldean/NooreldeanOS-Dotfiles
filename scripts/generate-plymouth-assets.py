#!/usr/bin/env python3
"""
Generate NooreldeanOS Ultra-Modern Minimalist Dark Glow Plymouth Boot Splash Assets
Creates:
  - logo.png (emblem + glowing typography)
  - animation-0001.png ... animation-0030.png (glowing rotary spinner)
  - background.png (deep dark subtle gradient)
  - box.png, bullet.png, entry.png, lock.png (password & dialog assets)
"""

import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_radial_gradient(width, height, center_color, edge_color):
    """Generate high-fidelity radial background."""
    img = Image.new("RGBA", (width, height), edge_color)
    draw = ImageDraw.Draw(img)
    max_radius = math.hypot(width / 2, height / 2)
    cx, cy = width / 2, height / 2

    # Draw concentric ellipses with interpolated color
    steps = 120
    for i in range(steps, 0, -1):
        ratio = i / steps
        r = max_radius * ratio
        # interpolate colors
        r_c = int(edge_color[0] * ratio + center_color[0] * (1 - ratio))
        g_c = int(edge_color[1] * ratio + center_color[1] * (1 - ratio))
        b_c = int(edge_color[2] * ratio + center_color[2] * (1 - ratio))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(r_c, g_c, b_c, 255))
    return img

def create_logo(output_path):
    """Create the central glowing emblem and typography."""
    size = 400
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, (size // 2) - 30

    # Draw glowing halo behind logo
    halo = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo)
    halo_draw.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], fill=(0, 229, 255, 60))
    halo = halo.filter(ImageFilter.GaussianBlur(radius=25))
    img = Image.alpha_composite(img, halo)
    draw = ImageDraw.Draw(img)

    # Outer polygon (hexagon)
    hex_radius = 65
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        px = cx + hex_radius * math.cos(angle)
        py = cy + hex_radius * math.sin(angle)
        points.append((px, py))
    
    # Glow outline
    draw.polygon(points, outline=(0, 242, 254, 230), width=4)

    # Inner "N" monogram with modern geometric cuts
    n_w = 42
    n_h = 56
    left = cx - n_w // 2
    right = cx + n_w // 2
    top = cy - n_h // 2
    bottom = cy + n_h // 2

    # Left vertical stem
    draw.line([(left, top), (left, bottom)], fill=(79, 172, 254, 255), width=7)
    # Right vertical stem
    draw.line([(right, top), (right, bottom)], fill=(0, 242, 254, 255), width=7)
    # Diagonal stem
    draw.line([(left, top), (right, bottom)], fill=(168, 85, 247, 255), width=7)

    # Core accent dot
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 255, 255, 255))

    # Text: "NOORELDEAN OS"
    # Fallback to default font or system font
    font = None
    try:
        font = ImageFont.truetype("/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Bold.ttf", 20)
    except Exception:
        try:
            font = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Bold.ttf", 20)
        except Exception:
            font = ImageFont.load_default()

    text = "NOORELDEAN OS"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size - tw) // 2
    ty = cy + hex_radius + 35

    # Subtitle shadow/glow
    draw.text((tx, ty), text, font=font, fill=(0, 242, 254, 200))

    # Subtext: "NEXT-GEN HYPRLAND LINUX"
    sub_font = None
    try:
        sub_font = ImageFont.truetype("/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf", 10)
    except Exception:
        sub_font = font

    sub_text = "HYPRLAND • ZEN KERNEL"
    s_bbox = draw.textbbox((0, 0), sub_text, font=sub_font)
    st_w = s_bbox[2] - s_bbox[0]
    st_x = (size - st_w) // 2
    draw.text((st_x, ty + th + 10), sub_text, font=sub_font, fill=(148, 163, 184, 180))

    img.save(output_path, "PNG")
    print(f"[✔] Logo generated: {output_path}")

def create_spinner_frames(output_dir, num_frames=30):
    """Create smooth 360-degree rotating glowing arc frames."""
    size = 96
    cx, cy = size // 2, size // 2
    radius = 32

    for frame in range(num_frames):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background faint track
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                     outline=(255, 255, 255, 25), width=3)

        # Animated arc
        angle_start = (frame * (360 / num_frames))
        angle_extent = 110
        angle_end = angle_start + angle_extent

        # Draw glowing blurred arc
        glow_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        glow_draw.arc([cx - radius, cy - radius, cx + radius, cy + radius],
                      start=angle_start, end=angle_end, fill=(0, 242, 254, 180), width=6)
        glow_img = glow_img.filter(ImageFilter.GaussianBlur(radius=3))
        img = Image.alpha_composite(img, glow_img)

        # Sharp foreground arc
        draw = ImageDraw.Draw(img)
        draw.arc([cx - radius, cy - radius, cx + radius, cy + radius],
                 start=angle_start, end=angle_end, fill=(79, 172, 254, 255), width=3)

        # Leading bright dot
        lead_rad = math.radians(angle_end)
        lead_x = cx + radius * math.cos(lead_rad)
        lead_y = cy + radius * math.sin(lead_rad)
        draw.ellipse([lead_x - 3.5, lead_y - 3.5, lead_x + 3.5, lead_y + 3.5], fill=(255, 255, 255, 255))

        # Two-step module naming convention: animation-0001.png to animation-0030.png
        filename = f"animation-{frame + 1:04d}.png"
        img.save(os.path.join(output_dir, filename), "PNG")

    print(f"[✔] Generated {num_frames} spinner animation frames in {output_dir}")

def create_dialog_assets(output_dir):
    """Generate dialog, password input and box icons for Plymouth."""
    # lock.png (16x20)
    lock = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lock)
    ld.rectangle([5, 10, 19, 21], fill=(148, 163, 184, 255), outline=(203, 213, 225, 255))
    ld.arc([7, 3, 17, 13], start=180, end=0, fill=(203, 213, 225, 255), width=2)
    lock.save(os.path.join(output_dir, "lock.png"))

    # bullet.png (password dot)
    bullet = Image.new("RGBA", (14, 14), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bullet)
    bd.ellipse([2, 2, 12, 12], fill=(0, 242, 254, 255))
    bullet.save(os.path.join(output_dir, "bullet.png"))

    # entry.png (input field line/box)
    entry = Image.new("RGBA", (260, 38), (15, 23, 42, 220))
    ed = ImageDraw.Draw(entry)
    ed.rectangle([0, 0, 259, 37], outline=(56, 189, 248, 180), width=1)
    entry.save(os.path.join(output_dir, "entry.png"))

    # box.png (message box backdrop)
    box = Image.new("RGBA", (320, 140), (15, 23, 42, 230))
    xd = ImageDraw.Draw(box)
    xd.rectangle([0, 0, 319, 139], outline=(56, 189, 248, 120), width=1)
    box.save(os.path.join(output_dir, "box.png"))

    # capslock.png
    caps = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    cd = ImageDraw.Draw(caps)
    cd.polygon([(12, 3), (4, 13), (9, 13), (9, 20), (15, 20), (15, 13), (20, 13)], fill=(239, 68, 68, 255))
    caps.save(os.path.join(output_dir, "capslock.png"))

    print(f"[✔] Dialog assets generated in {output_dir}")

def create_background(output_path):
    """Generate subtle 1920x1080 dark background."""
    bg = create_radial_gradient(1920, 1080, (14, 19, 28), (8, 10, 15))
    bg.save(output_path, "PNG")
    print(f"[✔] Background canvas generated: {output_path}")

def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "./nooreldeanos"
    os.makedirs(target_dir, exist_ok=True)

    create_background(os.path.join(target_dir, "background.png"))
    create_logo(os.path.join(target_dir, "logo.png"))
    create_spinner_frames(target_dir, num_frames=30)
    create_dialog_assets(target_dir)
    print("\n[🎉] All Plymouth assets generated successfully!")

if __name__ == "__main__":
    main()
