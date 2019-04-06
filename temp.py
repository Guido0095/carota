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
        self.bssid.append(bssid)
        self.clients = {}
        self.power = power
        self.lastseen = datetime.now()
        mappone[self.ssid] = self

    def updateClient(self, mac, power):
        now = datetime.now()
        self.lastseen = now
        self.clients[mac] = now
        self.power = power

    def printStatus(self):
        if self.ssid != "":
            print(self.power, "  ", self.ssid, "  ", str(len(self.clients)))

    def updatessid(self, bssid, ssid):
        if bssid in self.bssid and (self.ssid != ssid or self.ssid != '** ', ssid, ' **'):
            del mappone[self.ssid]
            self.ssid = '** ', ssid, ' **'
            mappone[self.ssid] = self

    def addbssid(self, bssid):
        if bssid not in self.bssid:
            self.bssid.append(bssid)

    def frombssidtossid(self, ssid, bssid):
        if self.ssid == ssid:
            return self.bssid
        else:
            return False


class NetTest:
    def testTshark(self, iface):

        cmd = 'tshark -l -I -Y "!(wlan.ra[0] & 1)" -e "wlan_radio.signal_dbm" -e "wlan.fc.type_subtype" -e "wlan.ra" -e "wlan.ta" -e "wlan.ssid" -e "wlan.bssid" -Tfields -i' + iface
        args = shlex.split(cmd)
        tshark = subprocess.Popen(args, stdout=subprocess.PIPE)

        for line in io.TextIOWrapper(tshark.stdout, encoding="utf-8"):
            # print('%s' % line.rstrip())
            capture = line.rstrip().split('\t')
            dim = len(capture)
            for dim in range(dim, 6):
                capture.append('0')

            power = capture[0]
            packetType = capture[1]
            receiver = capture[2]
            transmitter = capture[3]
            ssid = capture[4]
            bssid = capture[5]

            if packetType == '5':
                if ssid not in mappone:
                    Hotstrippamilaminchia(ssid, bssid, power)
            for name, address in mappone.items():
                address.addbssid(bssid)
            # if receiver != "ff:ff:ff:ff:ff:ff":
            #     strippatore = mappone[ssid]
            #     strippatore.updateClient(receiver, power)

            for name, address in mappone.items():
                address.printStatus()
            print("--------")

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
