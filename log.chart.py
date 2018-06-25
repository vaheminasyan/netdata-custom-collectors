# -*- coding: utf-8 -*-
# esps_log.chart.py
# Description: Netdata pythond module, which does monitor log files for specified patterns.
# Author: Vahe Minasyan (vaheminasyan)

import sys
from re import search, match
from subprocess import check_output
from bases.FrameworkServices.LogService import LogService

update_every = 10
retries = 100000000


ORDER = ['example']

CHARTS = {
    'example': {
        'options': [None, 'example', 'rate', 'example', 'example', 'line'],
        'lines': [
                # Generated dynamically
        ]},
}


class Service(LogService):
    def __init__(self, configuration=None, name=None):
        LogService.__init__(self, configuration=configuration, name=name)
        self.directory = self.configuration.get('dir', '/var/log/')
        self.file_name = self.configuration.get('file', r'syslog')
        self.log_path = self.directory + [x for x in check_output(['ls', self.directory]).split('\n') if match(self.file_name,x)][0]
        self.patterns = self.configuration.get('patterns')
        self.order = ORDER
        self.definitions = CHARTS

    def logik(self,msg):
        sys.stderr.write('logmonitor: {0}\n'.format(str(msg)))

    def _get_data(self):
        name = self.name
        self.charts.add_chart([name, None, self.log_path, 'count', self.file_name, 'log', 'logMonitor', 'line', 'log'])
        try:
            pathik = self.directory + [x for x in check_output(['ls', self.directory]).split('\n') if match(self.file_name,x)][0]
        except:
            pathik = self.log_path

        if pathik != self.log_path:
            self.log_path = pathik

        result = dict()
        for pattern in self.patterns:
            result[pattern] = 0

        try:
            for line in self._get_raw_data():
                self.logik('line: {0}'.format(line))
                for reg_ex in self.patterns:
                    if search(reg_ex, line):
                        result[reg_ex] += 1
                    if reg_ex not in self.charts[name]:
                        self.charts[name].add_dimension([reg_ex, reg_ex, 'absolute', 1, 1])
            # self.logik('for end:{0}::'.format(result))
            return result
        except (ValueError, AttributeError):
            return None
