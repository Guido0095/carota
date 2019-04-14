#!/usr/bin/env python3
import subprocess
from datetime import datetime, timedelta
from threading import Thread
import shlex
import sys
import io
import firebase_admin
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout
from firebase_admin import credentials, db

mappone = {}

class Hotspot:
    def __init__(self, ssid, bssid, power):
        self.ssid = ssid
        self.bssid = [bssid]
        self.clients = {}
        self.powerarray = [int(power)]
        self.lastseen = datetime.now()
        self.power = int(power)
        mappone[self.ssid] = self

    def updateClient(self, mac, power):
        now = datetime.now()
        if int(mac[:2], 16) & 1 == 0:
            self.lastseen = now
            self.clients[mac] = now
            if len(self.powerarray) > 20:
                del self.powerarray[0]
            if power != '':
                self.powerarray.append(int(power))
            self.power = int(sum(self.powerarray)/len(self.powerarray))

    def printStatus(self):
        if self.ssid != "x":
            print(self.power, "  ", self.ssid, "  ", str(len(self.clients)), list(self.clients.keys()))

    def addbssid(self, bssid, power):
        if bssid not in self.bssid:
            self.bssid.append(bssid)
            self.lastseen = datetime.now()
            self.power = int(power)
        else:
            return False

    def givemessid(self, mac1, mac2):
        if mac1 in self.bssid:
            return mac2, self.ssid
        elif mac2 in self.bssid:
            return mac1, self.ssid


class NetTest:
    def testTshark(self, iface):

        cmd = 'tshark -l -I -Y "wlan.fc.type_subtype != 4" -e "wlan_radio.signal_dbm" -e "wlan.fc.type_subtype" -e "wlan.ra" -e "wlan.ta" -e "wlan.ssid" -e "wlan.bssid" -Tfields -i' + iface
        args = shlex.split(cmd)
        tshark = subprocess.Popen(args, stdout=subprocess.PIPE)

        cred = credentials.Certificate('stachiave.json')

        try:
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://stocazzo-cc471.firebaseio.com/'
            })
            child = 'ACCESS POINTS'
            ref = db.reference(child)
        except:
            print('No connection with the Firebase Database')
            pass

        update = datetime.now() - timedelta(seconds=5)
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
                    Hotspot(ssid, bssid, power)
                else:
                    address = mappone[ssid]
                    address.addbssid(bssid, power)
            elif receiver != "ff:ff:ff:ff:ff:ff":
                ret = ''
                if transmitter != '0':
                    for name, address in mappone.items():
                        if address.givemessid(receiver, transmitter) is not None:
                            mac, ret = address.givemessid(receiver, transmitter)
                            break
                    if ret != '':
                        strippatore = mappone[ret]
                        strippatore.updateClient(mac, power)

            copymappone = []

            for name, address in mappone.items():
                time = (datetime.now() - timedelta(seconds=60))
                if address.lastseen < time:
                    copymappone.append(name)
            for netname in copymappone:
                del mappone[netname]
            for name, address in mappone.items():
                clienttodel = []
                for client, lastconnection in address.clients.items():
                    time = (datetime.now() - timedelta(seconds=60))
                    if lastconnection < time:
                        clienttodel.append(client)
                for clientmac in clienttodel:
                    del address.clients[clientmac]
            if update < (datetime.now() - timedelta(seconds=5)):
                update = datetime.now()
                for name, address in mappone.items():
                    address.printStatus()
                    try:
                        ref.update({
                            name:
                                {
                                    'NUMBER OF CLIENTS': str(len(address.clients)),
                                    'SINGNAL POWER IN dB': address.power
                                }
                        })
                    except:
                        pass

                try:
                    if ref.get(False, True) is not None:
                        for key in ref.get(False, True):
                            if key not in mappone:
                                db.reference(child + '/' + key).delete()
                except:
                    pass

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
    if len(sys.argv) == 2:
        iface = sys.argv[1]
    else:
        print('\nInvalid nuber of arguments.')
        print('\nEx:    Python3.7 temp.py wlan0')
        sys.exit(0)
    net = NetTest()
    net.run(iface)
