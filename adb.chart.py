# -*- coding: utf-8 -*-
# Description: example netdata python.d module
# Author: Pawel Krupa (paulfantom)

import random
from subprocess import Popen, PIPE, check_output
import re
import sys
import time

from bases.FrameworkServices.SimpleService import SimpleService

# Global VARS
adb = '/opt/android-sdk-linux/platform-tools/adb'
# default module values
update_every = 1
priority = 90000
retries = 60
#
ORDER = ['battery', 'device_cpu']
CHARTS = {
    'battery': {
        'options': ['Battery', 'Small title battery', '%', 'battery', 'adb_battery', 'line'],
        'lines': [
            # Generate automatically
        ]
    },
    'device_cpu': {
        'options': ['Cpu', 'Small title cpu', '%', 'cpu', 'adb_cpu', 'line'],
        'lines': [
            # Generate automatically
        ]
    }
}


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS

    @staticmethod
    def check():
        return True

    @staticmethod
    def runcommand(commands):
        a = check_output(commands.split(' ')).decode('utf-8').split('\n')
        return a

    # Checked, Working
    def c_devices(self):
        devices = dict()
        try:
            devs = self.runcommand('{0} devices -l'.format(adb))[1:-2]
        except AttributeError:
            sys.stderr.write('adb: ERROR finding device(s). Exiting.\n')
            sys.exit(1)

        for i in devs[:]:
            uuid = re.search(r'([0-9a-z]+)( .+)', str(i)).group(1)
            try:
                model = re.search(r'.+?model:([a-zA-Z0-9_-]+) .+', str(i)).group(1)
                devices[uuid] = model
            except AttributeError:
                sys.stderr.write('adb: ERROR There is unauthorized device. Passing\n')
                pass
        return devices

    # Checked, Working
    def c_battery(self, uid):
        uid = str(uid)
        result = self.runcommand('{0} -s {1} shell  dumpsys battery'.format(adb, uid))
        for i in result:
            if re.search(r'level[^0-9]+([0-9]+)', i):
                try:
                    level = re.search(r'([0-9]+)', i).group(1)
                    return float(level)
                except AttributeError:
                    sys.stderr.write('adb: ERROR finding device battery level. Passing.\n')
                    return -1
        return -111

#    # Checked, Working: Version
#    def c_version(self, uid):
#        uid = str(uid)
#        result = str(self.runcommand('{0} -s {0} shell getprop ro.build.version.release'.format(adb, uid))[0])
#        sys.stderr.write(result)
#        return result

    def c_cpu(self, uid):
        uid = str(uid)
        result = str(self.runcommand('{0} -s {1} shell dumpsys cpuinfo'.format(adb, uid))[-2])
        try:
            overall = re.match(r'([0-9.]+)', result).group(1)
            return float(overall)
        except AttributeError:
            sys.stderr.write('adb: ERROR finding CPU usage. Passing.\n')
            return -1

    def _get_data(self):
        data = {}
        # Get Devices(uuid:model)
        d = self.c_devices()

        for i in d:
            # Get Battery
            dimension_id = str('{0}_cpu'.format(i))
            if dimension_id not in self.charts['battery']:
                self.charts['battery'].add_dimension([dimension_id, d[i]])
            data[dimension_id] = self.c_battery(i)
            # Get CPU
            dimension_id = str('{0}_battery'.format(i))
            if dimension_id not in self.charts['device_cpu']:
                self.charts['device_cpu'].add_dimension([dimension_id, d[i]])
            data[dimension_id] = self.c_cpu(i)
        return data
