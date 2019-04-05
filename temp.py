#!/usr/bin/env python3
import subprocess
from datetime import datetime
from threading import Thread
import shlex
import sys
import io

mappone = {}


class Hotstrippamilaminchia:
    def __init__(self, ssid, bssid, power):
        self.ssid = ssid
        self.bssid = bssid
        self.clients = {}
        self.power = power
        self.lastseen = datetime.now()
        mappone[self.ssid] = self

    def updateClient(self, mac):
        now = datetime.now()
        self.lastseen = now
        self.clients[mac] = now

    def printStatus(self):
        if self.ssid == "":
            return
        print(self.power, "  ", self.ssid, "  ", str(len(self.clients)))

    def traducistobssid(self, bssid):
        if self.bssid == bssid:
            return self.ssid
        else:
            return -1


class NetTest:
    def testTshark(self, iface):
        print(f"Testing if tshark works. Using {iface}")

        cmd = 'tshark -l -I -Y "!(wlan.ra[0] & 1)" -e "wlan_radio.signal_dbm" -e "wlan.fc.type_subtype" -e "wlan.ra" -e "wlan.ta" -e "wlan.ssid" -e "wlan.bssid" -Tfields -i' + iface
        args = shlex.split(cmd)
        tshark = subprocess.Popen(args, stdout=subprocess.PIPE)

        for line in io.TextIOWrapper(tshark.stdout, encoding="utf-8"):
            print('%s' % line.rstrip())
            capture = line.rstrip().split('\t')
            dim = len(capture)
            for dim in range(dim, 6):
                capture.append(0)

            power = capture[0]
            packetType = capture[1]
            receiver = capture[2]
            transmitter = capture[3]
            ssid = capture[4]
            bssid = capture[5]

            # if ssid != 0 and packetType != "4":
            #     mac = (transmitter, receiver)[bssid == transmitter]
            #     if ssid not in mappone:
            #         Hotstrippamilaminchia(ssid, bssid, power)
            #     if mac != "ff:ff:ff:ff:ff:ff":
            #         strippatore = mappone[ssid]
            #         strippatore.updateClient(mac)
            #
            # for name, address in mappone.items():
            #     address.printStatus()
            # print("\n\n")

    def run(self, iface):
        try:
            t = Thread(target=self.testTshark, args=(iface,))
            t.daemon = True
            t.start()
            t.join()
        except KeyboardInterrupt:
            print("\nExiting the dog...")
            sys.exit(0)


if __name__ == '__main__':
    net = NetTest()
    net.run('wlp2s0')
