import os
import subprocess
import re
from pathlib import Path

def get_duration(input_path):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        str(input_path)
    ]
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, text=True)
        return float(result.stdout.strip())
    except Exception:
        return 0.0

def convert_video(input_path, output_format, progress_callback=None, codec_mode="copy"):
    """
    Converts video using specified codec mode.
    output_format should be either 'mp4' or 'mov'.
    Returns the path to the converted file, or raises Exception on failure.
    """
    input_file = Path(input_path)
    if not input_file.exists() or not input_file.is_file():
        raise FileNotFoundError(f"الملف غير موجود: {input_path}")
        
    output_dir = input_file.parent / f"Converted_{output_format.upper()}"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"{input_file.stem}.{output_format}"
    
    # If the output file already exists, we will create a unique name
    counter = 1
    while output_file.exists():
        output_file = output_dir / f"{input_file.stem}_{counter}.{output_format}"
        counter += 1
        
    total_duration = get_duration(input_file)
        
    if codec_mode == "dnxhr":
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(input_file),
            "-c:v", "dnxhd",
            "-profile:v", "dnxhr_sq",
            "-pix_fmt", "yuv422p",
            "-c:a", "pcm_s16le",
            str(output_file)
        ]
    elif codec_mode == "mpeg4":
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(input_file),
            "-c:v", "mpeg4",
            "-q:v", "2",
            "-c:a", "pcm_s16le",
            str(output_file)
        ]
    else:
        cmd = [
            "ffmpeg",
            "-y",               # Overwrite output files
            "-i", str(input_file),
            "-c", "copy",       # Stream copy (lossless and extremely fast)
            str(output_file)
        ]
    
    try:
        process = subprocess.Popen(
            cmd, 
            stderr=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            text=True, 
            bufsize=1, 
            universal_newlines=True
        )
        
        time_regex = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
        error_log = []
        
        for line in process.stderr:
            error_log.append(line)
            if progress_callback and total_duration > 0:
                match = time_regex.search(line)
                if match:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = float(match.group(3))
                    current_time = hours * 3600 + minutes * 60 + seconds
                    
                    percent = int((current_time / total_duration) * 100)
                    percent = min(99, percent)
                    progress_callback(percent)
                    
        process.wait()
        if process.returncode != 0:
            error_output = "".join(error_log[-10:]) # last 10 lines
            raise RuntimeError(f"فشل التحويل:\n{error_output}")
            
        if progress_callback:
            progress_callback(100)
            
        return str(output_file)
    except Exception as e:
        raise RuntimeError(str(e))

def get_convertible_files(directory, from_format):
    """
    Get a list of all files in a directory that match the format.
    """
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        return []
    
    # from_format is either 'mp4' or 'mov'
    return list(dir_path.glob(f"*.{from_format}"))
