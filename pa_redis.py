# -*- coding: utf-8 -*-
# Description: Netdata pythond module, which does monitor redis master link status.
# It exposes metric for prometheus as 'netdata_redis_stats_average'
# Author: Vahe Minasyan (vaheminasyan)

from subprocess import check_output
import re

from bases.FrameworkServices.SimpleService import SimpleService


# Global VARS
# default module values
update_every = 1
priority = 90000
retries = 99999999
#
ORDER = ['pa_redis']
CHARTS = {
    'pa_redis': {
        'options': ['replication', 'Redis Info', 'stats', 'redis', 'redis', 'line'],
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

    def get_repl(self): # Only gets 'master_link_status' metric for now.
        metrics = dict()
        keys = list()  # keys = ['conntrack_max', 'conntrack_count', 'conntrack_percent']
        values = list()
        out = self.runcommand('/usr/bin/redis-cli info replication')[1:-1]
        # Extract keys
        for item in out:  # Strip both sides of colon. First are keys, second are values
            keys.append(re.match(r'([^:]+)', item).group(1))
            values.append(re.search(r':([^:]+)', item).group(1).replace('\r', ''))

        for i, k in zip(keys[:], values[:]):
            if i != 'master_link_status':
                keys.pop(keys.index(i))
                values.pop(values.index(k))
            else:
                if k == 'up':
                    val = 1
                else:
                    val = 0
                metrics[i] = 100000000.0 * val

        return metrics

#        c_max = str(self.runcommand('/sbin/sysctl net.nf_conntrack_max')[0])
#        metrics[keys[0]] = 100000000.0 * (float(re.search(r'([0-9]+)', c_max).group(1)))
#
#        c_count = str(self.runcommand('/sbin/sysctl net.netfilter.nf_conntrack_count')[0])
#        metrics[keys[1]] = 100000000.0 * (float(re.search(r'([0-9]+)', c_count).group(1)))
#
#        metrics[keys[2]] = 100000000.0 * ((float(metrics[keys[1]]) * 100.0) / float(metrics[keys[0]]))
#        return metrics

    def _get_data(self):
        data = self.get_repl()
        for key in data:
            if key not in self.charts['pa_redis']:
                self.charts['pa_redis'].add_dimension([key, key, 'absolute', 1, 100000000])
        return data
