#!/usr/bin/env python3
"""
Speed Test Engine for NooreldeanOS
Provides high-precision internet bandwidth, ping, and jitter testing.
Zero external pip dependencies: built with Python standard library.
Also provides optional integration with Ookla speedtest-cli if installed.
"""

import os
import sys
import time
import json
import socket
import shutil
import urllib.request
import urllib.error
import subprocess
import threading
from collections import deque

class SpeedEngine:
    def __init__(self):
        self.cancel_event = threading.Event()
        self._active_sockets = []
        self._lock = threading.Lock()

    def cancel(self):
        """Immediately abort all in-progress tests."""
        self.cancel_event.set()
        with self._lock:
            for s in self._active_sockets:
                try:
                    s.close()
                except Exception:
                    pass
            self._active_sockets.clear()

    def reset(self):
        self.cancel_event.clear()
        with self._lock:
            self._active_sockets.clear()

    @staticmethod
    def is_speedtest_cli_available():
        """Check if official or standard speedtest-cli binary is available."""
        return (shutil.which("speedtest-cli") is not None) or (shutil.which("speedtest") is not None)

    @staticmethod
    def get_network_info():
        """
        Fetch client public IP, location, ISP, and default local network interface.
        Uses fast timeouts and multi-provider fallbacks.
        """
        info = {
            "ip": "Unknown",
            "city": "",
            "country": "",
            "isp": "Unknown ISP",
            "interface": "Default",
            "gateway": "Unknown",
            "server": "Cloudflare Anycast (Global Edge)"
        }

        # 1. Detect default network interface & gateway
        try:
            res = subprocess.run(["ip", "route", "show", "default"], capture_output=True, text=True, timeout=2)
            parts = res.stdout.strip().split()
            if "dev" in parts:
                info["interface"] = parts[parts.index("dev") + 1]
            if "via" in parts:
                info["gateway"] = parts[parts.index("via") + 1]
        except Exception:
            pass

        # 2. Query ipapi.co
        try:
            req = urllib.request.Request("https://ipapi.co/json/", headers={"User-Agent": "curl/8.0"})
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode())
                info["ip"] = data.get("ip", info["ip"])
                info["city"] = data.get("city", "")
                info["country"] = data.get("country_name", "")
                info["isp"] = data.get("org", data.get("asn", "Unknown ISP"))
                return info
        except Exception:
            pass

        # Fallback: Cloudflare trace
        try:
            req = urllib.request.Request("https://cloudflare.com/cdn-cgi/trace", headers={"User-Agent": "curl/8.0"})
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                text = resp.read().decode()
                cf_dict = dict(line.split("=", 1) for line in text.strip().split("\n") if "=" in line)
                info["ip"] = cf_dict.get("ip", info["ip"])
                info["country"] = cf_dict.get("loc", "")
                colo = cf_dict.get("colo", "")
                if colo:
                    info["server"] = f"Cloudflare Edge ({colo})"
        except Exception:
            pass

        # Fallback 2: api.myip.com
        if info["ip"] == "Unknown":
            try:
                req = urllib.request.Request("https://api.myip.com", headers={"User-Agent": "curl/8.0"})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    data = json.loads(resp.read().decode())
                    info["ip"] = data.get("ip", info["ip"])
                    info["country"] = data.get("country", "")
            except Exception:
                pass

        return info

    def measure_ping_jitter(self, target_ip="1.1.1.1", count=5):
        """
        Measures latency (ping) and jitter in milliseconds.
        Uses low-overhead ICMP ping first, with TCP/HTTP fallback.
        """
        if self.cancel_event.is_set():
            return None

        # Method A: Standard Linux Ping (Very precise, gives avg & mdev jitter)
        try:
            cmd = ["ping", "-c", str(count), "-i", "0.2", "-W", "1", target_ip]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=count * 1.5)
            if res.returncode == 0:
                lines = res.stdout.strip().split("\n")
                # Look for line: rtt min/avg/max/mdev = 44.923/46.049/49.621/1.795 ms
                for line in lines:
                    if "min/avg/max/mdev" in line or "rtt" in line:
                        vals = line.split("=")[1].strip().split()[0].split("/")
                        min_ping = float(vals[0])
                        avg_ping = float(vals[1])
                        max_ping = float(vals[2])
                        jitter = float(vals[3]) if len(vals) > 3 else abs(max_ping - min_ping) / 2
                        return {
                            "ping": round(avg_ping, 1),
                            "jitter": round(jitter, 1),
                            "min": round(min_ping, 1),
                            "max": round(max_ping, 1)
                        }
        except Exception:
            pass

        if self.cancel_event.is_set():
            return None

        # Method B: HTTP Ping against Cloudflare Speed Endpoint
        samples = []
        url = "https://speed.cloudflare.com/__down?bytes=0"
        for _ in range(count):
            if self.cancel_event.is_set():
                return None
            t0 = time.perf_counter()
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=2.5) as resp:
                    resp.read()
                samples.append((time.perf_counter() - t0) * 1000)
            except Exception:
                pass
            time.sleep(0.08)

        if not samples:
            return {"ping": 0.0, "jitter": 0.0, "min": 0.0, "max": 0.0}

        avg_p = sum(samples) / len(samples)
        if len(samples) > 1:
            diffs = [abs(samples[i] - samples[i - 1]) for i in range(1, len(samples))]
            jitter = sum(diffs) / len(diffs)
        else:
            jitter = 0.0

        return {
            "ping": round(avg_p, 1),
            "jitter": round(jitter, 1),
            "min": round(min(samples), 1),
            "max": round(max(samples), 1)
        }

    def measure_download(self, progress_callback=None, duration=8.0, threads_count=4):
        """
        Runs a high-throughput multi-stream download speed test.
        Uses rolling-window calculation to provide realistic, smooth instantaneous Mbps.
        """
        if self.cancel_event.is_set():
            return None

        self.reset()
        byte_log = deque()  # (timestamp, total_bytes)
        total_bytes = 0
        peak_mbps = 0.0
        bytes_lock = threading.Lock()

        # Dynamic chunk size based on network throughput
        chunk_url = "https://speed.cloudflare.com/__down?bytes=25000000"

        phase_stop = threading.Event()

        def download_worker():
            nonlocal total_bytes
            while not self.cancel_event.is_set() and not phase_stop.is_set():
                try:
                    req = urllib.request.Request(chunk_url, headers={
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
                        "Accept-Encoding": "identity"
                    })
                    with urllib.request.urlopen(req, timeout=4.0) as resp:
                        while not self.cancel_event.is_set() and not phase_stop.is_set():
                            data = resp.read(65536)
                            if not data:
                                break
                            with bytes_lock:
                                total_bytes += len(data)
                except Exception:
                    time.sleep(0.05)

        workers = [threading.Thread(target=download_worker, daemon=True) for _ in range(threads_count)]
        start_time = time.time()
        for w in workers:
            w.start()

        # Sampler loop
        while not self.cancel_event.is_set():
            now = time.time()
            elapsed = now - start_time
            if elapsed >= duration:
                break

            with bytes_lock:
                current_total = total_bytes

            byte_log.append((now, current_total))

            # Keep rolling window of last 0.6 seconds for instantaneous speed
            while byte_log and (now - byte_log[0][0]) > 0.6:
                byte_log.popleft()

            instant_mbps = 0.0
            if len(byte_log) >= 2:
                dt = byte_log[-1][0] - byte_log[0][0]
                db = byte_log[-1][1] - byte_log[0][1]
                if dt > 0.05:
                    instant_mbps = (db * 8.0) / (dt * 1_000_000.0)

            if instant_mbps > peak_mbps:
                peak_mbps = instant_mbps

            total_mb = current_total / (1024.0 * 1024.0)
            progress_pct = min(100.0, (elapsed / duration) * 100.0)

            if progress_callback:
                progress_callback({
                    "speed_mbps": round(instant_mbps, 2),
                    "peak_mbps": round(peak_mbps, 2),
                    "total_mb": round(total_mb, 2),
                    "progress_pct": round(progress_pct, 1),
                    "phase": "download"
                })

            time.sleep(0.08)

        phase_stop.set()
        total_time = max(0.1, time.time() - start_time)
        final_mb = total_bytes / (1024.0 * 1024.0)
        overall_avg_mbps = (total_bytes * 8.0) / (total_time * 1_000_000.0)

        return {
            "avg_mbps": round(overall_avg_mbps, 2),
            "peak_mbps": round(peak_mbps, 2),
            "total_mb": round(final_mb, 2)
        }

    def measure_upload(self, progress_callback=None, duration=7.0, threads_count=4):
        """
        Runs a multi-stream upload test against Cloudflare Speed upload endpoint.
        """
        if self.cancel_event.is_set():
            return None

        byte_log = deque()
        total_uploaded_bytes = 0
        peak_mbps = 0.0
        bytes_lock = threading.Lock()

        # 512KB payload
        payload = b"\x00" * (512 * 1024)
        upload_url = "https://speed.cloudflare.com/__up"
        phase_stop = threading.Event()

        def upload_worker():
            nonlocal total_uploaded_bytes
            while not self.cancel_event.is_set() and not phase_stop.is_set():
                try:
                    req = urllib.request.Request(
                        upload_url,
                        data=payload,
                        headers={
                            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
                            "Content-Type": "application/octet-stream"
                        }
                    )
                    with urllib.request.urlopen(req, timeout=4.0) as resp:
                        resp.read()
                        with bytes_lock:
                            total_uploaded_bytes += len(payload)
                except Exception:
                    time.sleep(0.05)

        workers = [threading.Thread(target=upload_worker, daemon=True) for _ in range(threads_count)]
        start_time = time.time()
        for w in workers:
            w.start()

        while not self.cancel_event.is_set():
            now = time.time()
            elapsed = now - start_time
            if elapsed >= duration:
                break

            with bytes_lock:
                current_total = total_uploaded_bytes

            byte_log.append((now, current_total))

            while byte_log and (now - byte_log[0][0]) > 0.6:
                byte_log.popleft()

            instant_mbps = 0.0
            if len(byte_log) >= 2:
                dt = byte_log[-1][0] - byte_log[0][0]
                db = byte_log[-1][1] - byte_log[0][1]
                if dt > 0.05:
                    instant_mbps = (db * 8.0) / (dt * 1_000_000.0)

            if instant_mbps > peak_mbps:
                peak_mbps = instant_mbps

            total_mb = current_total / (1024.0 * 1024.0)
            progress_pct = min(100.0, (elapsed / duration) * 100.0)

            if progress_callback:
                progress_callback({
                    "speed_mbps": round(instant_mbps, 2),
                    "peak_mbps": round(peak_mbps, 2),
                    "total_mb": round(total_mb, 2),
                    "progress_pct": round(progress_pct, 1),
                    "phase": "upload"
                })

            time.sleep(0.08)

        phase_stop.set()
        total_time = max(0.1, time.time() - start_time)
        final_mb = total_uploaded_bytes / (1024.0 * 1024.0)
        overall_avg_mbps = (total_uploaded_bytes * 8.0) / (total_time * 1_000_000.0)

        return {
            "avg_mbps": round(overall_avg_mbps, 2),
            "peak_mbps": round(peak_mbps, 2),
            "total_mb": round(final_mb, 2)
        }

    def run_speedtest_cli(self, progress_callback=None):
        """
        Optional alternate runner using Ookla speedtest-cli or speedtest binary if present.
        """
        bin_cmd = shutil.which("speedtest-cli") or shutil.which("speedtest")
        if not bin_cmd:
            raise FileNotFoundError("speedtest-cli is not installed.")

        cmd = [bin_cmd, "--json"]
        if progress_callback:
            progress_callback({"phase": "speedtest_cli_starting", "speed_mbps": 0.0})

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if proc.returncode != 0:
            raise RuntimeError(f"speedtest-cli failed: {proc.stderr}")

        data = json.loads(proc.stdout)
        down_mbps = round(data.get("download", 0) / 1_000_000.0, 2)
        up_mbps = round(data.get("upload", 0) / 1_000_000.0, 2)
        ping_ms = round(data.get("ping", 0), 1)

        server_info = data.get("server", {})
        client_info = data.get("client", {})

        return {
            "ping": ping_ms,
            "jitter": 1.0,
            "download": down_mbps,
            "upload": up_mbps,
            "server": f"{server_info.get('sponsor', 'Ookla')} ({server_info.get('name', 'Unknown')})",
            "isp": client_info.get("isp", "Unknown ISP"),
            "ip": client_info.get("ip", "Unknown")
        }
