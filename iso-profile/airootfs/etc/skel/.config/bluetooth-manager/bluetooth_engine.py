#!/usr/bin/env python3
"""
Bluetooth Engine for NooreldeanOS Bluetooth Manager.
Direct BlueZ D-Bus integration + Persistent BlueZ Agent Session.
Handles both outgoing connections and incoming pairing requests from phones/tablets.
"""

import subprocess
import threading
import time
import dbus

class AgentSession:
    """Manages an active background bluetoothctl agent session for auto-pairing and visibility."""
    def __init__(self, on_prompt=None):
        self.proc = None
        self._running = False
        self._lock = threading.Lock()
        self.last_output = []
        self.on_prompt = on_prompt

    def set_prompt_callback(self, cb):
        self.on_prompt = cb

    def start(self):
        with self._lock:
            if self._running and self.proc and self.proc.poll() is None:
                return
            self._running = True
            try:
                self.proc = subprocess.Popen(
                    ["bluetoothctl"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                self.proc.stdin.write(
                    "discoverable-timeout 0\n"
                    "pairable on\n"
                    "discoverable on\n"
                    "agent NoInputNoOutput\n"
                    "default-agent\n"
                )
                self.proc.stdin.flush()
                threading.Thread(target=self._reader, daemon=True).start()
            except Exception:
                pass

    def _reader(self):
        while self._running and self.proc and self.proc.poll() is None:
            try:
                line = self.proc.stdout.readline()
                if not line:
                    break
                line_str = line.strip()
                if line_str:
                    self.last_output.append(line_str)
                    if len(self.last_output) > 150:
                        self.last_output.pop(0)

                lower = line_str.lower()
                import re
                m_pass = re.search(r"confirm passkey\s+([0-9]{4,6})", lower)
                if m_pass:
                    passkey = m_pass.group(1)
                    if self.on_prompt:
                        try: self.on_prompt("passkey", passkey)
                        except Exception: pass
                    self.send("yes")
                    continue

                if "enter pin" in lower:
                    if self.on_prompt:
                        try: self.on_prompt("pin", "0000")
                        except Exception: pass
                    self.send("0000")
                    continue

                if any(k in lower for k in ["authorize service", "request confirmation", "(yes/no)"]):
                    if self.on_prompt:
                        try: self.on_prompt("authorize", "")
                        except Exception: pass
                    self.send("yes")
                    continue
            except Exception:
                break

    def send(self, cmd: str):
        with self._lock:
            if self.proc and self.proc.poll() is None:
                try:
                    self.proc.stdin.write(cmd.strip() + "\n")
                    self.proc.stdin.flush()
                except Exception:
                    pass

    def execute_commands(self, commands: list, timeout=12):
        with self._lock:
            if not self.proc or self.proc.poll() is not None:
                self.start()

        start_idx = len(self.last_output)
        for c in commands:
            self.send(c)

        start_time = time.time()
        success = False
        msg = ""
        while time.time() - start_time < timeout:
            time.sleep(0.3)
            recent = self.last_output[start_idx:]
            full_text = " ".join(recent).lower()

            if any(k in full_text for k in ["connection successful", "connected: yes", "pairing successful"]):
                success = True
                msg = "تم الاتصال بنجاح"
                break
            if any(k in full_text for k in ["failed to connect", "failed to pair", "not available", "failed"]):
                for r in reversed(recent):
                    if "failed" in r.lower() or "error" in r.lower() or "not available" in r.lower():
                        msg = r
                        break
                break

        return success, msg or ("تم الاتصال" if success else "انتهت المهلة دون رد من الجهاز")

    def stop(self):
        self._running = False
        with self._lock:
            if self.proc:
                try:
                    self.proc.stdin.write("quit\n")
                    self.proc.stdin.flush()
                    self.proc.terminate()
                except Exception:
                    pass
                self.proc = None


class BluetoothEngine:
    _bus = None
    _manager = None
    _adapter_path = None
    _agent_session = None

    @classmethod
    def get_agent_session(cls):
        if cls._agent_session is None:
            cls._agent_session = AgentSession()
            cls._agent_session.start()
        return cls._agent_session

    @classmethod
    def get_bus(cls):
        if cls._bus is None:
            try:
                cls._bus = dbus.SystemBus()
                cls._manager = dbus.Interface(
                    cls._bus.get_object("org.bluez", "/"),
                    "org.freedesktop.DBus.ObjectManager"
                )
            except Exception:
                pass
        return cls._bus

    @classmethod
    def get_adapter_path(cls):
        bus = cls.get_bus()
        if not bus or not cls._manager:
            return "/org/bluez/hci0"
        try:
            objects = cls._manager.GetManagedObjects()
            for path, ifaces in objects.items():
                if "org.bluez.Adapter1" in ifaces:
                    cls._adapter_path = str(path)
                    return cls._adapter_path
        except Exception:
            pass
        return "/org/bluez/hci0"

    @classmethod
    def get_controller(cls):
        bus = cls.get_bus()
        adapter_path = cls.get_adapter_path()
        if not bus or not adapter_path:
            return {
                "available": False,
                "error": "خدمة البلوتوث غير متوفرة أو لم يتم العثور على محول",
                "powered": False,
                "discovering": False,
                "pairable": False,
                "discoverable": False,
                "mac": "",
                "name": ""
            }

        try:
            props = dbus.Interface(
                bus.get_object("org.bluez", adapter_path),
                "org.freedesktop.DBus.Properties"
            )
            all_props = props.GetAll("org.bluez.Adapter1")

            return {
                "available": True,
                "powered": bool(all_props.get("Powered", False)),
                "discovering": bool(all_props.get("Discovering", False)),
                "pairable": bool(all_props.get("Pairable", False)),
                "discoverable": bool(all_props.get("Discoverable", False)),
                "mac": str(all_props.get("Address", "")),
                "name": str(all_props.get("Alias", all_props.get("Name", "Bluetooth Adapter")))
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "powered": False,
                "discovering": False,
                "pairable": False,
                "discoverable": False,
                "mac": "",
                "name": ""
            }

    @classmethod
    def set_power(cls, state: bool):
        bus = cls.get_bus()
        adapter_path = cls.get_adapter_path()
        if bus and adapter_path:
            try:
                props = dbus.Interface(
                    bus.get_object("org.bluez", adapter_path),
                    "org.freedesktop.DBus.Properties"
                )
                props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(state))
                if state:
                    cls.get_agent_session().start()
                else:
                    cls.get_agent_session().stop()
                return True
            except Exception:
                pass
        return False

    @classmethod
    def set_discoverable(cls, state: bool):
        """Set whether the PC is visible to other devices (phones, tablets)."""
        session = cls.get_agent_session()
        session.send(f"discoverable {'on' if state else 'off'}")
        session.send(f"pairable {'on' if state else 'off'}")
        return True

    @classmethod
    def start_discovery(cls):
        bus = cls.get_bus()
        adapter_path = cls.get_adapter_path()
        if not bus or not adapter_path:
            return False

        try:
            adapter = dbus.Interface(
                bus.get_object("org.bluez", adapter_path),
                "org.bluez.Adapter1"
            )
            filter_dict = {
                "Transport": dbus.String("auto", variant_level=1),
                "DuplicateData": dbus.Boolean(True, variant_level=1)
            }
            try:
                adapter.SetDiscoveryFilter(filter_dict)
            except Exception:
                pass

            adapter.StartDiscovery()
            return True
        except dbus.DBusException as e:
            if "org.bluez.Error.InProgress" in str(e):
                return True
            return False
        except Exception:
            return False

    @classmethod
    def stop_discovery(cls):
        bus = cls.get_bus()
        adapter_path = cls.get_adapter_path()
        if not bus or not adapter_path:
            return False

        try:
            adapter = dbus.Interface(
                bus.get_object("org.bluez", adapter_path),
                "org.bluez.Adapter1"
            )
            adapter.StopDiscovery()
            return True
        except Exception:
            return False

    @classmethod
    def get_all_devices(cls):
        bus = cls.get_bus()
        if not bus or not cls._manager:
            return [], []

        paired = []
        discovered = []

        try:
            objects = cls._manager.GetManagedObjects()
            for path, ifaces in objects.items():
                if "org.bluez.Device1" in ifaces:
                    d = ifaces["org.bluez.Device1"]
                    mac = str(d.get("Address", "")).upper()
                    if not mac:
                        continue

                    name = str(d.get("Name", d.get("Alias", ""))).strip()
                    if not name:
                        name = mac

                    icon = str(d.get("Icon", "bluetooth"))
                    is_paired = bool(d.get("Paired", False))
                    is_connected = bool(d.get("Connected", False))
                    is_trusted = bool(d.get("Trusted", False))

                    battery = None
                    if "BatteryPercentage" in d:
                        battery = int(d["BatteryPercentage"])
                    elif "org.bluez.Battery1" in ifaces:
                        battery = int(ifaces["org.bluez.Battery1"].get("Percentage", 0))

                    rssi = None
                    if "RSSI" in d:
                        rssi = int(d["RSSI"])

                    dev_item = {
                        "mac": mac,
                        "name": name,
                        "icon": icon,
                        "paired": is_paired,
                        "connected": is_connected,
                        "trusted": is_trusted,
                        "battery": battery,
                        "rssi": rssi,
                        "path": str(path)
                    }

                    if is_paired:
                        paired.append(dev_item)
                    else:
                        discovered.append(dev_item)
        except Exception:
            pass

        paired.sort(key=lambda x: (not x["connected"], x["name"].lower()))
        discovered.sort(key=lambda x: (x["name"] == x["mac"], x["name"].lower()))

        return paired, discovered

    @classmethod
    def auto_route_incoming_audio(cls):
        """
        Ensures any connected phone or tablet acting as audio gateway
        has its profile enabled and its audio output stream routed to active speakers.
        """
        try:
            cards_out = subprocess.check_output(["pactl", "list", "cards"], text=True, stderr=subprocess.DEVNULL)
            for block in cards_out.split("Card #"):
                if "bluez_card." in block and "Active Profile: off" in block and "audio-gateway" in block:
                    import re
                    m = re.search(r"Name:\s*(bluez_card\.[A-Za-z0-9_]+)", block)
                    if m:
                        subprocess.run(["pactl", "set-card-profile", m.group(1), "audio-gateway"], capture_output=True, timeout=2)

            links_out = subprocess.check_output(["pw-link", "-o"], text=True, stderr=subprocess.DEVNULL)
            bluez_inputs_fl = [l.strip() for l in links_out.splitlines() if "bluez_input" in l and "output_FL" in l]
            bluez_inputs_fr = [l.strip() for l in links_out.splitlines() if "bluez_input" in l and "output_FR" in l]

            if bluez_inputs_fl or bluez_inputs_fr:
                sinks_in = subprocess.check_output(["pw-link", "-i"], text=True, stderr=subprocess.DEVNULL)
                playback_fl = [l.strip() for l in sinks_in.splitlines() if "playback_FL" in l and "bluez_input" not in l]
                playback_fr = [l.strip() for l in sinks_in.splitlines() if "playback_FR" in l and "bluez_input" not in l]

                for b_fl in bluez_inputs_fl:
                    for p_fl in playback_fl:
                        subprocess.run(["pw-link", b_fl, p_fl], capture_output=True, timeout=1)
                for b_fr in bluez_inputs_fr:
                    for p_fr in playback_fr:
                        subprocess.run(["pw-link", b_fr, p_fr], capture_output=True, timeout=1)
        except Exception:
            pass

    @classmethod
    def connect(cls, mac: str):
        # Stop discovery so the single radio can cleanly connect
        cls.stop_discovery()
        time.sleep(0.3)

        session = cls.get_agent_session()
        cmds = [
            f"trust {mac}",
            f"connect {mac}"
        ]
        return session.execute_commands(cmds, timeout=12)

    @classmethod
    def disconnect(cls, mac: str):
        session = cls.get_agent_session()
        cmds = [f"disconnect {mac}"]
        return session.execute_commands(cmds, timeout=8)

    @classmethod
    def pair_and_connect(cls, mac: str):
        cls.stop_discovery()
        time.sleep(0.3)

        session = cls.get_agent_session()
        cmds = [
            f"trust {mac}",
            f"pair {mac}",
            f"connect {mac}"
        ]
        return session.execute_commands(cmds, timeout=15)

    @classmethod
    def remove(cls, mac: str):
        session = cls.get_agent_session()
        cmds = [f"remove {mac}"]
        ok, msg = session.execute_commands(cmds, timeout=6)
        return ok or "removed" in msg.lower(), msg

    @staticmethod
    def get_glyph_for_icon(icon_name: str, dev_name: str = ""):
        icon_name = (icon_name or "").lower()
        dev_name = (dev_name or "").lower()

        if any(k in icon_name for k in ["headset", "headphone"]) or any(k in dev_name for k in ["buds", "airplus", "airpods", "wh-", "headphone", "headset"]):
            return "󰋋"
        if any(k in icon_name for k in ["audio", "speaker", "sound"]) or any(k in dev_name for k in ["speaker", "soundbar", "jbl"]):
            return "󰓃"
        if "keyboard" in icon_name or "keyboard" in dev_name:
            return "󰌌"
        if "mouse" in icon_name or "mouse" in dev_name:
            return "󰍽"
        if any(k in icon_name for k in ["gaming", "gamepad", "joystick"]) or any(k in dev_name for k in ["controller", "xbox", "dualsense", "gamepad"]):
            return "󰊖"
        if "phone" in icon_name or any(k in dev_name for k in ["phone", "realme", "galaxy", "iphone", "pixel", "xiaomi", "honor"]):
            return "󰏲"
        if any(k in icon_name for k in ["computer", "laptop"]) or any(k in dev_name for k in ["laptop", "pc", "desktop"]):
            return "󰌢"
        return "󰂯"
