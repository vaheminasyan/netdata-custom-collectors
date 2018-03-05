# -*- coding: utf-8 -*-
# Description: example netdata python.d module
# Author: Pawel Krupa (paulfantom)

from subprocess import Popen, PIPE, check_output
import re
import sys
import time

from bases.FrameworkServices.SimpleService import SimpleService

# Global VARS
# default module values
update_every = 1
priority = 90000
retries = 60
#
ORDER = ['conntrack']
CHARTS = {
    'conntrack': {
        'options': ['conntrack', 'Conntrack Count', 'count', 'conntrack', 'conntrack', 'line'],
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

    def get_conntrack(self):
        metrics = dict()
        keys = ['conntrack_max', 'conntrack_count', 'conntrack_percent']

        c_max = str(self.runcommand('/sbin/sysctl net.nf_conntrack_max')[0])
        metrics[keys[0]] = 100000000.0 * (float(re.search(r'([0-9]+)', c_max).group(1)))

        c_count = str(self.runcommand('/sbin/sysctl net.netfilter.nf_conntrack_count')[0])
        metrics[keys[1]] = 100000000.0 * (float(re.search(r'([0-9]+)', c_count).group(1)))

        metrics[keys[2]] = 100000000.0 * ((float(metrics[keys[1]]) * 100.0) / float(metrics[keys[0]]))
        sys.stderr.write('kannasun' + str(metrics) + '\n')
        return metrics

    def _get_data(self):
        data = self.get_conntrack()
        for key in data:
            if key not in self.charts['conntrack']:
                self.charts['conntrack'].add_dimension([key, key, 'absolute', 1, 100000000])
        return data
