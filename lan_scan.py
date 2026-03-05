from scapy.all import ARP,Ether,srp

def scan_lan():

    arp=ARP(pdst="192.168.1.0/24")

    ether=Ether(dst="ff:ff:ff:ff:ff:ff")

    packet=ether/arp

    result=srp(packet,timeout=2,verbose=0)[0]

    devices=[]

    for sent,received in result:

        devices.append({

        "ip":received.psrc,
        "mac":received.hwsrc

        })

    return devices