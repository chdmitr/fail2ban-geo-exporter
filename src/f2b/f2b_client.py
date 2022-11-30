import re
from .f2b_socket import F2BSocket
from datetime import datetime as dt


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class F2BClient:
    def __init__(self, sock_path):
        self.sock_path = sock_path

    def __send_cmd(self, command):
        with F2BSocket(sock_path=self.sock_path) as s:
            return s.send(command.split(' '))

    def __ban_ips_parse(self, ip_raw):
        ip, date, time, _, ban_time, _, exp_date, exp_time = re.split(r'\s+', ip_raw)
        report = dict(
            ip=ip,
            date=dt.strptime(date + ' ' + time, DATE_FORMAT),
            bantime=ban_time,
            exp_date=dt.strptime(exp_date + ' ' + exp_time, DATE_FORMAT)
        )
        return report

    def get_jails(self):
        return self.__send_cmd('status')[1][1][1:]

    def get_jail_ban_ips(self, jail):
        cmd = f'get {jail} banip --with-time'
        ips_raw = self.__send_cmd(cmd)[1]
        return list(map(self.__ban_ips_parse, ips_raw))

    def get_jail_status(self, jail):
        cmd = f'status {jail}'
        filter, action = self.__send_cmd(cmd)[1]
        return dict(filter[1] + action[1])
