# fail2ban-geo-exporter

https://github.com/vdcloudcraft/fail2ban-geo-exporter#readme

# Changes
- Added the ability to receive geo-information about IP from https://ipapi.co/. It takes time to poll the current list when starting the exporter (**need to register to get access_key**)
- Disabled grouping
- Changed sqlite database query logic to fail2ban default socket request `/var/run/fail2ban/fail2ban.sock`

## Changes in this fork
- Added support for IPApi free tier api

Works on Fail2Ban v1.0.2
[Grafana dashboards](grafana/) work on Grafana v9.3.0
## Docker example
```bash
# Please use your host's timezone to display the correct time
docker run -it --rm \
    -v ./conf.yml:/f2b-exporter/conf.yml \
    -v /var/run/fail2ban/fail2ban.sock:/f2b-exporter/fail2ban.sock \
    -p 9332:9332 \
    -e TZ=Europe/London \
    --name fail2ban-geo-exporter \
    chdmitr/fail2ban-geo-exporter
```

## Docker-compose example
```yaml
version: '3.8'

networks:
  monitoring:
    driver: bridge

services:
  f2b_exporter:
    image: chdmitr/fail2ban-geo-exporter
    container_name: f2b-exporter
    # Please use your host's timezone to display the correct time
    environment:
      - TZ=Europe/London
    volumes:
      - /var/run/fail2ban/fail2ban.sock:/f2b-exporter/fail2ban.sock
      - /path/conf.yml:/f2b-exporter/conf.yml
      # for MaxmindDB
      # - /path/GeoLite2-City.mmdb:/f2b-exporter/db/GeoLite2-City.mmdb:ro
    restart: unless-stopped
    networks:
      - monitoring
```

## Example config for IPApi (free tier)
```yaml
server:
  listen_address: 0.0.0.0
  port: 9332
geo:
  enabled: True
  provider: IPApiFree
# Optional
# f2b:
#   socket_path: /f2b-exporter/fail2ban.sock
```

## Example config for IPApi (paid tiers)
```yaml
server:
  listen_address: 0.0.0.0
  port: 9332
geo:
  enabled: True
  provider: IPApi
  ipapi:
    access_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Optional
# f2b:
#   socket_path: /f2b-exporter/fail2ban.sock
```

## Example config for MaxmindDB
```yaml
server:
  listen_address: 0.0.0.0
  port: 9332
geo:
  enabled: true
  provider: MaxmindDB
  maxmind:
    db_path: /f2b-exporter/db/GeoLite2-City.mmdb
    ## Uncomment the following section to set default values for IPs that are not in the database
    ## Otherwise entry will be discarded
    # on_error:
    #   city: Error
    #   latitude: 0
    #   longitude: 0
```
