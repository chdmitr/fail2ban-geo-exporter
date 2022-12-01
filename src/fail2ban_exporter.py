import yaml
import argparse
import geoip2
from prometheus_client import make_wsgi_app, PROCESS_COLLECTOR, \
                                             PLATFORM_COLLECTOR, \
                                             GC_COLLECTOR
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from wsgiref.simple_server import make_server
from f2b.f2b_client import F2BClient
from datetime import datetime as dt
from pathlib import Path


DEFAULT_SOCKET_PATH = '/f2b-exporter/fail2ban.sock'


class IPAddress:
    def __init__(self, ip: str, date_of_ban: dt,
                 ban_exp_date: dt, geo_info: dict = {}):
        self.ip_address = ip
        self.date_of_ban = date_of_ban
        self.ban_exp_date = ban_exp_date
        self.geo_info = geo_info


class Jail:
    def __init__(self, name: str, ban_time: int,
                 geo_provider: object, ip_list: list = []):
        self.geo_provider = geo_provider
        self.name = name
        self.ban_time = ban_time
        self.ip_list = self._fill_ips_with_geo(ip_list=ip_list)

    def _fill_ips_with_geo(self, ip_list: list = []) -> list[IPAddress]:
        ip_geo = []
        for ip_dict in ip_list:
            geo_info = self.geo_provider.annotate(ip_dict.get('ip'))
            ip_geo.append(IPAddress(ip=ip_dict.get('ip'),
                                    date_of_ban=ip_dict.get('date_of_ban'),
                                    ban_exp_date=ip_dict.get('ban_exp_date'),
                                    geo_info=geo_info))
        return ip_geo


class F2bCollector:
    def __init__(self, config: str):
        self.geo_provider = self._import_provider(config)
        try:
            socket_path = config['f2b']['socket_path']
        except KeyError:
            socket_path = DEFAULT_SOCKET_PATH
        self.f2b_client = F2BClient(sock_path=socket_path)
        self.jails = []
        self.extra_labels = sorted(self.geo_provider.get_labels())

    def _import_provider(self, config: dict) -> geoip2:
        if config['geo']['enabled']:
            class_name = config['geo']['provider']
            mod = __import__('geoip_provider.{}'.format(class_name.lower()),
                             fromlist=[class_name])
        else:
            class_name = 'BaseProvider'
            mod = __import__('geoip_provider.base', fromlist=['BaseProvider'])

        geo_provider = getattr(mod, class_name)
        return geo_provider(config)

    def parse_f2b_jails(self, jails) -> list[Jail]:
        jails_ips = []
        for jail in jails:
            ip_list = self.f2b_client.get_jail_ban_ips(jail=jail)
            ban_time = self.f2b_client.get_jail_ban_time(jail=jail)
            jails_ips.append(Jail(name=jail,
                                  ban_time=ban_time,
                                  ip_list=ip_list,
                                  geo_provider=self.geo_provider))
        return jails_ips

    def expose_jails_status(self, jails) -> list[GaugeMetricFamily]:
        metric_labels = ['jail']
        parseKeys = {
            'Currently failed': ('fail2ban_failed_current',
                                 'Number of currently failed connections.'),
            'Total failed': ('fail2ban_failed_total',
                             'Total number of failed connections.'),
            'Currently banned': ('fail2ban_banned_current',
                                 'Number of currently banned IP addresses.'),
            'Total banned': ('fail2ban_banned_total',
                             'Total number of banned IP addresses.')
        }

        gauges = []
        for jail in jails:
            jail_status = self.f2b_client.get_jail_status(jail)
            for metric, value in jail_status.items():
                if metric not in parseKeys.keys():
                    continue
                gauge = GaugeMetricFamily(parseKeys[metric][0],
                                          parseKeys[metric][1],
                                          labels=metric_labels)
                gauge.add_metric([jail], value)
                gauges.append(gauge)
        return gauges

    def expose_banned_ips(self, jails: list) -> GaugeMetricFamily:
        metric_labels = ['ip', 'jail', 'date_of_ban'] + self.extra_labels
        gauge = GaugeMetricFamily('fail2ban_banned_ip',
                                  'IP banned by fail2ban',
                                  labels=metric_labels)

        for jail in jails:
            for ip in jail.ip_list:
                date_of_ban_unix = str(int(ip.date_of_ban.timestamp())) + '000'
                values = [ip.ip_address, jail.name, date_of_ban_unix] + \
                         [ip.geo_info.get(x) for x in self.extra_labels]
                gauge.add_metric(values, 1)

        return gauge

    def collect(self) -> GaugeMetricFamily:
        jails = self.f2b_client.get_jails()
        enriched_jails = self.parse_f2b_jails(jails)
        yield self.expose_banned_ips(jails=enriched_jails)
        for gauge in self.expose_jails_status(jails=jails):
            yield gauge


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf-file", type=str, default='conf.yml')
    conf_file = parser.parse_args().conf_file

    if not Path(conf_file).is_file():
        print(f'Config file "{conf_file}" not found')
        exit(1)

    with open(conf_file) as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)

    REGISTRY.unregister(PROCESS_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.register(F2bCollector(conf))

    app = make_wsgi_app()
    print("Starting fail2ban exporter.",
          f"Listen {conf['server']['listen_address']}" +
          f":{conf['server']['port']}")
    httpd = make_server(host=conf['server']['listen_address'],
                        port=conf['server']['port'],
                        app=app)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
