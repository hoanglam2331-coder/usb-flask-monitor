import time
import socket
import psutil
import requests
import wmi
from datetime import datetime

SERVER="http://192.168.1.43:5000/log"

known=set()

def get_ip():

    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    return s.getsockname()[0]


def get_mac():

    for iface,addrs in psutil.net_if_addrs().items():

        for addr in addrs:

            if addr.family.name=="AF_LINK":

                return addr.address


def detect_usb():

    devices=[]

    c=wmi.WMI()

    for disk in c.Win32_DiskDrive():

        if disk.InterfaceType=="USB":

            devices.append(disk.Model)

    return devices


def detect_phone():

    c=wmi.WMI()

    for device in c.Win32_PnPEntity():

        name=device.Name

        if name:

            if "Android" in name:

                return name

            if "iPhone" in name:

                return name

    return None


print("Agent dang chay - Theo doi USB...")


while True:

    usb=detect_usb()

    phone=detect_phone()

    current=set(usb)

    inserted=current-known
    removed=known-current

    hostname=socket.gethostname()
    ip=get_ip()
    mac=get_mac()

    for u in inserted:

        print("USB cam vao:",u)

        data={

        "time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "computer":hostname,
        "ip":ip,
        "mac":mac,
        "device":u,
        "manufacturer":u,
        "size":0,
        "event":"USB Inserted"

        }

        requests.post(SERVER,json=data)


    for r in removed:

        print("USB rut ra:",r)

        data={

        "time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "computer":hostname,
        "ip":ip,
        "mac":mac,
        "device":r,
        "manufacturer":r,
        "size":0,
        "event":"USB Removed"

        }

        requests.post(SERVER,json=data)


    if phone:

        print("Dien thoai ket noi:",phone)

        data={

        "time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "computer":hostname,
        "ip":ip,
        "mac":mac,
        "device":phone,
        "manufacturer":"Phone",
        "size":0,
        "event":"Phone Connected"

        }

        requests.post(SERVER,json=data)

    known=current

    time.sleep(2)