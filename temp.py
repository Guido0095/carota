#!/usr/bin/env python3
import subprocess
from threading import Thread
import shlex
import sys
import io


class ARPSniffer:
    def testTshark(self, iface):
        print(f"Testing if tshark works. Using {iface}")

        cmd = 'tshark -l -I -e "wlan_radio.signal_dbm" -e "wlan_radio.start_tsf" -e "wlan_radio.end_tsf" -e ' \
              '"wlan.fc.type_subtype" -e "wlan.ra" -e "wlan.ta" -e "wlan.ssid" -Tfields -i' + iface
        args = shlex.split(cmd)
        tshark = subprocess.Popen(args, stdout=subprocess.PIPE)
        for line in io.TextIOWrapper(tshark.stdout, encoding="utf-8"):
            print('Dio Cane: %s' % line.rstrip())

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
    arps = ARPSniffer()
    arps.run('wlp2s0')
