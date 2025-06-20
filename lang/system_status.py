import os
import platform
import psutil
import socket
import time

def get_system_status():
    # Uptime
    uptime_seconds = time.time() - psutil.boot_time()
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    uptime_str = f"{days}d {hours}h {minutes}m"

    # Hostname
    hostname = socket.gethostname()

    # OS version
    os_version = f"{platform.system()} {platform.release()}"

    # CPU
    cpu_model = platform.processor() or platform.uname().processor or "Unknown"

    # RAM
    mem = psutil.virtual_memory()
    total_ram = mem.total / (1024 ** 3)
    used_ram = (mem.total - mem.available) / (1024 ** 3)
    ram_str = f"{used_ram:.1f}GB / {total_ram:.1f}GB"

    # Disk
    disk = psutil.disk_usage('/')
    total_disk = disk.total / (1024 ** 3)
    used_disk = disk.used / (1024 ** 3)
    disk_str = f"{used_disk:.0f}GB / {total_disk:.0f}GB"

    # Load average
    if hasattr(os, "getloadavg"):
        load_avg = os.getloadavg()
        load_str = ", ".join(f"{x:.2f}" for x in load_avg)
    else:
        load_str = "N/A"

    return {
        "uptime": uptime_str,
        "hostname": hostname,
        "os_version": os_version,
        "cpu_model": cpu_model,
        "ram": ram_str,
        "disk": disk_str,
        "load": load_str
    }
