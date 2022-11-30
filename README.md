# fail2ban-geo-exporter

https://github.com/vdcloudcraft/fail2ban-geo-exporter#readme

# Changes
Added the ability to receive geo-information about IP from https://ipapi.co/. It takes time to poll the current list when starting the exporter
```yaml
server:
  listen_address: <ip>
  port: <port>
geo:
  enabled: True
  provider: IPApi
  enable_grouping: False
f2b:
  conf_path: /etc/fail2ban
  db: /var/lib/fail2ban/fail2ban.sqlite3
```
