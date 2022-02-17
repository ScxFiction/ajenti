import subprocess

from ajenti.api import *

from api import *
from nctp_linux import *


@plugin
class DebianNetworkConfig (LinuxIfconfig, INetworkConfig):
    platforms = ['debian']

    interfaces = None

    def __init__(self):
        self.rescan()

    def rescan(self):
        self.interfaces = {}

        try:
            with open('/etc/network/interfaces') as f:
                ss = f.read().splitlines()
        except IOError as e:
            return

        auto = []

        while len(ss) > 0:
            line = ss[0].strip(' \t\n')
            if len(line) > 0 and line[0] != '#':
                a = line.split(' ')
                for s in a:
                    if s == '':
                        a.remove(s)
                if (a[0] == 'auto'):
                    auto.append(a[1])
                elif (a[0] == 'allow-hotplug'):
                    pass
                elif (a[0] == 'iface'):
                    tmp = NetworkInterface()
                    tmp.addressing = a[3]
                    tmp.type = a[2]
                    e = self.get_iface(a[1], self.detect_iface_bits(tmp))
                    del tmp
                    e.type = a[2]
                    e.addressing = a[3]
                    e.devclass = self.detect_dev_class(e)
                    try:
                        e.up = 'UP' in subprocess.check_output(['ifconfig', e.name])
                    except:
                        e.up = False
                else:
                    e.params[a[0]] = ' '.join(a[1:])
            ss = ss[1:] if len(ss) > 1 else []
        for x in auto:
            if x in self.interfaces:
                self.interfaces[x].auto = True

    def get_iface(self, name, bits):
        if name not in self.interfaces:
            self.interfaces[name] = NetworkInterface()
            self.interfaces[name].bit_classes = bits
            self.interfaces[name].name = name
        return self.interfaces[name]

    def save(self):
        with open('/etc/network/interfaces', 'w') as f:
            for i in self.interfaces:
                self.save_iface(self.interfaces[i], f)
        return

    def save_iface(self, iface, f):
        if iface.auto:
            f.write(f'auto {iface.name}' + '\n')
        f.write('iface %s %s %s\n' % (iface.name, iface.type, iface.addressing))
        for x in iface.params:
            if iface.params[x]:
                f.write('\t%s %s\n' % (x, iface.params[x]))
        f.write('\n')
