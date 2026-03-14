"""
SystemController: Executes OS-level control commands on student machines.
Handles: Lock/Unlock PC, Block/Unblock Internet, Enable/Disable USB, App Whitelist.
"""
import subprocess
import ctypes
import threading
import time
import sys
import os


class SystemController:
    """Executes OS-level commands received from the faculty Control Panel."""

    def __init__(self, dashboard=None):
        self.dashboard = dashboard
        self.whitelist_active = False
        self.whitelisted_apps = []
        self._whitelist_thread = None

    def execute(self, command_type: str, payload: dict = None):
        """Dispatch a control command to the appropriate handler."""
        payload = payload or {}
        handlers = {
            'lock_pc': self.lock_pc,
            'unlock_pc': self.unlock_pc,
            'block_internet': self.block_internet,
            'unblock_internet': self.unblock_internet,
            'disable_usb': self.disable_usb,
            'enable_usb': self.enable_usb,
            'app_whitelist': self.set_app_whitelist,
        }
        handler = handlers.get(command_type)
        if handler:
            try:
                handler(payload)
                return True
            except Exception as e:
                print(f"[SystemController] Error executing {command_type}: {e}")
                return False
        return False

    # ── Lock / Unlock PC ──────────────────────────────────────────────
    def lock_pc(self, payload=None):
        """Show fullscreen lock overlay on the student dashboard."""
        if self.dashboard:
            from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
            QMetaObject.invokeMethod(
                self.dashboard, "show_lock_overlay",
                Qt.ConnectionType.QueuedConnection
            )
        print("[SystemController] PC Locked")

    def unlock_pc(self, payload=None):
        """Hide the lock overlay."""
        if self.dashboard:
            from PyQt6.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(
                self.dashboard, "hide_lock_overlay",
                Qt.ConnectionType.QueuedConnection
            )
        print("[SystemController] PC Unlocked")

    # ── Internet Block / Unblock ──────────────────────────────────────
    def block_internet(self, payload=None):
        """Block internet by adding a firewall rule."""
        try:
            subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                 'name=SmartLabBlockInternet', 'dir=out', 'action=block',
                 'remoteip=0.0.0.0-255.255.255.255'],
                capture_output=True, creationflags=0x08000000
            )
            # Allow LAN traffic (keep WebSocket alive)
            subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                 'name=SmartLabAllowLAN', 'dir=out', 'action=allow',
                 'remoteip=localsubnet'],
                capture_output=True, creationflags=0x08000000
            )
            print("[SystemController] Internet Blocked")
        except Exception as e:
            print(f"[SystemController] block_internet failed: {e}")

    def unblock_internet(self, payload=None):
        """Remove the internet block firewall rule."""
        try:
            subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                 'name=SmartLabBlockInternet'],
                capture_output=True, creationflags=0x08000000
            )
            subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                 'name=SmartLabAllowLAN'],
                capture_output=True, creationflags=0x08000000
            )
            print("[SystemController] Internet Unblocked")
        except Exception as e:
            print(f"[SystemController] unblock_internet failed: {e}")

    # ── USB Enable / Disable ──────────────────────────────────────────
    def disable_usb(self, payload=None):
        """Disable USB storage by modifying the registry."""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\USBSTOR",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)
            winreg.CloseKey(key)
            print("[SystemController] USB Disabled")
        except Exception as e:
            print(f"[SystemController] disable_usb failed: {e}")

    def enable_usb(self, payload=None):
        """Re-enable USB storage."""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\USBSTOR",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 3)
            winreg.CloseKey(key)
            print("[SystemController] USB Enabled")
        except Exception as e:
            print(f"[SystemController] enable_usb failed: {e}")

    # ── App Whitelist ─────────────────────────────────────────────────
    def set_app_whitelist(self, payload=None):
        """Start monitoring and killing non-whitelisted applications."""
        apps = payload.get('apps', []) if payload else []
        if not apps:
            self.whitelist_active = False
            print("[SystemController] App Whitelist cleared")
            return

        self.whitelisted_apps = [a.lower() for a in apps]
        # Always allow essential system + smartlab processes
        self.whitelisted_apps.extend([
            'python.exe', 'pythonw.exe', 'cmd.exe',
            'conhost.exe', 'explorer.exe', 'svchost.exe',
            'csrss.exe', 'winlogon.exe', 'dwm.exe',
            'taskhostw.exe', 'smartlab', 'student_dashboard'
        ])
        self.whitelist_active = True

        if not self._whitelist_thread or not self._whitelist_thread.is_alive():
            self._whitelist_thread = threading.Thread(target=self._whitelist_loop, daemon=True)
            self._whitelist_thread.start()
        print(f"[SystemController] App Whitelist active: {apps}")

    def _whitelist_loop(self):
        """Background thread that kills non-whitelisted processes."""
        import psutil
        while self.whitelist_active:
            try:
                for proc in psutil.process_iter(['name']):
                    pname = proc.info['name'].lower()
                    if not any(w in pname for w in self.whitelisted_apps):
                        try:
                            proc.kill()
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            pass
            except Exception:
                pass
            time.sleep(5)
