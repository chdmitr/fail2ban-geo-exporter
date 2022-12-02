import re
from .f2b_socket import F2BSocket
from datetime import datetime as dt
from pathlib import Path


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class F2BClient:
    def __init__(self, sock_path: str) -> dict:
        print('Using socket file', sock_path)
        if not Path(sock_path).is_socket():
            raise FileNotFoundError(f'{sock_path} not found')
        self.sock_path = sock_path

    def _send_cmd(self, command: str) -> tuple:
        with F2BSocket(sock_path=self.sock_path) as s:
            return s.send(command.split(' '))

    def _ban_ips_parse(self, ip_raw: str) -> dict:
        ip, date, time, _, ban_time, _, exp_date, exp_time \
            = re.split(r'\s+', ip_raw)
        report = dict(
            ip=ip,
            date_of_ban=dt.strptime(date + ' ' + time, DATE_FORMAT),
            ban_exp_date=dt.strptime(exp_date + ' ' + exp_time, DATE_FORMAT),
            ban_time=int(ban_time)
        )
        return report

    def get_jails(self) -> tuple:
        return self._send_cmd('status')[1][1][1:]

    def get_jail_ban_ips(self, jail: str) -> list[dict]:
        cmd = f'get {jail} banip --with-time'
        ips_raw = self._send_cmd(cmd)[1]
        return list(map(self._ban_ips_parse, ips_raw))

    def get_jail_ban_time(self, jail: str) -> int:
        return self._send_cmd(f'get {jail} bantime')[1]

    def get_jail_status(self, jail: str) -> dict:
        cmd = f'status {jail}'
        filter, action = self._send_cmd(cmd)[1]
        return dict(filter[1] + action[1])
