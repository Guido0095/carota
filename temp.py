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


class NetTest:
    def testTshark(self, iface):
        print(f"Testing if tshark works. Using {iface}")

        cmd = 'tshark -l -I -e "wlan_radio.signal_dbm" -e "wlan.fc.type_subtype" -e "wlan.ra" -e "wlan.ta" -e "wlan.ssid" -e "wlan.bssid" -Tfields -i' + iface
        args = shlex.split(cmd)
        tshark = subprocess.Popen(args, stdout=subprocess.PIPE)

        for line in io.TextIOWrapper(tshark.stdout, encoding="utf-8"):
            print('%s' % line.rstrip())
            bssid =
            if ssid not in mappone:
                Hotstrippamilaminchia(ssid, bssid)
            strippatore = mappone[ssid]
            strippatore.updateClient(mac)

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
