#!/usr/bin/env python3
"""
Fast Multi-Threaded Resumable ISO Downloader for NooreldeanOS
Fetches the latest artifact from GitHub Actions and downloads it via concurrent threads
with automatic SAS token refresh and chunk-level resume support.
"""

import os
import sys
import time
import subprocess
import threading
import json
import requests
from concurrent.futures import ThreadPoolExecutor

CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB per chunk
NUM_WORKERS = 16
DEST_DIR = "/mnt/data3/NooreldeanOS-ISO"
DEST_ZIP = os.path.join(DEST_DIR, "NooreldeanOS-ISO.zip")
PROGRESS_FILE = os.path.join(DEST_DIR, "download_progress.json")
REPO = "coach-nooreldean/NooreldeanOS-Dotfiles"

url_lock = threading.Lock()
current_url = None
current_art_id = None

def get_latest_artifact_info():
    """Get the latest artifact ID and size from GitHub Actions"""
    print("🔍 Fetching latest build info from GitHub API...")
    token_proc = subprocess.run(["gh", "auth", "token"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if token_proc.returncode != 0:
        print("❌ Error: GitHub CLI ('gh') is not authenticated. Run 'gh auth login' first.")
        sys.exit(1)
        
    token = token_proc.stdout.strip()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    
    url = f"https://api.github.com/repos/{REPO}/actions/artifacts?name=NooreldeanOS-ISO&per_page=1"
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch artifacts: {resp.status_code} - {resp.text}")
        
    artifacts = resp.json().get("artifacts", [])
    if not artifacts:
        raise RuntimeError("No NooreldeanOS-ISO artifact found!")
        
    art = artifacts[0]
    art_id = art["id"]
    art_size = art["size_in_bytes"]
    created_at = art.get("created_at", "Unknown")
    
    print(f"📦 Found Artifact ID: {art_id} (Created: {created_at}, Size: {art_size / (1024*1024):.2f} MB)")
    return art_id, art_size

def get_direct_url(force_refresh=False):
    """Retrieve direct Azure Blob URL with automatic refresh on token expiry"""
    global current_url, current_art_id
    with url_lock:
        if current_url and not force_refresh:
            return current_url

        token_proc = subprocess.run(["gh", "auth", "token"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        token = token_proc.stdout.strip()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        api_url = f"https://api.github.com/repos/{REPO}/actions/artifacts/{current_art_id}/zip"
        resp = requests.head(api_url, headers=headers, allow_redirects=False, timeout=15)
        if resp.status_code in (301, 302, 303, 307):
            current_url = resp.headers["Location"]
            return current_url
        raise RuntimeError(f"Failed to get SAS redirect URL: status {resp.status_code}")

def download_chunk(chunk_idx, start, end, filepath, progress_state):
    headers = {"Range": f"bytes={start}-{end}"}
    max_retries = 8
    expected_bytes = end - start + 1
    
    for attempt in range(max_retries):
        url = get_direct_url()
        try:
            r = requests.get(url, headers=headers, timeout=30, stream=True)
            if r.status_code in (401, 403):
                # Token expired, force refresh
                get_direct_url(force_refresh=True)
                time.sleep(1)
                continue
                
            if r.status_code not in (200, 206):
                raise RuntimeError(f"Bad status code: {r.status_code}")
            
            bytes_written = 0
            with open(filepath, "r+b") as f:
                f.seek(start)
                for chunk in r.iter_content(chunk_size=256 * 1024):
                    if chunk:
                        f.write(chunk)
                        bytes_written += len(chunk)
                        with progress_state["lock"]:
                            progress_state["downloaded"] += len(chunk)
                            
            if bytes_written == expected_bytes:
                with progress_state["lock"]:
                    progress_state["completed_chunks"].append(chunk_idx)
                    # Periodically save state
                    if len(progress_state["completed_chunks"]) % 10 == 0:
                        try:
                            with open(PROGRESS_FILE, "w") as pf:
                                json.dump({
                                    "art_id": current_art_id,
                                    "completed": progress_state["completed_chunks"]
                                }, pf)
                        except Exception:
                            pass
                return
            else:
                # Incomplete chunk write, adjust downloaded counter and retry
                with progress_state["lock"]:
                    progress_state["downloaded"] -= bytes_written
                time.sleep(1)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(1 + attempt)

def main():
    global current_art_id
    os.makedirs(DEST_DIR, exist_ok=True)
    
    art_id, total_size = get_latest_artifact_info()
    current_art_id = art_id
    
    # Check for existing progress file
    completed_chunks = set()
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as pf:
                data = json.load(pf)
                if data.get("art_id") == current_art_id:
                    completed_chunks = set(data.get("completed", []))
                    print(f"🔄 Resuming download! {len(completed_chunks)} chunks already verified.")
        except Exception:
            pass

    # Pre-allocate destination file if not already right size
    if not os.path.exists(DEST_ZIP) or os.path.getsize(DEST_ZIP) != total_size:
        print("💾 Pre-allocating disk space for archive...")
        with open(DEST_ZIP, "wb") as f:
            f.truncate(total_size)
            
    chunks = []
    chunk_idx = 0
    already_downloaded = 0
    for start in range(0, total_size, CHUNK_SIZE):
        end = min(start + CHUNK_SIZE - 1, total_size - 1)
        if chunk_idx in completed_chunks:
            already_downloaded += (end - start + 1)
        else:
            chunks.append((chunk_idx, start, end))
        chunk_idx += 1
        
    print(f"⚡ Launching {NUM_WORKERS} concurrent connections (Remaining chunks: {len(chunks)}/{chunk_idx})...")
    
    progress_state = {
        "downloaded": already_downloaded,
        "completed_chunks": list(completed_chunks),
        "lock": threading.Lock()
    }
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = [executor.submit(download_chunk, idx, s, e, DEST_ZIP, progress_state) for idx, s, e in chunks]
        
        while not all(f.done() for f in futures):
            time.sleep(1.5)
            elapsed = time.time() - start_time
            with progress_state["lock"]:
                downloaded = progress_state["downloaded"]
            pct = (downloaded / total_size) * 100 if total_size > 0 else 0
            session_downloaded = downloaded - already_downloaded
            speed_mb = (session_downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
            remaining_bytes = max(0, total_size - downloaded)
            eta_sec = remaining_bytes / (speed_mb * 1024 * 1024) if speed_mb > 0 else 0
            
            bar_len = 25
            filled_len = int(bar_len * downloaded // total_size)
            bar = '█' * filled_len + '░' * (bar_len - filled_len)
            print(f"\r[{bar}] {pct:5.1f}% | {downloaded/(1024*1024):.1f}/{total_size/(1024*1024):.1f} MB | {speed_mb:.2f} MB/s | ETA: {eta_sec:.0f}s ", end="", flush=True)

        for f in futures:
            f.result()

    print()
    total_time = time.time() - start_time
    avg_speed = ((total_size - already_downloaded) / (1024 * 1024)) / total_time if total_time > 0 else 0
    print(f"✅ Download completed successfully in {total_time:.1f}s ({avg_speed:.2f} MB/s)!")
    
    # Remove progress file
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        
    print("📂 Extracting ISO image from zip archive...")
    res = subprocess.run(["unzip", "-o", DEST_ZIP, "-d", DEST_DIR], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"❌ Error unzipping: {res.stderr}")
        sys.exit(1)
        
    print("🧹 Cleaning up temporary zip archive...")
    if os.path.exists(DEST_ZIP):
        os.remove(DEST_ZIP)
        
    print(f"\n🎉 Everything is ready in {DEST_DIR}!")
    print("Files ready for flashing:")
    for root, dirs, files in os.walk(DEST_DIR):
        for f in files:
            if f.endswith(".iso") or f.endswith(".part"):
                p = os.path.join(root, f)
                sz = os.path.getsize(p) / (1024 * 1024)
                print(f"  👉 {p} ({sz:.2f} MB)")

if __name__ == "__main__":
    main()
